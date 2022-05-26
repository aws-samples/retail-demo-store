# Running Tests with GNU Make
The Makefile in this folder allows tests to be ran in bulk (or by service/function) without any additional setup.

Run the below commands in this directory (`src/run-tests`)

## Targets
### `make`

Runs default target (`test`).

### `make test`

Run all tests of all types. Currently, only integration tests are supported.

### `make setup`

Depends on `venv` target. Installs test requirements inside a virtual environment.

### `make venv`

Create virtual environment.

### `make integ service=`

Depends on `setup` target. Run all integration tests. (Optional: Specify service parameter to run tests for that service only).

### `make clean`

Remove virtual environment.