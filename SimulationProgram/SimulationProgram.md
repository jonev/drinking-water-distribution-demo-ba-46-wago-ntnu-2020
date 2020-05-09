# Simulation program

This application simulates objects regarding the drinking water distribution.
Objects which are simulated:

- Water
- Rain forcast
- Water distribution pipes
- Battery levels
The application is communicating with the different PLC's using MQTT.

## Publish

Prerequisites: Readme.md "Build to PLC"

To publish a new version of this application use the following command:  
`./push.bat`

Executing the file will build and publish the application.

## Run

This application is a part of `../docker-compose-server.yaml`.
