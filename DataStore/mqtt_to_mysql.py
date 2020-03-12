import paho.mqtt.client as mqtt
import json
import datetime
import mysql.connector
import datetime
import time
import logging

logging.basicConfig(level=logging.INFO)

## MQTT
mqttBroker = "broker.hivemq.com"
mqttPort = 1883
mqttTopics = ["ba/wago/opcua/plc3/plcpub", "ba/wago/opcua/plc2/plcpub", "ba/wago/opcua/plc1/plcpub"]
# MySQL
dbName = "processvalues"
signalAnalogTableName = "SignalAnalogHmiPv"
signalAnalogTableFormat = "(id INT AUTO_INCREMENT PRIMARY KEY, _tagId VARCHAR(124), metric VARCHAR(3), timestamp TIMESTAMP, Output_Pv FLOAT)"
signalAnalogTableInsert = (
    "INSERT INTO "
    + signalAnalogTableName
    + " (_tagId, metric, timestamp, Output_Pv) VALUES (%s, %s, %s, %s)"
)
valveAnalogTableName = "ValveAnalogHmiPv"
valveAnalogTableFormat = "(id INT AUTO_INCREMENT PRIMARY KEY, _tagId VARCHAR(124), metric VARCHAR(3), timestamp TIMESTAMP, ControlValue_Pv FLOAT, Interlocked_Pv BOOLEAN, Position_Pv FLOAT)"
valveAnalogTableInsert = (
    "INSERT INTO "
    + valveAnalogTableName
    + " (_tagId, metric, timestamp, ControlValue_Pv, Interlocked_Pv, Position_Pv) VALUES (%s, %s, %s, %s, %s, %s)"
)
motorDigitalTableName = "MotorDigitalHmiPv"
motorDigitalTableFormat = "(id INT AUTO_INCREMENT PRIMARY KEY, _tagId VARCHAR(124), metric VARCHAR(3), timestamp TIMESTAMP, ControlValue_Pv BOOLEAN, Interlocked_Pv BOOLEAN, Started_Pv BOOLEAN, Stopped_Pv BOOLEAN)"
motorDigitalTableInsert = (
    "INSERT INTO "
    + motorDigitalTableName
    + " (_tagId, metric, timestamp, ControlValue_Pv, Interlocked_Pv, Started_Pv, Stopped_Pv) VALUES (%s, %s, %s, %s, %s, %s, %s)"
)

while True:
    try:
        db = mysql.connector.connect(host="db", user="root", passwd="example",)
        cursor = db.cursor()

        try:  # Add if not exist
            cursor.execute("CREATE DATABASE " + dbName)
        except Exception:
            logging.info("Could not create database")

        try:  # Create tables if not exist
            cursor.execute(
                "SELECT * FROM information_schema.tables WHERE table_name='"
                + signalAnalogTableName
                + "'"
            )
            tables = cursor.fetchall()
            if len(tables) == 0:
                cursor.execute(
                    "CREATE TABLE "
                    + dbName
                    + "."
                    + signalAnalogTableName
                    + " "
                    + signalAnalogTableFormat
                )
            cursor.execute(
                "SELECT * FROM information_schema.tables WHERE table_name='"
                + valveAnalogTableName
                + "'"
            )
            tables = cursor.fetchall()
            if len(tables) == 0:
                cursor.execute(
                    "CREATE TABLE "
                    + dbName
                    + "."
                    + valveAnalogTableName
                    + " "
                    + valveAnalogTableFormat
                )
            cursor.execute(
                "SELECT * FROM information_schema.tables WHERE table_name='"
                + motorDigitalTableName
                + "'"
            )
            tables = cursor.fetchall()
            if len(tables) == 0:
                cursor.execute(
                    "CREATE TABLE "
                    + dbName
                    + "."
                    + motorDigitalTableName
                    + " "
                    + motorDigitalTableFormat
                )
            # Connect to DB
            db = mysql.connector.connect(host="db", user="root", passwd="example", database=dbName)
            cursor = db.cursor()
        except Exception:
            logging.exception("Could not create tables")

        def on_connect(client, userdata, flags, rc):
            print("MQTT Connected with result code " + str(rc))
            for topic in mqttTopics:
                client.subscribe(topic)

        def on_message(client, userdata, msg):
            # print(msg.topic + str(msg.payload))
            try:
                receivedObject = json.loads(str(msg.payload, encoding="utf-8"))
                # print(receivedObject)
                if receivedObject["_type"] == "SignalAnalog":
                    val = (
                        receivedObject["_tagId"],
                        "na",
                        receivedObject["_timestamp"],
                        receivedObject["Output_Pv"],
                    )
                    cursor.execute(signalAnalogTableInsert, val)
                    db.commit()
                elif receivedObject["_type"] == "ValveAnalog":
                    val = (
                        receivedObject["_tagId"],
                        "na",
                        receivedObject["_timestamp"],
                        receivedObject["ControlValue_Pv"],
                        receivedObject["Interlocked_Pv"],
                        receivedObject["Position_Pv"],
                    )
                    cursor.execute(valveAnalogTableInsert, val)
                    db.commit()
                elif receivedObject["_type"] == "MotorDigital":
                    val = (
                        receivedObject["_tagId"],
                        "na",
                        receivedObject["_timestamp"],
                        receivedObject["ControlValue_Pv"],
                        receivedObject["Interlocked_Pv"],
                        receivedObject["Started_Pv"],
                        receivedObject["Stopped_Pv"],
                    )
                    cursor.execute(motorDigitalTableInsert, val)
                    db.commit()
                else:
                    logging.info("Unsuported type: " + receivedObject["_type"])
            except Exception:
                logging.exception("Exception on received object.")

        mqttClient = mqtt.Client()
        mqttClient.connect(mqttBroker, mqttPort, 60)
        mqttClient.on_connect = on_connect
        mqttClient.on_message = on_message
        mqttClient.loop_forever()
    except Exception as e:
        logging.exception("Exception in connect loop.")
    time.sleep(10)
