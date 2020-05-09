# Data store

This is a simple data store application which subscribes to mqtt topics and stores them in a MySQL database.

## Publish

Prerequisites: ../README.md "Build to PLC"

To publish a new version of this application use the following command:  
`./push.bat`

Executing the file will build and publish the application.

## Run

This application is a part of `../docker-compose-server.yaml`.
