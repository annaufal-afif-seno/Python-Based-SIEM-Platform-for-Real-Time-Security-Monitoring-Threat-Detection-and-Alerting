import sqlite3

conn = sqlite3.connect(

"database/siem.db"

)

cur = conn.cursor()

cur.execute(

"SELECT COUNT(*) FROM events"

)

total_events = cur.fetchone()[0]

cur.execute(

"SELECT COUNT(*) FROM alerts"

)

total_alerts = cur.fetchone()[0]

cur.execute(

"""

SELECT event,

COUNT(*)

FROM events

GROUP BY event

"""

)

summary = cur.fetchall()

file = open(

"report/report_summary.txt",

"w"

)

file.write(

"===== SIEM REPORT =====\n\n"

)

file.write(

f"Total Event : {total_events}\n"

)

file.write(

f"Total Alert : {total_alerts}\n\n"

)

file.write(

"Rangkuman Event\n\n"

)

for item in summary:

    file.write(

    f"{item[0]} : {item[1]}\n"

    )

file.close()

conn.close()

print(

"Report selesai"

)