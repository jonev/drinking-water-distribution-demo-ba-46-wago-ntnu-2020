cp .plc2 .env
cd ..
cd ..
docker buildx build --platform linux/amd64,linux/arm64,linux/arm/v7 -f OPCUA_MQTT_link/PLC/Dockerfile -t jonev/opcua-mqtt-link-plc2 --push .