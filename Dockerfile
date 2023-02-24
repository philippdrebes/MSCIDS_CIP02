FROM python:3.11-bullseye

# install prerequisites
RUN python3 -m pip install --user --upgrade setuptools wheel
RUN python3 -m pip install --upgrade pytest
RUN apt-get update
RUN apt-get install -y git-all build-essential

# add source
RUN mkdir /app
COPY requirements.txt /app

# install requirements
WORKDIR /app
RUN pip install -r requirements.txt
RUN pip install pytest pytest-cov coverage

# test library
ENV PYTHONPATH="/app"
