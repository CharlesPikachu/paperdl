.PHONY: install develop build publish clean

install:
	python -m pip install .

develop:
	python -m pip install -e .

build: clean
	python -m pip install --upgrade build twine
	python -m build
	twine check dist/*

publish: build
	twine upload dist/*

clean:
	rm -rf build dist *.egg-info