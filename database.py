from flask import g
import sqlite3
import os

def connect_db():
    # Determine the path to the database based on the environment
    if os.getenv('FLASK_ENV') == 'production':
        # Use a relative path that will work on Render
        db_path = 'absence.db'
    else:
        # Local development path
        db_path = 'C:\\Users\\ANAS\\Desktop\\The-Abs-Project\\absence.db'
    
    sql = sqlite3.connect(db_path)
    sql.row_factory = sqlite3.Row
    return sql

def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db
