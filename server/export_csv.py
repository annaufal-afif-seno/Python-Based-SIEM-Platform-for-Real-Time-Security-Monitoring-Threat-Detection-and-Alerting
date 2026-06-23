import sqlite3

import pandas as pd

conn = sqlite3.connect(

"database/siem.db"

)

events = pd.read_sql_query(

"SELECT * FROM events",

conn

)

alerts = pd.read_sql_query(

"SELECT * FROM alerts",

conn

)

events.to_csv(

"report/events.csv",

index=False

)

alerts.to_csv(

"report/alerts.csv",

index=False

)

conn.close()

print(

"CSV berhasil dibuat"

)