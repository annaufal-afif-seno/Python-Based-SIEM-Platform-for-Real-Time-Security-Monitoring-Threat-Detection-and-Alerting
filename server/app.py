from flask import Flask, request, render_template, jsonify
import sqlite3

from database import create_table
from rule_engine import rule

app = Flask(__name__, template_folder="../templates")

create_table()


@app.route("/")
def dashboard():
    selected_event = request.args.get("event")

    conn = sqlite3.connect("database/siem.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    if selected_event:
        cur.execute(
            "SELECT * FROM events WHERE event=? ORDER BY id DESC",
            (selected_event,),
        )
    else:
        cur.execute("SELECT * FROM events ORDER BY id DESC")

    events = cur.fetchall()

    cur.execute("SELECT * FROM alerts ORDER BY id DESC")
    alerts = cur.fetchall()

    cur.execute("SELECT DISTINCT event FROM events")
    event_types = cur.fetchall()

    total_events = len(events)
    total_alerts = len(alerts)

    conn.close()

    return render_template(
        "dashboard.html",
        events=events,
        alerts=alerts,
        event_types=event_types,
        selected_event=selected_event,
        total_events=total_events,
        total_alerts=total_alerts,
    )


@app.route("/event", methods=["POST"])
def receive_event():
    data = request.json

    conn = sqlite3.connect("database/siem.db")
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO events (waktu, event, hostname, deskripsi) VALUES (?, ?, ?, ?)",
        (data["waktu"], data["event"], data["hostname"], data["deskripsi"]),
    )
    conn.commit()
    conn.close()

    rule(data)

    return {"status": "success"}


@app.route("/api/events", methods=["GET"])
def api_events():
    conn = sqlite3.connect("database/siem.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM events ORDER BY id DESC")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return jsonify(rows)


@app.route("/api/alerts", methods=["GET"])
def api_alerts():
    conn = sqlite3.connect("database/siem.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM alerts ORDER BY id DESC")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return jsonify(rows)


@app.route("/api/report", methods=["GET"])
def api_report():
    conn = sqlite3.connect("database/siem.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) as count FROM events")
    total_events = cur.fetchone()["count"]

    cur.execute("SELECT COUNT(*) as count FROM alerts")
    total_alerts = cur.fetchone()["count"]

    cur.execute("SELECT event, COUNT(*) as count FROM events GROUP BY event")
    event_summary = [dict(r) for r in cur.fetchall()]

    cur.execute("SELECT severity, COUNT(*) as count FROM alerts GROUP BY severity")
    alert_summary = [dict(r) for r in cur.fetchall()]

    conn.close()

    return jsonify({
        "total_events": total_events,
        "total_alerts": total_alerts,
        "event_summary": event_summary,
        "alert_summary": alert_summary,
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
