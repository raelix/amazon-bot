#!/bin/bash

# export POOL_SIZE=20
export WAIT_RANDOM=false
export SAMPLES=10
export PERCENTAGE=60
export REQUEST_TIMEOUT=10
export WAIT_BEFORE_LOGIN=1800
export STANDALONE_PROXY=true
export PROXY_TYPE=tor
export IS_TEST=false
export IS_CONTAINERIZED=false
cd src && python3 main.py
