FROM python:3.8

RUN pip --disable-pip-version-check --no-cache-dir install paho-mqtt

COPY . .

CMD ["python", "main.py"]