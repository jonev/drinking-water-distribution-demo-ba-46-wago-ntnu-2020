FROM python:3.8
RUN pip --disable-pip-version-check --no-cache-dir install paho-mqtt \
    && pip --disable-pip-version-check --no-cache-dir install mysql-connector

COPY mqtt_to_mysql.py mqtt_to_mysql.py

CMD ["python", "mqtt_to_mysql.py"]


