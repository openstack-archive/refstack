FROM ubuntu:14.04

RUN \
    groupadd dev && \
    useradd -g dev -s /bin/bash -d /home/dev -m dev && \
    ( umask 226 && echo "dev ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/50_dev )

ENV DEBIAN_FRONTEND noninteractive

RUN \
    apt-get update && \
    apt-get -y install \
    sudo git vim wget \
    nginx \
    python-dev python3-dev python-pip \
    libmysqlclient-dev mysql-client-5.6 mysql-server-5.6 \
    npm && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /var/lib/mysql/* && \
    rm -rf /etc/nginx/sites-enabled/default

RUN \
    pip install virtualenv tox ipython ipdb httpie && \
    ln -s /usr/bin/nodejs /usr/bin/node

ADD /docker/scripts/* /usr/bin/
ADD . /refstack

ENV PYTHONPATH=/home/dev/refstack \
    SQL_DIR=/home/dev/mysql

ENV REFSTACK_MYSQL_URL="mysql+pymysql://root@localhost/refstack?unix_socket=${SQL_DIR}/mysql.socket&charset=utf8"

USER dev

RUN  \
    echo "cd /home/dev/refstack" >> /home/dev/.bashrc &&\
    echo "alias activate='source /home/dev/refstack/.venv/bin/activate'" >> /home/dev/.bashrc &&\
    echo "alias mysql='mysql --no-defaults -S ${SQL_DIR}/mysql.socket'" >> /home/dev/.bashrc &&\
    start.sh &&\
    api-init-db

CMD start.sh -s
EXPOSE 443