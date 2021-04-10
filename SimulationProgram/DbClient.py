import mysql.connector
import logging
from datetime import datetime
import threading
from mysql.connector import Error
from mysql.connector.connection import MySQLConnection
from mysql.connector import pooling


class DbClient:
    def __init__(self):
        self.__dbLock = threading.Lock()
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
        logging.info("Connecting to db host")

        db = mysql.connector.connect(
            host="db",
            user="root",
            passwd="example",
        )
        cursor = db.cursor()

        logging.info("Creating tables if not exist")
        cursor.execute(
            "SELECT * FROM information_schema.tables WHERE table_name='"
            + self.__flowValueTableName
            + "'"
        )
        tables = cursor.fetchall()
        if len(tables) == 0:
            logging.info("Creating table " + self.__flowValueTableName)
            cursor.execute(
                "CREATE TABLE "
                + self.__dbName
                + "."
                + self.__flowValueTableName
                + " "
                + self.__flowValueTableFormat
            )
        else:
            logging.info("Table " + self.__flowValueTableName + " already exist")

        # Connect to database
        logging.info("Connecting to db " + self.__dbName)
        self.connection_pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name="pynative_pool",
            pool_size=3,
            pool_reset_session=False,
            host="db",
            database=self.__dbName,
            user="root",
            password="example",
        )
        logging.info("DbClient ready")

    def insertFlowValuesBatch8DifferentTags(self, tags, values, datetimestamp):
        with self.__dbLock:
            con = self.connection_pool.get_connection()
            try:
                cursor = con.cursor()

                val = [
                    (tags[0], "na", datetimestamp, values[0]),
                    (tags[1], "na", datetimestamp, values[1]),
                    (tags[2], "na", datetimestamp, values[2]),
                    (tags[3], "na", datetimestamp, values[3]),
                    (tags[4], "na", datetimestamp, values[4]),
                    (tags[5], "na", datetimestamp, values[5]),
                    (tags[6], "na", datetimestamp, values[6]),
                ]
                cursor.executemany(self.__flowValueTableInsert, val)
                con.commit()
            except:
                con.rollback()
                logging.exception("Failed to insert flow values batch 8")
            finally:
                cursor.close()
                con.close()

    def deleteDataOlderThan(self, tableName, olderThan):
        q = "DELETE FROM " + tableName + " WHERE timestamp < %s"
        logging.info("DeleteDataOlderThan: " + q)
        with self.__dbLock:
            con = self.connection_pool.get_connection()
            try:
                cursor = con.cursor()
                cursor.execute(q, (olderThan,))
                con.commit()
                return cursor.rowcount
            except:
                con.rollback()
                logging.exception("Failed to delete old samples")
            finally:
                cursor.close()
                con.close()
