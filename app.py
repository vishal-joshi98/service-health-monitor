from flask import Flask, jsonify, render_template
import socket, time, json, psutil
import datetime 
from apscheduler.schedulers.background import BackgroundScheduler
from db import init_db, insert_service_status, fetch_all_records
live_status = []

app = Flask(__name__)

with open("services.json", "r") as f:
    services = json.load(f)

# Create table if not exists
with app.app_context():
    init_db()

# ---------------------------------------------
# SERVICE CHECK FUNCTIONS
# ---------------------------------------------
def port_service(service):
    try:
        socket.create_connection((service["host"], service["Port"]), timeout=5)
        return "Up"
    except:
        return "Down"

def win_service(service):
    try:
        svc = psutil.win_service_get(service["Name"])
        status = svc.as_dict()["status"]
        return "Up" if status.lower() == "running" else "Down"
    except:
        return "Not Found"

# Background task (runs every 30 seconds)
def background_check():
    print("[Scheduler] Running background service check...")
    last_check = time.strftime("%Y-%m-%d %H:%M:%S")

    global live_status
    live_status = []   # reset before each run

    for service in services:
        start = time.time()

        if service["type"].upper() == "PORT":
            status = port_service(service)
        elif service["type"].upper() == "WIN_SERV":
            status = win_service(service)
        else:
            status = "Unknown"

        end = time.time()
        response_ms = round((end - start) * 1000, 2)

        record = {
            "Service": service["Name"],
            "Host": service.get("host", "localhost"),
            "Port": service.get("Port", "NA"),
            "Type": service["type"],
            "Status": status,
            "Response_time": response_ms,
            "Last_Checked": last_check
        }

        # Save LIVE status in memory
        live_status.append(record)

        # Insert only DOWN into DB
        if status != "Up":
            insert_service_status(record, last_check)
            print(f"[DB] Inserted DOWN status for {record['Service']}")

# Run first check immediately when app starts
with app.app_context():
    print("[INIT] Running first service check...")
    background_check()

# Start background scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(background_check, "interval", seconds=5)
scheduler.start()

# ---------------------------------------------
# ROUTES
# ---------------------------------------------
@app.route("/")
def home():
    return "Service Monitoring is Running"

@app.route("/health")
def health():
    return jsonify({"status": "Background checks running", "timestamp": time.ctime()})

@app.route("/dashboard")
def dashboard():
    history = fetch_all_records()

    # Build last 7 days range
    today = datetime.datetime.now().date()
    last_7_days = [(today - datetime.timedelta(days=i)) for i in range(6, -1, -1)]
    labels = [d.strftime("%Y-%m-%d") for d in last_7_days]

    # Dictionary for storing unique down services per day
    day_data = {label: {"services": set()} for label in labels}

    for h in history:
        ts = h["Last_Checked"]

        # Convert string timestamps to datetime
        if isinstance(ts, str):
            try:
                ts = datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
            except:
                continue

        day_str = ts.strftime("%Y-%m-%d")

        # Only count DOWN events
        if day_str in day_data and h["Status"].lower() != "up":
            day_data[day_str]["services"].add(h["Service"])  # UNIQUE only

    # Build chart data
    chart_labels = labels
    chart_values = [len(day_data[d]["services"]) for d in labels]  # number of unique services
    chart_services = [list(day_data[d]["services"]) for d in labels]  # convert sets to list

    return render_template(
        "dashboard.html",
        live=live_status,
        history=history,
        chart_labels=chart_labels,
        chart_values=chart_values,
        chart_services=chart_services
    )


# ---------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
