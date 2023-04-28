.EXPORT_ALL_VARIABLES:

# see https://stackoverflow.com/questions/4219255/how-do-you-get-the-list-of-targets-in-a-makefile
THIS_FILE := $(lastword $(MAKEFILE_LIST))

# see https://stackoverflow.com/a/3931814/5151324
.PHONY: docs

# Include other definitions
include *.mk

###########################
# PROJECT UTILS
###########################
docs: ##@Utils Builds the documentation
	./venv/bin/pdoc3 --html --force --output-dir docs ./src/extractors ./src/loaders
