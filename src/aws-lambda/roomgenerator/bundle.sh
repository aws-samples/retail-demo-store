#!/bin/bash
set -e

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

BASE_DIR=${OLDPWD}
cd ${OLDPWD}
echo "Building Main Lambdas"
for dir in src/*/
    do
        function_name=${dir%*/} 
        function_name=${function_name##*/}
        if [ -f ./${dir}lambda_function.py ]; then             
            echo "  + Building $function_name"
            cd $dir
            zip -r9 ${OLDPWD}/dist/room_generator_$function_name.zip .
            cd -
        fi
    done

cd ${BASE_DIR}
echo "Building Product Load Lambdas"
for dir in src/product_load/*/
    do
        function_name=${dir%*/} 
        function_name=${function_name##*/}
        if [ -f ./${dir}lambda_function.py ]; then             
            echo "  + Building Product Load $function_name"
            cd $dir
            zip -r9 ${OLDPWD}/dist/room_generator_load_$function_name.zip .
            cd -
        fi
    done

echo "Done!"