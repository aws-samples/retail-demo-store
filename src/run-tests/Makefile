.PHONY: test setup venv integ clean

test: integ
 
venv:
	test -d venv || (python3 -m venv .venv)

setup: venv
	bash ./install-requirements-integ.sh

integ: venv
	bash ./run-tests-integ.sh $(SERVICE)

clean:
	rm -rf .venv