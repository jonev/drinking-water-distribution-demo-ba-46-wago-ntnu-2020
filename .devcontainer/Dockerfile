#-------------------------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See https://go.microsoft.com/fwlink/?linkid=2090316 for license information.
#-------------------------------------------------------------------------------------------------------------

FROM python:3.8
# Avoid warnings by switching to noninteractive
ENV DEBIAN_FRONTEND=noninteractive

RUN pip --disable-pip-version-check --no-cache-dir install pylint \
    && pip --disable-pip-version-check --no-cache-dir install black \
    && pip --disable-pip-version-check --no-cache-dir install rope \
    && pip --disable-pip-version-check --no-cache-dir install ddt \
    && pip --disable-pip-version-check --no-cache-dir install paho-mqtt \
    && pip --disable-pip-version-check --no-cache-dir install opcua \
    && pip --disable-pip-version-check --no-cache-dir install mysql-connector \
    && pip --disable-pip-version-check --no-cache-dir install python-dotenv \
    && pip --disable-pip-version-check --no-cache-dir install python-yr \
    # Clean up
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

# Switch back to dialog for any ad-hoc use of apt-get
ENV DEBIAN_FRONTEND=dialog


