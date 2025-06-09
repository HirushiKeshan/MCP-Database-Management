# mysql_utils.py
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

def fetch_employees_by_department(dept: str):
    try:
        conn = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST"),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DATABASE"),
        )
        if conn.is_connected():
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, department FROM employees WHERE department = %s", (dept,))
            rows = cursor.fetchall()
            return rows
    except Error as e:
        return f"MySQL Error: {e}"
    finally:
        if conn.is_connected():
            conn.close()
