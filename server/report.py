import sqlite3
import json

conn = sqlite3.connect("database/siem.db")
conn.row_factory = sqlite3.Row
cur = conn.cursor()

cur.execute("SELECT * FROM events")
events = [dict(row) for row in cur.fetchall()]

cur.execute("SELECT * FROM alerts")
alerts = [dict(row) for row in cur.fetchall()]

report = {
    "total_events": len(events),
    "total_alerts": len(alerts),
    "events": events,
    "alerts": alerts
}

with open("report/report.json", "w") as f:
    json.dump(report, f, indent=2, default=str)

conn.close()
print("Report JSON berhasil dibuat")
