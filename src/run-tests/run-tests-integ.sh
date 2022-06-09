source .venv/bin/activate

dir="$PWD"
home_dir="$(dirname "$dir")"
cd "$home_dir" || exit

: '
If we have accepted an argument (service name), attempt to change into that directory.
This ensures we only run tests for that service as requested.
'
if [ ! -z "$1" ]; then
  cd "$1" || { echo "Service does not exist."; exit 1; }
fi

# Find directories containing integration tests
find . -type d  -name 'integ' | while read dir; do
  cd "$dir" || exit
  find . -type f -name 'test*.py' -exec pytest {} +
  # Change back into home directory after each set of tests have been run in order to reset process.
  cd "$home_dir" || exit
done

deactivate