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

from bibdata import *

import warnings
import unittest
from PythonUtils.testdata import TestData

class ValidatorTest(unittest.TestCase):
    @TestData([
        ['/path'],
        ['/path;parameters'],
        ['/path;parameters?query'],
        ['/path;parameters?query#fragment'],
        ['/path;parameters#fragment'],
        ['/path?query'],
        ['/path?query#fragment'],
        ['/path#fragment'],
        ['netloc'],
        ['netloc;parameters'],
        ['netloc;parameters?query'],
        ['netloc;parameters?query#fragment'],
        ['netloc;parameters#fragment'],
        ['netloc?query'],
        ['netloc?query#fragment'],
        ['netloc#fragment'],
        ['netloc/path'],
        ['netloc/path;parameters'],
        ['netloc/path;parameters?query'],
        ['netloc/path;parameters?query#fragment'],
        ['netloc/path;parameters#fragment'],
        ['netloc/path?query'],
        ['netloc/path?query#fragment'],
        ['netloc/path#fragment'],
        ['scheme:///path'],
        ['scheme:///path;parameters'],
        ['scheme:///path;parameters?query'],
        ['scheme:///path;parameters?query#fragment'],
        ['scheme:///path;parameters#fragment'],
        ['scheme:///path?query'],
        ['scheme:///path?query#fragment'],
        ['scheme:///path#fragment'],
        ['scheme://netloc'],
        ['scheme://netloc;parameters'],
        ['scheme://netloc;parameters?query'],
        ['scheme://netloc;parameters?query#fragment'],
        ['scheme://netloc;parameters#fragment'],
        ['scheme://netloc?query'],
        ['scheme://netloc?query#fragment'],
        ['scheme://netloc#fragment'],
        ['scheme://netloc/path'],
        ['scheme://netloc/path;parameters'],
        ['scheme://netloc/path;parameters?query'],
        ['scheme://netloc/path;parameters?query#fragment'],
        ['scheme://netloc/path;parameters#fragment'],
        ['scheme://netloc/path?query'],
        ['scheme://netloc/path?query#fragment'],
        ['scheme://netloc/path#fragment'],
    ])
    def testUrlValidator(self, data):
        self.assertIs(urlValidator(data), True)


    @TestData([
        ['99921-58-10-7'],
        ['9971-5-0210-0'],
        ['960-425-059-0'],
        ['80-902734-1-6'],
        ['85-359-0277-5'],
        ['1-84356-028-3'],
        ['0-684-84328-5'],
        ['0-85131-041-9'],
        ['93-86954-21-4'],
        ['0-943396-04-2'],
        ['978-0-306-40615-7']
    ])
    def testValidIsbn(self, data):
        self.assertIs(isbnValidator(data), True)

    @TestData([
        ['99921-58-10-6'],
        ['99921-58-10-8'],
        ['9971-5-0209-0'],
        ['9971-5-0211-0'],
        ['960-424-059-0'],
        ['960-426-059-0'],
        ['79-902734-1-6'],
        ['81-902734-1-6'],
        ['80-902734-1-X'],
        ['-80-90274-1-6'],
    ])
    def testInalidIsbn(self, data):
        self.assertFalse(isbnValidator(data))

    @TestData([
        ['0378-5955'],
    ])
    def testValidIssn(self, data):
        self.assertIs(issnValidator(data), True)

    @TestData([
        ['0378-5954'],
        ['0378-5956'],
        ['0378-595X'],
    ])
    def testInvalidIssn(self, data):
        self.assertFalse(issnValidator(data))

class DoiTest(unittest.TestCase):
    @TestData([
        {'value': '10.1234/56789',  'prefix': '10.1234', 'suffix': '56789'},
        {'value': '10.abcd/suffix', 'prefix': '10.abcd', 'suffix': 'suffix'},
        {'value': '10.1234/suffix', 'prefix': '10.1234', 'suffix': 'suffix'},
        {'value': '10.abcd/56789',  'prefix': '10.abcd', 'suffix': '56789'},
    ])
    def testValidDOI(self, value, prefix, suffix):
        doi = DOI(value)
        self.assertEqual(doi.prefix, prefix)
        self.assertEqual(doi.suffix, suffix)

    @TestData([
        {'value': '11.1234/56789'   },
        {'value': '11.abcd/suffix'  },
        {'value': '10.123/56789'    },
        {'value': '10.abc/suffix'   },
        {'value': '10.12345/56789'  },
        {'value': '10.abcde/suffix' },
        {'value': '10.123456789'    },
        {'value': '10.abcdsuffix'   },
        {'value': '10.1234.56789'   },
        {'value': '10.abcd.suffix'  },
    ])
    def testInvalidDOI(self, value):
        with self.assertRaises(ValueError):
            doi = DOI(value)

class AuthorTest(unittest.TestCase):
    @TestData([
        {'value': ["Name1", "Firstname"],                                   'name': "Name1"},
        {'value': ["Name1", "Firstname", "Secondname"],                     'name': "Name1"},
        {'value': ["Name1", "Firstname", "Secondname", "Thirdname"],        'name': "Name1"},
        {'value': ["Name1-Name2", "Firstname"],                             'name': "Name1-Name2"},
        {'value': ["Name1-Name2", "Firstname", "Secondname"],               'name': "Name1-Name2"},
        {'value': ["Name1-Name2", "Firstname", "Secondname", "Thirdname"],  'name': "Name1-Name2"},
        {'value': "Name1, Firstname",                                       'name': "Name1"},
        {'value': "Name1, Firstname Secondname",                            'name': "Name1"},
        {'value': "Name1, Firstname Secondname Thirdname",                  'name': "Name1"},
        {'value': "Name1-Name2, Firstname",                                 'name': "Name1-Name2"},
        {'value': "Name1-Name2, Firstname Secondname",                      'name': "Name1-Name2"},
        {'value': "Name1-Name2, Firstname Secondname Thirdname",            'name': "Name1-Name2"},
        {'value': "Firstname Name1",                                        'name': "Name1"},
        {'value': "Firstname Secondname Name1",                             'name': "Name1"},
        {'value': "Firstname Secondname Thirdname Name1",                   'name': "Name1"},
        {'value': "Firstname Name1-Name2",                                  'name': "Name1-Name2"},
        {'value': "Firstname Secondname Name1-Name2",                       'name': "Name1-Name2"},
        {'value': "Firstname Secondname Thirdname Name1-Name2",             'name': "Name1-Name2"},
    ])
    def testName(self, value, name):
        author = Author(value)
        self.assertEqual(author['name'], name)

    @TestData([
        {'value': ["Name1", "Firstname"],                                   'forenames': ["Firstname"]},
        {'value': ["Name1", "Firstname", "Secondname"],                     'forenames': ["Firstname", "Secondname"]},
        {'value': ["Name1", "Firstname", "Secondname", "Thirdname"],        'forenames': ["Firstname", "Secondname", "Thirdname"]},
        {'value': ["Name1-Name2", "Firstname"],                             'forenames': ["Firstname"]},
        {'value': ["Name1-Name2", "Firstname", "Secondname"],               'forenames': ["Firstname", "Secondname"]},
        {'value': ["Name1-Name2", "Firstname", "Secondname", "Thirdname"],  'forenames': ["Firstname", "Secondname", "Thirdname"]},
        {'value': "Name1, Firstname",                                       'forenames': ["Firstname"]},
        {'value': "Name1, Firstname Secondname",                            'forenames': ["Firstname", "Secondname"]},
        {'value': "Name1, Firstname Secondname Thirdname",                  'forenames': ["Firstname", "Secondname", "Thirdname"]},
        {'value': "Name1-Name2, Firstname",                                 'forenames': ["Firstname"]},
        {'value': "Name1-Name2, Firstname Secondname",                      'forenames': ["Firstname", "Secondname"]},
        {'value': "Name1-Name2, Firstname Secondname Thirdname",            'forenames': ["Firstname", "Secondname", "Thirdname"]},
        {'value': "Firstname Name1",                                        'forenames': ["Firstname"]},
        {'value': "Firstname Secondname Name1",                             'forenames': ["Firstname", "Secondname"]},
        {'value': "Firstname Secondname Thirdname Name1",                   'forenames': ["Firstname", "Secondname", "Thirdname"]},
        {'value': "Firstname Name1-Name2",                                  'forenames': ["Firstname"]},
        {'value': "Firstname Secondname Name1-Name2",                       'forenames': ["Firstname", "Secondname"]},
        {'value': "Firstname Secondname Thirdname Name1-Name2",             'forenames': ["Firstname", "Secondname", "Thirdname"]},
    ])
    def testForenames(self, value, forenames):
        author = Author(value)
        self.assertEqual(author['forenames'], forenames)

    @TestData([
        {'value': ["Name1", "Firstname"],                                   'initial': "N"},
        {'value': ["Name1", "Firstname", "Secondname"],                     'initial': "N"},
        {'value': ["Name1", "Firstname", "Secondname", "Thirdname"],        'initial': "N"},
        {'value': ["Name1-Name2", "Firstname"],                             'initial': "N"},
        {'value': ["Name1-Name2", "Firstname", "Secondname"],               'initial': "N"},
        {'value': ["Name1-Name2", "Firstname", "Secondname", "Thirdname"],  'initial': "N"},
        {'value': "Name1, Firstname",                                       'initial': "N"},
        {'value': "Name1, Firstname Secondname",                            'initial': "N"},
        {'value': "Name1, Firstname Secondname Thirdname",                  'initial': "N"},
        {'value': "Name1-Name2, Firstname",                                 'initial': "N"},
        {'value': "Name1-Name2, Firstname Secondname",                      'initial': "N"},
        {'value': "Name1-Name2, Firstname Secondname Thirdname",            'initial': "N"},
        {'value': "Firstname Name1",                                        'initial': "N"},
        {'value': "Firstname Secondname Name1",                             'initial': "N"},
        {'value': "Firstname Secondname Thirdname Name1",                   'initial': "N"},
        {'value': "Firstname Name1-Name2",                                  'initial': "N"},
        {'value': "Firstname Secondname Name1-Name2",                       'initial': "N"},
        {'value': "Firstname Secondname Thirdname Name1-Name2",             'initial': "N"},
    ])
    def testInitial(self, value, initial):
        author = Author(value)
        self.assertEqual(author['initial'], initial)

    @TestData([
        {'value': ["Name1", "Firstname"],                                   'string': "Name1-Name2, Firstname"},
        {'value': ["Name1", "Firstname", "Secondname"],                     'string': "Name1, Firstname Secondname"},
        {'value': ["Name1", "Firstname", "Secondname", "Thirdname"],        'string': "Name1, Firstname Secondname Thirdname"},
        {'value': ["Name1-Name2", "Firstname"],                             'string': "Name1-Name2, Firstname"},
        {'value': ["Name1-Name2", "Firstname", "Secondname"],               'string': "Name1-Name2, Firstname Secondname"},
        {'value': ["Name1-Name2", "Firstname", "Secondname", "Thirdname"],  'string': "Name1-Name2, Firstname Secondname Thirdname"},
        {'value': "Name1, Firstname",                                       'string': "Name1, Firstname"},
        {'value': "Name1, Firstname Secondname",                            'string': "Name1, Firstname Secondname"},
        {'value': "Name1, Firstname Secondname Thirdname",                  'string': "Name1, Firstname Secondname Thirdname"},
        {'value': "Name1-Name2, Firstname",                                 'string': "Name1-Name2, Firstname"},
        {'value': "Name1-Name2, Firstname Secondname",                      'string': "Name1-Name2, Firstname Secondname"},
        {'value': "Name1-Name2, Firstname Secondname Thirdname",            'string': "Name1-Name2, Firstname Secondname Thirdname"},
        {'value': "Firstname Name1",                                        'string': "Name1, Firstname"},
        {'value': "Firstname Secondname Name1",                             'string': "Name1, Firstname Secondname"},
        {'value': "Firstname Secondname Thirdname Name1",                   'string': "Name1, Firstname Secondname Thirdname"},
        {'value': "Firstname Name1-Name2",                                  'string': "Name1-Name2, Firstname"},
        {'value': "Firstname Secondname Name1-Name2",                       'string': "Name1-Name2, Firstname Secondname"},
        {'value': "Firstname Secondname Thirdname Name1-Name2",             'string': "Name1-Name2, Firstname Secondname Thirdname"},
    ])
    def testString(self, value, string):
        author = Author(value)
        self.assertEqual(str(author), string)

class AuthorListTest(unittest.TestCase):
    @TestData([
        {'authors': ['Alicename, Alice']},
        {'authors': ['Alicename, Alice', 'Bobname, Bob']},
    ])
    def testConstructor(self, authors):
        authorList = AuthorList(authors)
        self.assertEqual(len(authorList), len(authors))
        for author, expected in zip(authorList, authors):
            self.assertEqual(str(author), expected)
        for a in range(0, len(authorList)):
            self.assertEqual(str(authorList[a]), authors[a])

    @TestData([
        {'authors': ['Alicename, Alice']},
        {'authors': ['Alicename, Alice', 'Bobname, Bob']},
    ])
    def testString(self, authors):
        authorList = AuthorList(authors)
        self.assertEqual(str(authorList), ' and '.join(authors))

class MockBibData(BibData):
    fields = {
        'field1': {
            'type': int,
            'min': 1,
        },
        'field2': {
            'type': int,
            'min': 1,
        }
    }

class MockBibDataSet(BibDataSet):
    dataType = MockBibData

class MockBibDataTest(unittest.TestCase):
    def __checkWarnings(self, actual, expected):
        expectedMessages = {
            'field0': 'Unknown result field "field0"',
            'field1': 'Too small value for result field "field1": 0',
        }
        self.assertEqual(len(actual), len(expected))
        for i, k in enumerate(expected):
            self.assertTrue(issubclass(actual[i].category, UserWarning))
            self.assertEqual(str(actual[i].message), expectedMessages[k])

    @TestData([
        {'raw': {'field1': 1}},
        {'raw': {'field2': 1}},
        {'raw': {'field1': 1, 'field2': 1}},
    ])
    def testConstructor(self, raw):
        data = MockBibData(raw)
        for k in raw:
            self.assertIn(k, data)
            self.assertEqual(data[k], raw[k])
        self.assertEqual({k: v for k, v in data}, raw)

    @TestData([
        {'raw': {'field0': 1}},
        {'raw': {'field1': 0}},
        {'raw': {'field0': 1, 'field1': 0}},
    ])
    def testInvalidConstructor(self, raw):
        with warnings.catch_warnings(record=True) as warns:
            data = MockBibData(raw)

            self.__checkWarnings(warns, raw)

        for k in raw:
            self.assertNotIn(k, data)
        self.assertEqual({k: v for k, v in data}, {})

    @TestData([
        {'raw': {'field1': 1}},
        {'raw': {'field2': 1}},
        {'raw': {'field1': 1, 'field2': 1}},
    ])
    def testValidSetItem(self, raw):
        data = MockBibData()
        for k, v in raw.items():
            data[k] = v

        for k in raw:
            self.assertIn(k, data)
            self.assertEqual(data[k], raw[k])
        self.assertEqual({k: v for k, v in data}, raw)

    @TestData([
        {'raw': {'field0': 1}},
        {'raw': {'field1': 0}},
        {'raw': {'field0': 1, 'field1': 0}},
    ])
    def testInvalidSetItem(self, raw):
        data = MockBibData()
        with warnings.catch_warnings(record=True) as warns:
            for k, v in raw.items():
                data[k] = v

            self.__checkWarnings(warns, raw)

        for k in raw:
            self.assertNotIn(k, data)
        self.assertEqual({k: v for k, v in data}, {})

class BibDataSetTest(unittest.TestCase):
    @TestData([
        [[{'field1': 1}]],
        [[{'field1': 1}, {'field1': 2}]],
        [[{'field1': 1}, {'field1': 2}, {'field1': 3}]],
    ])
    def testConstructor(self, data):
        dataSet = MockBibDataSet(data)
        self.assertEqual(len(dataSet), len(data))
        self.assertEqual([dict(d) for d in dataSet], data)

    @TestData([
        [[], [{'field1': 1}], [{'field1': 1}]],
        [[{'field1': 1}], [], [{'field1': 1}]],
        [[{'field1': 1}], [{'field1': 2}], [{'field1': 1}, {'field1': 2}]],
        [[{'field1': 1}, {'field1': 2}], [{'field1': 3}], [{'field1': 1}, {'field1': 2}, {'field1': 3}]],
        [[{'field1': 1}], [{'field1': 2}, {'field1': 3}], [{'field1': 1}, {'field1': 2}, {'field1': 3}]],
    ])
    def testIncrementalAdd(self, data1, data2, data):
        dataSet = MockBibDataSet(data1)
        dataSet += MockBibDataSet(data2)
        self.assertEqual(len(dataSet), len(data))
        self.assertEqual([dict(d) for d in dataSet], data)



