import bibdata

import re
import datetime

class BibTeXData(bibdata.BibData):
    """ An instance of this class represents BibTex data, which is validated following BibTeX rules, when necessary.

        :param data: Bibliography data:

        * An instance of :class:`BibData` for copy.
        * A :class:`dict` containing bibliography data. In this case, the data will be validated before adding it.
    """

    class __BibTexFields:
        def __monthValidator(month):
            months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'];
            longMonths = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']

            if month.lower() in months:
                return month.lower()

            try:
                return months[longMonths.index(month.lower())]
            except ValueError:
                pass

            try:
                return months[int(month) - 1]
            except ValueError:
                pass

            return False

        class __PageRange:
            def __init__(self, value):
                match = re.fullmatch(r'(?P<begin>\d+)\s*(?:-{1,2}\s*(?P<end>\d+))?', value)
                if not match:
                    raise ValueError(f"Invalid page range: \"{value}\"")
                self.begin = int(match['begin'])
                try:
                    self.end = int(match['end'])
                except KeyError:
                    self.end = self.begin

            def __str__(self):
                if self.begin == self.end:
                    return str(self.begin)
                return str(self.begin) + '--' + str(self.end)

            def __repr__(self):
                return f"PageRange({self.begin}, {self.end})"

        __fields = {
            'address': {
                'doc': "Publisher's address (usually just the city, but can be the full address for lesser-known publishers).",
                'type': str,
            },
            'annote': {
                'doc': "An annotation for annotated bibliography styles (not typical).",
                'type': str,
            },
            'author': {
                'doc': "The name(s) of the author(s) (in the case of more than one author, separated by and).",
                'type': bibdata.AuthorList,
            },
            'booktitle': {
                'doc': "The title of the book, if only part of it is being cited.",
                'type': str,
            },
            'chapter': {
                'doc': "The chapter number.",
                'type': int,
                'min': 1,
            },
            'content_type': {
                'doc': "BibTeX entry type",
                'type': str,
                'values': ['article', 'book', 'booklet', 'inbook', 'incollection', 'inproceedings', 'manual', 'mastersthesis', 'misc', 'phdthesis', 'proceedings', 'techreport', 'unpublished'],
            },
            'crossref': {
                'doc': "The key of the cross-referenced entry.",
                'type': str,
            },
            'doi': {
                'doc': "Digital object identifier.",
                'type': bibdata.DOI,
            },
            'edition': {
                'doc': "The edition of a book, long form (such as \"First\" or \"Second\").",
                'type': str,
            },
            'editor': {
                'doc': "The name(s) of the editor(s).",
                'type': str,
            },
            'howpublished': {
                'doc': "How it was published, if the publishing method is nonstandard.",
                'type': str,
            },
            'institution': {
                'doc': "The institution that was involved in the publishing, but not necessarily the publisher.",
                'type': str,
            },
            'journal': {
                'doc': "The journal or magazine the work was published in.",
                'type': str,
            },
            'key': {
                'doc': "A hidden field used for specifying or overriding the alphabetical order of entries (when the \"author\" and \"editor\" fields are missing). Note that this is very different from the key (mentioned just after this list) that is used to cite or cross-reference the entry.",
                'type': str,
            },
            'month': {
                'doc': "The month of publication (or, if unpublished, the month of creation).",
                'type': str,
                'validator': __monthValidator,
            },
            'note': {
                'doc': "Miscellaneous extra information.",
                'type': str,
            },
            'number': {
                'doc': "The \"(issue) number\" of a journal, magazine, or tech-report, if applicable. Note that this is not the \"article number\" assigned by some journals.",
                'type': int,
                'min': 1,
            },
            'organization': {
                'doc': "The conference sponsor.",
                'type': str,
            },
            'pages': {
                'doc': "Page numbers, separated either by commas or double-hyphens.",
                'type': __PageRange,
            },
            'publisher': {
                'doc': "The publisher's name.",
                'type': str,
            },
            'school': {
                'doc': "The school where the thesis was written.",
                'type': str,
            },
            'series': {
                'doc': "The series of books the book was published in (e.g. \"The Hardy Boys\" or \"Lecture Notes in Computer Science\").",
                'type': str,
            },
            'title': {
                'doc': "The title of the work.",
                'type': str,
            },
            'type': {
                'doc': "The field overriding the default type of publication (e.g.  \"Research Note\" for techreport, \"{PhD} dissertation\" for phdthesis, \"Section\" for inbook/incollection)?",
                'type': str,
            },
            'volume': {
                'doc': "The volume of a journal or multi-volume book.",
                'type': int,
                'min': 1,
            },
            'year': {
                'doc': "The year of publication (or, if unpublished, the year of creation).",
                'type': int,
                'max': datetime.date.today().year,
            },
        }

        def __getitem__(self, name):
            try:
                return self.__fields[name]
            except KeyError as e:
                if name.isalpha():
                    return {
                        'doc': "Unofficial user-defined field.",
                        'type': str,
                    }
                raise e

    fields = __BibTexFields()


class BibFile(bibdata.BibDataSet):
    """ An instance of this class represents a BibTeX file. It provides methods for reading from and writing to BibTeX files.
        It is implemented as a subclass of :class:`BibDataSet`.

        :param filePath: The ``*.bib`` file path.
        :param data: An instance of :class:`BibDataSet` or a :class:`list` of bibliography data (:class:`BibData` instances or dictionnaries).
    """
    bibTypes = {
        'article': {
            'doc': "An article from a journal or magazine.",
            'required': ['author', 'title', 'journal', 'year', 'volume'],
            'optional': ['number', 'pages', 'month', 'doi'],
        },
        'book': {
            'doc': "A book with an explicit publisher.",
            'required': ['author', 'title', 'publisher', 'year'],
            'optional': ['editor', 'volume', 'number', 'series', 'address', 'edition', 'month'],
        },
        'booklet': {
            'doc': "A work that is printed and bound, but without a named publisher or sponsoring institution.",
            'required': ['title'],
            'optional': ['author', 'howpublished', 'address', 'month', 'year'],
        },
        'inbook' : {
            'doc': "A part of a book, usually untitled. May be a chapter (or section, etc.) and/or a range of pages.",
            'required': ['author', 'title', 'pages', 'publisher', 'year'],
            'optional': ['editor', 'chapter', 'volume', 'number', 'series', 'type', 'address', 'edition', 'month'],
        },
        'incollection': {
            'doc': "A part of a book having its own title.",
            'required': ['author', 'title', 'booktitle', 'publisher', 'year'],
            'optional': ['editor', 'volume', 'number', 'series', 'type', 'chapter', 'pages', 'address', 'edition', 'month'],
        },
        'inproceedings': {
            'doc': "An article in a conference proceedings.",
            'required': ['author', 'title', 'booktitle', 'year'],
            'optional': ['editor', 'volume', 'number', 'series', 'pages', 'address', 'month', 'organization', 'publisher'],
        },
        'manual': {
            'doc': "Technical documentation.",
            'required': ['title'],
            'optional': ['author', 'organization', 'address', 'edition', 'month', 'year'],
        },
        'mastersthesis': {
            'doc': "A Master's thesis.",
            'required': ['author', 'title', 'school', 'year'],
            'optional': ['type', 'address', 'month'],
        },
        'misc': {
            'doc': "For use when nothing else fits.",
            'required': [],
            'optional': ['author', 'title', 'howpublished', 'month', 'year'],
        },
        'phdthesis': {
            'doc': "A Ph.D. thesis.",
            'required': ['author', 'title', 'school', 'year'],
            'optional': ['type', 'address', 'month'],
        },
        'proceedings': {
            'doc': "The proceedings of a conference.",
            'required': ['title', 'year'],
            'optional': ['editor', 'volume', 'number', 'series', 'address', 'month', 'publisher', 'organization'],
        },
        'techreport': {
            'doc': "A report published by a school or other institution, usually numbered within a series.",
            'required': ['author', 'title', 'institution', 'year'],
            'optional': ['type', 'number', 'address', 'month'],
        },
        'unpublished': {
            'doc': "A document having an author and title, but not formally published.",
            'required': ['author', 'title'],
            'optional': ['month', 'year'],
        },
    }

    fieldAliases = {
        'address': ['conference_location'],
        'author': ['authors'],
        'booktitle': ['publication_title'],
        'chapter': [],
        'crossref': [],
        'doi': [],
        'edition': [],
        'editor': [],
        'howpublished': [],
        'institution': [],
        'journal': ['publication_title'],
        'month': ['publication_month', 'conference_month'],
        'number': ['issue', 'is_number'],
        'organization': [],
        'pages': [],
        'publisher': [],
        'school': [],
        'series': [],
        'title': [],
        'type': [],
        'volume': [],
        'year': ['publication_year', 'conference_year'],
    }

    warningsDisabled = False
    @classmethod
    def __warning(cls, msg):
        if not cls.warningsDisabled:
            print(f'WARNING: {msg}')

    def __cleanGroup(self, group):
        return re.sub(r'\s+', ' ', group)

    def __getField(self, bibItem, field, required=False):
        if field in bibItem:
            return field
        if field in self.fieldAliases:
            for alias in self.fieldAliases[field]:
                if alias in bibItem:
                    return alias
        if required:
            self.__warning(f"Could not find required field: {field}")

    def __genKey(self, bibItem):
        authors = bibItem[self.__getField(bibItem, 'author')]
        key = ''.join([authors[0]['name']] + [author['initial'] for author in authors[1:]])

        try:
            key += str(bibItem[self.__getField(bibItem, 'year')])
        except KeyError:
            pass

        print(bibItem)
        print(type(bibItem))
        try:
            key += bibItem[self.__getField(bibItem, 'publication_code')]
        except KeyError:
            pass

        return key

    def __init__(self, filePath, data=None):
        super().__init__(data)
        self.__filePath = filePath
        if self.__filePath[-4:] != '.bib':
            self.__filePath += '.bib'

    def read(self):
        """ read()

            This method opens the ``*.bib`` file, parses it and loads its content into the underlying :class:`BibDataSet`
        """
        with open(self.__filePath, 'rt') as bibFile:
            self.parseFile(bibFile)

    def parseFile(self, bibFile):
        """ parseFile(bibFile)

            Parses the given ``*.bib`` file for entries and loads it in underlying data.

            :param bibFile: The :class:`file` instance to be parsed.
        """
        OUTSIDE = 0
        ENTRY_TYPE = 1
        COMMENT = 2

        mode = OUTSIDE

        while True:
            c = bibFile.read(1)
            if not c:
                return
            if mode == OUTSIDE:
                if not c.strip():
                    continue
                elif c == '@':
                    mode = ENTRY_TYPE
                    entryType = ''
                elif c == '%':
                    prevMode = mode
                    mode = COMMENT
                else:
                    self.__warning(f"Omitted unexpected charater: \"{c}\"")
            elif mode == COMMENT:
                if c == '\n':
                    mode = prevMode
            elif mode == ENTRY_TYPE:
                if c == '{':
                    self.__iadd__(self.parseEntry(bibFile, entryType.strip().lower()))
                    mode = OUTSIDE
                elif c == '%':
                    prevMode = mode
                    mode = COMMENT
                else:
                    entryType += c

    def parseEntry(self, bibFile, entryType):
        """ parseEntry(bibFile, entryType)

            Parses one entry in the given ``*.bib`` file and loads it in underlying data.

            :param bibFile: The :class:`file` instance to be parsed.
            :param entryType: BibTeX entry type

            :returns: A :class:`BibTeXData` containing the parsed entry.
        """
        OUTSIDE = 0
        COMMENT = 1
        FIELD_NAME = 2
        FIELD_VALUE = 3

        mode = OUTSIDE
        escaped = False
        bibData = BibTeXData({'content_type': entryType})

        while True:
            c = bibFile.read(1)
            if not c:
                self.__warning("Unexpected end of file inside entry")
                return bibData

            if mode == OUTSIDE:
                if c == '}':
                    return bibData
                elif not c.strip():
                    continue
                elif c == '%':
                    prevMode = mode
                    mode == COMMENT
                elif c.isalnum():
                    mode = FIELD_NAME
                    fieldName = c
            elif mode == COMMENT:
                if c == '\n':
                    mode = prevMode
            elif mode == FIELD_NAME:
                if c == '}':
                    #print(f"Parsed field name: \"{fieldName}\"")
                    bibData['key'] = fieldName.strip()
                    return bibData
                elif c == '=':
                    #print(f"Parsed field name: \"{fieldName}\"")
                    mode = FIELD_VALUE
                    fieldValue = ''
                elif c == ',':
                    #print(f"Parsed field name: \"{fieldName}\"")
                    bibData['key'] = fieldName.strip()
                    mode = OUTSIDE
                elif c == '%':
                    fieldName += ' '
                    prevMode = mode
                    mode = COMMENT
                else:
                    fieldName += c
            elif mode == FIELD_VALUE:
                if c == '}':
                    #print(f"Parsed field value: \"{fieldValue}\"")
                    bibData[fieldName.strip()] = fieldValue.strip()
                    return bibData
                if c == '\\':
                    escaped = not escaped
                elif (c == ',') and not escaped:
                    #print(f"Parsed field value: \"{fieldValue}\"")
                    bibData[fieldName.strip()] = fieldValue.strip()
                    mode = OUTSIDE
                elif (c == '%') and not escaped:
                    prevMode = mode
                    mode = COMMENT
                elif (c == '{') and not escaped:
                    fieldValue += self.parseGroup(bibFile)
                else:
                    fieldValue += c

    def parseGroup(self, bibFile):
        """ parseGroup(bibFile)

            Parses one group in the given ``*.bib`` file

            :param bibFile: The :class:`file` instance to be parsed.

            :returns: The contents of the group as a Python :class:`str`
        """
        escaped = False
        commented = False
        group = ''

        while True:
            c = bibFile.read(1)
            if not c:
                self.__warning("Unexpected end of file inside group")
                #print(f"Parsed group: {{{self.__cleanGroup(group)}}}")
                return self.__cleanGroup(group)

            if commented:
                if c == '\n':
                    commented = False
                continue

            if escaped:
                group += c
                escaped = False
                continue
            if (c == '\\'):
                escaped = not escaped

            if (c == '%'):
                commented = True
            elif (c == '}'):
                #print(f"Parsed group: {{{self.__cleanGroup(group)}}}")
                return self.__cleanGroup(group)
            elif (c == '{'):
                group += '{' + self.parseGroup(bibFile) + '}'
            else:
                group += c

    def write(self, mode='at'):
        """ write(mode='at')

            Writes the underlying bibliography data to the ``*.bib`` file.

            :param mode: The mode for opening the ``*.bib`` file (should be ``'at'`` for appending data or ``'wt'`` for overwriting data).
        """
        with open(self.__filePath, mode) as bibFile:
            for bibItem in self:
                bibFile.write(f"@{bibItem['content_type'].upper()} {{{self.__genKey(bibItem)},\n")
                fieldsDone = ['content_type']
                # Output required fields:
                for f in self.bibTypes[bibItem['content_type']]['required']:
                    field = self.__getField(bibItem, f, True)
                    if field:
                        bibFile.write(f"  {f} = {{{bibItem[field]}}},\n")
                        fieldsDone += [field]
                # Output optional fields:
                for f in self.bibTypes[bibItem['content_type']]['optional']:
                    field = self.__getField(bibItem, f, False)
                    if field:
                        bibFile.write(f"  {f} = {{{bibItem[field]}}},\n")
                        fieldsDone += [field]
                # Output available bibTeX fields:
                for field, aliases in self.fieldAliases.items():
                    for alias in aliases:
                        if alias in fieldsDone:
                            break
                        try:
                            bibFile.write(f"  {field} = {{{bibItem[alias]}}},\n")
                            break
                        except KeyError:
                            pass
                # Output other fields:
                for field, value in bibItem:
                    if field in fieldsDone:
                        continue
                    bibFile.write(f"  {field} = {{{value}}},\n")
                bibFile.write('}\n\n')

if __name__ == '__main__':
    #bibFile = BibFile('test')
    #bibFile = BibFile('/home/pascal/SharedDocs/These/Documents/Bibliographie/core')
    #bibFile = BibFile('/home/pascal/SharedDocs/These/Documents/Bibliographie/injection-signal.bib')
    #bibFile.read()
    #print(bibFile)

    from ieeexplore import ResultSet

    bibFile = BibFile('test', ResultSet(None, {
  "total_records": 6,
  "total_searched": 4804555,
  "articles": [
    {
      "doi": "10.1109/CDC.2014.7040330",
      "title": "Energy-based modeling of electric motors",
      "publisher": "IEEE",
      "isbn": "978-1-4673-6090-6",
      "issn": "0191-2216",
      "rank": 1,
      "authors": {
        "authors": [
          {
            "affiliation": "Akka Technologies, France",
            "authorUrl": "https://ieeexplore.ieee.org/author/38495559700",
            "id": 38495559700,
            "full_name": "Al Kassem Jebai",
            "author_order": 1
          },
          {
            "affiliation": "Centre Automatique et Syst\u00e8mes, MINES ParisTech, PSL Research University, France",
            "authorUrl": "https://ieeexplore.ieee.org/author/37085493932",
            "id": 37085493932,
            "full_name": "Pascal Combes",
            "author_order": 2
          },
          {
            "affiliation": "Schneider Toshiba Inverter Europe, 27120 Pacy-sur-Eure, France",
            "authorUrl": "https://ieeexplore.ieee.org/author/37590743800",
            "id": 37590743800,
            "full_name": "Fran\u00e7ois Malrait",
            "author_order": 3
          },
          {
            "affiliation": "Centre Automatique et Syst\u00e8mes, MINES ParisTech, PSL Research University, France",
            "authorUrl": "https://ieeexplore.ieee.org/author/37335302900",
            "id": 37335302900,
            "full_name": "Philippe Martin",
            "author_order": 4
          },
          {
            "affiliation": "Centre Automatique et Syst\u00e8mes, MINES ParisTech, PSL Research University, France",
            "authorUrl": "https://ieeexplore.ieee.org/author/37299202100",
            "id": 37299202100,
            "full_name": "Pierre Rouchon",
            "author_order": 5
          }
        ]
      },
      "access_type": "LOCKED",
      "content_type": "Conferences",
      "abstract": "We propose a new approach to modeling electrical machines based on energy considerations and construction symmetries of the motor. We detail the approach on the Permanent-Magnet Synchronous Motor and show that it can be extended to Synchronous Reluctance Motor and Induction Motor. Thanks to this approach we recover the usual models without any tedious computation. We also consider effects due to non-sinusoidal windings or saturation and provide experimental data.",
      "article_number": "7040330",
      "pdf_url": "https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=7040330",
      "html_url": "https://ieeexplore.ieee.org/document/7040330/",
      "abstract_url": "https://ieeexplore.ieee.org/document/7040330/",
      "publication_title": "53rd IEEE Conference on Decision and Control",
      "conference_location": "Los Angeles, CA",
      "conference_dates": "15-17 Dec. 2014",
      "publication_number": 7027307,
      "is_number": 7039338,
      "publication_year": 2014,
      "publication_date": "15-17 Dec. 2014",
      "start_page": "6009",
      "end_page": "6016",
      "citing_paper_count": 3,
      "citing_patent_count": 0,
      "index_terms": {
        "ieee_terms": {
          "terms": [
            "Torque",
            "Rotors",
            "Equations",
            "Stator windings",
            "Computational modeling",
            "Permanent magnet motors",
            "Reluctance motors"
          ]
        }
      }
    },
    {
      "doi": "10.1109/IECON.2017.8216352",
      "title": "Obtaining the current-flux relations of the saturated PMSM by signal injection",
      "publisher": "IEEE",
      "isbn": "978-1-5386-1127-2",
      "rank": 2,
      "authors": {
        "authors": [
          {
            "affiliation": "Schneider Toshiba Inverter Europe, 27120 Pacy-sur-Eure, France",
            "authorUrl": "https://ieeexplore.ieee.org/author/37085493932",
            "id": 37085493932,
            "full_name": "Pascal Combes",
            "author_order": 1
          },
          {
            "affiliation": "Schneider Toshiba Inverter Europe, 27120 Pacy-sur-Eure, France",
            "authorUrl": "https://ieeexplore.ieee.org/author/37590743800",
            "id": 37590743800,
            "full_name": "Fran\u00e7ois Malrait",
            "author_order": 2
          },
          {
            "affiliation": "Centre Automatique et Syst\u00e8mes, MINES ParisTech, PSL Research University, 75006 Paris, France",
            "authorUrl": "https://ieeexplore.ieee.org/author/37335302900",
            "id": 37335302900,
            "full_name": "Philippe Martin",
            "author_order": 3
          },
          {
            "affiliation": "Centre Automatique et Syst\u00e8mes, MINES ParisTech, PSL Research University, 75006 Paris, France",
            "authorUrl": "https://ieeexplore.ieee.org/author/37299202100",
            "id": 37299202100,
            "full_name": "Pierre Rouchon",
            "author_order": 4
          }
        ]
      },
      "access_type": "LOCKED",
      "content_type": "Conferences",
      "abstract": "This paper proposes a method based on signal injection to obtain the saturated current-flux relations of a PMSM from locked-rotor experiments. With respect to the classical method based on time integration, it has the main advantage of being completely independent of the stator resistance; moreover, it is less sensitive to voltage biases due to the power inverter, as the injected signal may be fairly large.",
      "article_number": "8216352",
      "pdf_url": "https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=8216352",
      "html_url": "https://ieeexplore.ieee.org/document/8216352/",
      "abstract_url": "https://ieeexplore.ieee.org/document/8216352/",
      "publication_title": "IECON 2017 - 43rd Annual Conference of the IEEE Industrial Electronics Society",
      "conference_location": "Beijing",
      "conference_dates": "29 Oct.-1 Nov. 2017",
      "publication_number": 8168197,
      "is_number": 8216002,
      "publication_year": 2017,
      "publication_date": "29 Oct.-1 Nov. 2017",
      "start_page": "2097",
      "end_page": "2103",
      "citing_paper_count": 1,
      "citing_patent_count": 0,
      "index_terms": {
        "ieee_terms": {
          "terms": [
            "Stators",
            "Saturation magnetization",
            "Couplings",
            "Resistance",
            "Rotors",
            "Torque",
            "Current measurement"
          ]
        }
      }
    },
    {
      "doi": "10.1109/ACC.2016.7525045",
      "title": "Adding virtual measurements by signal injection",
      "publisher": "IEEE",
      "isbn": "978-1-4673-8682-1",
      "issn": "2378-5861",
      "rank": 3,
      "authors": {
        "authors": [
          {
            "affiliation": "Centre Automatique et Syst\u00e8mes, MINES ParisTech, PSL Research University, Paris, France",
            "authorUrl": "https://ieeexplore.ieee.org/author/37085493932",
            "id": 37085493932,
            "full_name": "Pascal Combes",
            "author_order": 1
          },
          {
            "affiliation": "Schneider Toshiba Inverter Europe, 27120 Pacy-sur-Eure, France",
            "authorUrl": "https://ieeexplore.ieee.org/author/38495559700",
            "id": 38495559700,
            "full_name": "Al Kassem Jebai",
            "author_order": 2
          },
          {
            "affiliation": "Schneider Toshiba Inverter Europe, 27120 Pacy-sur-Eure, France",
            "authorUrl": "https://ieeexplore.ieee.org/author/37590743800",
            "id": 37590743800,
            "full_name": "Fran\u00e7ois Malrait",
            "author_order": 3
          },
          {
            "affiliation": "Centre Automatique et Syst\u00e8mes, MINES ParisTech, PSL Research University, Paris, France",
            "authorUrl": "https://ieeexplore.ieee.org/author/37335302900",
            "id": 37335302900,
            "full_name": "Philippe Martin",
            "author_order": 4
          },
          {
            "affiliation": "Centre Automatique et Syst\u00e8mes, MINES ParisTech, PSL Research University, Paris, France",
            "authorUrl": "https://ieeexplore.ieee.org/author/37299202100",
            "id": 37299202100,
            "full_name": "Pierre Rouchon",
            "author_order": 5
          }
        ]
      },
      "access_type": "LOCKED",
      "content_type": "Conferences",
      "abstract": "We propose a method to \u201ccreate\u201d a new measurement output by exciting the system with a high-frequency oscillation. This new \u201cvirtual\u201d measurement may be useful to facilitate the design of a suitable control law. The approach is especially interesting when the observability from the actual output degenerates at a steady-state regime of interest. The proposed method is based on second-order averaging and is illustrated by simulations on a simple third-order system.",
      "article_number": "7525045",
      "pdf_url": "https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=7525045",
      "html_url": "https://ieeexplore.ieee.org/document/7525045/",
      "abstract_url": "https://ieeexplore.ieee.org/document/7525045/",
      "publication_title": "2016 American Control Conference (ACC)",
      "conference_location": "Boston, MA",
      "conference_dates": "6-8 July 2016",
      "publication_number": 7518121,
      "is_number": 7524873,
      "publication_year": 2016,
      "publication_date": "6-8 July 2016",
      "start_page": "999",
      "end_page": "1005",
      "citing_paper_count": 6,
      "citing_patent_count": 0,
      "index_terms": {
        "ieee_terms": {
          "terms": [
            "Robot sensing systems",
            "Noise measurement",
            "Closed loop systems",
            "Oscillators",
            "Observability",
            "Current measurement",
            "Rotors"
          ]
        }
      }
    },
    {
      "doi": "10.1109/SPEEDAM.2016.7525835",
      "title": "An analysis of the benefits of signal injection for low-speed sensorless control of induction motors",
      "publisher": "IEEE",
      "isbn": "978-1-5090-2067-6",
      "rank": 4,
      "authors": {
        "authors": [
          {
            "affiliation": "Centre Automatique et Syst\u00e8mes, MINES ParisTech, PSL Research University, France",
            "authorUrl": "https://ieeexplore.ieee.org/author/37085493932",
            "id": 37085493932,
            "full_name": "Pascal Combes",
            "author_order": 1
          },
          {
            "affiliation": "Schneider Toshiba Inverter Europe, Pacysur-Eure, France",
            "authorUrl": "https://ieeexplore.ieee.org/author/37590743800",
            "id": 37590743800,
            "full_name": "Fran\u00e7ois Malrait",
            "author_order": 2
          },
          {
            "affiliation": "Centre Automatique et Syst\u00e8mes, MINES ParisTech, PSL Research University, France",
            "authorUrl": "https://ieeexplore.ieee.org/author/37335302900",
            "id": 37335302900,
            "full_name": "Philippe Martin",
            "author_order": 3
          },
          {
            "affiliation": "Centre Automatique et Syst\u00e8mes, MINES ParisTech, PSL Research University, France",
            "authorUrl": "https://ieeexplore.ieee.org/author/37299202100",
            "id": 37299202100,
            "full_name": "Pierre Rouchon",
            "author_order": 4
          }
        ]
      },
      "access_type": "LOCKED",
      "content_type": "Conferences",
      "abstract": "We analyze why low-speed sensorless control of the IM is intrinsically difficult, and what is gained by signal injection. The explanation relies on the control-theoretic concept of observability applied to a general model of the saturated IM. We show that the IM is not observable when the stator speed is zero in the absence of signal injection, but that observability is restored thanks to signal injection and magnetic saturation. The analysis also reveals that existing sensorless algorithms based on signal injection may perform poorly for some IMs under particular operating conditions. The approach is illustrated by simulations and experimental data.",
      "article_number": "7525835",
      "pdf_url": "https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=7525835",
      "html_url": "https://ieeexplore.ieee.org/document/7525835/",
      "abstract_url": "https://ieeexplore.ieee.org/document/7525835/",
      "publication_title": "2016 International Symposium on Power Electronics, Electrical Drives, Automation and Motion (SPEEDAM)",
      "conference_location": "Anacapri",
      "conference_dates": "22-24 June 2016",
      "publication_number": 7513173,
      "is_number": 7525803,
      "publication_year": 2016,
      "publication_date": "22-24 June 2016",
      "start_page": "721",
      "end_page": "727",
      "citing_paper_count": 1,
      "citing_patent_count": 0,
      "index_terms": {
        "ieee_terms": {
          "terms": [
            "Stators",
            "Rotors",
            "Observability",
            "Analytical models",
            "Algorithm design and analysis",
            "Current measurement",
            "Torque"
          ]
        }
      }
    },
    {
      "doi": "10.1109/IEMDC.2017.8002195",
      "title": "Modeling and identification of synchronous reluctance motors",
      "publisher": "IEEE",
      "isbn": "978-1-5090-4281-4",
      "rank": 5,
      "authors": {
        "authors": [
          {
            "affiliation": "Schneider Toshiba Inverter Europe, Pacy-sur-Eure, France",
            "authorUrl": "https://ieeexplore.ieee.org/author/37085493932",
            "id": 37085493932,
            "full_name": "Pascal Combes",
            "author_order": 1
          },
          {
            "affiliation": "Schneider Toshiba Inverter Europe, Pacy-sur-Eure, France",
            "authorUrl": "https://ieeexplore.ieee.org/author/37590743800",
            "id": 37590743800,
            "full_name": "Fran\u00e7ois Malrait",
            "author_order": 2
          },
          {
            "affiliation": "Centre Automatique et Syst\u00e8mes, MINES ParisTech, PSL Research University, Paris, France",
            "authorUrl": "https://ieeexplore.ieee.org/author/37335302900",
            "id": 37335302900,
            "full_name": "Philippe Martin",
            "author_order": 3
          },
          {
            "affiliation": "Centre Automatique et Syst\u00e8mes, MINES ParisTech, PSL Research University, Paris, France",
            "authorUrl": "https://ieeexplore.ieee.org/author/37299202100",
            "id": 37299202100,
            "full_name": "Pierre Rouchon",
            "author_order": 4
          }
        ]
      },
      "access_type": "LOCKED",
      "content_type": "Conferences",
      "abstract": "The goal of this paper is to propose a model of the (cross-)saturated SynRM suitable for sensorless control purposes, together with an identification procedure suitable for reasonably easy use in the field: the model contains about ten parameters, which are identified from only the drive current measurements, in experiments where the rotor is locked in a known position. The experimental procedure relies on signal injection to produce data that can be used for parameter identification.",
      "article_number": "8002195",
      "pdf_url": "https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=8002195",
      "html_url": "https://ieeexplore.ieee.org/document/8002195/",
      "abstract_url": "https://ieeexplore.ieee.org/document/8002195/",
      "publication_title": "2017 IEEE International Electric Machines and Drives Conference (IEMDC)",
      "conference_location": "Miami, FL",
      "conference_dates": "21-24 May 2017",
      "publication_number": 7995554,
      "is_number": 8001859,
      "publication_year": 2017,
      "publication_date": "21-24 May 2017",
      "start_page": "1",
      "end_page": "6",
      "citing_paper_count": 1,
      "citing_patent_count": 0,
      "index_terms": {
        "ieee_terms": {
          "terms": [
            "Saturation magnetization",
            "Rotors",
            "Current measurement",
            "Torque",
            "Magnetic analysis",
            "Reluctance motors",
            "Stators"
          ]
        },
        "author_terms": {
          "terms": [
            "Modeling",
            "Identification",
            "Saturation",
            "Synchronous Reluctance Motor",
            "Signal injection"
          ]
        }
      }
    }]
    }))


    print(bibFile)
    bibFile.write('wt')
