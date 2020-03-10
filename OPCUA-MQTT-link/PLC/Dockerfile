FROM jonev/ba-wago:opcua-mqtt
RUN pip --disable-pip-version-check --no-cache-dir install python-dotenv

COPY mqtt_opc_ua_link.py .
COPY .env .

CMD ["python", "mqtt_opc_ua_link.py"]


