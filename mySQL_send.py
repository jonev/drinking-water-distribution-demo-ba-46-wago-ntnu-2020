import mysql.connector
import datetime
import time

dbName = "processvalues"

db = mysql.connector.connect(host="db", user="root", passwd="example",)
cursor = db.cursor()

try:  # Add if not exist
    cursor.execute("CREATE DATABASE " + dbName)
except Exception as ex:
    print(ex)

flowAverageTableName = "FlowAverageValues"
flowAverageTableFormat = "(id INT AUTO_INCREMENT PRIMARY KEY, metric VARCHAR(3), timestamp TIMESTAMP, AverageValue FLOAT)"
flowAverageTableInsert = (
    "INSERT INTO " + flowAverageTableName + " (metric, timestamp, AverageValue) VALUES (%s, %s, %s)"
)

try:  # Create table if not exist
    cursor.execute(
        "SELECT * FROM information_schema.tables WHERE table_name='" + flowAverageTableName + "'"
    )
    all = cursor.fetchall()
    db = mysql.connector.connect(host="db", user="root", passwd="example", database=dbName)
    cursor = db.cursor()
    if len(all) == 0:
        cursor.execute("CREATE TABLE " + flowAverageTableName + " " + flowAverageTableFormat)
except Exception as ex:
    print(ex)
while True:
    # Skriver til database
    val = ("na", datetime.datetime.now(), 10.0)
    cursor.execute(flowAverageTableInsert, val)
    db.commit()
    time.sleep(3)
