#!/usr/bin/env bash

TARGET_PATH=$1

cd "${TARGET_PATH}"

pip install .

pip freeze > reqs.txt