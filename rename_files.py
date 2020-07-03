#! /usr/bin/python3

import os

from argparse import ArgumentParser
from appdirs import AppDirs
from configparser import ConfigParser
from warnings import warn as warning

from bibtex import BibFile

if __name__ == '__main__':
    # Parse command line arguments:
    argParser = ArgumentParser(
        description="Rename linked PDF files according to BibTeX key",
        epilog="""License: GPL v3, see <http://www.gnu.org/licenses/>
Copyright (c) 2019-2020 Pascal COMBES <pascom@orange.fr>""")
    argParser.add_argument('bibFile',
        nargs=1,
        help="BibTeX file where to write bibliographic data"
    )
    args = argParser.parse_args()

    # Load bibTeX file:
    bibFile = BibFile(args.bibFile[0])
    bibFile.read()

    # Backup bibTeX file:
    os.rename(args.bibFile[0], args.bibFile[0] + '.old')

    # Move files and update file entries:
    for bibItem in bibFile:
        oldPath = bibItem['file']
        if os.path.isabs(oldPath):
            oldPath = os.path.relpath(oldPath, os.path.dirname(args.bibFile[0]))
        newPath = os.path.join(os.path.dirname(oldPath), bibItem['key'] + '.pdf')
        print(f"Moving {oldPath} to {newPath}")
        try:
            os.rename(os.path.join(os.path.dirname(args.bibFile[0]), oldPath),
                      os.path.join(os.path.dirname(args.bibFile[0]), newPath))
            bibItem['file'] = newPath
        except FileNotFoundError:
            warning(f"Could not find {oldPath}")

    # Write bibTeX file:  
    bibFile.write()
    
