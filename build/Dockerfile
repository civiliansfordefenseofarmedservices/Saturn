FROM gcr.io/tensorflow/tensorflow:latest-devel

MAINTAINER Civilians for Defense of Armed Services Personnel (saturnrepository@yandex.com)

RUN apt-get update -y && apt-get upgrade -y && apt-get install libmagic-dev -y && pip install python-magic && pip install pillow && apt-get install -y git

WORKDIR "/root"

RUN git clone https://github.com/civiliansfordefenseofarmedservices/Saturn SATURN

ENTRYPOINT [ "/bin/sh", "-c" ]
CMD [ "bash" ]
