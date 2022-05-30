.PHONY: test setup venv integ clean

test: integ

setup: venv
	bash ./install-requirements-integ.sh

venv:
	test -d venv || (python3 -m venv .venv)

integ: setup
	bash ./run-tests-integ.sh $(service)

clean:
	rm -rf .venv