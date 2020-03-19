import mysql.connector
from datetime import timedelta, datetime
import time

mydb = mysql.connector.connect(host="db", user="root", passwd="example", database="processvalues")
date1 = datetime.now() + timedelta(days=3)  # Grunnet feil dato fra datetime
date2 = date1 + timedelta(days=1)
print("Mellom " + str(date1) + " og " + str(date2))
time_timestamp = time.strptime("10:00:00")
print(time_timestamp)
mycursor = mydb.cursor()
mycursor.execute(
    "SELECT * FROM flowValueValues WHERE timestamp >= %s AND timestamp <%s AND =%s ",
    (date1, date2, time_timestamp),
)
myresult = mycursor.fetchall()
for x in myresult:
    print(x)

