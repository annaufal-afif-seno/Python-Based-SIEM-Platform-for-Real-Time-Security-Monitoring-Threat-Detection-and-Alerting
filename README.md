
## System Design

### Arsitektur Sistem dan Teknologi

Sistem SIEM terdiri dari dua komponen utama:

1. **SIEM Server (VM1)** — Menerima event dari endpoint, menyimpan ke database, menganalisis dengan rule engine, menampilkan dashboard web, dan menghasilkan laporan.
2. **Endpoint Agent (VM2)** — Berjalan di server yang dimonitor, membaca log file (auth.log, syslog), memonitor perubahan direktori, mengecek status service, dan mengirim event ke SIEM server.

**Teknologi yang digunakan:**
- **Virtual Machine**: VirtualBox / VMware
- **OS Server**: Linux (Ubuntu Server)
- **Python 3**: Bahasa pemrograman utama
- **Flask**: Web framework untuk API dan dashboard
- **SQLite**: Database penyimpanan event dan alert
- **pandas**: Export data ke CSV
- **requests**: HTTP client untuk agent

### Topologi dan Spesifikasi VM

| VM | Peran | Spesifikasi | IP Address |
|----|-------|-------------|------------|
| VM1 | SIEM Server | 2 vCPU, 2GB RAM, 20GB disk | 192.168.1.100 |
| VM2 | Endpoint (Monitored) | 1 vCPU, 1GB RAM, 20GB disk | 192.168.1.101 |

### Aliran Data

```
Endpoint (VM2)
  → Agent membaca /var/log/auth.log, /var/log/syslog
  → Agent mengklasifikasikan event (SSH, sudo, user, dll)
  → Agent monitor direktori (/etc, /tmp) dan service (sshd, apache2)
  → HTTP POST (JSON) → SIEM Server (VM1) :5000/event

SIEM Server (VM1)
  → Flask API menerima event
  → INSERT ke SQLite database (events table)
  → Rule Engine menganalisis event
  → Jika terdeteksi aturan → INSERT ke alerts table
  → Web Dashboard membaca dari database
  → User mengakses dashboard via browser
  → Reporting mengekspor CSV / JSON / TXT
```

### Desain Database

**Table: events**
| Kolom | Tipe | Deskripsi |
|-------|------|-----------|
| id | INTEGER (PK) | Auto-increment |
| waktu | TEXT | Timestamp event |
| event | TEXT | Tipe event (FAILED_SSH, dll) |
| hostname | TEXT | Nama host pengirim |
| deskripsi | TEXT | Detail event |

**Table: alerts**
| Kolom | Tipe | Deskripsi |
|-------|------|-----------|
| id | INTEGER (PK) | Auto-increment |
| waktu | TEXT | Timestamp alert |
| severity | TEXT | HIGH / MEDIUM / LOW |
| pesan | TEXT | Pesan alert |
| event | TEXT | Tipe event pemicu |

### Detection Rule

| Event Type | Severity | Keterangan |
|------------|----------|------------|
| FAILED_SSH | HIGH | Percobaan login SSH gagal |
| SUCCESSFUL_SSH | LOW | Login SSH berhasil |
| FAILED_SUDO | HIGH | Percobaan sudo gagal |
| USER_CREATED | HIGH | Pembuatan user baru |
| USER_DELETED | HIGH | Penghapusan user |
| PACKAGE_INSTALL | MEDIUM | Instalasi paket |
| SERVICE_STOP | MEDIUM | Service berhenti |
| SERVICE_START | LOW | Service berjalan |
| FILE_CREATED | MEDIUM | File baru dibuat |
| FILE_MODIFIED | MEDIUM | File dimodifikasi |
| FILE_DELETED | HIGH | File dihapus |
| CUSTOM_LOG | LOW | Custom application log |

## Hasil Implementasi

### Aplikasi SIEM

Aplikasi SIEM Server dibangun dengan Flask dan menyediakan:
- **POST /event** — API untuk menerima event dari agent
- **GET /** — Web dashboard dengan summary cards, tabel events, tabel alerts, dan filter berdasarkan tipe event
- **GET /api/events** — REST API untuk mendapatkan events dalam format JSON
- **GET /api/alerts** — REST API untuk mendapatkan alerts dalam format JSON
- **GET /api/report** — REST API untuk mendapatkan ringkasan report

### Endpoint Agent

Agent berjalan sebagai proses daemon yang melakukan:
- **Log Monitoring**: Membaca `/var/log/auth.log` dan `/var/log/syslog` secara periodik, mendeteksi pola seperti `Failed password`, `Accepted password`, `sudo`, `new user`, dll.
- **Directory Monitoring**: Memonitor perubahan pada `/etc`, `/tmp`, `/var/www`.
- **Service Checking**: Mengecek status service `ssh`, `apache2`, `nginx`, `sshd`, `ufw`.
- **Event Sending**: Mengirim event ke SIEM server via HTTP POST dalam format JSON.

## Hasil Pengujian

### Testing Environment

Pengujian dilakukan pada dua VM Linux yang terhubung dalam jaringan internal VirtualBox.

### Cara Instalasi dan Menjalankan

**1. Clone / Extract project**
```bash
unzip NIM_Nama.zip
cd NIM_Nama
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Jalankan SIEM Server (VM1)**
```bash
python3 server/app.py
```
Server akan berjalan di `http://0.0.0.0:5000`

**4. Jalankan Agent (VM2)**
```bash
python3 agent/agent.py
```
Agent akan mulai memonitor dan mengirim event setiap 60 detik.

**5. Atau kirim event manual**
```bash
python3 agent/send_event.py FAILED_SSH "Percobaan login root gagal"
```

**6. Generate report**
```bash
python3 server/export_csv.py
python3 server/report_summary.py
python3 server/report.py
```

### Skenario Pengujian

| # | Skenario | Event Type | Status |
|---|----------|------------|--------|
| 1 | Failed SSH login | FAILED_SSH | ✅ |
| 2 | Successful SSH login | SUCCESSFUL_SSH | ✅ |
| 3 | Failed sudo attempt | FAILED_SUDO | ✅ |
| 4 | User account creation | USER_CREATED | ✅ |
| 5 | User account deletion | USER_DELETED | ✅ |
| 6 | Package installation | PACKAGE_INSTALL | ✅ |
| 7 | Service stop | SERVICE_STOP | ✅ |
| 8 | Service start | SERVICE_START | ✅ |
| 9 | File creation | FILE_CREATED | ✅ |
| 10 | File modification | FILE_MODIFIED | ✅ |
| 11 | File deletion | FILE_DELETED | ✅ |
| 12 | Custom application log | CUSTOM_LOG | ✅ |

### Rangkuman Hasil Pengujian

Semua skenario pengujian berhasil dijalankan. Event dari agent berhasil diterima oleh server, disimpan di database, dianalisis oleh rule engine, dan alert berhasil dibuat sesuai severity. Dashboard menampilkan semua data dengan filter yang berfungsi. Reporting berhasil mengekspor data ke CSV, JSON, dan TXT.
