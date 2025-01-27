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

Port forward the services required by cosmotech-api (redis):

```shell
kubectl port-forward cosmotechredis-<NAMESPACE>-master-0 6379:6379 -n <NAMESPACE>
```
and start a local api:

```shell
./gradlew :cosmotech-api:bootRun
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
to get a summary of users and their roles