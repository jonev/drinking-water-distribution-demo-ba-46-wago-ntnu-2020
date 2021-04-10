import mysql.connector
from datetime import timedelta, datetime, date
import time
import logging
from mysql.connector import Error
from mysql.connector.connection import MySQLConnection
from mysql.connector import pooling


class DbLeakDetectionClient:
    def __init__(self):
        pass

    def connectDatabase(self, host_name, user_name, password, database_name):
        self.connection_pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name="pynative_pool",
            pool_size=3,
            pool_reset_session=False,
            host=host_name,
            user=user_name,
            database=database_name,
            password=password,
        )

    def createDatabase(self, host_name, user_name, password, databaseName):
        con = mysql.connector.connect(host=host_name, user=user_name, passwd=password)
        cursor = con.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS " + databaseName)
        cursor.close()
        con.close()

    def createTable(self, tableName, tableFormat):
        logging.info("createTable %s %s", tableName, tableFormat)
        con = self.connection_pool.get_connection()
        try:
            cursor = con.cursor()
            cursor.execute(
                "SELECT * FROM information_schema.tables WHERE table_name='" + tableName + "'"
            )
            all = cursor.fetchall()
            if len(all) == 0:
                cursor.execute("CREATE TABLE " + tableName + " " + tableFormat)
                logging.warning("Table " + tableName + " was created")
            else:
                logging.warning("Table " + tableName + " aleready exist")
        except:
            logging.exception("Create table failed")
        finally:
            cursor.close()
            con.close()

    def deleteTable(self, table_name):
        # logging.debug("deleteTable %s", table_name)
        con = self.connection_pool.get_connection()
        try:
            cursor = con.cursor()
            cursor.execute("DROP TABLE IF EXISTS " + table_name)
        except:
            logging.exception("Delete table failed")
        finally:
            cursor.close()
            con.close()

    def getLastRowInTable(self, table_name):
        """
        Get the last row added to the database.
        """
        # logging.debug("getLastRowInTable %s", table_name)
        con = self.connection_pool.get_connection()
        try:
            cursor = con.cursor()
            cursor.execute("SELECT * FROM " + table_name + " ORDER BY ID DESC LIMIT 1")
            sample = cursor.fetchone()
            print(sample)
            return sample
        except:
            logging.exception("Get last row in table failed")
        finally:
            cursor.close()
            con.close()

    def getValuesBetweenTimestamps(self, table_name, timestamp_from, timestamp_to, _tagId):
        # logging.debug(
        #    "getValuesBetweenTimestamps %s %s %s %s",
        #    table_name,
        #    timestamp_from,
        #    timestamp_to,
        #    _tagId,
        # )
        con = self.connection_pool.get_connection()
        try:
            cursor = con.cursor()
            cursor.execute(
                (
                    "SELECT * FROM "
                    + table_name
                    + " WHERE timestamp >= %s AND timestamp <%s AND _tagId=%s"
                ),
                (timestamp_from, timestamp_to, _tagId),
            )
            return cursor.fetchall()
        except:
            logging.exception("Get values between timestamp failed")
        finally:
            cursor.close()
            con.close()

    def getAverageHourValues(self, table_name, _tagId, secondStart, secondEnd, maxSamples):
        # logging.debug(
        #    "getAverageHourValues %s %s %s %s %s",
        #    table_name,
        #    _tagId,
        #    secondStart,
        #    secondEnd,
        #    maxSamples,
        # )
        con = self.connection_pool.get_connection()
        try:
            cursor = con.cursor()
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
            cursor.execute(
                query,
                (secondStart, secondEnd, _tagId, maxSamples),
            )
            return cursor.fetchall()
        except:
            logging.exception("Get average hour values failed")
        finally:
            cursor.close()
            con.close()

    def getValues_BetweenTimestampsOnTime(
        self, table_name, timestamp_from, timestamp_to, on_time, _tagId
    ):
        # logging.debug(
        #    "getValues_BetweenTimestampsOnTime %s %s %s %s %s",
        #    table_name,
        #    timestamp_from,
        #    timestamp_to,
        #    on_time,
        #    _tagId,
        # )
        con = self.connection_pool.get_connection()
        try:
            cursor = con.cursor()
            # HACK HOUR() must be used in a real case
            cursor.execute(
                "SELECT * FROM "
                + table_name
                + " WHERE datetimestamp >= %s AND datetimestamp <%s AND timestamp=%s AND _tagId=%s",
                (timestamp_from, timestamp_to, on_time, _tagId),
            )

            samples = cursor.fetchall()
            return samples
        except:
            logging.exception("Get values between timestamps on time failed")
        finally:
            cursor.close()
            con.close()

    def pushValueOnTimestamp(self, tableName, datetimestamp, _tagId, value):
        # logging.debug("pushValueOnTimestamp %s %s %s %s", tableName, datetimestamp, _tagId, value)
        con = self.connection_pool.get_connection()
        try:
            cursor = con.cursor()
            tableValues = "(metric, timestamp, _tagId, value) VALUES (%s, %s, %s, %s)"
            tableInsert = "INSERT INTO " + tableName + " " + tableValues
            val = (
                "na",
                datetimestamp,
                _tagId,
                value,
            )
            cursor.execute(tableInsert, val)
            con.commit()
        except:
            logging.exception("Push values on timestamp failed")
        finally:
            cursor.close()
            con.close()

    def pushPointsOnTimestamp(
        self, tableName, datetimestamp, _tagId, pointsOver10, pointsOver20, pointsOver30
    ):
        # logging.debug(
        #    "pushPointsOnTimestamp %s %s %s %s %s %s",
        #    tableName,
        #    datetimestamp,
        #    _tagId,
        #    pointsOver10,
        #    pointsOver20,
        #    pointsOver30,
        # )
        con = self.connection_pool.get_connection()
        try:
            cursor = con.cursor()
            tableValues = "(timestamp, _tagId, pointsOver10, pointsOver20, pointsOver30) VALUES (%s, %s, %s, %s, %s)"
            tableInsert = "INSERT INTO " + tableName + " " + tableValues
            val = (
                datetimestamp,
                _tagId,
                pointsOver10,
                pointsOver20,
                pointsOver30,
            )
            cursor.execute(tableInsert, val)
            con.commit()
        except:
            logging.exception("Push points on timestamp failed")
        finally:
            cursor.close()
            con.close()

    def pushValue_BetweenTimestamps(
        self, table_name, datetimestamp_from, datetimestamp_to, _tagId, value
    ):
        # logging.debug(
        #    "pushValue_BetweenTimestamps %s %s %s %s %s",
        #    table_name,
        #    datetimestamp_from,
        #    datetimestamp_to,
        #    _tagId,
        #    value,
        # )
        con = self.connection_pool.get_connection()
        try:
            cursor = con.cursor()
            tableValues = "(metric, datetimestamp, datestamp, timestamp, time_from, time_to, _tagId, value) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            tableName = table_name
            tableInsert = "INSERT INTO " + tableName + " " + tableValues
            val = (
                "na",
                datetimestamp_from,
                datetimestamp_from.date(),
                datetimestamp_from.time(),
                datetimestamp_from,
                datetimestamp_to,
                _tagId,
                value,
            )
            cursor.execute(tableInsert, val)
            con.commit()
        except:
            logging.exception("Push value between timestamps failed")
        finally:
            cursor.close()
            con.close()
