import re
from urllib.parse import urlparse

class DOI:
    """ An instance of this class represents a DOI (Document Object Identifier). The provided *value* is validated upon instance construction.

        :param value: shoud be a :class:`str` representing a valid DOI.
    """

    def __init__(self, value):
        match = re.fullmatch(r'(?P<prefix>10\..{4})/(?P<suffix>.+)', value)
        if not match:
            raise ValueError(f"Invalid DOI: {value}")
        self.prefix = match['prefix']
        self.suffix = match['suffix']

    def __str__(self):
        return self.prefix + '/' + self.suffix

    def __repr__(self):
        return f"DOI({self.prefix}/{self.suffix})"

def isbnValidator(isbn):
    """ A validator for ISBN (International Standard Book Number). Returns `True` for valid ISBNs and `False` for invalid ISBNs.

        :param isbn: A :class:`str` to validate as an ISBN.

        :returns:

        * ``True`` if the given :class:`str` is a valid ISBN;
        * ``False`` if the given :class:`str` is an invalid ISBN.
    """

    if re.compile(r'(\d+-){3,4}\d+').fullmatch(isbn) is None:
        return False
    digits = list(isbn.replace('-', ''))

    s = 0
    i = 1
    for d in digits:
        if (len(digits) == 10):
            s += (11 - i)*int(d)
        elif (len(digits) == 13):
            s += (3 - 2*(i % 2))*int(d)
        i += 1

    if (len(digits) == 10):
        return (s % 11 == 0)
    elif (len(digits) == 13):
        return (s % 10 == 0)
    else:
        return False

def issnValidator(issn):
    """ A validator for ISSN (International Standard Serial Number). Returns `True` for valid ISSNs and `False` for invalid ISSNs.

        :param issn: A :class:`str` to validate as an ISSN.

        :returns:

        * ``True`` if the given :class:`str` is a valid ISSN;
        * ``False`` if the given :class:`str` is an invalid ISSN.
    """

    if re.compile(r'\d{4}-\d{4}').fullmatch(issn) is None:
        return False
    digits = list(issn.replace('-', ''))

    s = 0
    i = 1
    for d in digits:
        s += (9 - i)*int(d)
        i += 1

    return (s % 11 == 0)

def urlValidator(url):
    """ A validator for URL (Uniform Ressource Locator). Returns `True` for valid URLSs and `False` for invalid URLs.

        :param url: A :class:`str` to validate as an URL.

        :returns:

        * ``True`` if the given :class:`str` is a valid URL;
        * ``False`` if the given :class:`str` is an invalid URL.
    """

    try:
        r = urlparse(url)
    except ValueError:
        return False

    return bool(r.netloc or r.path)

class Author:
    """ Author(value)

        An instance of this class represents an author.
        The author name and forenames can be provided as a :class:`list` or as a :class:`str`.

        This class behaves as an immutable :class:`dict` with the following attributes:
            * name -- The name of the author
            * forenames -- The forenames of the author as a :class:`list`
            * initial -- The initial of the name of the author.

        :param value: A :class:`str` or a :class:`list` representing an author:

        * If it is a :class:`list`, it should be `[name, forename1, frename2...]`
        * If it is a :class:`str` it should be in one of those forms:
            * `"name, forename1 forename2 ..."`
            * `"name forename1 forename2 ..."`

        **Examples**::

            Author(["Smith", "John", "Junior"])
            Author(["Smith, John Junior"])
            Author(["Smith John Junior"])
    """
    def __init__(self, value):
        if isinstance(value, list):
            self.__name = value[0]
            self.__forenames = value[1:]
        elif isinstance(value, str):
            parts = value.split(',')
            if len(parts) == 2:
                self.__name = parts[0].strip()
                self.__forenames = [p.strip() for p in parts[1].split(' ') if (len(p.strip()) > 1)]
            elif len(parts) == 1:
                parts = [p.strip() for p in value.split(' ') if (len(p.strip()) > 1)]
                self.__name = parts[-1]
                self.__forenames = parts[:-1]
            else:
                raise ValueError('Invalid author name')
        else:
            raise TypeError(f"Cannot construct Author from: {type(value)}")

    def __contains__(self, name):
        return (name in ['name', 'forenames', 'initial'])

    def __getitem__(self, name):
        if name == 'name':
            return self.__name
        if name == 'forenames':
            return self.__forenames
        if name == 'initial':
            return self.__name[0].upper()
        raise KeyError(name)

    def __str__(self):
        return self.__name + ', ' + ' '.join(self.__forenames)

    def __repr__(self):
        return f"Author({self.__name}, {self.__forenames})"

class AuthorList:
    """ An instance of this class represents a list of authors. It behaves essentially as a :class:`list` of :class:`Author` instances and can be initialized by giving a list of :class:`Author` instances, a :class:`list` of :class:`str` which are valid author names, or the author names joined by `" and "` as a :class:`str`.

        :param authors: A string or a list representing the author list:

        * A :class:`list` of :class:`Author` instances
        * A :class:`list` of valid author names
        * A :class:`str` which should be the result of joining multiple authors names with ``" and "``.

        **Examples**::

            AuthorList(Author("Smith, John"), Author("Dupont, Jean"))
            AuthorList("Smith, John", "Dupont Jean")
            AuthorList("Smith, John and Dupont, Jean")
    """
    def __init__(self, authors):
        if isinstance(authors, list):
            self.__authors = [(author if isinstance(author, Author) else Author(author)) for author in authors]
        elif isinstance(authors, str):
            self.__authors = [Author(p) for p in authors.split(' and ')]
        else:
            raise TypeError(f"Cannot construct AuthorList from: {type(value)}")

    def __iter__(self):
        return iter(self.__authors)

    def __len__(self):
        return len(self.__authors)

    def __getitem__(self, index):
        return self.__authors[index]

    def __str__(self):
        return ' and '.join([str(a) for a in self.__authors])

    def __repr__(self):
        return f"AuthorList({str(self.__authors)})"

class BibData:
    """ An instance of this class represents bibliography data. The argument can be an instance of :class:`BibData` itself for duplication, or bibliography data as a dictionnary, which is validated.

        The validation rules are defined when subclassing this class.

        :param data: Bibliography data:

        * An instance of :class:`BibData` for copy.
        * A :class:`dict` containing bibliography data. In this case, the data will be validated before adding it.
    """
    fields = {}

    warningsDisabled = False
    @classmethod
    def __warning(cls, msg):
        if not cls.warningsDisabled:
            print(f'WARNING: {msg}')

    def __check(self, value, name):
        try:
            field = self.fields[name]
        except KeyError:
            return self.__warning(f"Unknown result field \"{name}\"")

        try:
            v = field['type'](value)
        except ValueError:
            return self.__warning(f"Value for result field \"{name}\" has bad type: {value}")

        try:
            if (v < field['min']):
                return self.__warning(f"Too small value for result field \"{name}\": {value}")
        except KeyError:
            pass

        try:
            if (v > field['max']):
                return self.__warning(f"Too large value for result field \"{name}\": {value}")
        except KeyError:
            pass

        try:
            valid = field['validator'](v)
            if not valid:
                return self.__warning(f"Invalid value for result field \"{name}\": {value}")
            elif valid is not True:
                v = valid
        except ValueError:
            return self.__warning(f"Invalid value for result field \"{name}\": {value}")
        except KeyError:
            pass

        try:
            if v not in field['values']:
                return self.__warning(f"Invalid value for result field \"{name}\": {value}")
        except KeyError:
            pass

        return v


    def __init__(self, data=None):
        self.__data = {}
        if isinstance(data, BibData):
            self.__data = data.__data
        elif data is not None:
            for k, v in data.items():
                v = self.__check(v, k)
                if v is not None:
                    self.__data[k] = v

    def __iter__(self):
        for k, v in self.__data.items():
            yield (k, v)

    def __contains__(self, name):
        return name in self.__data

    def __getitem__(self, name):
        return self.__data[name]

    def __setitem__(self, name, value):
        v = self.__check(value, name)
        if v is not None:
            if name in self.__data:
                self.__warning(f"Field \"{name}\" is already present in entry")
            else:
                self.__data[name] = v

    def __repr__(self):
        return f"{type(self).__name__}({repr(self.__data)})"

    def __str__(self):
        return f"{type(self).__name__}({str(self.__data)})"

class BibDataSet:
    """ An instance of this class behaves as a list of bibliography data. The given data can be either an existing :class:`BibDataSet` for copy construction or a list of bibliography data as :class:`BibData` instances or dictionnaries.

        :param data: An instance of :class:`BibDataSet` of a :class:`list` of bibliography data (:class:`BibData` instances or dictionnaries).
    """
    dataType = BibData

    def __init__(self, data=None):
        if data is None:
            data = []
        if isinstance(data, BibDataSet):
            self.__data = data.__data
        else:
            try:
                self.__data = [self.dataType(d) for d in data]
            except KeyError:
                self.__data = []

    def __len__(self):
        return len(self.__data)

    def __iter__(self):
        return iter(self.__data)

    def __iadd__(self, other):
        if isinstance(other, BibDataSet):
            self.__data += other.__data
        elif isinstance(other, BibData):
            self.__data += [other]
        else:
            raise ValueError("Only BibDataSets and BibData can be added to a BibDataSet")
        return self

    def __repr__(self):
        return f"{type(self).__name__}({repr(self.__data)})"

    def __str__(self):
        return f"{type(self).__name__}({str(self.__data)})"