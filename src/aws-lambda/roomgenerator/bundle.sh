#!/bin/bash
set -e

# LAMBDA_SOURCE=lambda_function.py
# PACKAGE_FILE=roomgen.zip

# echo "Cleaning up intermediate files"
# [ -e ${PACKAGE_FILE} ] && rm ${PACKAGE_FILE}
# [ -e "package" ] && rm -rf package

# echo "Installing Lambda dependencies"
# pip install -r requirements.txt --target ./package
# pip install --platform manylinux2014_x86_64 --target=./package --implementation cp --python-version 3.11 --only-binary=:all: --upgrade Pillow

# echo "Building Lambda deployment package"
# cd package
# zip -r9 ${OLDPWD}/${PACKAGE_FILE} .
# cd ${OLDPWD}

# echo "Adding Lambda function source code to package"
# zip -g ${PACKAGE_FILE} ${LAMBDA_SOURCE}

echo "Cleaning up intermediate files"
[ -e "dist" ] && rm -rf dist

echo "Installing base layer dependencies"
pip install -r src/_layers/base/requirements.txt --target ./dist/_layers/base/python
echo "Building base layer package"
cd dist/_layers/base/
zip -r9 ${OLDPWD}/dist/room_generator_base_layer.zip .

cd ${OLDPWD}
echo "Installing shared layer dependencies"
pip install -r src/_layers/shared/requirements.txt --target ./dist/_layers/shared/python
pip install --platform manylinux2014_x86_64 --target ./dist/_layers/shared/python --implementation cp --python-version 3.12 --only-binary=:all: --upgrade pydantic_core
pip install --platform manylinux2014_x86_64 --target ./dist/_layers/shared/python --implementation cp --python-version 3.12 --only-binary=:all: --upgrade Pillow
echo "Building shared layer package"
cp -R src/_layers/shared/src/* ./dist/_layers/shared/python/
cd dist/_layers/shared/
zip -r9 ${OLDPWD}/dist/room_generator_shared_layer.zip .

cd ${OLDPWD}
echo "Build dynamodb stream handler package"
cd src/dynamodb_stream_handler
zip -r9 ${OLDPWD}/dist/room_generator_dynamodb_stream_handler.zip .

cd ${OLDPWD}
echo "Build image analyzer package"
cd src/image_analyzer
zip -r9 ${OLDPWD}/dist/room_generator_image_analyzer.zip .

cd ${OLDPWD}
echo "Build image generation package"
cd src/image_generation
zip -r9 ${OLDPWD}/dist/room_generator_image_generation.zip .

cd ${OLDPWD}
echo "Build result processor package"
cd src/inference_result_processor
zip -r9 ${OLDPWD}/dist/room_generator_inference_result_processor.zip .

cd ${OLDPWD}
echo "Build inference sns subscriber package"
cd src/inference_sns_subscriber
zip -r9 ${OLDPWD}/dist/room_generator_inference_sns_subscriber.zip .

cd ${OLDPWD}
echo "Build API package"
cd src/api_handler
zip -r9 ${OLDPWD}/dist/room_generator_api_handler.zip .

cd ${OLDPWD}

echo "Done!"