#!/bin/bash

export LIMIT_PRICE=900
export AMAZON_EMAIL=
export AMAZON_PASSWORD=
export IS_TEST=False
export USE_TOR=False
export IS_CONTAINERIZED=False
python3 src/main.py
