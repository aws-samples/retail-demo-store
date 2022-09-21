source .venv/bin/activate

pip install -r requirements.txt

dir="$PWD"
home_dir="$(dirname "$dir")"
cd "$home_dir" || exit

# Find all directories containing tests
find . -type d  -name 'test' | while read dir; do
  cd "$dir" || exit
  # Install requirements. We currently only have integration tests.
  if [ -f integ/requirements.txt ]; then
    pip install -r integ/requirements.txt
  fi
  cd "$home_dir" || exit
done

deactivate
