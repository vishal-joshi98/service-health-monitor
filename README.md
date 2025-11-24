📊 Service Health Monitoring Dashboard

A real-time Service Health Monitoring System built using Python, Flask, APScheduler, SQL Server/MySQL, and Chart.js.
This tool continuously checks the status of critical application services (Port-based and Windows services), logs failures, and displays a visually rich dashboard for support teams.

🚀 Features
✅ Real-time Service Monitoring

Monitors services via:

Port checks (TCP connectivity)

Windows service checks (using psutil)

Response time measurement (ms)

Background monitoring independent of dashboard refresh

✅ Background Scheduler

Continuous health checks every X seconds using APScheduler

Logs only DOWN events to database (avoids unnecessary data flood)

Dashboard remains fast and responsive

✅ Interactive Web Dashboard

Built with Flask + HTML + CSS

Displays:

Live service status (Up/Down)

Response time

Host & Port info

Timestamp of last check

Auto-refresh supported

✅ 7-Day Down Event Trend Graph

Shows daily count of unique down services

Clean, professional bar chart built using Chart.js

Hover tooltips for more detail

✅ Database Logging (SQL Server / MySQL)

Stores:

Service name

Status

Response time

Timestamp

Only DOWN entries are logged (efficient storage)

Optimized queries for fast dashboard load

📁 Project Structure
service-health-check/
│── app.py               # Flask app + Routing + Scheduler + Dashboard logic
│── db.py                # Database connection + init + insert + fetch
│── services.json        # Configuration file for service definitions
│── templates/
│     └── dashboard.html # Web UI (status table + chart)
│── static/              # (Optional) JS/CSS
│── README.md

⚙️ Technologies Used
Backend

Python 3

Flask

APScheduler

psutil

socket (TCP checks)

Database

SQL Server (pyodbc) or

MySQL (mysql-connector-python)

Frontend

HTML5, CSS3

Chart.js

Auto-refresh meta tags

🧠 How It Works
1️⃣ Background Scheduler Runs Every X Seconds

Loops through services.json

Performs:

TCP port connection test

Windows service status check

Stores only DOWN records in DB

2️⃣ Dashboard Displays:

Live status table, taken from memory (live_status)

Last 7 days down events graph

History table (if needed)

3️⃣ Graph Construction

Fetches last 7 days from DB (efficient)

Groups by date

Counts unique down services per day

Chart.js renders clean 7-bar graph

🗄️ Example services.json
[
    {
        "Name": "Tomcat",
        "type": "PORT",
        "host": "localhost",
        "Port": 8080
    },
    {
        "Name": "DataExchangeRuntime",
        "type": "WIN_SERV"
    }
]

▶️ Running the Project
Step 1: Install dependencies
pip install flask apscheduler psutil mysql-connector-python pyodbc

Step 2: Update DB credentials in db.py
Step 3: Start the app
python app.py

Step 4: Visit the dashboard
http://localhost:5000/dashboard