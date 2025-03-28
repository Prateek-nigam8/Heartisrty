import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",       # Change if needed
        password="1234",    # Your MySQL password
        database="heartistry"
    )
