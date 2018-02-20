# PySFedit
An editor for psf files written in python3.

## Building the docker image for the tests
`$ docker build -f Dockerfile.arm -t karsten/pysfedit-testing:arm .`
## Running unit tests
`$ xvfb-run -a python3 -m unittest -v`

## Extracting translation strings
`$ xgettext --keyword=_ --language=python -o res/locale/pysfedit.pot *.py`
