FROM ubuntu:18.04
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update
RUN apt-get install -y gnupg
RUN apt-get -y upgrade
RUN apt-get install -y git
RUN apt-get install -y python3
RUN apt-get install -y python3-pip

RUN pip3 install -y configparser

RUN git clone https://github.com/Vlad104/Highload_Server.git # anticache comment
WORKDIR Highload_Server

EXPOSE 80

CMD python3 server.py