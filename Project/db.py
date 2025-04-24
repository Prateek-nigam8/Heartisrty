import mysql.connector
from dotenv import dotenv_values

env_vars = dotenv_values(".env")

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",       # Change if needed
        password=env_vars["DB_PASSWORD"],    # Your MySQL password
        database="heartistry"
    )
