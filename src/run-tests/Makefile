.PHONY: test setup venv integ clean

# TODO: add documentation
test: integ

# TODO: can this be optional? Doesn't make sense to pip install every run.
setup: venv
	bash ./install-requirements-integ.sh

venv:
	test -d venv || (python3 -m venv .venv)

integ: setup
	bash ./run-tests-integ.sh $(service)

clean:
	rm -rf .venv