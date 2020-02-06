FROM python:3.8

RUN pip --disable-pip-version-check --no-cache-dir install paho-mqtt

COPY mqtt_test.py .

CMD ["python", "mqtt_test.py"]


