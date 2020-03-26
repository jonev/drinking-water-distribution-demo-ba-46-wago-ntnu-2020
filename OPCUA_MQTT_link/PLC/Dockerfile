FROM jonev/python-opcua-mqtt-template
RUN pip --disable-pip-version-check --no-cache-dir install python-dotenv

COPY ./OPCUA_MQTT_link ./OPCUA_MQTT_link

CMD ["python", "-m" "OPCUA_MQTT_link.PLC"]


