import sqlite3

def connect():

    return sqlite3.connect("database/siem.db")

def create_table():

    conn = connect()

    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS events(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    waktu TEXT,

    event TEXT,

    hostname TEXT,

    deskripsi TEXT

    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS alerts(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    waktu TEXT,

    severity TEXT,

    pesan TEXT,

    event TEXT
    )
    """)

    conn.commit()

    conn.close()