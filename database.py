from flask import g
#import sqlite3
import psycopg2
from psycopg2.extras import DictCursor

'''
def connect_db():
    db_path = 'C:\\Users\\ANAS\\Desktop\\The-Abs-Project\\absence.db'
    sql = sqlite3.connect(db_path)
    sql.row_factory = sqlite3.Row
    return sql

def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db
'''

def connect_db():
    conn = psycopg2.connect('postgresql://abs_project_user:XvQmpauXnUqdhlwcG9zPa4R5oPTLNJsR@dpg-creo43rv2p9s73d13u2g-a.frankfurt-postgres.render.com/abs_project', cursor_factory=DictCursor)
    conn.autocommit = True
    return conn

def get_db():
    if 'postgres_db_conn' not in g:
        g.postgres_db_conn = connect_db()
        g.postgres_db_cur = g.postgres_db_conn.cursor()
    return g.postgres_db_cur

def close_db(error):
    if 'postgres_db_cur' in g:
        g.postgres_db_cur.close()
    if 'postgres_db_conn' in g:
        g.postgres_db_conn.close()
        


def init_db():
    db = connect_db()
    db[1].execute(open('schema.sql', 'r').read())
    
    
    db[1].close()
    db[0].close()