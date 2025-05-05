# DockerManager

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

A lightweight Python-based console tool to manage Docker containers for backend development. 
Supports container creation from templates or GitHub repositories, full lifecycle commands, log monitoring, and environment configuration.


## DESCRIPTION
DockerManager allows developers to create, delete, and manage Docker containers for backend services (Node.js, Django, Flask, etc.) using a guided command-line interface. 
It supports cloning GitHub repositories, injecting `.env` files, and monitoring logs.


## FEATURES
- Create containers from local templates or GitHub repos
- Customize exposed port and environment variables
- Auto-detect main entry file (e.g., server.js, index.js)
- Container lifecycle management:
  - Start
  - Stop
  - Restart
  - Pause
  - Unpause
- Log monitoring with live follow
- List all containers with status and port info


## USAGE
After running `python manager.py`, choose from the following options:
```markdown
1. Create container
2. Delete container
3. List all containers
4. Monitor logs
5. Manage container (start/stop/restart/pause)
6. Exit
```
### Creating a Container
- You can create a container from a local template or clone a GitHub repo.
- If a `.env` file is present, it will be passed to the container at runtime.
- The entry point (e.g., `server.js`) is auto-detected and used in the Dockerfile.

### Managing Containers
Supported commands during runtime:
- Restart a container
- Pause/unpause execution
- Start or stop containers


## REQUIREMENTS
- Docker
- Python 3.7+
- `docker` CLI installed and available on PATH
- Python packages:
```bash 
pip install python-dotenv
```


## NOTES
- Host network access is required if you use database services running on the host (e.g., MariaDB at `172.17.0.1`).
- If using GitHub repositories, ensure they contain a valid `package.json` (Node.js) or manage.py (Django) in the root or nested folder.


## AUTHOR
Created by Kenet Ortiz <br/>
2025