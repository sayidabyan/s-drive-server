from typing import List, Optional
from uuid import UUID, uuid4

from sqlmodel import (
    Column,
    Field,
    ForeignKey,
    Relationship,
    Session,
    SQLModel,
    UniqueConstraint,
)


class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    is_admin: bool = Field(default=False)
    username: str = Field(index=True, unique=True)
    hashed_password: str
    top_folder_id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(ForeignKey("folder.id", ondelete="SET NULL"), nullable=True),
    )
    top_folder: Optional["Folder"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "User.top_folder_id"}
    )
    folders: List["Folder"] = Relationship(
        back_populates="owner",
        sa_relationship_kwargs={
            "foreign_keys": "Folder.owner_id",
            "passive_deletes": True,
        },
    )


class Folder(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("folder_name", "parent_id", name="uq_folder_name_parent"),
    )
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    folder_name: str = Field(index=True)
    owner_id: UUID = Field(
        sa_column=Column(ForeignKey("user.id", ondelete="CASCADE")),
    )
    owner: Optional[User] = Relationship(
        back_populates="folders",
        sa_relationship_kwargs={"foreign_keys": "Folder.owner_id"},
    )
    parent_id: Optional[UUID] = Field(
        sa_column=Column(ForeignKey("folder.id", ondelete="CASCADE")),
    )
    parent: Optional["Folder"] = Relationship(
        back_populates="child_folders",
        sa_relationship_kwargs={"remote_side": "Folder.id", "passive_deletes": True},
    )
    child_folders: List["Folder"] = Relationship(
        back_populates="parent", sa_relationship_kwargs={"passive_deletes": True}
    )

    files: List["File"] = Relationship(
        back_populates="folder", sa_relationship_kwargs={"passive_deletes": True}
    )


class File(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("filename", "folder_id", name="uq_filename_folder"),
    )
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    filename: str = Field(index=True)
    owner_id: UUID = Field(foreign_key="user.id")
    folder_id: UUID = Field(
        sa_column=Column(ForeignKey("folder.id", ondelete="CASCADE")),
    )
    folder: Folder = Relationship(back_populates="files")
