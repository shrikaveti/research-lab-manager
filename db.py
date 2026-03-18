import mysql.connector
from mysql.connector import Error

def get_conn():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="myroot",
        database="research_lab"
    )

def run_query(sql, params=None):
    conn = get_conn()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(sql, params or ())

        # For SELECT queries
        if sql.strip().lower().startswith("select"):
            rows = cursor.fetchall()
            cursor.close()
            return rows

        # For INSERT / UPDATE / DELETE
        conn.commit()
        affected = cursor.rowcount
        cursor.close()
        return affected

    finally:
        conn.close()
