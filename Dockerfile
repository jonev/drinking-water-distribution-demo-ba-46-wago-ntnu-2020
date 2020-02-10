FROM python:3.8

RUN pip --disable-pip-version-check --no-cache-dir install pymodbus


COPY modbus_test_slave.py .

CMD ["python", "modbus_test_slave.py"]


