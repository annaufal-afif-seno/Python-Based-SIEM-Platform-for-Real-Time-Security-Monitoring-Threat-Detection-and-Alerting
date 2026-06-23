import sqlite3

def get_db():
    return sqlite3.connect("database/siem.db")

def rule(data):
    conn = get_db()
    cur = conn.cursor()
    event_type = data["event"]
    waktu = data["waktu"]

    rules = {
        "FAILED_SSH": ("HIGH", "Failed SSH login detected"),
        "SUCCESSFUL_SSH": ("LOW", "Successful SSH login"),
        "FAILED_SUDO": ("HIGH", "Failed sudo attempt detected"),
        "USER_CREATED": ("HIGH", "New user account created"),
        "USER_DELETED": ("HIGH", "User account deleted"),
        "PACKAGE_INSTALL": ("MEDIUM", "Package installation detected"),
        "SERVICE_STOP": ("MEDIUM", "Service stopped"),
        "SERVICE_START": ("LOW", "Service started"),
        "FILE_CREATED": ("MEDIUM", "File created"),
        "FILE_MODIFIED": ("MEDIUM", "File modified"),
        "FILE_DELETED": ("HIGH", "File deleted"),
        "CUSTOM_LOG": ("LOW", "Custom application log event"),
    }

    if event_type in rules:
        severity, message = rules[event_type]
        cur.execute(
            "INSERT INTO alerts (waktu, severity, pesan, event) VALUES (?, ?, ?, ?)",
            (waktu, severity, message, event_type),
        )
        conn.commit()

    conn.close()
