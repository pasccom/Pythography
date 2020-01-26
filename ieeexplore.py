# Copyright 2020 Pascal COMBES <pascom@orange.fr>
# 
# This file is part of Pythography.
# 
# Pythography is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Pythography is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Pythography. If not, see <http://www.gnu.org/licenses/>

import bibdata

import re
import datetime
from warnings import warn as warning
import json

from urllib.request import urlopen
from urllib.parse import urlencode, urlparse
import urllib.error as urlerrors

class QueryString:
    """ Representation of a query string. Query strings can be negated, or'ed and and'ed using the Python ``~``, ``|`` and ``&`` operators respectively, even with Python :class:`str`. Query strings also support wildchars ``*`` (any characters) and ``?`` (any character).

        :param text: The text for this query string.

        **Examples**::

            QueryString("Smith John")
            QueryString("Smith John*")
            QueryString("Smith Jo?n")
            ~QueryString("Smith John")
            QueryString("Smith John") | "Dupont Jean"
            "Smith John" & QueryString("Dupont Jean")
    """
    class __Compound:
        class Operator:
            def __init__(self, op):
                self.__str = op
            def __str__(self):
                return self.__str

        def __check(self, other):
            if type(other) is type(self):
                return other
            elif type(other) is QueryString:
                if other.isNegated() and (self.__operator is QueryString.OR):
                    raise ValueError("Inverted QueryString can only be used with AND operator")
                return other
            elif type(other) is str:
                return QueryString(other)
            else:
                raise TypeError('Expected a string or a query string')

        def __merge_check(self, operator, operand):
            if type(operand) is type(self):
                if operand.__operator is operator:
                    return operand.__children
                else:
                    return (operand,)
            elif type(operand) is QueryString:
                return (operand, )
            elif type(operand) is str:
                return (QueryString(operand), )
            else:
                raise TypeError('Expected a string or a query string')

        def __init__(self, op, *args):
            if type(op) is not self.__class__.Operator:
                raise TypeError(f"Invalid operator {op} ({type(op)})")
            self.__operator = op

            if len(args) < 2:
                raise TypeError("A compound QueryString must have at least two children")
            self.__children = [self.__check(a) for a in args]

        def __str__(self):
            nonInverted = [c for c in self.__children if (type(c) is not QueryString) or not c.isNegated()]
            if len(nonInverted) == 0:
                raise ValueError("At least one QueryString must be not inverted in a compound expression")
            inverted = [c for c in self.__children if (type(c) is QueryString) and c.isNegated()]

            query = f' {self.__operator} '.join([str(c) for c in nonInverted])
            if len(inverted) > 0:
                query += ' NOT ' + ' NOT '.join([str(c) for c in inverted])
            return f'{query}'

        def __repr__(self):
            query = f' {self.__operator} '.join([repr(c) for c in self.__children])
            return f'({query})'

        def __or__(self, other):
            return self.__class__(QueryString.OR, *self.__merge_check(QueryString.OR, self), *self.__merge_check(QueryString.OR, other))

        def __ror__(self, other):
            return self.__class__(QueryString.OR, *self.__merge_check(QueryString.OR, other), *self.__merge_check(QueryString.OR, self))

        def __and__(self, other):
            return self.__class__(QueryString.AND, *self.__merge_check(QueryString.AND, self), *self.__merge_check(QueryString.AND, other))

        def __rand__(self, other):
            return self.__class__(QueryString.AND, *self.__merge_check(QueryString.AND, other), *self.__merge_check(QueryString.AND, self))

        def __contains__(self, string):
            return any([string in c for c in self.__children])

        def index(self, sub):
            return min([c.index(sub) for c in self.__children if sub in c])

        def count(self, sub):
            return sum([c.count(sub) for c in self.__children])

    OR = __Compound.Operator('OR')
    AND = __Compound.Operator('AND')

    def __check(self, other):
        if type(other) is self.__Compound:
            raise NotImplementedError('This should be handled by QueryString.__Compound class')
        elif type(other) is QueryString:
            return other
        elif type(other) is str:
            return QueryString(other)
        else:
            raise TypeError('Expected a string or a query string')

    def __init__(self, text):
        if type(text) is not str:
            raise TypeError('Expected a string')
        self.__str = text
        self.__neg = False

    def __str__(self):
        return f'"{self.__str}"'

    def __repr__(self):
        return f'q!{str(self)}' if self.__neg else f'q{str(self)}'

    def __or__(self, other):
        try:
            return self.__Compound(QueryString.OR, self, self.__check(other))
        except (NotImplementedError):
            return NotImplemented

    def __ror__(self, other):
        return self.__Compound(QueryString.OR, self.__check(other), self)

    def __and__(self, other):
        try:
            return self.__Compound(QueryString.AND, self, self.__check(other))
        except (NotImplementedError):
            return NotImplemented

    def __rand__(self, other):
        return self.__Compound(QueryString.AND, self.__check(other), self)

    def __invert__(self):
        self.__neg = True
        return self

    def __contains__(self, string):
        return string in self.__str

    def __eq__(self, other):
        return self.__str == other

    def isNegated(self):
        return self.__neg

    def index(self, sub, start=None, end=None):
        return self.__str.index(sub, start, end)

    def count(self, sub, start=None, end=None):
        return self.__str.count(sub, start, end)

    @classmethod
    def isQueryString(cls, obj):
        return (type(obj) is cls) or (type(obj) is cls.__Compound)

class Query:
    """ An instance of this class represents a query to a bibliography database. Query fields are validated upon query construction.

        Query fields can also be added or deleted in a dictionnary like fashion

        :param db: The database to query.
        :param kwArgs: Keywords arguments. Each argument represents a query search field.

        **Examples**::

            q = Query(db, author="Smith John")
            del q['author']
            q['author'] = "Smith John"

    """
    class __ContentType(str):
        pass
    class __Publisher(str):
        pass
    class __SortOrder(str):
        pass

    Journals = __ContentType('Journals')
    Conferences = __ContentType('Conferences')
    EarlyAccess = __ContentType('Early Access')
    Standards = __ContentType('Standards')
    Books = __ContentType('Books')
    Courses = __ContentType('Courses')

    AlcatelLucent = __Publisher('Alcatel-Lucent')
    AGU = __Publisher('AGU')
    BIAI = __Publisher('BIAI')
    CSEE = __Publisher('CSEE')
    IBM = __Publisher('IBM')
    IEEE = __Publisher('IEEE')
    IET = __Publisher('IET')
    MITP = __Publisher('MITP')
    MorganClaypool = __Publisher('Morgan & Claypool')
    SMPTE = __Publisher('SMPTE')
    TUP = __Publisher('TUP')
    VDE = __Publisher('VDE')

    AscendingOrder = __SortOrder('asc')
    DescendingOrder = __SortOrder('desc')

    params = {
# Search parameters:
        'abstract': {
            'type': 'search',
            'doc': "Brief summary or statement of the contents of a journal article, conference paper, standard, book, book chapter, or course.",
            'boolean_operators': True,
        },
        'affiliation': {
            'type': 'search',
            'doc': "This field is used to submit a query that specifies part or all of an organization/institution name and receive a response of all available metadata with articles authored by an individual(s) associated with that organization/institution.",
            'boolean_operators': True,
            'wildcard': True,
            'wildcard_min_length': 3,
        },
        'article_number': {
            'type': 'search',
            'doc': "This is IEEE’s unique identifier for a specific article.",
            'value_type': int,
            'alone': True,
        },
        'article_title': {
            'type': 'search',
            'doc': "Title of an individual document (journal article, conference paper, standard, eBook chapter, or course).",
        },
        'author': {
            'type': 'search',
            'doc': "An author's name. Searches both first name and last name.",
            'boolean_operators': True,
            'wildcard' : True,
            'wildcard_min_length': 3,
        },
        'd_au': {
            'type': 'search',
            'doc': "Open Author facet; results contain a refinement link that returns all documents by a given author relevant to that search.",
            'name': 'd-au',
        },
        'doi': {
            'type': 'search',
            'doc': "The Digital Object Identifier (doi) is the unique identifier assigned to an article / document by CrossRef.",
            'value_type': bibdata.DOI,
            'alone': True,
        },
        'd_publisher': {
            'type': 'search',
            'doc': "Publisher facet; results contain a refinement link that returns all documents by a given publisher relevant to that search.",
            'name': 'd-publisher',
        },
        'd_pubtype': {
            'type': 'search',
            'doc': "Content Type facet; results contain a refinement link that returns all documents by a given content type relevant to that search.",
            'name': 'd-pubtype',
        },
        'd_year': {
            'type': 'search',
            'doc': "Publication Year facet",
            'value_type': int,
            'max': datetime.date.today().year,
            'name': 'd-year',
        },
        'facet': {
            'type': 'search',
            'doc': "Open/Facet dimension",
        },
        'index_terms': {
            'type': 'search',
            'doc': "This is a combined field which allows users to search the Author Keywords, IEEE Terms, and Mesh Terms.",
            'boolean_operators': True,
            'wildcard' : True,
            'wildcard_min_length': 3,
            'wildcard_max': 2,
        },
        'isbn': {
            'type': 'search',
            'doc': "International Standard Book Number. A number used to uniquely identify a book or non-serial.",
            'value_type': bibdata.isbnValidator,
        },
        'issn': {
            'type': 'search',
            'doc': "International Standard Serial Number. An 8-digit number used to uniquely identify a periodical publication (journal or serial).",
            'value_type': bibdata.issnValidator,
        },
        'is_number': {
            'type': 'search',
            'doc': "Issue number (for Journals only)",
            'value_type': int,
        },
        'meta_data': {
            'type': 'search',
            'doc': "This field enables a free-text search of all configured metadata fields and the abstract.",
            'boolean_operators': True,
            'wildcard' : True,
            'wildcard_min_length': 3,
            'wildcard_max': 2,
        },
        'publication_title': {
            'type': 'search',
            'doc': "Title of a publication (Journal, Conference, or Standard).",
        },
        'publication_year': {
            'type': 'search',
            'doc': "The value for publication year varies by publication. It is recommended to verify the format of the particular publication within the Xplore Web product to learn how to structure your search query.",
            'value_type': int,
            'max': datetime.date.today().year,
        },
        'querytext': {
            'type': 'search',
            'doc': "This field enables a free-text search of all configured metadata fields, abstract and document text.",
            'boolean_operators': True,
            'wildcard' : True,
            'wildcard_min_length': 3,
            'wildcard_max': 2,
        },
        'thesaurus_terms': {
            'type': 'search',
            'doc': "Also referred to as IEEE Terms. These are keywords assigned to IEEE journal articles and conference papers from a controlled vocabulary created by the IEEE.",
            'wildcard' : True,
            'wildcard_min_length': 3,
            'wildcard_max': 2,
        },
# Filtering parameters:
        'content_type': {
            'type': 'filter',
            'doc': "Type of content",
            'value_type': __ContentType,
            #'values': ['Journals', 'Conferences', 'Early Access', 'Standards', 'Books', 'Courses'],
        },
        'end_year': {
            'type': 'filter',
            'doc': "End value of Publication Year to restrict results by.",
            'value_type': int,
        },
        'open_access': {
            'type': 'filter',
            'doc': "Open access content",
            'value_type': bool,
        },
        'publication_number': {
            'type': 'filter',
            'doc': "The IEEE identification number associated with the specific publication.",
            'value_type': int,
        },
        'publisher': {
            'type': 'filter',
            'doc': "Publisher of document",
            'value_type': __Publisher,
            #'values': ['Alcatel-Lucent', 'AGU', 'BIAI', 'CSEE', 'IBM', 'IEEE', 'IET', 'MITP', 'Morgan & Claypool', 'SMPTE', 'TUP', 'VDE'],
        },
        'start_year': {
            'type': 'filter',
            'doc': "Start value of Publication Year to restrict results by.",
            'value_type': int,
        },
# Paging parameters:
        'max_records': {
            'type': 'page',
            'doc': "The number of records to fetch.",
            'value_type': int,
            'max': 200,
        },
        'start_record': {
            'type': 'page',
            'doc': "Sequence number of first record to fetch.",
            'value_type': int,
        },
# Sorting parameters:
        'sort_field': {
            'type': 'sort',
            'doc': "Field name on which to sort.",
            'values': ['article_number', 'article_title', 'author', 'publication_title', 'publication_year'],
        },
        'sort_order': {
            'type': 'sort',
            'doc': "Sorting order.",
            'value_type': __SortOrder,
            #'values': ['asc', 'desc'],
        },
    }

    def __name(self, param):
        try:
            return Query.params[param]['name']
        except (KeyError):
            return param

    def __check(self, name, value):
        alone = False
        acceptWildcard = False
        acceptBooleanOperators = False

        if self.__alone and (name != 'article_number'):
            warning("Parameter would be ignored")
            return False

        for k, v in Query.params[name].items():
            if (k == 'type') or (k == 'doc') or (k == 'name'):
                continue
            elif (k == 'value_type'):
                if type(value) is not v:
                    try:
                        v(value)
                    except ValueError:
                        warning(f"Value \"{value}\" is not castable into {v}")
                        return False
                    except TypeError:
                        warning(f"Value \"{value}\" is not of accepted type")
                        return False
            elif (k == 'values'):
                if value not in v:
                    warning(f"Value \"{value}\" is not in {v}")
                    return False
            elif (k == 'min'):
                if (value < v):
                    warning(f"Value \"{value}\" is smaller than minimum value {v}")
                    return False
            elif (k == 'max'):
                if (value > v):
                    warning(f"Value \"{value}\" is larger than maximum value {v}")
                    return False
            elif (k == 'alone'):
                alone = v
            elif (k == 'boolean_operators'):
                acceptBooleanOperators = v
            elif (k == 'wildcard'):
                acceptWildcard = v
            elif (k == 'wildcard_min_length'):
                try:
                    if (value.index('*') < v):
                        warning(f"There must be {v} characters before wildcard")
                        return False
                except (ValueError):
                    pass
            elif (k == 'wildcard_max'):
                if (value.count('*') > v):
                    warning(f"There must at most {v} wildcards")
                    return False
            else:
                raise NotImplementedError(k)

        if (name == 'start_year') and ('end_year' in self.__params):
            if (value > self.__params['end_year']):
                warning('Start year should be smaller than end year')
                return False

        if (name == 'end_year') and ('start_year' in self.__params):
            if (value < self.__params['start_year']):
                warning('End year should be greater than start year')
                return False

        if not acceptBooleanOperators and QueryString.isQueryString(value):
            warning("Boolean operators are not accepted")
            return False

        if not acceptWildcard and ((type(value) is str) or QueryString.isQueryString(value)) and ('*' in value):
            warning("Wildcards are not accepted")
            return False

        self.__alone = alone
        return True

    def __init__(self, db, **kwArgs):
        self.__db = db
        self.__alone = False
        self.__params = {}
        for k, v in kwArgs.items():
            self.__setitem__(k, v)

    def __iter__(self):
        for k, v in self.__params.items():
            yield (k, v)

    def __contains__(self, name):
        return (name in self.__params)

    def __delitem__(self, name):
        self.reset()
        del(self.__params[name])

    def __getitem__(self, name):
        return self.__params[name]

    def __setitem__(self, name, value):
        if name not in Query.params:
            raise KeyError(f"Invalid search parameter \"{name}\"")
        if (Query.params[name]['type'] != 'search'):
            raise KeyError(f"\"{name}\" is not a search parameter")
        #print(f"{name} -> {value}: {self.__check(name, value)}")
        if self.__check(name, value):
            if (self.__alone):
                for k, v in self.__params.items():
                    warning(f"Parameter \"{k}\" will be superseeded by parameter \"{name}\"")
                self.__params.clear()
            self.reset()
            self.__params[name] = value

    def filterBy(self, **kwArgs):
        """ Sets the query filtering method.

            :param kwArgs: Keyword arguments. Each keyword represents a filtering field. When set to ``None``, the filter is removed.

            **Examples**::

                q.filterBy(start_year=2000)
                q.filterBy(start_year=None)
                q.filterBy(start_year=2000, end_year=2010)
        """
        self.reset()

        for k, v in kwArgs.items():
            if v is None:
                try:
                    del self.__params[k]
                except (KeyError):
                    pass
            elif self.__check(k, v):
                self.__params[k] = v

    def sortBy(self, *args, **kwArgs):
        """ Sets the result sorting method. To remove sorting pass `None` to keyword argument.

            :param args: A single :class:`str` to sort in ascending order
            :param kwArgs: A single keyword argument to sort in given order according to the given order.

            **Examples**::

                q.sortBy('publication_year')
                q.sortBy(publication_year=Query.DescendingOrder)
                q.sortBy(publication_year=None)
        """
        if (len(args) == 1) and (len(kwArgs) == 0):
            field = args[0]
            order = Query.AscendingOrder
        elif (len(args) == 0) and (len(kwArgs) == 1):
            for f, o in kwArgs.items():
                field = f
                order = o
        else:
            raise TypeError('Invalid sort arguments')

        self.reset()

        if order is None:
            try:
                del self.__params['sort_field']
            except (KeyError):
                pass
            try:
                del self.__params['sort_order']
            except (KeyError):
                pass
        elif self.__check('sort_field', field) and self.__check('sort_order', order):
            self.__params['sort_field'] = field
            self.__params['sort_order'] = order

    def clear(self):
        """ Removes all query paramters (set by constructor or dictionnary-style methods).
        """
        self.__params.clear()
        self.__alone = False

    def reset(self):
        """ Reset query to first record.
        """
        try:
            del(self.__params['start_record'])
        except KeyError:
            pass

    def send(self, start=None):
        """ Send query and get results from given index.

            :param start: Start record. If `None` continues to the next record (after the last retrieved).

            :returns: The result of the query to the associated database as a :class:`ResultSet`
        """
        if start is None:
            try:
                start = self.__params['start_record']
                try:
                    start += self.__params['max_records']
                except (KeyError):
                    start += 200
            except (KeyError):
                start = 1
        self.__params['start_record'] = start

        queryStr=urlencode({self.__name(k): v for k, v in self.__params.items()})
        return ResultSet(self, self.__db.send(queryStr))

    def limit(self, records):
        """ Limits the number of returned records.

            :param records: The maximum number of returned records.
        """
        if records is None:
            del self.__params['max_records']
        elif self.__check('max_records', records):
            self.__params['max_records'] = records

class Author(bibdata.Author, bibdata.BibData):
    """ An instance of this class represents a IEEE Xplore author. This includes (on top of the author name and forenames) an URL to the author profile and an author identifier.

        :param value: A :class:`dict` representing the author as returned by IEEE Xplore API.
    """
    fields = {
        'authorUrl': {
            'doc': "IEEE Xplore URL that returns the author details. For more information please go to: https://ieeexplore.ieee.org/Xplorehelp/#/author-center/author-details.",
            'type': str,
            'validator': bibdata.urlValidator,
        },
        'author_order': {
            'doc': "Where multiple authors are listed, the author_order provides a number for each author.",
            'type': int,
            'min': 1,
        },
        'affiliation': {
            'doc': "Name of the affiliation listed in the document. Affiliation names are provided as full names along with their listed order.",
            'type': str,
        },
        'full_name': {
            'doc': "The full name of an author.",
            'type': str,
        },
        'id': {
            'doc': "Internal IEEE author identifier",
            'type': int,
            'min': 0,
        }
    }

    def __init__(self, value):
        super(bibdata.Author, self).__init__(value)

        parts = super(bibdata.Author, self).__getitem__('full_name').split(' ')
        parts = [parts[-1]] + parts
        del(parts[-1])

        super().__init__(parts)

    def __contains__(self, name):
        return super(bibdata.Author, self).__contains__(name) or super().__contains__(name)

    def __getitem__(self, name):
        try:
            return super(bibdata.Author, self).__getitem__(name)
        except KeyError as e:
            return super().__getitem__(name)

class Result(bibdata.BibData):
    """ An instance of this class represents an item of bibliography data resulting from a query to IEEE Xplore API. It should not be constructed, but obtained as an item of a :class:`ResultSet`.

        :param data: A :class:`dict` containing bibliography data as returned by IEEE Xplore API.

    """
    def __contentTypeValidator(contentType):
        contentTypeMap = {
            'Journals':     'article',
            'Conferences':  'inproceedings',
            'Early Access': 'unpublished',
            'Standards':    'booklet',
            'Books':        'book',
            'Courses':      'misc',
        }

        try:
            return contentTypeMap[contentType]
        except KeyError:
            return False

    class __Dates:
        def __init__(self, value):
            months = ['Jan.', 'Feb.', 'Mar.', 'Apr.', 'May', 'June', 'July', 'Aug.', 'Sep.', 'Oct.', 'Nov.', 'Dec.']

            day = r'\d{1,2}'
            month = '|'.join(months)
            year = r'\d{4}'

            m = re.fullmatch(f'(?P<beginDay>{day}) (?P<beginMonth>{month}) (?P<beginYear>{year})', value)
            if m is None:
                m = re.fullmatch(f'(?P<beginDay>{day})-(?P<endDay>{day}) (?P<beginMonth>{month}) (?P<beginYear>{year})', value)
            if m is None:
                m = re.fullmatch(f'(?P<beginDay>{day}) (?P<beginMonth>{month})-(?P<endDay>{day}) (?P<endMonth>{month}) (?P<beginYear>{year})', value)
            if m is None:
                m = re.fullmatch(f'(?P<beginDay>{day}) (?P<beginMonth>{month}) (?P<beginYear>{year})-(?P<endDay>{day}) (?P<endMonth>{month}) (?P<endYear>{year})', value)
            if m is None:
                raise ValueError(f"Invalid date: {value}")
            m = m.groupdict()

            # Validate begin day:
            try:
                m['beginDay'] = int(m['beginDay'])
            except ValueError:
                raise ValueError(f"Invalid begin day: {m['beginDay']}")

            # Validate begin month:
            try:
                m['beginMonth'] = months.index(m['beginMonth']) + 1
            except ValueError:
                raise ValueError(f"Invalid begin month: {m['beginMonth']}")

            # Validate begin year:
            try:
                m['beginYear'] = int(m['beginYear'])
            except ValueError:
                raise ValueError(f"Invalid begin year: {m['beginYear']}")

            # Validate end day:
            try:
                m['endDay'] = int(m['endDay'])
            except KeyError:
                m['endDay'] = m['beginDay']
            except ValueError:
                raise ValueError(f"Invalid end day: {m['endDay']}")

            # Validate end month:
            try:
                m['endMonth'] = months.index(m['endMonth']) + 1
            except KeyError:
                m['endMonth'] = m['beginMonth']
            except ValueError:
                raise ValueError(f"Invalid end month: {m['endMonth']}")

            # Validate end year:
            try:
                m['endYear'] = int(m['endYear'])
            except KeyError:
                m['endYear'] = m['beginYear']
            except ValueError:
                raise ValueError(f"Invalid end year: {m['endYear']}")

            self.begin = datetime.date(m['beginYear'], m['beginMonth'], m['beginDay'])
            self.end = datetime.date(m['endYear'], m['endMonth'], m['endDay'])

        def __repr__(self):
            return f"{repr(self.begin)} -- {repr(self.end)}"

        def __str__(self):
            return f"{self.begin.isoformat().replace('-', '.')}--{str(self.end.isoformat().replace('-', '.'))}"


    class __IndexTerms:
        def __init__(self, value):
            self.__terms = {}
            for k, v in value.items():
                self.__terms[k.replace('_terms', '')] = [str(t) for t in v['terms']]

        def __len__(self):
            return sum(len(v) for v in self.__terms.values())

        def __iter__(self):
            for v in self.__terms.values():
                for t in v:
                    yield t

        def __contains__(self, name):
            return name in self.__terms

        def __getitem__(self, name):
            return self.__terms[name]

        def __str__(self):
            return ', '.join(', '.join(v) for v in self.__terms.values())

        def __repr__(self):
            return f"IndexTerms({repr(self.__terms)})"

    class __AuthorList(bibdata.AuthorList):
        def __init__(self, value):
            authors = []
            for a in value['authors']:
                authors += [Author(a)]
            super().__init__(authors)

# Result fields:
    fields = {
        'abstract': {
            'doc': "Brief summary or statement of the contents of a journal article, conference paper, standard, book / book chapter, and/or course.",
            'type': str,
        },
        'abstract_url': {
            'doc': "IEEE Xplore URL that will return the abstract.",
            'type': str,
            'validator': bibdata.urlValidator,
        },
        'author_url': {
            'doc': "IEEE Xplore URL that returns the author details.",
            'type': str,
            'validator': bibdata.urlValidator,
        },
        'access_type': {
            'doc': """Access type key:
    - \"Open Access\": Freely available from IEEE.
    - \"Ephemera\": Freely available from IEEE.
    - \"Locked\": Sign in or learn about subscription options.
    - \"Plagarized\": Marked as a plagarized article.""",
            'type': str,
            'values': ['LOCKED', 'OPEN ACCESS', 'EPHEMERA', 'PLAGARIZED'],
        },
        'article_number': {
            'doc': "IEEE’s unique identifier for a specific article.",
            'type': int,
            'min': 0,
        },
        #'author_terms': {
        #    'doc': "Terms provided by the author which describe the topics or subjects of the document.",
        #},
        'authors': {
            'doc': "Name of the author(s) listed in the document. Author names are provided as full names along with their listed order.",
            'type': __AuthorList,
        },
        'citing_paper_count': {
            'doc': "Number of papers citing the given article.",
            'type': int,
            'min': 0,
        },
        'citing_patent_count': {
            'doc': "Number of patents citing the given article.",
            'type': int,
            'min': 0,
        },
        'conference_dates': {
            'doc': "Date of conference event. Date format is not standardized and varies by conference.",
            'type': __Dates,
        },
        'conference_location': {
            'doc': "Location of conference event (can be one or more city, state, country).",
            'type': str,
        },
        'content_type': {
            'doc': "Specifies what kind of publication the content is from.",
            'type': str,
            'validator': __contentTypeValidator,
            #'values': ['Journals', 'Conferences', 'Early Access', 'Standards', 'Books', 'Courses'],
        },
        #'d-au': {
        #    'doc': "Open Author Facet",
        #},
        'doi': {
            'doc': "The Digital Object Identifier (doi) is the unique identifier assigned to an article / document by CrossRef.",
            'type': str,
            'validator': bibdata.DOI,
        },
        #'d-publisher': {
        #    'doc': "Open Publisher's Facet",
        #},
        #'d-pubtype': {
        #    'doc': "Open Content Type Facet",
        #},
        #'d-year': {
        #    'doc': "Open Publication Facet",
        #},
        'end_page': {
            'doc': "The final page number in the print version of the article.",
            'type': int,
            'min': 1,
        },
        #'facet': {
        #    'doc': "Open/Facet dimension",
        #},
        'html_url': {
            'doc': "IEEE Xplore URL that will return the full-text HTML.",
            'type': str,
            'validator': bibdata.urlValidator,
        },
        'index_terms': {
            'doc': "This is a combined field which returns Author Keywords and IEEE Terms.",
            'type': __IndexTerms,
        },
        #'ieee_terms': {
        #    'doc': "Keywords assigned to IEEE journal articles and conference papers from a controlled vocabulary created by the IEEE.",
        #},
        'is_number': {
            'doc': "Internal issue identifier (Journals only).",
            'type': int,
            'min': 0,
        },
        'isbn': {
            'doc': "International Standard Book Number. A number used to uniquely identify a book or non-serial.",
            'type': str,
            'validator': bibdata.isbnValidator,
        },
        'issn': {
            'doc': "International Standard Serial Number. An 8-digit number used to uniquely identify a periodical publication (journal or serial).",
            'type': str,
            'validator': bibdata.issnValidator,
        },
        'issue': {
            'doc': "Number of the journal issue in which the article was published.",
            'type': int,
            'min': 1,
        },
        'pdf_url': {
            'doc': "IEEE Xplore URL that returns the full-text pdf.",
            'type': str,
            'validator': bibdata.urlValidator,
        },
        'publication_date': {
            'doc': "Date the article was published; this data can be represented as full date, month and year, or quarter and year. Format varies by publication.",
            'type': __Dates,
        },
        'publication_number': {
            'doc': "A unique IEEE record number assigned to a publication.",
            'type': int,
            'min': 0,
        },
        'publication_title': {
            'doc': "Title of a publication (journal, conference, book / ebook, standard, course).",
            'type': str,
        },
        'publication_year': {
            'doc': "Year the article was published.",
            'type': int,
            'max': datetime.date.today().year,
        },
        'publisher': {
            'doc': "Name of Publisher for the specific publication referenced.",
            'type': str,
            'values': ['Alcatel-Lucent', 'AGU', 'BIAI', 'CSEE', 'IBM', 'IEEE', 'IET', 'MITP', 'Morgan & Claypool', 'SMPTE', 'TUP', 'VDE'],
        },
        'rank': {
            'doc': "Rank indicates the hierarchy of the returned documents based on an IEEE algorithm used.",
            'type': int,
            'min': 1,
        },
        'standard_number': {
            'doc': "Standard designation (e.g., IEEE 802.11u-2011). Standard designations are allocated by the Administrator of the IEEE-SA Standards Board New Standards Committee (NesCom).",
            'type': int,
            'min': 0,
        },
        #'standard_status': {
        #    'doc': "Status of standard (e.g. Active, Draft, etc.); applies only to Standards.",
        #},
        'start_page': {
            'doc': "Starting page number on print version of article.",
            'type': int,
            'min': 1,
        },
        'title': {
            'doc': "Title of an individual document (journal article, conference paper, standard, Book / eBook chapter or Course).",
            'type': str,
        },
        #'total_records': {
        #    'doc': "Total number of documents found that match the query criteria.",
        #    'type': int,
        #    'min': 0,
        #},
        #'total_searched': {
        #    'doc': "Total number of documents searched.",
        #    'type': int,
        #    'min': 1,
        #},
        'volume': {
            'doc': "Volume number. Detail associated with Journals and Conferences only.",
            'type': int,
            'min': 1,
        },
    }

    def __contains__(self, name):
        if super().__contains__(name):
            return True
        try:
            self.__getitem__(name)
        except KeyError:
            return False
        return True

    def __getitem__(self, name):
        try:
            return super().__getitem__(name)
        except KeyError as e:
            if name == 'pages':
                return f"{self.__getitem__('start_page')}--{self.__getitem__('end_page')}"
            if name == 'publication_year':
                return self.__getitem__('publication_date').begin.year
            if name == 'conference_year':
                return self.__getitem__('conference_dates').begin.year
            if name == 'publication_month':
                return self.__getitem__('publication_date').begin.month
            if name == 'conference_month':
                return self.__getitem__('conference_dates').begin.month
            if name == 'publication_code':
                parts = self.__getitem__('doi').suffix.split('.')
                if len(parts) > 1:
                    return parts[0]
            raise e

class ResultSet(bibdata.BibDataSet):
    """ An instance of this class represents the result of a query to IEEE Xplore API. It should not be constructed, but obtained as a result of calling the :meth:`Query.send`.

        :param query: The query which yielded this result.
        :param results: The results returned by IEEE Xplore API.

    """
    dataType = Result

    def __init__(self, query, results):
        self.__query = query
        self.__lazyComplete = False
        try:
            self.searched = results['total_searched']
            self.__total = results['total_records']
        except KeyError as e:
            raise ValueError('Invalid result set') from e

        try:
            super().__init__(results['articles'])
        except KeyError as e:
            super().__init__()

    def __getitem__(self, item):
        while (item >= super().__len__()):
            self.fetchMore()
        return super().__getitem__(item)

    def __len__(self):
        return self.__total if self.__lazyComplete else super().__len__()

    def __iter__(self):
        # Yield items already in data set:
        it = super().__iter__()
        while True:
            try:
                yield next(it)
            except StopIteration:
                break

        if not self.__lazyComplete:
            return

        # Fetch more items and yield them:
        while True:
            try:
                more = self.fetchMore()
                for m in more:
                    yield m
            except EOFError as e:
                if (super().__len__() != self.__total):
                    raise ResourceWarning(f"Expected number of articles does not match actual number of articles ({super().__len__()} != {self.__total})") from e
                return

    def __iadd__(self, other):
        if (self.__total != other.__total):
            print(f"WARNING: Total number of articles mismatch")
        super().__iadd__(other)


    def fetchMore(self):
        """ Fetches more bibliography data from IEEE Xplore API using the same query as previously.
            This is useful only if all results were not already returned.

            It raises a :class:`EOFError` if there are no more results:

            :retuns: The data fetched from the database as a :class:`ResultSet`
        """
        more = self.__query.send()
        if len(more) == 0:
            raise EOFError("Could not fetch more articles")
        self.__iadd__(more)
        return more


    def complete(self, lazy=True):
        """ Completes the results set.

            :param lazy: If `True`, the set is completed lazily (i.e. only when needed). Otherwise, the set is completed immediately and as many queries as needed are issued.

            :returns: ``self``
        """
        self.__lazyComplete = lazy
        if self.__lazyComplete:
            return self

        while True:
            try:
                self.fetchMore()
            except EOFError as e:
                if (super().__len__() != self.__total):
                    raise ResourceWarning(f"Expected number of articles does not match actual number of articles ({super().__len__()} != {self.__total})") from e
                return self


class Database:
    """ An instance of this class respresents an access to IEEE Xplore bibliography database associated with the given access key.

        :param key: The key to access IEEE Xplore API.
    """
    API_URL = "http://ieeexploreapi.ieee.org/api/v1/search/articles"

    def __init__(self, key):
        self.__key = key

    def query(self, **kwArgs):
        """ Creates a :class:`Query` to this database

            :param kwArgs: Keywords arguments. Each argument represents a query search field.

            :retuns: A :class:`Query` associated to this database.

            **Examples**::

                q = db.query(author="Smith John")
        """
        return Query(self, **kwArgs)

    def send(self, queryStr):
        """ Sends the given query to IEEE Xplore API.

            This method is not intended to be used directly. It is used internally by :meth:`Query.send`.

            :param queryStr: A string containing the query encoded for HTTP GET.

            :returns: The result of the query as a :class:`ResultSet`.
        """
        queryStr = Database.API_URL + '?' + queryStr + '&' + urlencode({'apikey': self.__key})
        print(f"Query URL {queryStr}")
        #return
        try:
            with urlopen(queryStr) as ans:
                data = json.load(ans)
                print(json.dumps(data, indent=2))
                return data
        except urlerrors.HTTPError as err:
            print(err)
            raise err

if __name__ == '__main__':
    db = Database("4dm73j4bqk6k73knw333wzh7")
    query = db.query(author=QueryString("Pascal COMBE*"))
    #query = db.query(author=QueryString("Pascal COMBES") & "Al Kassem JEBAI" | "Philippe MARTIN")
    query.limit(5)
    #query = db.query(author="Philippe MARTIN" | QueryString("Pascal COMBES") & "Al Kassem JEBAI")
    #query['publication_year'] = '2016'
    assert 'author' in query
    for k, v in query:
        print(f"{k} -> {v}")
    #query['doi'] = 'test'
    for k, v in query:
        print(f"{k} -> {v}")
    #query['article_number'] = 1
    for k, v in query:
        print(f"{k} -> {v}")

    print("FIRST QUERY:")
    result = query.send()
    print(len(result))
    for r in result:
        print(r)
    print("SECOND QUERY:")
    result = query.send()
    print(len(result))
    for r in result:
        print(r)
    print("THIRD QUERY:")
    result = query.send()
    print(len(result))
    for r in result:
        print(r)

"11 Mar. 1989"
"15-17 Dec. 2014"
"29 Oct.-1 Nov. 2017"
"6-8 July 2016"
"22-24 June 2016"
"21-24 May 2017"
"5-7 June 2018"

"""
FIRST QUERY:
Query URL http://ieeexploreapi.ieee.org/api/v1/search/articles?author=%22Pascal+COMBE%2A%22&max_records=5&start_record=1&apikey=4dm73j4bqk6k73knw333wzh7
{
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
    }
  ]
}
SECOND QUERY:
Query URL http://ieeexploreapi.ieee.org/api/v1/search/articles?author=%22Pascal+COMBE%2A%22&max_records=5&start_record=6&apikey=4dm73j4bqk6k73knw333wzh7
{
  "total_records": 6,
  "total_searched": 4804555,
  "articles": [
    {
      "title": "Modeling and Analyzing the Stability of an Induction Motor Drive System Using an Output LC Filter",
      "publisher": "VDE",
      "isbn": "978-3-8007-4646-0",
      "rank": 6,
      "authors": {
        "authors": [
          {
            "full_name": "Pascal Combes",
            "author_order": 1
          },
          {
            "full_name": "Al Kassem Jebai",
            "author_order": 2
          }
        ]
      },
      "access_type": "LOCKED",
      "content_type": "Conferences",
      "abstract": "Output LC filters are commonly used to filter the high frequency harmonics induced by PWM switching. Their effect is generally disregarded, as nonmodeled dynamics are handled by control law robustness. We show that the output filter can easily be modeled and be taken into account in the control design. We provide numeric stability analysis of control laws with or without current feedback. We also prove that it is more favorable to feed back the drive current than to feed back the motor current.",
      "article_number": "8402995",
      "pdf_url": "https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=8402995",
      "abstract_url": "https://ieeexplore.ieee.org/document/8402995/",
      "publication_title": "PCIM Europe 2018; International Exhibition and Conference for Power Electronics, Intelligent Motion, Renewable Energy and Energy Management",
      "conference_location": "Nuremberg, Germany",
      "conference_dates": "5-7 June 2018",
      "publication_number": 8402798,
      "is_number": 8402799,
      "publication_year": 2018,
      "publication_date": "5-7 June 2018",
      "start_page": "1",
      "end_page": "8",
      "citing_paper_count": 0,
      "citing_patent_count": 0,
      "index_terms": {}
    }
  ]
}
THIRD QUERY:
Query URL http://ieeexploreapi.ieee.org/api/v1/search/articles?author=%22Pascal+COMBE%2A%22&max_records=5&start_record=11&apikey=4dm73j4bqk6k73knw333wzh7
{
  "total_records": 6,
  "total_searched": 4804555
}
"""
