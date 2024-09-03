from flask import g
import sqlite3

def connect_db():
    # Update the path to point to your database file
    sql = sqlite3.connect('C:\\Users\\ANAS\\Desktop\\The-Abs-Project\\absence.db')
    sql.row_factory = sqlite3.Row
    return sql

def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db
