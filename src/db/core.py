import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()


HOST = os.environ.get("HOST")
USER = os.environ.get("USER")
PASSWORD = os.environ.get("PASSWORD")
DB = os.environ.get("DB")
PORT = os.environ.get("PORT")


def connection():
    return psycopg2.connect(
        user=USER, host=HOST, port=PORT, password=PASSWORD, database=DB
    )


def query(conn, sql):
    with conn.cursor() as cursor:
        cursor.execute(sql)
        result = cursor.fetchall()
        return result


def check(conn, sql, values):
    with conn.cursor() as cursor:
        cursor.execute(sql, values)
        result = cursor.fetchall()
        return result
    


def update(conn, sql, values, should_commit=True):
    with conn.cursor() as cursor:
        cursor.execute(sql, values)
        if should_commit:  # atomicity - ensure the update completes/fails entirely
            conn.commit()
