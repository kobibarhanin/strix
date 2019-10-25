FROM ubuntu:16.04
FROM python:3.7

RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev
RUN apt-get install -y vim

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app
RUN pip3 install -r requirements.txt

COPY . /app
RUN mkdir -p /app/tasks

RUN /bin/bash infra/setup.sh

ENTRYPOINT [ "python3" ]
CMD [ "agent.py" ]

