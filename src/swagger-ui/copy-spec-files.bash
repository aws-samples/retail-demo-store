#!/bin/bash

# This script is to be run from the root folder of this repository

mkdir -p src/swagger-ui/specs
declare -a SERVICES=(offers location carts orders products users videos search recommendations)
for SERVICE in "${SERVICES[@]}";
  do
    mkdir -p "src/swagger-ui/specs/$SERVICE";
    cp "src/$SERVICE/openapi/spec.yaml" "src/swagger-ui/specs/$SERVICE/";
  done