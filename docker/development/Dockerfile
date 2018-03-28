FROM python:3.6.1

RUN mkdir /code/
WORKDIR /code/
ADD ./requirements/ /code/requirements/

RUN pip install -r /code/requirements/development.txt

RUN rm -rf /etc/id_rsa
RUN rm -rf ${HOME}/.ssh
