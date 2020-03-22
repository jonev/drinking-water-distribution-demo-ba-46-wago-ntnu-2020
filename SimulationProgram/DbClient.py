import mysql.connector
import logging
from datetime import datetime


class DbClient:
    def __init__(self,):
        # Constants - Database setup
        self.__dbName = "processvalues"
        self.__flowValueTableName = "SignalAnalogHmiPv"
        self.__flowValueTableFormat = "(id INT AUTO_INCREMENT PRIMARY KEY, _tagId VARCHAR(124), metric VARCHAR(3), timestamp DATETIME(6), Output_Pv FLOAT)"
        self.__flowValueTableInsert = (
            "INSERT INTO "
            + self.__flowValueTableName
            + " (_tagId, metric, timestamp, Output_Pv) VALUES (%s, %s, %s, %s)"
        )
        # Connection to database server
        self.__db = mysql.connector.connect(host="db", user="root", passwd="example",)
        self.__cursor = self.__db.cursor()

        try:  # Add database if not exist
            self.__cursor.execute("CREATE DATABASE " + self.__dbName)
        except Exception:
            logging.info("Could not create database, it exist")

        try:  # Create tables if not exist
            self.__cursor.execute(
                "SELECT * FROM information_schema.tables WHERE table_name='"
                + self.__flowValueTableName
                + "'"
            )
            tables = self.__cursor.fetchall()
            if len(tables) == 0:
                self.__cursor.execute(
                    "CREATE TABLE "
                    + self.__dbName
                    + "."
                    + self.__flowValueTableName
                    + " "
                    + self.__flowValueTableFormat
                )
            # Connect to database
            self.__db = mysql.connector.connect(
                host="db", user="root", passwd="example", database=self.__dbName
            )
            self.__cursor = self.__db.cursor()
        except Exception:
            logging.exception("Could not create tables")

    def insertFlowValuesBatch8DifferentTags(self, tags, values, datetimestamp):
        val = [
            (tags[0], "na", datetimestamp, values[0]),
            (tags[1], "na", datetimestamp, values[1]),
            (tags[2], "na", datetimestamp, values[2]),
            (tags[3], "na", datetimestamp, values[3]),
            (tags[4], "na", datetimestamp, values[4]),
            (tags[5], "na", datetimestamp, values[5]),
            (tags[6], "na", datetimestamp, values[6]),
        ]
        self.__cursor.executemany(self.__flowValueTableInsert, val)
        self.__db.commit()

    def deleteDataOlderThan(self, tableName, olderThan):
        self.__cursor.execute("DELETE FROM " + tableName + " WHERE timestamp < %s", (olderThan,))
        self.__db.commit()
        return self.__cursor.rowcount
