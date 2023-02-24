.EXPORT_ALL_VARIABLES:

OS_NAME := $(shell uname -m)

ifeq ($(OS_NAME) , arm64)
ENV_FILE := .env.aarch
else
ENV_FILE := .env.latest
endif

# see https://stackoverflow.com/questions/4219255/how-do-you-get-the-list-of-targets-in-a-makefile
THIS_FILE := $(lastword $(MAKEFILE_LIST))

# Docker CMD:
NOTEBOOK_DOCKER_CLI = docker compose  --env-file ./$(ENV_FILE) run --entrypoint=$(ENTRYPOINT) -it notebook
NOTEBOOK_DOCKER_START = docker compose --env-file ./$(ENV_FILE) up -d notebook && docker compose logs -f notebook
NOTEBOOK_DOCKER_BUILD = docker compose --env-file ./$(ENV_FILE) build notebook 

# Include other definitions
include *.mk
###########################
# PROJECT UTILS
###########################
build: ##@Utils Builds the docker images
	$(DOCKER_BUILD)

###########################
# JUPYTER
###########################
jupyter: ##@Jupyterlab Starts jupyterlab service
	@echo "Starting jupyter lab"
	$(NOTEBOOK_DOCKER_START)

clean: ##@Jupyterlab Cleans the notebook
	$(eval ENTRYPOINT := "/bin/bash -c 'ls . && cd ./work && jupyter nbconvert --clear-output --inplace Exercises/**/*.ipynb'")
	$(NOTEBOOK_DOCKER_CLI)

stop: ##@Jupyterlab Stops all services including the database
	@echo "Stop Jupyter lab, Mongo DB and MongoExpress..."
	docker compose down -v
