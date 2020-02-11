#!/usr/bin/env bash

TARGET_PATH="$1"
UNZIP="$2"
TARGET="$3"

cd "${TARGET_PATH}"

if [[ -n "${UNZIP}" ]] ; then
    cd job_pack
    unzip ${TARGET}
    cd ..
fi

pip install .

pip freeze > reqs.txt