FROM python:3.8

RUN pip --disable-pip-version-check --no-cache-dir install opcua

COPY opc_ua_test.py .

CMD ["python", "opc_ua_test.py"]


