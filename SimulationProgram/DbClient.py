import mysql.connector
import logging
from datetime import datetime


class DbClient:
    def __init__(self,):
        self.__dbName = "processvalues"
        self.__flowValueTableName = "flowValueValues"
        self.__flowValueTableFormat = "(id INT AUTO_INCREMENT PRIMARY KEY, _tagId VARCHAR(124), metric VARCHAR(3), timedatestamp DATETIME, datestamp DATE, timestamp TIME, FlowValue FLOAT)"
        self.__flowValueTableInsert = (
            "INSERT INTO "
            + self.__flowValueTableName
            + " (_tagId, metric, timedatestamp, datestamp, timestamp, FlowValue) VALUES (%s, %s, %s, %s, %s, %s)"
        )
        self.__flowValueTableInsertBatch7 = (
            "INSERT INTO "
            + self.__flowValueTableName
            + " (_tagId, metric, timedatestamp, datestamp, timestamp, FlowValue) VALUES (%s, %s, %s, %s, %s, %s), (%s, %s, %s, %s, %s, %s), (%s, %s, %s, %s, %s, %s), (%s, %s, %s, %s, %s, %s), (%s, %s, %s, %s, %s, %s), (%s, %s, %s, %s, %s, %s), (%s, %s, %s, %s, %s, %s)"
        )
        self.__db = mysql.connector.connect(host="db", user="root", passwd="example",)
        self.__cursor = self.__db.cursor()

        try:  # Add if not exist
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
            # Connect to DB
            db = mysql.connector.connect(
                host="db", user="root", passwd="example", database=self.__dbName
            )
            self.__cursor = db.cursor()
        except Exception:
            logging.exception("Could not create tables")

    def insertFlowValuesBatch7DifferentTags(self, tags, values, timestamp):
        datestamp = datetime.fromtimestamp(timestamp)
        val = (
            tags[0],
            "na",
            timestamp,
            datestamp.date(),
            datestamp.time(),
            values[0],
            tags[1],
            "na",
            timestamp,
            datestamp.date(),
            datestamp.time(),
            values[1],
            tags[2],
            "na",
            timestamp,
            datestamp.date(),
            datestamp.time(),
            values[2],
            tags[3],
            "na",
            timestamp,
            datestamp.date(),
            datestamp.time(),
            values[3],
            tags[4],
            "na",
            timestamp,
            datestamp.date(),
            datestamp.time(),
            values[4],
            tags[5],
            "na",
            timestamp,
            datestamp.date(),
            datestamp.time(),
            values[5],
            tags[6],
            "na",
            timestamp,
            datestamp.date(),
            datestamp.time(),
            values[6],
        )
        self.__cursor.execute(self.__flowValueTableInsertBatch7, val)
        self.__db.commit()

