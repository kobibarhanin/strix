FROM ubuntu:16.04
FROM python:3.7

RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev
RUN apt-get install -y vim
RUN apt-get install -y zip

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app
RUN pip3 install -r requirements.txt

COPY . /app
RUN mkdir -p /app/tasks
RUN mkdir -p /app/temp

#RUN /bin/bash infra/setup.sh
ENV PYTHONPATH "${PYTHONPATH}:/app:/app/lib/:/app/infra/:/app/app/"

ENTRYPOINT [ "python3" ]
CMD [ "app/app.py" ]
