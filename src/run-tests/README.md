# Running integration tests with GNU Make

## Getting started

The Makefile in this folder allows tests to be ran in bulk (or by service/function) without any additional setup.

Run commands in this directory (`src/run-tests`)

Example usage:

```sh
# Run this only once to generate `.venv` folder with all dependencies in all `integ` folders
make setup 

# Run integation tests of all services
make integ

# Run integration test of a specific service (default to running against local Docker container)
make integ SERVICE=recommendations

# Run integration test of a specific on a target endpoint
make integ SERVICE=recommendations RECOMMENDATIONS_API_URL=http://retai-LoadB-xxx-yyy.us-west-2.elb.amazonaws.com
```

## List of environment variables used in the integration tests

You can find the list in `<root_project_folder>/.env.template`. All of them have default values and should work out of the box.

The important variables are the `<SERVICE>_API_URL`. They are used to redirect the tests to run against different URLs.

NB: For local development you may need to set up dependencies like local dynamodb before testing. Refer to individual service test READMEs for more detailed info on local dependencies

## Targets

### `make`

Runs default target (`test`).

### `make test`

Run all tests of all types. Currently, only integration tests are supported.

### `make setup`

Installs test requirements inside a virtual environment `.venv`.

### `make venv`

Create virtual environment.

### `make integ SERVICE=`

Depends on `setup` target. Run all integration tests. (Optional: Specify SERVICE parameter to run tests for that service only).

### `make clean`

Remove virtual environment.
