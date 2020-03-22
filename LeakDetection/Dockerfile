FROM python:3.8

RUN pip --disable-pip-version-check --no-cache-dir install mysql-connector


COPY ./LeakDetection ./LeakDetection
COPY ./utils ./utils

CMD ["python", "-m", "LeakDetection"]