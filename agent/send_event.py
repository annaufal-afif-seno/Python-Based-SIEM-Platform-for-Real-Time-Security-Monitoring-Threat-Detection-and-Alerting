import sys
import requests
from datetime import datetime

SERVER_URL = "http://127.0.0.1:5001/event"

if len(sys.argv) < 2:
    print("Usage: python send_event.py <EVENT_TYPE> [deskripsi]")
    sys.exit(1)

event = sys.argv[1]
deskripsi = sys.argv[2] if len(sys.argv) > 2 else event

data = {
    "waktu": str(datetime.now()),
    "event": event,
    "hostname": "Endpoint-VM",
    "deskripsi": deskripsi,
}

try:
    r = requests.post(SERVER_URL, json=data, timeout=5)
    if r.status_code == 200:
        print(f"[OK] {event} berhasil dikirim")
    else:
        print(f"[ERROR] Server returned {r.status_code}")
except requests.exceptions.ConnectionError:
    print(f"[FAILED] Cannot reach server at {SERVER_URL}")
