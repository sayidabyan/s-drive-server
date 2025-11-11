# S-Drive-Server
S-Drive-Server is the backend component for S-Drive, a self-hosted cloud storage solution.

## Dependencies:
- python 3.12
- pip 25
## How to Run
- clone or grab the latest version of the repository [here](https://github.com/sayidabyan/s-drive-server/archive/refs/heads/master.zip)
- configure environment variable, either using `.env`  file or export each variable manually

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| STORAGE_ROOT | Root directory path for file storage | `/var/storage` or `./uploads` | No |
| DB_URL | Database connection URL, currently sqlite only | `sqlite:///database.db` | No |
| JWT_SECRET_KEY | Secret key for JWT signing | `your-secret-key-here` | Recommended |
| JWT_ACCESS_TOKEN_DURATION | Token expiration time in minutes | `60` | No |
| JWT_ALGORITHM | Algorithm for JWT encoding | `HS256` | No |
| DEFAULT_ADMIN_USERNAME | Default admin account username | `admin` | No |
| DEFAULT_ADMIN_PASSWORD | Default admin account password | `SecurePassword123!` | Recommended |
After you're done, you can continue and do
```
cd s-drive-server # or whatever you name the repo/folder
python -m venv venv
source venv/bin/activate

fastapi dev main.py
# OR
fastapi run main.py
```


## TODO
- File Sharing
- Tests
- Docker package
- nix package & module
