import psycopg2
from psycopg2 import pool
from utils.config import DATABASE_URL

connection_pool = None

def init_db_pool(min_conn=1, max_conn=10):
    global connection_pool
    connection_pool = psycopg2.pool.SimpleConnectionPool(
        min_conn, max_conn, dsn=DATABASE_URL
    )
    # Creating tables if they don't exist (script from schema.sql)
    create_tables()

def get_connection():
    return connection_pool.getconn()

def put_connection(conn):
    connection_pool.putconn(conn)

def create_tables():
    conn = get_connection()
    cur = conn.cursor()
    # Execute DDL from the provided schema.sql
    with open("schema.sql", "r") as f:
        sql = f.read()
    cur.execute(sql)
    conn.commit()
    cur.close()
    put_connection(conn)