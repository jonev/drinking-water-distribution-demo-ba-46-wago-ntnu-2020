FROM python:3.8

RUN pip --disable-pip-version-check --no-cache-dir install paho-mqtt \
    && pip --disable-pip-version-check --no-cache-dir install mysql-connector


COPY ./SimulationProgram ./SimulationProgram
COPY ./utils ./utils

CMD ["python", "-m", "SimulationProgram"]