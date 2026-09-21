#!/bin/bash

set -e

export CHIA_ROOT=/data/chia/${CHIA_NETWORK:=mainnet}

trap "killall python" TERM

simpleproxy -d -L 127.0.0.1:25 -R ${MAIL_HOSTNAME:=mail}:25

if [ ! -e "${CHIA_ROOT}/config/config.yaml" ]; then
    ./venv/bin/chia init
fi

exec ./venv/bin/python \
    -m pool.pool_server \
    --log-level ${LOGLEVEL:=INFO} \
    --log-dir ${LOGDIR:=/data/logs} \
    -c ${CONFIG_FILE:=/data/config.yaml}

