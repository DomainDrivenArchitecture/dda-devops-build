FROM docker:latest

RUN set -eux; 
RUN apk add --no-cache build-base rust python3 python3-dev py3-pip py3-setuptools py3-wheel libffi-dev openssl-dev cargo;
RUN python3 -m pip install -U pip;
RUN pip3 install pybuilder ddadevops deprecation dda-python-terraform boto3 mfa;