FROM ubuntu:16.04
EXPOSE 443

ENV DEBIAN_FRONTEND noninteractive
ENV PYTHONPATH=/home/dev/refstack \
    SQL_DIR=/home/dev/mysql
ENV REFSTACK_MYSQL_URL="mysql+pymysql://root@localhost/refstack?unix_socket=${SQL_DIR}/mysql.socket&charset=utf8"

ADD /docker/scripts/* /usr/bin/
ADD . /refstack

RUN apt update -y \
 && apt upgrade -y

RUN apt install -y curl \
                   sudo \
 && groupadd dev \
 && useradd -g dev -s /bin/bash -d /home/dev -m dev \
 && ( umask 226 && echo "dev ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/50_dev ) \
 && curl -sL https://deb.nodesource.com/setup_8.x -o /tmp/setup_8.x.sh \
 && sudo bash /tmp/setup_8.x.sh \
 && apt install -y git \
                   libffi-dev \
                   libmysqlclient-dev \
                   mysql-client \
                   mysql-server \
                   nginx \
                   nodejs \
                   python-dev \
                   python-pip \
                   python3-dev \
                   sudo \
                   vim \
                   wget \
 && rm -rf /var/lib/apt/lists/* \
 && rm -rf /var/lib/mysql/* \
 && rm -rf /etc/nginx/sites-enabled/default \
 && npm install -g yarn \
 && pip install virtualenv tox httpie

USER dev

RUN echo "cd /home/dev/refstack" >> /home/dev/.bashrc \
 && echo "alias activate='source /home/dev/refstack/.venv/bin/activate'" >> /home/dev/.bashrc \
 && echo "alias mysql='mysql --no-defaults -S ${SQL_DIR}/mysql.socket'" >> /home/dev/.bashrc \
 && start.sh \
 && api-init-db

CMD start.sh -s
