FROM ubuntu:18.04

RUN apt-get update
RUN apt-get install -y gnupg
RUN apt-get -y upgrade
RUN apt-get -y git
RUN apt-get install python3
RUN apt-get install python3-pip

RUN pip3 install configparser
RUN pip3 install urllib3

RUN git clone https://github.com/Vlad104/Highload_Server.git # anticache comment
WORKDIR Highload_Server

EXPOSE 80

CMD python3 server.py