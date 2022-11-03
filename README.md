# Library project

a7pd project

## Overview

Calls to database and endpoints are located in: [actions](actions.py)  
Datamodels: [Datamodels](datamodels.py)  
The connection to mongo db and testing of endpoints: [database file](database.py)  

[UI/FE is from this project](https://github.com/TomSchimansky/CustomTkinter)
but if you find better one or easier one that you can do something in please do so :see_no_evil:
prety much just trying stuff with it in [main.py](main.py)

## Connecting to database

You need connection string to connect to db  
create .env file in root folder as: api_key.env and it will be loaded from there  
example of connection string `mongodb+srv://USERNAME:PASSWORD@cluster0.i5qgq5p.mongodb.net/DATABASE_NAME?retryWrites=true&w=majority`  
replace:

* USERNAME - your username
* PASSWORD - your password
* DATABASE_NAME - name of database
