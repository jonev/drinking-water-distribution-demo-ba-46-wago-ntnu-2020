import mysql.connector
from datetime import timedelta, datetime, date
import time


class DbLeakDetectionClient:
    def __init__(self):
        pass

    def connectHost(self, host_name, user_name, password):
        self.db = mysql.connector.connect(host=host_name, user=user_name, passwd=password)
        self.cursor = self.db.cursor()

    def connectDatabase(self, host_name, user_name, password, database_name):
        self.db = mysql.connector.connect(
            host=host_name, user=user_name, passwd=password, database=database_name
        )
        self.cursor = self.db.cursor()

    def createDatabase(self, database_name):
        try:
            self.cursor.execute("CREATE DATABASE " + database_name)
            print("Database " + database_name + " was created")
        except Exception as ex:
            print(ex)

    def createTable(self, table_name, table_format, database_name):
        self.tableName = table_name
        self.tableFormat = table_format
        try:
            self.cursor.execute(
                "SELECT * FROM information_schema.tables WHERE table_name='" + self.tableName + "'"
            )
            all = self.cursor.fetchall()
            if len(all) == 0:
                self.cursor.execute("CREATE TABLE " + self.tableName + " " + self.tableFormat)
                print("Table " + self.tableName + " was created")
        except Exception as ex:
            print(ex)

    def deleteTable(self, table_name):
        self.cursor.execute("DROP TABLE IF EXISTS " + table_name)

    def getLastRowInTable(self, table_name):
        """
        Get the last row added to the database.
        """
        self.cursor.execute("SELECT * FROM " + table_name + " ORDER BY ID DESC LIMIT 1")
        sample = self.cursor.fetchone()
        print(sample)
        return sample

    def getValuesBetweenTimestamps(self, table_name, timestamp_from, timestamp_to, _tagId):
        self.cursor.execute(
            (
                "SELECT * FROM "
                + table_name
                + " WHERE timestamp >= %s AND timestamp <%s AND _tagId=%s"
            ),
            (timestamp_from, timestamp_to, _tagId),
        )
        return self.cursor.fetchall()

    def getAverageHourValues(self, table_name, _tagId, secondStart, secondEnd, maxSamples):
        if secondStart < secondEnd:
            query = (
                "SELECT * FROM "
                + table_name
                + " WHERE SECOND(timestamp) > %s"
                + " AND SECOND(timestamp) < %s"
                + " AND _tagId = %s ORDER BY timestamp DESC LIMIT %s"
            )
        else:
            query = (
                "SELECT * FROM "
                + table_name
                + " WHERE (SECOND(timestamp) > %s"
                + " OR SECOND(timestamp) < %s)"
                + " AND _tagId = %s ORDER BY timestamp DESC LIMIT %s"
            )
        self.cursor.execute(
            query, (secondStart, secondEnd, _tagId, maxSamples),
        )
        # print(self.cursor._executed)
        return self.cursor.fetchall()

    def getValues_BetweenTimestampsOnTime(
        self, table_name, timestamp_from, timestamp_to, on_time, _tagId
    ):
        # TODO HOUR() must be used in real case
        self.cursor.execute(
            "SELECT * FROM "
            + table_name
            + " WHERE datetimestamp >= %s AND datetimestamp <%s AND timestamp=%s AND _tagId=%s",
            (timestamp_from, timestamp_to, on_time, _tagId),
        )

        samples = self.cursor.fetchall()
        # print(samples)
        return samples

    def pushValueOnTimestamp(self, tableName, datetimestamp, _tagId, value):
        tableValues = "(metric, timestamp, _tagId, value) VALUES (%s, %s, %s, %s)"
        tableInsert = "INSERT INTO " + tableName + " " + tableValues
        val = (
            "na",
            datetimestamp,
            _tagId,
            value,
        )
        self.cursor.execute(tableInsert, val)
        self.db.commit()

    def pushValue_BetweenTimestamps(
        self, table_name, datetimestamp_from, datetimestamp_to, _tagId, value
    ):
        self.tableValues = "(metric, datetimestamp, datestamp, timestamp, time_from, time_to, _tagId, value) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        self.tableName = table_name
        self.tableInsert = "INSERT INTO " + self.tableName + " " + self.tableValues
        self.val = (
            "na",
            datetimestamp_from,
            datetimestamp_from.date(),
            datetimestamp_from.time(),
            datetimestamp_from,
            datetimestamp_to,
            _tagId,
            value,
        )
        self.cursor.execute(self.tableInsert, self.val)
        self.db.commit()
