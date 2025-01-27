# Eye - TUI Application

A Textual-based Terminal User Interface (TUI) application for viewing and
managing the cosmotech simulation platform.

## Installation

```sh
uv venv
uv pip install -e .
```

## Configuration
Create a .env file with the following configuration, replacing the <NAMESPACE> by
your tenant name:

```shell
host="https://kubernetes.cosmotech.com/cosmotech-api/<NAMESPACE>/v4"
server_url="https://kubernetes.cosmotech.com/keycloak/"
client_id="local test client"
realm_name="<NAMESPACE>"
client_secret_key="<client secret>"
```

## Usage

Activate the virtual environment:

```shell
source .venv/bin/activate
```

Get a summary of the object tree in the current namespace:

```shell
python3 eye/main.py
```

or use the app:

```shell
python3 eye/app.py
```
to get an various screens with an overview of the platform state