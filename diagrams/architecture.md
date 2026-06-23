# Diagram Arsitektur Sistem

```mermaid
graph TB
    subgraph VM2["VM2 - Endpoint (Monitored)"]
        A1[Agent: log reader]
        A2[Agent: directory monitor]
        A3[Agent: service checker]
        A4[Agent: event sender]
        LOG[(/var/log/auth.log<br/>/var/log/syslog)]
        DIR[/etc, /tmp, /var/www]
        SVC[systemctl/service]
    end

    subgraph VM1["VM1 - SIEM Server"]
        API[Flask API<br/>POST /event]
        DB[(SQLite Database<br/>events + alerts)]
        RE[Rule Engine]
        DASH[Web Dashboard<br/>GET /]
        RPT[Reporting<br/>CSV / JSON / TXT]
    end

    A1 -->|baca baris baru| LOG
    A2 -->|monitor perubahan| DIR
    A3 -->|cek status| SVC
    A4 -->|HTTP POST JSON| API
    API -->|simpan| DB
    API -->|panggil| RE
    RE -->|tulis alert| DB
    DASH -->|baca| DB
    RPT -->|baca| DB
    DASH -->|render| HTML[Browser User]
```

**Teknologi:**
- VM: VirtualBox / VMware
- OS VM: Linux (Ubuntu Server)
- Bahasa: Python 3
- Framework Web: Flask
- Database: SQLite
- HTTP Client: requests
- Reporting: pandas (CSV), json (JSON)
