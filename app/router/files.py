from pathlib import Path
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends
from fastapi import File as FastAPIFile
from fastapi import Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlmodel import Session, create_engine, select

from ..auth import get_current_user
from ..config import STORAGE_ROOT
from ..db import get_session
from ..models import File, Folder, User
from ..query import get_owned_file, get_owned_folder
from ..schemas import FolderChildrenResponse, FolderCreate
from ..utils import ensure_storage_exist, sanitize_filename

router = APIRouter()
engine = create_engine("sqlite:///database.db")


@router.get("/folder/{folder_id}", response_model=FolderChildrenResponse)
def get_folder_children(
    folder_id: UUID,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Return list of files and folders metadata
    """
    folder = get_owned_folder(user, folder_id, session)
    return folder


@router.post("/folder", response_model=Folder)
def create_folder(
    payload: FolderCreate,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Create a new folder under a specific parent
    """
    parent_id = payload.parent_id
    if parent_id is None:
        parent_id = user.top_folder_id

    get_owned_folder(user, parent_id, session)
    existing = session.exec(
        select(Folder)
        .where(Folder.folder_name == payload.folder_name)
        .where(Folder.parent_id == parent_id)
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Folder with this name already exists in the parent folder",
        )

    new_folder = Folder(
        folder_name=payload.folder_name,
        owner_id=user.id,
        parent_id=parent_id,
    )
    ensure_storage_exist(user, new_folder)
    session.add(new_folder)
    session.commit()
    session.refresh(new_folder)

    return new_folder


@router.delete("/folder/{folder_id}", response_model=Folder)
def delete_folder(
    folder_id: UUID,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Delete a folder and all its contents, then return the deleted folder
    """
    folder = get_owned_folder(user, folder_id, session)
    session.delete(folder)
    session.commit()

    # remove object data from filesystem
    folder_path = STORAGE_ROOT / str(user.id) / str(folder_id)
    try:
        if folder_path.exists():
            for p in sorted(folder_path.rglob("*"), reverse=True):
                if p.is_file() or p.is_symlink():
                    p.unlink(missing_ok=True)
                elif p.is_dir():
                    p.rmdir()
            folder_path.rmdir()
    except Exception:
        # Do not crash the API in case the clean up went wrong
        pass
    return folder


@router.get("/file/{file_id}")
def download_file(
    file_id: UUID,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    """
    Return the file if found and owned by the current user
    """
    file = get_owned_file(user, file_id, session)
    file_location = (
        STORAGE_ROOT / str(user.id) / str(file.folder_id) / str(file.filename)
    )

    if not file_location.exists() or not file_location.is_file():
        raise HTTPException(status_code=404, detail="Stored file not found")

    return FileResponse(
        path=file_location,
        filename=file.filename,
        media_type="application/octet-stream",
    )


@router.post("/file", response_model=File)
async def upload_file(
    folder_id: UUID = Form(...),
    uploaded: UploadFile = FastAPIFile(...),
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    """
    Upload a file into a specific folder.
    """

    folder = get_owned_folder(user, folder_id, session)

    original_name = sanitize_filename(uploaded.filename or "unnamed")

    existing = session.exec(
        select(File)
        .where(File.folder_id == folder.id)
        .where(File.filename == original_name)
        .where(File.owner_id == user.id)
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A file with this name already exists in the folder",
        )

    # Save to disk
    folder_path = ensure_storage_exist(user, folder)
    target_path = folder_path / original_name

    try:
        with target_path.open("wb") as out_f:
            content = await uploaded.read()
            out_f.write(content)
    finally:
        await uploaded.close()

    new_file = File(
        id=uuid4(),
        filename=original_name,
        owner_id=user.id,
        folder_id=folder.id,
    )
    session.add(new_file)
    session.commit()
    session.refresh(new_file)
    return new_file


@router.delete("/file/{file_id}", response_model=File)
def delete_file(
    file_id: UUID,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    """
    Delete a file.
    """
    file = get_owned_file(user, file_id, session)

    # remove object data from filesystem
    file_location = str(
        STORAGE_ROOT / str(user.id) / str(file.folder_id) / str(file.filename)
    )
    if file_location:
        try:
            if file_location.exists() and file_location.is_file():
                file_location.unlink(missing_ok=True)
        except Exception:
            # Do not crash the API in case the clean up went wrong
            pass

    session.delete(file)
    session.commit()
    return file
