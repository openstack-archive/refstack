#!/bin/bash

wait_for_line () {
    while read line; do
        echo "$line" | grep -q "$1" && break
    done < "$2"
    # Read the fifo for ever otherwise process would block
    cat "$2" >/dev/null &
}

build_tmpl () {
    TEMPLATE="$1"
    TARGET="$2"
    cat ${TEMPLATE} | \
    while read LINE; do
        NEWLINE=$(eval echo ${LINE})
        [[ ! -z "$NEWLINE" ]] && echo ${NEWLINE}
    done > ${TARGET}
}

start_mysql () {
    # Start MySQL process for tests
    [ ! -d ${SQL_DIR} ] && mkdir ${SQL_DIR}
    sudo chown dev:dev ${SQL_DIR}
    rm -rf ${SQL_DIR}/out && mkfifo ${SQL_DIR}/out
    rm -rf ${SQL_DIR}/mysql.socket
    # On systems like Fedora here's where mysqld can be found
    PATH=$PATH:/usr/libexec
    mysqld --no-defaults --datadir=${SQL_DIR} --pid-file=${SQL_DIR}/mysql.pid \
        --socket=${SQL_DIR}/mysql.socket --skip-networking \
        --skip-grant-tables &> ${SQL_DIR}/out &
    # Wait for MySQL to start listening to connections
    wait_for_line "mysqld: ready for connections." ${SQL_DIR}/out
}

build_refstack_env () {
    api-sync
    cd /home/dev/refstack
    [ ! -d .venv ] && virtualenv .venv
    .venv/bin/pip install -r requirements.txt
    #Install some dev tools
    .venv/bin/pip install ipython ipdb httpie
    cd /home/dev/refstack
    npm install
#    bower install --config.interactive=false

    build_tmpl /refstack/docker/templates/config.json.tmpl /home/dev/refstack/refstack-ui/app/config.json
    build_tmpl /refstack/docker/templates/refstack.conf.tmpl /home/dev/refstack.conf
    sudo cp /home/dev/refstack.conf /etc
}

start_nginx () {
    [ ! -d /etc/nginx/certificates ] && sudo mkdir /etc/nginx/certificates
    sudo cp /refstack/docker/nginx/refstack_dev.key /etc/nginx/certificates
    sudo cp /refstack/docker/nginx/refstack_dev.crt /etc/nginx/certificates
    sudo cp /refstack/docker/nginx/refstack-site.conf /etc/nginx/sites-enabled/
    sudo nginx
}

while getopts ":s" opt; do
    case ${opt} in
        s) SLEEP=true;;
    esac
done

[[ ${DEBUG_MODE} ]] && set -x

touch /tmp/is-not-ready

start_mysql
start_nginx
build_refstack_env

rm -rf /tmp/is-not-ready

if [[ ${SLEEP} ]]; then
    set +x
    sleep 1024d
fi
