import paho.mqtt.client as mqtt
import json
import datetime
import mysql.connector
import datetime
import time

## MQTT
mqttBroker = "broker.hivemq.com"
mqttPort = 1883
mqttTopics = ["ba/wago/opcua/plc3/plcpub", "ba/wago/opcua/plc2/plcpub", "ba/wago/opcua/plc1/plcpub"]
# MySQL
dbName = "processvalues"
signalAnalogTableName = "SignalAnalogHmiPv"
signalAnalogTableFormat = (
    "(id INT AUTO_INCREMENT PRIMARY KEY, metric VARCHAR(3), timestamp TIMESTAMP, Output_Pv FLOAT)"
)
signalAnalogTableInsert = (
    "INSERT INTO " + signalAnalogTableName + " (metric, timestamp, Output_Pv) VALUES (%s, %s, %s)"
)
valveAnalogTableName = "ValveAnalogHmiPv"
valveAnalogTableFormat = "(id INT AUTO_INCREMENT PRIMARY KEY, metric VARCHAR(3), timestamp TIMESTAMP, ControlValue_Pv FLOAT, Interlocked_Pv BOOLEAN, Position_Pv FLOAT)"
valveAnalogTableInsert = (
    "INSERT INTO "
    + valveAnalogTableName
    + " (metric, timestamp, ControlValue_Pv, Interlocked_Pv, Position_Pv) VALUES (%s, %s, %s, %s, %s)"
)
motorDigitalTableName = "MotorDigitalHmiPv"
motorDigitalTableFormat = "(id INT AUTO_INCREMENT PRIMARY KEY, metric VARCHAR(3), timestamp TIMESTAMP, ControlValue_Pv BOOLEAN, Interlocked_Pv BOOLEAN, Started_Pv BOOLEAN, Stopped_Pv BOOLEAN)"
motorDigitalTableInsert = (
    "INSERT INTO "
    + motorDigitalTableName
    + " (metric, timestamp, ControlValue_Pv, Interlocked_Pv, Started_Pv, Stopped_Pv) VALUES (%s, %s, %s, %s, %s, %s)"
)

while True:
    try:
        db = mysql.connector.connect(host="db", user="root", passwd="example",)
        cursor = db.cursor()

        try:  # Add if not exist
            cursor.execute("CREATE DATABASE " + dbName)
        except Exception as ex:
            print(ex)

        try:  # Create table if not exist
            cursor.execute(
                "SELECT * FROM information_schema.tables WHERE table_name='" + valveAnalogTableName + "'"
            )
            all = cursor.fetchall()
            db = mysql.connector.connect(host="db", user="root", passwd="example", database=dbName)
            cursor = db.cursor()
            if len(all) == 0:
                cursor.execute("CREATE TABLE " + valveAnalogTableName + " " + valveAnalogTableFormat)
        except Exception as ex:
            print(ex)


        def on_connect(client, userdata, flags, rc):
            print("MQTT Connected with result code " + str(rc))
            for topic in mqttTopics:
                client.subscribe(topic)


        def on_message(client, userdata, msg):
            print(msg.topic + str(msg.payload))
            try:
                receivedObject = json.loads(str(msg.payload, encoding="utf-8"))
                print(receivedObject)
                if receivedObject["_type"] == "SignalAnalog":
                    val = ("na", receivedObject["_timestamp"], receivedObject["Output_Pv"])
                    cursor.execute(valveAnalogTableInsert, val)
                    db.commit()
                if receivedObject["_type"] == "ValveAnalog":
                    val = (
                        "na",
                        receivedObject["_timestamp"],
                        receivedObject["ControlValue_Pv"],
                        receivedObject["Interlocked_Pv"],
                        receivedObject["Position_Pv"],
                    )
                    cursor.execute(valveAnalogTableInsert, val)
                    db.commit()
                if receivedObject["_type"] == "MotorDigital":
                    val = (
                        "na",
                        receivedObject["_timestamp"],
                        receivedObject["ControlValue_Pv"],
                        receivedObject["Interlocked_Pv"],
                        receivedObject["Started_Pv"],
                        receivedObject["Stopped_Pv"],
                    )
                    cursor.execute(valveAnalogTableInsert, val)
                    db.commit()
            except Exception as e:
                print(e)


        mqttClient = mqtt.Client()
        mqttClient.connect(mqttBroker, mqttPort, 60)
        mqttClient.on_connect = on_connect
        mqttClient.on_message = on_message
        mqttClient.loop_forever()
    except Exception as e:
        print(e)
    time.sleep(10)
