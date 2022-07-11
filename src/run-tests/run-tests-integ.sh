#!/bin/bash

source .venv/bin/activate

dir="$PWD"
home_dir="$(dirname "$dir")"
cd "$home_dir" || exit 1

: '
If we have accepted the first argument argument (service name), attempt to change into that directory.
This ensures we only run tests for that service as requested.
'
if [ ! -z "$1" ]; then
  cd "$1" || { echo "Service does not exist."; exit 1; }
fi

echo "#######################################################"
echo "### Starting integration tests..."
echo "#######################################################"
echo "### List of API URLs in the environment variable"
echo "#######################################################"
echo "# PRODUCTS_API_URL = $PRODUCT_API_URL"
echo "# USERS_API_URL = $USERS_API_URL"
echo "# ORDERS_API_URL = $ORDERS_API_URL"
echo "# RECOMMENDATIONS_API_URL = $RECOMMENDATIONS_API_URL"
echo "# Empty values will be defaulted to local URL"
echo "########################################"

#########################
####### Functions #######
#########################
# Execute pytest in all directory with the name "integ"
run_all_tests() {
  failed_tests=0
  total_tests=0
  for dir in $(find . -type d  -name 'integ')
  do
    pushd "$dir"
    pytest test*.py || failed_tests=$[failed_tests + 1]
    total_tests=$[total_tests + 1]

    # Change back into home directory after each set of tests
    popd
  done

  passed_tests=$(($total_tests - $failed_tests))
  echo "########################################"
  echo "#### Summary: ($passed_tests/$total_tests) test suits pass ####"
  echo "########################################"
  return $failed_tests
}

run_all_tests
result=$?

deactivate

exit $result
