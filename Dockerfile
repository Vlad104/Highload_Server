FROM ubuntu:18.04
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update
RUN apt-get install -y gnupg
RUN apt-get -y upgrade
RUN apt-get install -y git
RUN apt-get install -y python3
RUN apt-get install -y python3-pip

RUN pip3 install configparser
RUN pip3 install psutil

RUN git clone https://github.com/Vlad104/Highload_Server.git # anticache comment 1
WORKDIR Highload_Server

RUN git clone https://github.com/init/http-test-suite.git # anticache comment
RUN mkdir -p /var/www/html
RUN mv http-test-suite/httptest /var/www/html

EXPOSE 80

CMD python3 server.py