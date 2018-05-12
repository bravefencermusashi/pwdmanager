all: build_dist

clean :
	-rm -rf build dist

build_dist : clean setup.py
	python setup.py bdist_wheel
