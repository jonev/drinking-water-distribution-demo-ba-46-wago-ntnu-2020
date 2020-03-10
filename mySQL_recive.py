import mysql.connector
from datetime import timedelta, datetime

mydb = mysql.connector.connect(host="db", user="root", passwd="example", database="processvalues")
date1 = datetime.utcnow().date() + timedelta(days=3)  # Grunnet feil dato fra datetime
date2 = date1 + timedelta(days=1)
print("Mellom " + str(date1) + " og " + str(date2))
mycursor = mydb.cursor()
mycursor.execute(
    "SELECT * FROM flowValueValues WHERE timestamp >= %s AND timestamp <%s AND (cast(timestamp as time))=10:00:00 ",
    (date1, date2),
)
myresult = mycursor.fetchall()
for x in myresult:
    print(x)

