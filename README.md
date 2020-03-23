Master: [![Build Status](https://travis-ci.com/jonev/wago-demo-plc-python.svg?branch=master)](https://travis-ci.com/jonev/wago-demo-plc-python)

Develop: [![Build Status](https://travis-ci.com/jonev/wago-demo-plc-python.svg?branch=develop)](https://travis-ci.com/jonev/wago-demo-plc-python)
# README

## Start develoopment environment
Prerequisites: Docker and Visual Studio Code (With remote development extension)
- Open root folder in container with VS code.

## Run tests local
- Use vs code Test menu (recommended)
- Or from root:
```
python -m unittest discover test -p '*_test.py'
```
## Run tests as in Travis
1. `docker build -f Dockerfile-tests -t pythontestapp .`
2. `docker run -d --name app pythontestapp sleep infinity`
3. `docker ps -a`
4. `docker exec app python -m unittest discover test -p '*_test.py' -s test -v`
5. `docker rm -f app`


## Run current file, Leakdetection or Simulation program
- Use vs code run and debug menu, choose from the dropdown

## Code Documentation with Sphinx
### New files *.py
- New files need to be added to `docs/modules.rst`, and `*.rst` file need to be added for each file
### Create/Update
To create/update the documentation, run `make html`from /docs directory.
### View
To view the documentation open `docs/_build/html/index.html` in a browser.


## Build to PLC [(source)](https://www.docker.com/blog/multi-arch-images/)
### Prerequisites: 
- To avoid long pull-time, re-use image tag
- Docker [hub account](https://hub.docker.com/)
- Docker settings -> Daemon -> Enable Experimental features
- Add builder:  
`docker buildx create --name builder-for-plc`
### Build (and push) from root:
`docker buildx build -f dockerfile-name --platform linux/amd64,linux/arm64,linux/arm/v7 -t username/imagename:tag --push .`  
E.g:  
`docker buildx build -f Dockerfile-plc2-pressure --platform linux/amd64,linux/arm64,linux/arm/v7 -t jonev/ba-wago:v6 --push .`
- For the different applications, this build and push command is simplified to a simple command `./push.bat`

### Common errors
- "No space left on device", run `docker system prune` and delete also images with `docker image prune -a`

## Run on PLC/HMI
### Prerequisites:
- Download [.ipk file](https://github.com/WAGO/docker-ipk/releases)
- Follow [this guide.](https://github.com/Wago-Norge/Docker-Support)
### Run
1. Connect to the PLC with SSH
2. Pull image with:  
`docker-compose pull`    
3. Run image with output to terminal connected:  
`docker-compose up`  
- Or run detached
`docker-compose up -d`
- Or restart
`docker-compose restart`
- Or restart only one container
`docker-compose restart "service name"`

### Sources:
- [Docker on PFC200 2. Gen](https://github.com/Wago-Norge/Docker-Support)

## Tools
### SSH Client
Putty, or Termius (supports saving passwords and transfer files)
### Transfer files from Windows to Linux
[WinSCP](https://winscp.net/eng/download.php)
- Log inn and drag files between the two computers