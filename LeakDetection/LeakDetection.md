# Leak detection

This is a application that process data to be able to detect leak in the distribution of drinking water.

There are two functions.

1. Collect sample values from a database, calculate average values and store them in the database.
2. Use these average values to calculate balances of flow in and out of a pipe.

There are a containing Grafana application which visualize the calculated values.

## Publish

Prerequisites: Readme.md "Build to PLC"

To publish a new version of this application use the following command:  
`./push.bat`

For Grafana application:  
`./pushgrafana.bat`

Executing the file will build and publish the application.

Grafana will be build with the configuration in `grafana.ini`, and to access the dashboard, import `grafanadashboard.json`.

## Run

This application is a part of `../docker-compose-server.yaml`.
