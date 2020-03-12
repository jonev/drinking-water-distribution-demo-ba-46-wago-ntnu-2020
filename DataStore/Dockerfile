FROM jonev/ba-wago:opcua-mqtt
RUN pip --disable-pip-version-check --no-cache-dir install mysql-connector

COPY mqtt_to_mysql.py mqtt_to_mysql.py

CMD ["python", "mqtt_to_mysql.py"]


