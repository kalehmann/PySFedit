# PySFedit
An editor for psf files written in python3.

## Running unit tests
`$ python3 -m unittest tests/test_psflib*.py`

## Extracting translation strings
`$ xgettext --keyword=_ --language=python -o res/locale/pysfedit.pot *.py`