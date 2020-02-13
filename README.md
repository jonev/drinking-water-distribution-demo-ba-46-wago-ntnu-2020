Master: [![Build Status](https://travis-ci.com/jonev/wago-demo-plc-python.svg?branch=master)](https://travis-ci.com/jonev/wago-demo-plc-python)

Develop: [![Build Status](https://travis-ci.com/jonev/wago-demo-plc-python.svg?branch=develop)](https://travis-ci.com/jonev/wago-demo-plc-python)
# README

## Start develoopment environment
Prerequisites: Docker and Visual Studio Code (With remote development extension)
- Open root folder in container with VS code.

## Run tests
- Use vs code Test menu
- Or from root:
```
python -m unittest discover test -p '*_test.py'
```

## Run current file, PLC 2 or PLC 3
- Use vs code run and debug menu, choose plc from the dropdown

## Code Documentation with Sphinx
### New files *.py
- New files need to be added to `docs/modules.rst`, and `*.rst` file need to be added for each file
### Create/Update
To create/update the documentation, run `make html`from /docs directory.
### View
To view the documentation open `docs/_build/html/index.html` in a browser.



## Build to PLC [(source)](https://www.docker.com/blog/multi-arch-images/)
### Prerequisites: 
- Docker [hub account](https://hub.docker.com/)
- Docker settings -> Daemon -> Enable Experimental features
- Add builder:  
`docker buildx create --name builder-for-plc`
### Build (and push) from root:
`docker buildx build -f dockerfile-name --platform linux/arm/v7 -t username/imagename:tag --push .`  
E.g:  
`docker buildx build -f Dockerfile-plc2-pressure --platform linux/arm/v7 -t jonev/python-test:v6 --push .`

### Common errors
- "No space left on device", run `docker system prune` and delete also images with `docker image prune -a`

## Run on PLC
- To avoid long pull-time, reuse image tag
### Prerequisites:
- Download [.ipk file](https://github.com/WAGO/docker-ipk/releases)
- Follow [this guide.](https://github.com/Wago-Norge/Docker-Support)

1. Pull image with:  
`docker pull username/imagename:tag`    
E.g:  
`docker pull jonev/python-test:v6`
2. Run image with output to terminal connected:  
`docker run -it username/imagename:tag`  
E.g:  
`docker run -it jonev/python-test:v6`

### Sources:
- [Docker on PFC200 2. Gen](https://github.com/Wago-Norge/Docker-Support)

## Tools
### Simple mongodb client
Docker:  
`mongo-express -u user -p password -d database -H mongoDBHost -P mongoDBPort`