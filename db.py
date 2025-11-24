import pyodbc
from datetime import datetime

# --------------- Connection String -----------------
conn_str = ( "DRIVER={ODBC Driver 17 for SQL Server};" "SERVER=localhost,1433;" "DATABASE=ServiceHealthDB;" "TRUSTED_CONNECTION=yes;" )


def get_db_connection():
    return pyodbc.connect(conn_str)

#--------------- Database and Table Creation -----------------
def init_db():
    # Step 1: Connect to master DB and create ServiceHealthDB if missing
    conn_master = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost,1433;DATABASE=ServiceHealthDB;Trusted_Connection=yes;"
    )
    cursor_master = conn_master.cursor()

    cursor_master.execute("""
        IF DB_ID('ServiceHealthDB') IS NULL
            CREATE DATABASE ServiceHealthDB
    """)

    conn_master.commit()
    cursor_master.close()
    conn_master.close()

    # Step 2: Create table inside ServiceHealthDB
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
