# Diagram Aliran Data

```mermaid
sequenceDiagram
    participant LOG as Log File<br/>(auth.log/syslog)
    participant AGT as Agent<br/>(endpoint)
    participant API as Flask API<br/>POST /event
    participant DB as SQLite<br/>Database
    participant RE as Rule Engine
    participant DASH as Web Dashboard
    participant USER as User/Admin

    loop Setiap 60 detik
        LOG-->>AGT: Baca baris log baru
        AGT->>AGT: Klasifikasikan event type
        AGT->>AGT: Cek direktori & service
        AGT->>API: HTTP POST {waktu, event, hostname, deskripsi}
        API->>DB: INSERT INTO events
        API->>RE: rule(data)
        RE->>RE: Cocokkan dengan aturan
        RE->>DB: INSERT INTO alerts (jika terdeteksi)
    end

    USER->>DASH: Buka browser
    DASH->>DB: SELECT * FROM events/alerts
    DB-->>DASH: Data events & alerts
    DASH-->>USER: Tampilkan di dashboard

    USER->>DASH: Pilih filter event
    DASH->>DB: SELECT WHERE event=?
    DB-->>DASH: Data terfilter
    DASH-->>USER: Tampilkan hasil filter
```

**Aliran Data:**
1. Agent membaca log file di endpoint → mengklasifikasikan event
2. Agent mengirim event ke SIEM server via HTTP POST (JSON)
3. Server menyimpan event ke SQLite
4. Rule Engine menganalisis event dan membuat alert jika perlu
5. Dashboard membaca dari database dan menampilkan ke user
6. Reporting module mengekspor ke CSV, JSON, dan TXT
