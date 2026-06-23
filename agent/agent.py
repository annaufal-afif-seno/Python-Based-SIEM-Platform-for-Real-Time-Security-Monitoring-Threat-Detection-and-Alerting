import os
import time
import subprocess
import requests
from datetime import datetime

SERVER_URL = "http://192.168.1.100:5000/event"
HOSTNAME = "Endpoint-VM"

LOG_PATHS = [
    "/var/log/auth.log",
    "/var/log/syslog",
    "/var/log/system.log",
]

WATCH_DIRS = ["/etc", "/tmp", "/var/www"]
SERVICES = ["ssh", "apache2", "nginx", "sshd", "ufw"]

LOG_FINGERPRINTS = {
    "Failed password": "FAILED_SSH",
    "Accepted password": "SUCCESSFUL_SSH",
    "Failed password for": "FAILED_SSH",
    "session opened for user": "SUCCESSFUL_SSH",
    "sudo": "FAILED_SUDO",
    "new user": "USER_CREATED",
    "delete user": "USER_DELETED",
    "install": "PACKAGE_INSTALL",
    "apt-get install": "PACKAGE_INSTALL",
    "dpkg": "PACKAGE_INSTALL",
    "stop": "SERVICE_STOP",
    "start": "SERVICE_START",
}


def send_event(event_type, deskripsi):
    data = {
        "waktu": str(datetime.now()),
        "event": event_type,
        "hostname": HOSTNAME,
        "deskripsi": deskripsi,
    }
    try:
        requests.post(SERVER_URL, json=data, timeout=5)
        print(f"[SENT] {event_type}: {deskripsi}")
    except requests.exceptions.ConnectionError:
        print(f"[FAILED] Cannot reach server {SERVER_URL}")


def tail_log(path):
    if not os.path.exists(path):
        return None

    try:
        result = subprocess.run(
            ["tail", "-n", "1", path],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.stdout.strip()
    except Exception:
        return None


def monitor_logs():
    for path in LOG_PATHS:
        if os.path.exists(path):
            line = tail_log(path)
            if line:
                for keyword, event_type in LOG_FINGERPRINTS.items():
                    if keyword.lower() in line.lower():
                        send_event(event_type, line[:200])
                        break


def monitor_directories():
    for d in WATCH_DIRS:
        if os.path.isdir(d):
            for f in os.listdir(d):
                fpath = os.path.join(d, f)
                if os.path.isfile(fpath):
                    mtime = os.path.getmtime(fpath)
                    age = time.time() - mtime
                    if age < 300:
                        send_event("FILE_CREATED", f"File baru: {fpath}")
                        break


def check_services():
    for svc in SERVICES:
        try:
            result = subprocess.run(
                ["systemctl", "is-active", svc],
                capture_output=True,
                text=True,
                timeout=5,
            )
            status = result.stdout.strip()
            if status == "active":
                send_event("SERVICE_START", f"Service {svc} is running")
            elif status == "inactive":
                send_event("SERVICE_STOP", f"Service {svc} is not running")
        except FileNotFoundError:
            try:
                result = subprocess.run(
                    ["service", svc, "status"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if "running" in result.stdout.lower():
                    send_event("SERVICE_START", f"Service {svc} is running")
                else:
                    send_event("SERVICE_STOP", f"Service {svc} is not running")
            except Exception:
                pass
        except Exception:
            pass


def send_custom_log():
    send_event("CUSTOM_LOG", "Periodic health check from endpoint agent")


if __name__ == "__main__":
    print("SIEM Agent started. Monitoring logs, services, and directories...")
    iteration = 0
    while True:
        monitor_logs()
        check_services()
        if iteration % 5 == 0:
            monitor_directories()
            send_custom_log()
        time.sleep(60)
        iteration += 1
