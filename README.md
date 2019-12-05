# internship
A web application made in flask that covers:
- Flask basics
- database concepts
- user authentication

Information:
- Python 2.7.10
- Flask 1.1.1

#### Note: I cannot host a python application on Github pages, it's designed for simple static file hosting rather than dynamic webpages. Please clone this repo and run on your local server with the following steps

## Installation
After installing Python 2.7 and cloning the project, open a terminal within the project directory and install the following to meet the Pipfile requirements:

```csh
pip install flask
```
```csh
pip install flask_sqlalchemy
```
```csh
pip install flask_bcrypt
```
```csh
pip install flask_login
```

Next is to set up the database:
- Install TablePlus and follow these instructions to connect TablePlus to the Postgres Server
  - http://jonathansoma.com/lede/foundations-2019/sql-management/postgres-tableplus-import-query/
- Import 'dogs.sqlite3' onto TablePlus

## Setup
To run the application on Mac:

```csh
python hello.py
```
