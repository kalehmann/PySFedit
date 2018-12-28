# PySFedit

## Summary
PySFedit is an editor for pc screen fonts written in Python3 with the
Gtk+-binding pygobject.

The main features of the application are creating headers for a font,
painting glyph bitmaps, adding unicode information for glyhps and
exporting the font to many formats. Supported are binary psf files, gzip
compressed psf files and even assembler files.


## Installation
Simply run `# python3 setup.py install` to install it globally for all
users on your system. If you do not have root privilegs or want to
install PySFedit only for yourself, you can use
`$ python3 setup.py install --user`

## Running without installation
Install the following dependencies:
- gir1.2-gtk-3.0
- python3
- python3-pillow
- python3-gi
- python3-gi-cairo  
Then you can run PySFedit with `python3 bin/pysfedit`

## Further development

### Running unit tests
`$ xvfb-run -a python3 -m unittest -v`

### Adding translations
This application uses gettext for internationalization. First extract
the strings with the following command inside the pysfedit directory:
`$ xgettext --keyword=_ --language=python -o res/locale/pysfedit.pot *.py`

After that you can use poedit to edit existing translations or add new
ones.
