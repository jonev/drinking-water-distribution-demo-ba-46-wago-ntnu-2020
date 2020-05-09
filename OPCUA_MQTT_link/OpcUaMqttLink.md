# OPC UA - MQTT link

This directory contains two applications. Together they provide a server - client functionality for OPC UA server to server, via MQTT.

## Publish

Prerequisites: Readme.md "Build to PLC"

To publish a new version of the PLC application use :  
`./PLC/plcX.bat` (Change X with plc number)

To publish a new version of the HMI application use :  
`./HMI/push.bat` (Change X with plc number)

Environment variables for the different environment is stored in `./PLC/plcX` and `./HMI/.hmi`

Executing the file will build and publish the application.

## Run

To run the application, use docker-compose.
Add a `docker-compose.yaml` file to the target, containing:

```yaml
version: "3.1"
services:
  pythonapp:
    image: imagename
    restart: always
```

E.g:

```yaml
version: "3.1"
services:
  pythonapp:
    image: jonev/opcua-mqtt-link-hmi
    restart: always
```

Then follow ../README.md "Run on PLC/HMI - Run".

## Image template

Due to long build time for these images, a image template is added. The image contains python, mqtt and opcua.
