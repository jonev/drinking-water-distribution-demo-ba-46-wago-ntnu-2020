import mysql.connector
from datetime import timedelta, datetime


class DataBase:
    def __init__(self):
        pass

    def test(self, tekst):
        print(tekst)

    def createDatabase(self, host_name, user_name, password, database_name):
        self.db = mysql.connector.connect(host=host_name, user=user_name, passwd=password)
        self.cursor = self.db.cursor()

        try:  # Add if not exist
            self.cursor.execute("CREATE DATABASE " + database_name)
            print("Database " + database_name + " was created")
        except Exception as ex:
            print(ex)

    def createTable(self, table_name, table_format, database_name):
        self.tableName = table_name
        self.tableFormat = table_format  # "(id INT AUTO_INCREMENT PRIMARY KEY, metric VARCHAR(3), timestamp DATETIME, from_start TIME, to_end TIME, avarageFlowValue FLOAT)"
        try:
            self.cursor.execute(
                "SELECT * FROM information_schema.tables WHERE table_name='" + self.tableName + "'"
            )
            all = self.cursor.fetchall()
            self.db = mysql.connector.connect(
                host="db", user="root", passwd="example", database=database_name
            )
            self.cursor = self.db.cursor()
            if len(all) == 0:
                self.cursor.execute("CREATE TABLE " + self.tableName + " " + self.tableFormat)
                print("Table " + self.tableName + " was created")
        except Exception as ex:
            print(ex)

    def deleteTable(self, table_name):
        self.cursor.execute(
            "DROP TABLE IF EXISTS " + table_name
        )  # Delete table if it's already excist. #Kan muligens fjernes når det er funksjonelt

    def getValues_BetweenTimestamps(self, table_name, timestamp_from, timestamp_to, tag="na"):
        # self.cursor = self.db.cursor()
        self.cursor.execute(
            "SELECT * FROM "
            + table_name
            + " WHERE timestamp >= %s AND timestamp <%s AND metric=%s",
            (timestamp_from, timestamp_to, tag),
        )

        self.samples = self.cursor.fetchall()
        print(self.samples)
        return self.samples

    def getValues_BetweenTimestampsOnTime(
        self, table_name, timestamp_from, timestamp_to, on_time, tag
    ):
        self.cursor.execute(
            "SELECT * FROM "
            + table_name
            + " WHERE timestamp < %s AND timestamp >=%s AND time_=%s AND metric=%s ",
            (timestamp_from, timestamp_to, on_time, tag),
        )  # Import average values with the same time span and between date1 and date2
        self.samples = self.cursor.fetchall()
        print(self.samples)
        return self.samples

    def pushValue_OnTimestamp(self, table_name, timestamp, tag, value):
        self.tableValues = "(metric, timestamp, date_, time_, time_from, time_to, tag, value) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        self.tableName = table_name
        self.tableInsert = "INSERT INTO " + self.tableName + " " + self.tableValues
        self.val = (
            "na",
            timestamp,
            timestamp.date(),
            timestamp.time(),
            timestamp.time(),
            timestamp.time(),
            tag,
            value,
        )
        self.cursor.execute(
            self.tableInsert, self.val
        )  # Send avarage value to new table flowAvarageValues
        self.db.commit()

    def pushValue_BetweenTimestamp(self, table_name, timestamp_from, timestamp_to, tag, value):
        pass
        self.tableValues = "(metric, timestamp, date_, time_, time_from, time_to, tag, value) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        self.tableName = table_name
        self.tableInsert = "INSERT INTO " + self.tableName + " " + self.tableValues
        self.val = (
            "na",
            timestamp_from,
            timestamp_from.date(),
            timestamp_from.time(),
            timestamp_from.time(),
            timestamp_to.time(),
            tag,
            value,
        )
        self.cursor.execute(
            self.tableInsert, self.val
        )  # Send avarage value to new table flowAvarageValues
        self.db.commit()


dbclient = DataBase()
# while True:
dbclient.createDatabase("db", "root", "example", "test_database")
dbclient.createTable(
    "testtable",
    "(id INT AUTO_INCREMENT PRIMARY KEY, metric VARCHAR(3), timestamp DATETIME, date_ DATE, time_ TIME, time_from TIME, time_to TIME, tag VARCHAR(20), value FLOAT)",
    "test_database",
)
dbclient.pushValue_OnTimestamp("testtable", datetime.now(), "ft1", 55.5)
dbclient.pushValue_BetweenTimestamp(
    "testtable", datetime.now(), datetime.now() + timedelta(hours=1), "ft1_ave", 52.5
)
date1 = datetime(2020, 3, 13, 0, 0, 0)
date2 = datetime(2020, 3, 14, 0, 0, 0)
time3 = datetime(2020, 3, 13, 5, 0, 0).time()
# dbclient.getValues_BetweenTimestamps("flowValueValues", date1, date2, "na")
dbclient.getValues_BetweenTimestampsOnTime("flowValueValues", date1, date2, time3, "na")
# dbclient.deleteTable("testtable")
