#!/bin/bash

export LIMIT_PRICE=900
export AMAZON_EMAIL=raelix@hotmail.it
export AMAZON_PASSWORD=
export IS_TEST=False
export USE_TOR=False
export IS_CONTAINERIZED=False
cd src && python3 main.py
