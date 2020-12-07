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
# While we don't have access to a pre-packaged version of Botocore with the latest Waypoint SDK, the script manually adds it to the package
echo "Manually adding Waypoint service description to botocore"
mkdir -p botocore/data/location/2020-11-19
cp service-description/service-2.json botocore/data/location/2020-11-19/service-2.json

echo "Building Lambda deployment package"
zip -r9 ${PACKAGE_FILE} .
