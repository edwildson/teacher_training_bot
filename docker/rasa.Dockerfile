FROM python:3.8-slim-buster as base

# Setup env
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1

# Install compilation dependencies
RUN apt-get update && apt-get install -y --no-install-recommends gcc

# Install python dependencies in /.venv
COPY amadeus_bot/requirements.txt .
RUN pip install -r requirements.txt
#RUN python -m spacy download pt_core_news_md

# Create and switch to a new user
RUN useradd --create-home app-user
WORKDIR /home/app-user
USER app-user
