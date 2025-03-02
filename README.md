# Dockerized FastAPI

## Requirements
Check the following links:

[Python](https://www.python.org/doc/)

[Docker](https://docs.docker.com/)

[FastAPI](https://fastapi.tiangolo.com/learn/)

[Pydantic](https://docs.pydantic.dev/latest/)

[SQLAlchemy](https://www.sqlalchemy.org/)

[Redis](https://redis.io/docs/latest/)


## Installation

#### Install python3.11 in your machine
```
# Install python3.11
brew install python@3.11

# Add python3.11 to PATH
export PATH="/opt/homebrew/opt/python@3.11/bin:$PATH"

# Reload shell
source ~/.zshrc  
# or
source ~/.bash_profile

# Check version
python3 --version
```

#### Create virtual environment in project root
```
python3 -m venv .venv
```

#### Activate project virtual environment
```
source .venv/bin/activate
```

#### Deactivate project virtual environment
```
deactivate
```


#### Install project dependencies
```
# Install uv
pip3 install uv

# Install project dependencies
uv pip install -r requirements.in
```

#### Remove project dependencies locally
```
rm -rf .venv
```
