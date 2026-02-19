import pyodbc
from datetime import datetime
import os


# --------------- Connection String -----------------
DB_SERVER = os.getenv("DB_SERVER")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

conn_str = (
    f"DRIVER={{ODBC Driver 18 for SQL Server}};"
    f"SERVER={DB_SERVER},1433;"
    f"DATABASE={DB_NAME};"
    f"UID={DB_USER};"
    f"PWD={DB_PASSWORD};"
)

def get_db_connection():
    return pyodbc.connect(conn_str)

#--------------- Database and Table Creation -----------------
def init_db():

    # Step 1: Connect to master database
    master_conn_str = (
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={DB_SERVER},1433;"
        f"DATABASE=master;"
        f"UID={DB_USER};"
        f"PWD={DB_PASSWORD};"
    )

    conn_master = pyodbc.connect(master_conn_str)
    cursor_master = conn_master.cursor()

    cursor_master.execute("""
        IF DB_ID('ServiceHealthDB') IS NULL
            CREATE DATABASE ServiceHealthDB
    """)

    conn_master.commit()
    cursor_master.close()
    conn_master.close()

    # Step 2: Connect to actual DB
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='ServiceStatus' AND xtype='U')
        CREATE TABLE ServiceStatus (
            id INT PRIMARY KEY IDENTITY(1,1),
            Service NVARCHAR(100),
            Host NVARCHAR(100),
            Port NVARCHAR(10),
            Type NVARCHAR(20),
            Status NVARCHAR(20),
            Response_time FLOAT,
            Last_Checked DATETIME
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()

# ---------------- Insert Service Status -----------------
def insert_service_status(service, last_checked):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO ServiceStatus (Service, Host, Port, Type, Status, Response_time, Last_Checked)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            service["Service"],
            service["Host"],
            service["Port"],
            service["Type"],
            service["Status"],
            service["Response_time"],
            last_checked
        ))

        conn.commit()

    except Exception as e:
        print(f"[DB ERROR] {e}")

    cursor.close()
    conn.close()

# ---------------- Fetch All Records -----------------
def fetch_all_records():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM ServiceStatus ORDER BY Last_Checked DESC")
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    # Convert pyodbc Row → dict for dashboard
    records = []
    for row in rows:
        records.append({
            "id": row[0],
            "Service": row[1],
            "Host": row[2],
            "Port": row[3],
            "Type": row[4],
            "Status": row[5],
            "Response_time": row[6],
            "Last_Checked": row[7]
        })
    return records
