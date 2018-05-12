all: build_dist

clean :
	-rm -rf build dist

build_wheel : clean setup.py
	python setup.py bdist_wheel

test :
	pytest

build_dist : test build_wheel
