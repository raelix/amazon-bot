#!/bin/bash

export WAIT_RANDOM=false
export REQUESTS_TIMEOUT=10
export WAIT_BEFORE_LOGIN=1800
export STANDALONE_PROXY=true
export PROXY_TYPE=tor
export AMAZON_EMAIL=raelix@hotmail.it
export AMAZON_PASSWORD=
export PORTAL=https://www.amazon.it
export IS_TEST=false
export USE_TOR=True
export IS_CONTAINERIZED=false
cd src && python3 main.py
