#!/bin/bash
set -e

readonly OUT_FILE=$1
readonly DO_DEBUG=$2

echo $OUT_FILE
echo $DO_DEBUG

pip () {
    command pip3 "$@"
}

PACKAGE_FILE=build.zip

echo "Cleaning up intermediate files"
[ -e ${PACKAGE_FILE} ] && rm ${PACKAGE_FILE}
[ -e "package" ] && rm -rf package

echo "Installing Lambda dependencies"
pip install -r requirements.txt --target .

echo "Building Lambda deployment package"
zip -r9 ${PACKAGE_FILE} .
