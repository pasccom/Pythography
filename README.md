# Repository description
This repository contains Pythography, a Python library which simplifies the management of bibliography.

It also contains some Python scripts using this library to manage bibliographic databases.

# Content

## Library files
The library is composed of three files:

- [`bibdata.py`](bibdata.py) Generic bibliography management classes
- [`bibtex.py`](bibtex.py) BibTeX file interface
- [`ieeexplore.py`](ieeexplore.py) IEEExplore API interface

See the sphinx documentation for more details on the library usage.

## Scripts
These scripts use the library to automate bibliography management tasks:

- [`download_bibliography`](download_bibliography) Download the bibliography for files from IEEExplore (using [IEEExplore API](https://developer.ieee.org/))
- [`rename_files`](rename_files) Rename linked files according to their bibTeX keys in a bibTeX database.

See the `man` pages for details on the command line arguments for the scripts.

# Developper information
## Sphinx documentation
The documentation of the utilities included in Pythography is provided as
Sphinx reStructuredText, which can be compiled into beatiful documentation
by [Sphinx](http://www.sphinx-doc.org).

To compile the documentation you have to install Sphinx, which can be done using
```
pip install -U sphinx
```
If you are using Unix, you will also need `make`, which is generally provided
by default.

Then `cd` into the `doc` subdirectory and run e.g.
```
make html
```
to generate HTML documentation. The documentation is output in `doc/_build` by default.

## Tests
Tests are included in the library. They can be run using [unittest](https://docs.python.org/fr/3/library/unittest.html) as follows:
```
python3 -m unittest -v
```

# Licensing information
Pythography is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Pythography is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Pythography. If not, see http://www.gnu.org/licenses/
