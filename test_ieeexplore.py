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

from ieeexplore import QueryString as Q
from ieeexplore import Query
from ieeexplore import Result

import warnings
import unittest
from PythonUtils.testdata import TestData

from datetime import date
from random import randrange

class QueryStringTest(unittest.TestCase):
    @TestData([
        ('test',  '"test"'),
        ('test*',  '"test*"'),
        ('test space',  '"test space"'),
        (u'test', '"test"'),
        (u'test*', '"test*"'),
        (u'test space', '"test space"'),
    ])
    def testConstructor(self, string, query):
        queryString = Q(string)
        self.assertTrue(Q.isQueryString(queryString))
        self.assertEqual(str(queryString), query)
        self.assertFalse(queryString.isNegated())

    @TestData([
        ('test',  '"test"'),
        ('test*',  '"test*"'),
        ('test space',  '"test space"'),
        (u'test', '"test"'),
        (u'test*', '"test*"'),
        (u'test space', '"test space"'),
    ])
    def testInvert(self, string, query):
        queryString = ~Q(string)
        self.assertTrue(Q.isQueryString(queryString))
        self.assertEqual(str(queryString), query)
        self.assertTrue(queryString.isNegated())

    @TestData([b'test', 0, 1, True, False])
    def testConstructInvalidType(self, value):
        with self.assertRaises(TypeError):
            Q(value)

    @TestData([
        (Q('test1'), Q('test2'), '"test1" OR "test2"'),
        (Q('test1'), 'test2', '"test1" OR "test2"'),
        (Q('test1'), u'test2', '"test1" OR "test2"'),
        ('test1', Q('test2'), '"test1" OR "test2"'),
        (u'test1', Q('test2'), '"test1" OR "test2"'),
    ])
    def testOperatorOr(self, value1, value2, query):
        self.assertTrue(Q.isQueryString(value1 | value2))
        self.assertEqual(str(value1 | value2), query)

    @TestData([
        (Q('test1'), ~Q('test2')),
        (~Q('test1'), Q('test2')),
        ('test1', ~Q('test2')),
        (~Q('test1'), 'test2'),
    ])
    def testOperatorOrInvalidValue(self, value1, value2):
        with self.assertRaises(ValueError):
            value1 | value2

    @TestData([
        (Q('test1'), b'test2'),
        (Q('test1'), 0),
        (Q('test1'), 1),
        (Q('test1'), True),
        (Q('test1'), False),
        (b'test1', Q('test2')),
        (0, Q('test2')),
        (1, Q('test2')),
        (True, Q('test2')),
        (False, Q('test2')),
    ])
    def testOperatorOrInvalidType(self, value1, value2):
        with self.assertRaises(TypeError):
            value1 | value2

    @TestData([
        (Q('test1'), Q('test2'), '"test1" AND "test2"'),
        (Q('test1'), 'test2', '"test1" AND "test2"'),
        (Q('test1'), u'test2', '"test1" AND "test2"'),
        ('test1', Q('test2'), '"test1" AND "test2"'),
        (u'test1', Q('test2'), '"test1" AND "test2"'),
        (Q('test1'), ~Q('test2'), '"test1" NOT "test2"'),
        (~Q('test1'), Q('test2'), '"test2" NOT "test1"'),
        ('test1', ~Q('test2'), '"test1" NOT "test2"'),
        (u'test1', ~Q('test2'), '"test1" NOT "test2"'),
        (~Q('test1'), u'test2', '"test2" NOT "test1"'),
        (~Q('test1'), 'test2', '"test2" NOT "test1"'),
    ])
    def testOperatorAnd(self, value1, value2, query):
        self.assertTrue(Q.isQueryString(value1 & value2))
        self.assertEqual(str(value1 & value2), query)

    @TestData([
        (~Q('test1'), ~Q('test2')),
    ])
    def testOperatorAndInvalidValue(self, value1, value2):
        with self.assertRaises(ValueError):
            value1 | value2

    @TestData([
        (Q('test1'), b'test2'),
        (Q('test1'), 0),
        (Q('test1'), 1),
        (Q('test1'), True),
        (Q('test1'), False),
        (b'test1', Q('test2')),
        (0, Q('test2')),
        (1, Q('test2')),
        (True, Q('test2')),
        (False, Q('test2')),
    ])
    def testOperatorAndInvalidType(self, value1, value2):
        with self.assertRaises(TypeError):
            value1 & value2

    @TestData([
        (Q('test1') | Q('test2') | Q('test3'), '"test1" OR "test2" OR "test3"'),
        (Q('test1') & Q('test2') | Q('test3'), '"test1" AND "test2" OR "test3"'),
        (Q('test1') | Q('test2') & Q('test3'), '"test1" OR "test2" AND "test3"'),
        (Q('test1') & Q('test2') & Q('test3'), '"test1" AND "test2" AND "test3"'),
        (Q('test1') & ~Q('test2') | Q('test3'), '"test1" NOT "test2" OR "test3"'),
        (~Q('test1') & Q('test2') | Q('test3'), '"test2" NOT "test1" OR "test3"'),
        (Q('test1') | Q('test2') & ~Q('test3'), '"test1" OR "test2" NOT "test3"'),
        (Q('test1') | ~Q('test2') & Q('test3'), '"test1" OR "test3" NOT "test2"'),
        (Q('test1') & Q('test2') & ~Q('test3'), '"test1" AND "test2" NOT "test3"'),
        (Q('test1') & ~Q('test2') & Q('test3'), '"test1" AND "test3" NOT "test2"'),
        (~Q('test1') & Q('test2') & Q('test3'), '"test2" AND "test3" NOT "test1"'),
        (Q('test1') & ~Q('test2') & ~Q('test3'), '"test1" NOT "test2" NOT "test3"'),
        (~Q('test1') & Q('test2') & ~Q('test3'), '"test2" NOT "test1" NOT "test3"'),
        (~Q('test1') & ~Q('test2') & Q('test3'), '"test3" NOT "test1" NOT "test2"'),
    ])
    def testOperators(self, expr, query):
        self.assertTrue(Q.isQueryString(expr))
        self.assertEqual(str(expr), query)

    def testOperatorsInvalidValue(self):
        with self.assertRaises(ValueError):
            Q('test1') & Q('test2') | ~Q('test3')
        with self.assertRaises(ValueError):
            ~Q('test1') | Q('test2') & Q('test3')
        with self.assertRaises(ValueError):
            str(~Q('test1') & ~Q('test2') & ~Q('test3'))

    @TestData(['test', u'test', b'test', 0, 1, True, False])
    def testIsQueryString(self, value):
        self.assertFalse(Q.isQueryString(value))

    @TestData([
        (Q('test'), 'test'),
        (~Q('test'), 'test'),
        (Q('test'), u'test'),
        (Q('test*'), '*'),
        (Q('te*st'), '*'),
        (Q('*test'), '*'),
        (Q('test1') | Q('test2'), '1'),
        (Q('test1') | Q('test2'), '2'),
        (Q('test1') & Q('test2'), '1'),
        (Q('test1') & Q('test2'), '2'),
        (~Q('test1') & Q('test2'), '1'),
        (~Q('test1') & Q('test2'), '2'),
        (Q('test1') & ~Q('test2'), '1'),
        (Q('test1') & ~Q('test2'), '2'),
    ])
    def testContains(self, queryString, value):
        self.assertIn(value, queryString)

    @TestData([
        (Q('test'), '*'),
        (Q('test'), 'tset'),
        (Q('test*'), 'test0'),
        (Q('test1') | Q('test2'), '*'),
        (Q('test1') & Q('test2'), '*'),
        (~Q('test1') & Q('test2'), '*'),
        (Q('test1') & ~Q('test2'), '*'),
    ])
    def testDontContains(self, queryString, value):
        self.assertNotIn(value, queryString)

    @TestData([
        (Q('test'), 'test', 0),
        (~Q('test'), 'test', 0),
        (Q('test'), u'test', 0),
        (Q('test*'), '*', 4),
        (Q('te*st'), '*', 2),
        (Q('*test'), '*', 0),
        (Q('test1') | Q('test2'), '1', 4),
        (Q('test1') | Q('test2'), '2', 4),
        (Q('test1') & Q('test2'), '1', 4),
        (Q('test1') & Q('test2'), '2', 4),
        (~Q('test1') & Q('test2'), '1', 4),
        (~Q('test1') & Q('test2'), '2', 4),
        (Q('test1') & ~Q('test2'), '1', 4),
        (Q('test1') & ~Q('test2'), '2', 4),
        (Q('test1') | Q('tset2'), 'e', 1),
        (Q('test1') | Q('tset2'), 's', 1),
    ])
    def testIndex(self, queryString, value, index):
        self.assertEqual(queryString.index(value), index)

    @TestData([
        (Q('test'), '*'),
        (Q('test'), 'tset'),
        (Q('test*'), 'test0'),
        (Q('test1') | Q('test2'), '*'),
        (Q('test1') & Q('test2'), '*'),
        (~Q('test1') & Q('test2'), '*'),
        (Q('test1') & ~Q('test2'), '*'),
    ])
    def testIndexException(self, queryString, value):
        with self.assertRaises(ValueError):
            queryString.index(value)

    @TestData([
        (Q('test'), 'test', 1),
        (~Q('test'), 'test', 1),
        (Q('test'), u'test', 1),
        (Q('test*'), '*', 1),
        (Q('te*st'), '*', 1),
        (Q('*test'), '*', 1),
        (Q('test1') | Q('test2'), '1', 1),
        (Q('test1') | Q('test2'), '2', 1),
        (Q('test1') & Q('test2'), '1', 1),
        (Q('test1') & Q('test2'), '2', 1),
        (~Q('test1') & Q('test2'), '1', 1),
        (~Q('test1') & Q('test2'), '2', 1),
        (Q('test1') & ~Q('test2'), '1', 1),
        (Q('test1') & ~Q('test2'), '2', 1),
        (Q('test1') | Q('test2'), 'e', 2),
        (Q('test1') | Q('test2'), 't', 4),
    ])
    def testCount(self, queryString, value, count):
        self.assertEqual(queryString.count(value), count)

class MockDatabase:
    def __init__(self, searched=None, total=100):
        self.lastQuery = None
        self.queryNumber = 0
        self.totalRecords = total
        self.totalSearched = searched if searched is not None else randrange(1000000000)

    def clear(self):
        self.lastQuery = None
        self.queryNumber = 0

    def send(self, query):
        self.lastQuery = query
        self.queryNumber += 1

        startRecord = [p for p in query.split('&') if 'start_record=' in p]
        startRecord = int(startRecord[0].replace('start_record=', '')) if len(startRecord) > 0 else 1

        maxRecords = [p for p in query.split('&') if 'max_records=' in p]
        maxRecords = int(maxRecords[0].replace('max_records=', '')) if len(maxRecords) > 0 else 200

        if (startRecord > self.totalRecords):
            return {
                'total_searched': self.totalSearched,
                'total_records': self.totalRecords,
            }

        return {
            'total_searched': self.totalSearched,
            'total_records': self.totalRecords,
            'articles': [{'article_number': i} for i in range (startRecord, min(self.totalRecords + 1, startRecord + maxRecords))]
        }

class QueryTest(unittest.TestCase):
    def __init__(self, *args, **kwArgs):
        super().__init__(*args, **kwArgs)
        self.db = MockDatabase()

    @TestData([k for k, v in Query.params.items() if (v['type'] == 'search') and ('name' not in v) and ('value_type' not in v)])
    def testConstrctSearchParameterString(self, param):
        kwArgs = {param: 'test'}

        query = Query(self.db, **kwArgs)
        self.assertIn(param, query)
        self.assertEqual(query[param], 'test')
        self.assertEqual(dict(query), kwArgs)

        query.send()
        self.assertGreaterEqual(set(self.db.lastQuery.split('&')), {f'{param}=test'})
        self.db.clear()

        del query[param]
        self.assertNotIn(param, query)

    @TestData([k for k, v in Query.params.items() if (v['type'] == 'search') and ('name' not in v) and ('value_type' not in v)])
    def testConstrctSearchParameterUnistring(self, param):
        kwArgs = {param: u'test'}

        query = Query(self.db, **kwArgs)
        self.assertIn(param, query)
        self.assertEqual(query[param], u'test')
        self.assertEqual(dict(query), kwArgs)

        query.send()
        self.assertGreaterEqual(set(self.db.lastQuery.split('&')), {f'{param}=test'})
        self.db.clear()

        del query[param]
        self.assertNotIn(param, query)

    @TestData([k for k, v in Query.params.items() if (v['type'] == 'search') and ('boolean_operators' in v) and v['boolean_operators']])
    def testConstrctSearchParameterQueryString(self, param):
        kwArgs = {param: Q('test')}

        query = Query(self.db, **kwArgs)
        self.assertIn(param, query)
        self.assertEqual(query[param], Q('test'))
        self.assertEqual(dict(query), kwArgs)

        query.send()
        self.assertGreaterEqual(set(self.db.lastQuery.split('&')), {f'{param}=%22test%22'})
        self.db.clear()

        del query[param]
        self.assertNotIn(param, query)

    @TestData([k for k, v in Query.params.items() if (v['type'] == 'search') and ('value_type' not in v) and (('boolean_operators' not in v) or (not v['boolean_operators']))])
    def testInvalidConstrctSearchParameterQueryString(self, param):
        kwArgs = {param: Q('test')}

        with warnings.catch_warnings(record=True) as warns:
            query = Query(self.db, **kwArgs)

            self.assertEqual(len(warns), 1)
            self.assertTrue(issubclass(warns[0].category, UserWarning))
            self.assertEqual(str(warns[0].message), "Boolean operators are not accepted")

        self.assertNotIn(param, query)
        self.assertEqual(dict(query), {})

    @TestData([k for k, v in Query.params.items() if (v['type'] == 'search') and ('name' not in v) and ('value_type' in v) and (v['value_type'] == int)])
    def testConstrctSearchParameterInt(self, param):
        kwArgs = {param: 0}

        query = Query(self.db, **kwArgs)
        self.assertIn(param, query)
        self.assertEqual(query[param], 0)
        self.assertEqual(dict(query), kwArgs)

        query.send()
        self.assertGreaterEqual(set(self.db.lastQuery.split('&')), {f'{param}=0'})
        self.db.clear()

        del query[param]
        self.assertNotIn(param, query)

    @TestData([k for k, v in Query.params.items() if (v['type'] == 'search') and ('name' not in v) and ('value_type' in v) and (v['value_type'] == int)])
    def testInvalidConstrctSearchParameterInt(self, param):
        kwArgs = {param: 'test'}

        with warnings.catch_warnings(record=True) as warns:
            query = Query(self.db, **kwArgs)

            self.assertEqual(len(warns), 1)
            self.assertTrue(issubclass(warns[0].category, UserWarning))
            self.assertEqual(str(warns[0].message), "Value \"test\" is not castable into <class 'int'>")

        self.assertNotIn(param, query)
        self.assertEqual(dict(query), {})

    @TestData([k for k, v in Query.params.items() if (v['type'] == 'search') and ('wildcard' in v) and v['wildcard']])
    def testConstructSearchParameterWildcard(self, param):
        kwArgs = {param: 'test*'}

        query = Query(self.db, **kwArgs)
        self.assertIn(param, query)
        self.assertEqual(query[param], 'test*')
        self.assertEqual(dict(query), kwArgs)

        query.send()
        self.assertGreaterEqual(set(self.db.lastQuery.split('&')), {f'{param}=test%2A'})
        self.db.clear()

        del query[param]
        self.assertNotIn(param, query)

    @TestData([k for k, v in Query.params.items() if (v['type'] == 'search') and ('value_type' not in v) and (('wildcard' not in v) or (not v['wildcard']))])
    def testInvalidConstructSearchParameterWildcard(self, param):
        kwArgs = {param: 'test*'}

        with warnings.catch_warnings(record=True) as warns:
            query = Query(self.db, **kwArgs)

            self.assertEqual(len(warns), 1)
            self.assertTrue(issubclass(warns[0].category, UserWarning))
            self.assertEqual(str(warns[0].message), "Wildcards are not accepted")

        self.assertNotIn(param, query)
        self.assertEqual(dict(query), {})

    @TestData([(k, v['wildcard_min_length']) for k, v in Query.params.items() if (v['type'] == 'search') and ('wildcard_min_length' in v)])
    def testConstructSearchParameterWildcardMinLength(self, param, minLength):
        kwArgs = {param: ('x' * minLength) + '*'}

        query = Query(self.db, **kwArgs)
        self.assertIn(param, query)
        self.assertEqual(query[param], ('x' * minLength) + '*')
        self.assertEqual(dict(query), kwArgs)

        del query[param]
        self.assertNotIn(param, query)

    @TestData([(k, v['wildcard_min_length']) for k, v in Query.params.items() if (v['type'] == 'search') and ('wildcard_min_length' in v)])
    def testInvalidConstructSearchParameterWildcardMinLength(self, param, minLength):
        kwArgs = {param: ('x' * (minLength - 1)) + '*'}

        with warnings.catch_warnings(record=True) as warns:
            query = Query(self.db, **kwArgs)

            self.assertEqual(len(warns), 1)
            self.assertTrue(issubclass(warns[0].category, UserWarning))
            self.assertEqual(str(warns[0].message), f"There must be {minLength} characters before wildcard")

        self.assertNotIn(param, query)
        self.assertEqual(dict(query), {})

    @TestData([(k, v['wildcard_max']) for k, v in Query.params.items() if (v['type'] == 'search') and ('wildcard_max' in v)])
    def testConstructSearchParameterMaxWildcards(self, param, maxWildcards):
        kwArgs = {param: 'test' + ('*' * maxWildcards)}

        query = Query(self.db, **kwArgs)
        self.assertIn(param, query)
        self.assertEqual(query[param], 'test' + ('*' * maxWildcards))
        self.assertEqual(dict(query), kwArgs)

        del query[param]
        self.assertNotIn(param, query)

    @TestData([(k, v['wildcard_max']) for k, v in Query.params.items() if (v['type'] == 'search') and ('wildcard_max' in v)])
    def testInvalidConstructSearchParameterMaxWildcards(self, param, maxWildcards):
        kwArgs = {param: 'test' + ('*' * (maxWildcards + 1))}

        with warnings.catch_warnings(record=True) as warns:
            query = Query(self.db, **kwArgs)

            self.assertEqual(len(warns), 1)
            self.assertTrue(issubclass(warns[0].category, UserWarning))
            self.assertEqual(str(warns[0].message), f"There must at most {maxWildcards} wildcards")

        self.assertNotIn(param, query)
        self.assertEqual(dict(query), {})

    @TestData([(k, v['name']) for k, v in Query.params.items() if (v['type'] == 'search') and ('name' in v)])
    def testConstructNamedSearchParameterString(self, param, name):
        kwArgs = {param: 0}

        query = Query(self.db, **kwArgs)
        self.assertIn(param, query)
        self.assertEqual(query[param], 0)
        self.assertEqual(dict(query), kwArgs)

        query.send()
        self.assertGreaterEqual(set(self.db.lastQuery.split('&')), {f'{name}=0'})
        self.db.clear()

        del query[param]
        self.assertNotIn(param, query)

    @TestData([k for k, v in Query.params.items() if (v['type'] == 'search') and ('value_type' not in v) and (k not in ['article_number', 'doi'])])
    def testConstructDoiAlone(self, otherParam):
        kwArgs = {otherParam: 'delete', 'doi': '10.1234/56789'}

        with warnings.catch_warnings(record=True) as warns:
            query = Query(self.db, **kwArgs)

            self.assertEqual(len(warns), 1)
            self.assertTrue(issubclass(warns[0].category, UserWarning))
            self.assertEqual(str(warns[0].message), f"Parameter \"{otherParam}\" will be superseeded by parameter \"doi\"")

        self.assertIn('doi', query)
        self.assertNotIn(otherParam, query)
        self.assertEqual(query['doi'], '10.1234/56789')
        self.assertEqual(dict(query), {'doi': '10.1234/56789'})

        query.send()
        self.assertGreaterEqual(set(self.db.lastQuery.split('&')), {'doi=10.1234%2F56789'})
        self.db.clear()

    @TestData([k for k, v in Query.params.items() if (v['type'] == 'search') and ('value_type' not in v) and (k not in ['article_number'])])
    def testConstructArticleNumberAlone(self, otherParam):
        kwArgs = {otherParam: 'delete', 'article_number': 1}

        with warnings.catch_warnings(record=True) as warns:
            query = Query(self.db, **kwArgs)

            self.assertEqual(len(warns), 1)
            self.assertTrue(issubclass(warns[0].category, UserWarning))
            self.assertEqual(str(warns[0].message), f"Parameter \"{otherParam}\" will be superseeded by parameter \"article_number\"")

        self.assertIn('article_number', query)
        self.assertNotIn(otherParam, query)
        self.assertEqual(query['article_number'], 1)
        self.assertEqual(dict(query), {'article_number': 1})

        query.send()
        self.assertGreaterEqual(set(self.db.lastQuery.split('&')), {'article_number=1'})
        self.db.clear()

    @TestData([k for k, v in Query.params.items() if (v['type'] == 'search') and ('name' not in v) and ('value_type' not in v)])
    def testSetSearchParameterString(self, param):
        query = Query(self.db)
        query[param] = 'test'
        self.assertIn(param, query)
        self.assertEqual(query[param], 'test')
        self.assertEqual(dict(query), {param: 'test'})

        query.send()
        self.assertGreaterEqual(set(self.db.lastQuery.split('&')), {f'{param}=test'})
        self.db.clear()

        del query[param]
        self.assertNotIn(param, query)

    @TestData([k for k, v in Query.params.items() if (v['type'] == 'search') and ('name' not in v) and ('value_type' not in v)])
    def testSetSearchParameterUnistring(self, param):
        query = Query(self.db)
        query[param] = u'test'
        self.assertIn(param, query)
        self.assertEqual(query[param], u'test')
        self.assertEqual(dict(query), {param: u'test'})

        query.send()
        self.assertGreaterEqual(set(self.db.lastQuery.split('&')), {f'{param}=test'})
        self.db.clear()

        del query[param]
        self.assertNotIn(param, query)

    @TestData([k for k, v in Query.params.items() if (v['type'] == 'search') and ('boolean_operators' in v) and v['boolean_operators']])
    def testSetSearchParameterQueryString(self, param):
        query = Query(self.db)
        query[param] = Q('test')
        self.assertIn(param, query)
        self.assertEqual(query[param], Q('test'))
        self.assertEqual(dict(query), {param: Q('test')})

        query.send()
        self.assertGreaterEqual(set(self.db.lastQuery.split('&')), {f'{param}=%22test%22'})
        self.db.clear()

        del query[param]
        self.assertNotIn(param, query)

    @TestData([k for k, v in Query.params.items() if (v['type'] == 'search') and ('value_type' not in v) and (('boolean_operators' not in v) or (not v['boolean_operators']))])
    def testInvalidSetSearchParameterQueryString(self, param):
        query = Query(self.db)

        with warnings.catch_warnings(record=True) as warns:
            query[param] = Q('test')

            self.assertEqual(len(warns), 1)
            self.assertTrue(issubclass(warns[0].category, UserWarning))
            self.assertEqual(str(warns[0].message), "Boolean operators are not accepted")

        self.assertNotIn(param, query)
        self.assertEqual(dict(query), {})


    @TestData([k for k, v in Query.params.items() if (v['type'] == 'search') and ('name' not in v) and ('value_type' in v) and (v['value_type'] == int)])
    def testSetSearchParameterInt(self, param):
        query = Query(self.db)
        query[param] = 0
        self.assertIn(param, query)
        self.assertEqual(query[param], 0)
        self.assertEqual(dict(query), {param: 0})

        query.send()
        self.assertGreaterEqual(set(self.db.lastQuery.split('&')), {f'{param}=0'})
        self.db.clear()

        del query[param]
        self.assertNotIn(param, query)

    @TestData([k for k, v in Query.params.items() if (v['type'] == 'search') and ('name' not in v) and ('value_type' in v) and (v['value_type'] == int)])
    def testInvalidSetSearchParameterInt(self, param):
        query = Query(self.db)

        with warnings.catch_warnings(record=True) as warns:
            query[param] = 'test'

            self.assertEqual(len(warns), 1)
            self.assertTrue(issubclass(warns[0].category, UserWarning))
            self.assertEqual(str(warns[0].message), "Value \"test\" is not castable into <class 'int'>")

        self.assertNotIn(param, query)
        self.assertEqual(dict(query), {})

    @TestData([k for k, v in Query.params.items() if (v['type'] == 'search') and ('wildcard' in v) and v['wildcard']])
    def testSetSearchParameterWildcard(self, param):
        query = Query(self.db)
        query[param] = 'test*'
        self.assertIn(param, query)
        self.assertEqual(query[param], 'test*')
        self.assertEqual(dict(query), {param: 'test*'})

        query.send()
        self.assertGreaterEqual(set(self.db.lastQuery.split('&')), {f'{param}=test%2A'})
        self.db.clear()

        del query[param]
        self.assertNotIn(param, query)

    @TestData([k for k, v in Query.params.items() if (v['type'] == 'search') and ('value_type' not in v) and (('wildcard' not in v) or (not v['wildcard']))])
    def testInvalidSetSearchParameterWildcard(self, param):
        query = Query(self.db)

        with warnings.catch_warnings(record=True) as warns:
            query[param] = 'test*'

            self.assertEqual(len(warns), 1)
            self.assertTrue(issubclass(warns[0].category, UserWarning))
            self.assertEqual(str(warns[0].message), "Wildcards are not accepted")

        self.assertNotIn(param, query)
        self.assertEqual(dict(query), {})

    @TestData([(k, v['wildcard_min_length']) for k, v in Query.params.items() if (v['type'] == 'search') and ('wildcard_min_length' in v)])
    def testSetSearchParameterWildcardMinLength(self, param, minLength):
        query = Query(self.db)
        query[param] = ('x' * minLength) + '*'
        self.assertIn(param, query)
        self.assertEqual(query[param], ('x' * minLength) + '*')
        self.assertEqual(dict(query), {param: ('x' * minLength) + '*'})

        del query[param]
        self.assertNotIn(param, query)

    @TestData([(k, v['wildcard_min_length']) for k, v in Query.params.items() if (v['type'] == 'search') and ('wildcard_min_length' in v)])
    def testInvalidSetSearchParameterWildcardMinLength(self, param, minLength):
        query = Query(self.db)

        with warnings.catch_warnings(record=True) as warns:
            query[param] = ('x' * (minLength - 1)) + '*'

            self.assertEqual(len(warns), 1)
            self.assertTrue(issubclass(warns[0].category, UserWarning))
            self.assertEqual(str(warns[0].message), f"There must be {minLength} characters before wildcard")

        self.assertNotIn(param, query)
        self.assertEqual(dict(query), {})

    @TestData([(k, v['wildcard_max']) for k, v in Query.params.items() if (v['type'] == 'search') and ('wildcard_max' in v)])
    def testSetSearchParameterMaxWildcards(self, param, maxWildcards):
        query = Query(self.db)
        query[param] = 'test' + ('*' * maxWildcards)
        self.assertIn(param, query)
        self.assertEqual(query[param], 'test' + ('*' * maxWildcards))
        self.assertEqual(dict(query), {param: 'test' + ('*' * maxWildcards)})

        del query[param]
        self.assertNotIn(param, query)

    @TestData([(k, v['wildcard_max']) for k, v in Query.params.items() if (v['type'] == 'search') and ('wildcard_max' in v)])
    def testInvalidSetSearchParameterMaxWildcards(self, param, maxWildcards):
        query = Query(self.db)

        with warnings.catch_warnings(record=True) as warns:
            query[param] = 'test' + ('*' * (maxWildcards + 1))

            self.assertEqual(len(warns), 1)
            self.assertTrue(issubclass(warns[0].category, UserWarning))
            self.assertEqual(str(warns[0].message), f"There must at most {maxWildcards} wildcards")

        self.assertNotIn(param, query)
        self.assertEqual(dict(query), {})

    @TestData([(k, v['name']) for k, v in Query.params.items() if (v['type'] == 'search') and ('name' in v)])
    def testSetNamedSearchParameterString(self, param, name):
        query = Query(self.db)
        query[param] = 0
        self.assertIn(param, query)
        self.assertEqual(query[param], 0)
        self.assertEqual(dict(query), {param: 0})

        query.send()
        self.assertGreaterEqual(set(self.db.lastQuery.split('&')), {f'{name}=0'})
        self.db.clear()

        del query[param]
        self.assertNotIn(param, query)

    @TestData([k for k, v in Query.params.items() if (v['type'] == 'search') and ('value_type' not in v) and (k not in ['article_number', 'doi'])])
    def testSetDoiAlone(self, otherParam):
        kwArgs = {otherParam: 'delete'}

        query = Query(self.db, **kwArgs)
        with warnings.catch_warnings(record=True) as warns:
            query['doi'] = '10.1234/56789'

            self.assertEqual(len(warns), 1)
            self.assertTrue(issubclass(warns[0].category, UserWarning))
            self.assertEqual(str(warns[0].message), f"Parameter \"{otherParam}\" will be superseeded by parameter \"doi\"")

        self.assertIn('doi', query)
        self.assertNotIn(otherParam, query)
        self.assertEqual(query['doi'], '10.1234/56789')
        self.assertEqual(dict(query), {'doi': '10.1234/56789'})

        query.send()
        self.assertGreaterEqual(set(self.db.lastQuery.split('&')), {'doi=10.1234%2F56789'})
        self.db.clear()

    @TestData([k for k, v in Query.params.items() if (v['type'] == 'search') and ('value_type' not in v) and (k not in ['article_number'])])
    def testSetArticleNumberAlone(self, otherParam):
        kwArgs = {otherParam: 'delete'}

        query = Query(self.db, **kwArgs)
        with warnings.catch_warnings(record=True) as warns:
            query['article_number'] = 1

            self.assertEqual(len(warns), 1)
            self.assertTrue(issubclass(warns[0].category, UserWarning))
            self.assertEqual(str(warns[0].message), f"Parameter \"{otherParam}\" will be superseeded by parameter \"article_number\"")

        self.assertIn('article_number', query)
        self.assertNotIn(otherParam, query)
        self.assertEqual(query['article_number'], 1)
        self.assertEqual(dict(query), {'article_number': 1})

        query.send()
        self.assertGreaterEqual(set(self.db.lastQuery.split('&')), {'article_number=1'})
        self.db.clear()

    @TestData([
        {'start': None, 'end': None},
        {'start': 2000, 'end': None},
        {'start': None, 'end': 2019},
        {'start': 2000, 'end': 2019},
    ])
    def testFilterByYearRange(self, start=None, end=None):
        queryParts = set()
        query = Query(self.db)
        query.filterBy(start_year=start, end_year=end)

        if start is not None:
            self.assertEqual(query['start_year'], start)
        else:
            self.assertNotIn('start_year', query)

        if end is not None:
            self.assertEqual(query['end_year'], end)
        else:
            self.assertNotIn('end_year', query)

        if len(queryParts) == 0:
            queryParts.add('')

        query.send()
        if start is not None:
            self.assertIn(f'start_year={start}', self.db.lastQuery.split('&'))
        else:
            self.assertNotIn(f'start_year={start}', self.db.lastQuery.split('&'))
        if end is not None:
            self.assertIn(f'end_year={end}', self.db.lastQuery.split('&'))
        else:
            self.assertNotIn(f'end_year={end}', self.db.lastQuery.split('&'))
        self.db.clear()

        if start is not None:
            query.filterBy(start_year=None)
            with self.assertRaises(KeyError):
                query['start_year']

        if end is not None:
            query.filterBy(end_year=None)
            with self.assertRaises(KeyError):
                query['end_year']

        query.send()
        self.assertNotIn(f'start_year={start}', self.db.lastQuery.split('&'))
        self.assertNotIn(f'end_year={end}', self.db.lastQuery.split('&'))
        self.db.clear()

    def testFilterByInvalidYearRange(self):
        query = Query(self.db)
        with warnings.catch_warnings(record=True) as warns:
            query.filterBy(start_year=2019, end_year=2018)

            self.assertEqual(len(warns), 1)
            self.assertTrue(issubclass(warns[0].category, UserWarning))
            self.assertEqual(str(warns[0].message), "End year should be greater than start year")

        self.assertEqual(query['start_year'], 2019)
        self.assertNotIn('end_year', query)

        query.send()
        self.assertGreaterEqual(set(self.db.lastQuery.split('&')), {'start_year=2019'})
        self.db.clear()

    def testFilterByInvalidYearRangeStartBeforeEnd(self):
        query = Query(self.db)
        query.filterBy(start_year=2019)
        self.assertEqual(query['start_year'], 2019)
        with warnings.catch_warnings(record=True) as warns:
            query.filterBy(end_year=2018)

            self.assertEqual(len(warns), 1)
            self.assertTrue(issubclass(warns[0].category, UserWarning))
            self.assertEqual(str(warns[0].message), "End year should be greater than start year")
        self.assertNotIn('end_year', query)

        query.send()
        self.assertGreaterEqual(set(self.db.lastQuery.split('&')), {'start_year=2019'})
        self.db.clear()

    def testFilterByInvalidYearRangeEndBeforeStart(self):
        query = Query(self.db)
        query.filterBy(end_year=2018)
        self.assertEqual(query['end_year'], 2018)
        with warnings.catch_warnings(record=True) as warns:
            query.filterBy(start_year=2019)

            self.assertEqual(len(warns), 1)
            self.assertTrue(issubclass(warns[0].category, UserWarning))
            self.assertEqual(str(warns[0].message), "Start year should be smaller than end year")
        self.assertNotIn('start_year', query)

        query.send()
        self.assertGreaterEqual(set(self.db.lastQuery.split('&')), {'end_year=2018'})
        self.db.clear()

    def testFilterByOpenAccess(self):
        query = Query(self.db)
        query.filterBy(open_access=True)
        self.assertEqual(query['open_access'], True)

        query.send()
        self.assertGreaterEqual(set(self.db.lastQuery.split('&')), {'open_access=True'})
        self.db.clear()

        query.filterBy(open_access=None)
        self.assertNotIn('open_access', query)

        query.send()
        self.assertNotIn('open_access=True', self.db.lastQuery.split('&'))
        self.db.clear()

    @TestData([Query.Journals, Query.Conferences, Query.EarlyAccess, Query.Standards, Query.Books, Query.Courses])
    def testFilterByContentType(self, contentType):
        query = Query(self.db)
        query.filterBy(content_type=contentType)
        self.assertEqual(query['content_type'], contentType)

        query.send()
        self.assertGreaterEqual(set(self.db.lastQuery.split('&')), {f"content_type={str(contentType).replace(' ', '+')}"})
        self.db.clear()

        query.filterBy(content_type=None)
        self.assertNotIn('content_type', query)

        query.send()
        self.assertNotIn(f"content_type={str(contentType).replace(' ', '+')}", self.db.lastQuery.split('&'))
        self.db.clear()

    @TestData([Query.AlcatelLucent, Query.AGU, Query.BIAI, Query.CSEE, Query.IBM, Query.IEEE, Query.IET, Query.MITP, Query.MorganClaypool, Query.SMPTE, Query.TUP, Query.VDE])
    def testFilterByPublisher(self, publisher):
        query = Query(self.db)
        query.filterBy(publisher=publisher)
        self.assertEqual(query['publisher'], publisher)

        query.send()
        self.assertGreaterEqual(set(self.db.lastQuery.split('&')), {f"publisher={str(publisher).replace(' ', '+').replace('&', '%26')}"})
        self.db.clear()

        query.filterBy(publisher=None)
        self.assertNotIn('publisher', query)

        query.send()
        self.assertNotIn(f"publisher={str(publisher).replace(' ', '+').replace('&', '%26')}", self.db.lastQuery.split('&'))
        self.db.clear()

    @TestData([0, 1, 10, 100, 1000, 1000000])
    def testFilterByPublicationNumber(self, number):
        query = Query(self.db)
        query.filterBy(publication_number=number)
        self.assertEqual(query['publication_number'], number)

        query.send()
        self.assertGreaterEqual(set(self.db.lastQuery.split('&')), {f"publication_number={number}"})
        self.db.clear()

        query.filterBy(publication_number=None)
        self.assertNotIn('publication_number', query)

        query.send()
        self.assertNotIn(f"publication_number={number}", self.db.lastQuery.split('&'))
        self.db.clear()

    @TestData([
        {'field': 'article_number',    'order': Query.AscendingOrder },
        {'field': 'article_title',     'order': Query.AscendingOrder },
        {'field': 'author',            'order': Query.AscendingOrder },
        {'field': 'publication_title', 'order': Query.AscendingOrder },
        {'field': 'publication_year',  'order': Query.AscendingOrder },
        {'field': 'article_number',    'order': Query.DescendingOrder},
        {'field': 'article_title',     'order': Query.DescendingOrder},
        {'field': 'author',            'order': Query.DescendingOrder},
        {'field': 'publication_title', 'order': Query.DescendingOrder},
        {'field': 'publication_year',  'order': Query.DescendingOrder},
    ])
    def testSortKeywordArg(self, field, order):
        query = Query(self.db)
        kwArgs = {field: order}
        query.sortBy(**kwArgs)
        self.assertEqual(query['sort_field'], field)
        self.assertEqual(query['sort_order'], order)

        query.send()
        self.assertGreaterEqual(set(self.db.lastQuery.split('&')), {f"sort_field={field}", f"sort_order={order}"})
        self.db.clear()

        kwArgs = {field: None}
        query.sortBy(**kwArgs)
        self.assertNotIn('sort_field', query)
        self.assertNotIn('sort_order', query)

        query.send()
        self.assertNotIn(f"sort_field={field}", self.db.lastQuery.split('&'))
        self.assertNotIn(f"sort_order={order}", self.db.lastQuery.split('&'))
        self.db.clear()

    @TestData(['article_number', 'article_title', 'author', 'publication_title', 'publication_year'])
    def testSortStringArg(self, field):
        query = Query(self.db)
        args = (field,)
        query.sortBy(*args)
        self.assertEqual(query['sort_field'], field)
        self.assertEqual(query['sort_order'], Query.AscendingOrder)

        query.send()
        self.assertGreaterEqual(set(self.db.lastQuery.split('&')), {f"sort_field={field}", f"sort_order=asc"})
        self.db.clear()

        kwArgs = {field: None}
        query.sortBy(**kwArgs)
        self.assertNotIn('sort_field', query)
        self.assertNotIn('sort_order', query)

        query.send()
        self.assertNotIn(f"sort_field={field}", self.db.lastQuery.split('&'))
        self.assertNotIn(f"sort_order=asc", self.db.lastQuery.split('&'))
        self.db.clear()

    @TestData([1, 100, 200])
    def testLimit(self, limit):
        query = Query(self.db)
        query.limit(limit)
        self.assertEqual(query['max_records'], limit)

        query.send(1)
        self.assertGreaterEqual(set(self.db.lastQuery.split('&')), {f"max_records={limit}"})
        self.db.clear()

        query.limit(None)
        self.assertNotIn('max_records', query)

        query.send(1)
        self.assertNotIn(f"max_records={limit}", self.db.lastQuery.split('&'))
        self.db.clear()

    @TestData([201, 400])
    def testInvalidLimit(self, limit):
        query = Query(self.db)

        with warnings.catch_warnings(record=True) as warns:
            query.limit(limit)

            self.assertEqual(len(warns), 1)
            self.assertTrue(issubclass(warns[0].category, UserWarning))
            self.assertEqual(str(warns[0].message), f"Value \"{limit}\" is larger than maximum value 200")

        self.assertNotIn('max_records', query)

    def testSend(self):
        db = MockDatabase(total=400)
        query = Query(db)

        results = query.send()
        self.assertLessEqual(len(results), 200)
        self.assertGreaterEqual(set(db.lastQuery.split('&')), {f"start_record=1"})
        db.clear()

        results = query.send()
        self.assertLessEqual(len(results), 200)
        self.assertGreaterEqual(set(db.lastQuery.split('&')), {f"start_record=201"})
        db.clear()

    @TestData([1, 100, 200])
    def testSendLimit(self, limit):
        db = MockDatabase(total=2*limit)
        query = Query(db)
        query.limit(limit)

        results = query.send()
        self.assertLessEqual(len(results), limit)
        self.assertGreaterEqual(set(db.lastQuery.split('&')), {f"max_records={limit}", f"start_record=1"})
        db.clear()

        results = query.send()
        self.assertLessEqual(len(results), limit)
        self.assertGreaterEqual(set(db.lastQuery.split('&')), {f"max_records={limit}", f"start_record={limit + 1}"})
        db.clear()

class ResultSetTest(unittest.TestCase):
    @TestData([1, 100, 200])
    def testFetchAllAtOnce(self, limit):
        db = MockDatabase(total=limit)
        query = Query(db)
        query.limit(limit)

        results = query.send()
        self.assertEqual(len(results), limit)
        self.assertEqual([dict(result) for result in results], [{'article_number': i} for i in range(1, limit + 1)])

        with self.assertRaises(EOFError):
            results.fetchMore()
        self.assertEqual(len(results), limit)
        self.assertEqual([dict(result) for result in results], [{'article_number': i} for i in range(1, limit + 1)])

    @TestData([1, 100, 200])
    def testFetchTwice(self, limit):
        db = MockDatabase(total=2*limit)
        query = Query(db)
        query.limit(limit)

        results = query.send()
        self.assertEqual(len(results), limit)
        self.assertEqual([dict(result) for result in results], [{'article_number': i} for i in range(1, limit + 1)])

        results.fetchMore()
        self.assertEqual(len(results), 2*limit)
        self.assertEqual([dict(result) for result in results], [{'article_number': i} for i in range(1, 2*limit + 1)])

        with self.assertRaises(EOFError):
            results.fetchMore()
        self.assertEqual(len(results), 2*limit)
        self.assertEqual([dict(result) for result in results], [{'article_number': i} for i in range(1, 2*limit + 1)])

    @TestData([1, 100, 200])
    def testFetchAllOnce(self, limit):
        db = MockDatabase(total=limit)
        query = Query(db)
        query.limit(limit)

        results = query.send().complete(False)
        self.assertEqual(db.queryNumber, 2)
        self.assertEqual(len(results), limit)
        self.assertEqual([dict(result) for result in results], [{'article_number': i} for i in range(1, limit + 1)])

    @TestData([1, 100, 200])
    def testFetchAllTwice(self, limit):
        db = MockDatabase(total=2*limit)
        query = Query(db)
        query.limit(limit)

        results = query.send().complete(False)
        self.assertEqual(db.queryNumber, 3)
        self.assertEqual(len(results), 2*limit)
        self.assertEqual([dict(result) for result in results], [{'article_number': i} for i in range(1, 2*limit + 1)])

    @TestData([1, 100, 200])
    def testFetchAllLazyOnce(self, limit):
        db = MockDatabase(total=limit)
        query = Query(db)
        query.limit(limit)

        results = query.send().complete()
        self.assertEqual(db.queryNumber, 1)
        self.assertEqual(len(results), limit)
        self.assertEqual([dict(result) for result in results], [{'article_number': i} for i in range(1, limit + 1)])

    @TestData([1, 100, 200])
    def testFetchAllLazyTwice(self, limit):
        db = MockDatabase(total=2*limit)
        query = Query(db)
        query.limit(limit)

        results = query.send().complete()
        self.assertEqual(db.queryNumber, 1)
        self.assertEqual(len(results), 2*limit)
        self.assertEqual([dict(result) for result in results], [{'article_number': i} for i in range(1, 2*limit + 1)])

class ResultTest(unittest.TestCase):
    @TestData([
        {'name': "title",               'value': "Text"                 },
        {'name': "abstract",            'value': "Long text"            },
        {'name': "conference_location", 'value': "Text"                 },
        {'name': "publication_title",   'value': "Text"                 },
        {'name': "article_number",      'value': 123456789              },
        {'name': "rank",                'value': 18                     },
        {'name': "is_number",           'value': 123456789              },
        {'name': "publication_number",  'value': 123456789              },
        {'name': "standard_number",     'value': 123456789              },
        {'name': "publication_year",    'value': date.today().year      },
        {'name': "start_page",          'value': 18                     },
        {'name': "end_page",            'value': 36                     },
        {'name': "citing_paper_count",  'value': 18                     },
        {'name': "citing_patent_count", 'value': 18                     },
        {'name': "issue",               'value': 18                     },
        {'name': "volume",              'value': 18                     },
        {'name': "access_type",         'value': "LOCKED"               },
        {'name': "access_type",         'value': "OPEN ACCESS"          },
        {'name': "access_type",         'value': "EPHEMERA"             },
        {'name': "access_type",         'value': "PLAGARIZED"           },
        {'name': "abstract_url",        'value': "http://test.org"      },
        {'name': "abstract_url",        'value': "http://test.org/a.out"},
        {'name': "abstract_url",        'value': "test.org"             },
        {'name': "abstract_url",        'value': "test.org/file.txt"    },
        {'name': "abstract_url",        'value': "test.org:80"          },
        {'name': "abstract_url",        'value': "test.org:80/file.txt" },
        {'name': "html_url",            'value': "http://test.org"      },
        {'name': "html_url",            'value': "http://test.org/a.out"},
        {'name': "html_url",            'value': "test.org"             },
        {'name': "html_url",            'value': "test.org/file.txt"    },
        {'name': "html_url",            'value': "test.org:80"          },
        {'name': "html_url",            'value': "test.org:80/file.txt" },
        {'name': "pdf_url",             'value': "http://test.org"      },
        {'name': "pdf_url",             'value': "http://test.org/a.out"},
        {'name': "pdf_url",             'value': "test.org"             },
        {'name': "pdf_url",             'value': "test.org/file.txt"    },
        {'name': "pdf_url",             'value': "test.org:80"          },
        {'name': "pdf_url",             'value': "test.org:80/file.txt" },
        {'name': "isbn",                'value': "0-306-40615-2"        },
        {'name': "isbn",                'value': "978-0-306-40615-7"    },
        {'name': "issn",                'value': "0378-5955"            },
        {'name': "publisher",           'value': "Alcatel-Lucent"       },
        {'name': "publisher",           'value': "AGU"                  },
        {'name': "publisher",           'value': "BIAI"                 },
        {'name': "publisher",           'value': "CSEE"                 },
        {'name': "publisher",           'value': "IBM"                  },
        {'name': "publisher",           'value': "IEEE"                 },
        {'name': "publisher",           'value': "IET"                  },
        {'name': "publisher",           'value': "MITP"                 },
        {'name': "publisher",           'value': "Morgan & Claypool"    },
        {'name': "publisher",           'value': "SMPTE"                },
        {'name': "publisher",           'value': "TUP"                  },
        {'name': "publisher",           'value': "VDE"                  },
    ])
    def testConstructor(self, name, value):
        result = Result({name: value})
        self.assertIn(name, result)
        self.assertEqual(result[name], value)

    @TestData([
        {'name': "doi",                 'value': '11.1234/56789'        },
        {'name': "doi",                 'value': '11.abcd/suffix'       },
        {'name': "doi",                 'value': '10.123/56789'         },
        {'name': "doi",                 'value': '10.abc/suffix'        },
        {'name': "doi",                 'value': '10.12345/56789'       },
        {'name': "doi",                 'value': '10.abcde/suffix'      },
        {'name': "doi",                 'value': '10.123456789'         },
        {'name': "doi",                 'value': '10.abcdsuffix'        },
        {'name': "doi",                 'value': '10.1234.56789'        },
        {'name': "doi",                 'value': '10.abcd.suffix'       },
        {'name': "access_type",         'value': "OPEN"                 },
        {'name': "abstract_url",        'value': "http://"              },
        {'name': "author_url",          'value': "http://"              },
        {'name': "html_url",            'value': "http://"              },
        {'name': "pdf_url",             'value': "http://"              },
        {'name': "isbn",                'value': "0-306-40615-1"        },
        {'name': "isbn",                'value': "0-306-40615-3"        },
        {'name': "isbn",                'value': "978-0-306-40615-6"    },
        {'name': "isbn",                'value': "978-0-306-40615-8"    },
        {'name': "issn",                'value': "0378-5954"            },
        {'name': "issn",                'value': "0378-5956"            },
        {'name': "content_type",        'value': "Invalid"              },
        {'name': "publisher",           'value': "Invalid"              },
    ])
    def testConstructorInvalidValue(self, name, value):
        with warnings.catch_warnings(record=True) as warns:
            result = Result({name: value})

            self.assertEqual(len(warns), 1)
            self.assertTrue(issubclass(warns[0].category, UserWarning))
            self.assertEqual(str(warns[0].message), f"Invalid value for result field \"{name}\": {value}")

        self.assertNotIn(name, result)

    @TestData([
        {'name': "article_number",      'value': "Text"                 },
        {'name': "rank",                'value': "Text"                 },
        {'name': "is_number",           'value': "Text"                 },
        {'name': "publication_number",  'value': "Text"                 },
        {'name': "publication_year",    'value': "Text"                 },
        {'name': "start_page",          'value': "Text"                 },
        {'name': "end_page",            'value': "Text"                 },
        {'name': "citing_paper_count",  'value': "Text"                 },
        {'name': "citing_patent_count", 'value': "Text"                 },
        {'name': "volume",              'value': "Text"                 },
    ])
    def testConstructorInvalidType(self, name, value):
        with warnings.catch_warnings(record=True) as warns:
            result = Result({name: value})

            self.assertEqual(len(warns), 1)
            self.assertTrue(issubclass(warns[0].category, UserWarning))
            self.assertEqual(str(warns[0].message), f"Value for result field \"{name}\" has bad type: {value}")

        self.assertNotIn(name, result)

    @TestData([
        {'name': "article_number",      'value': -1                     },
        {'name': "rank",                'value': 0                      },
        {'name': "is_number",           'value': -1                     },
        {'name': "publication_number",  'value': -1                     },
        {'name': "standard_number",     'value': -1                     },
        {'name': "start_page",          'value': 0                      },
        {'name': "end_page",            'value': 0                      },
        {'name': "citing_paper_count",  'value': -1                     },
        {'name': "citing_patent_count", 'value': -1                     },
        {'name': "issue",               'value': 0                      },
        {'name': "volume",              'value': 0                      },
    ])
    def testConstructorTooSmallValue(self, name, value):
        with warnings.catch_warnings(record=True) as warns:
            result = Result({name: value})

            self.assertEqual(len(warns), 1)
            self.assertTrue(issubclass(warns[0].category, UserWarning))
            self.assertEqual(str(warns[0].message), f"Too small value for result field \"{name}\": {value}")

        self.assertNotIn(name, result)

    @TestData([
        {'name': "publication_year",    'value': date.today().year + 1  },
    ])
    def testConstructorTooLargeValue(self, name, value):
        with warnings.catch_warnings(record=True) as warns:
            result = Result({name: value})

            self.assertEqual(len(warns), 1)
            self.assertTrue(issubclass(warns[0].category, UserWarning))
            self.assertEqual(str(warns[0].message), f"Too large value for result field \"{name}\": {value}")

        self.assertNotIn(name, result)

    @TestData([
        {'value': "Journals"        , 'bibType': 'article'      },
        {'value': "Conferences"     , 'bibType': 'inproceedings'},
        {'value': "Early Access"    , 'bibType': 'unpublished'  },
        {'value': "Standards"       , 'bibType': 'booklet'      },
        {'value': "Books"           , 'bibType': 'book'         },
        {'value': "Courses"         , 'bibType': 'misc'         },
    ])
    def testContentType(self, value, bibType):
        result = Result({'content_type': value})
        self.assertIn('content_type', result)
        self.assertEqual(result['content_type'], bibType)

    @TestData([
        {'value': '10.1234/56789',  'prefix': '10.1234', 'suffix': '56789'},
        {'value': '10.abcd/suffix', 'prefix': '10.abcd', 'suffix': 'suffix'},
        {'value': '10.1234/suffix', 'prefix': '10.1234', 'suffix': 'suffix'},
        {'value': '10.abcd/56789',  'prefix': '10.abcd', 'suffix': '56789'},
    ])
    def testDOI(self, value, prefix, suffix):
        result = Result({'doi': value})
        self.assertIn('doi', result)
        self.assertEqual(result['doi'].prefix, prefix)
        self.assertEqual(result['doi'].suffix, suffix)

    @TestData([
        {'indexTerms': {
            "ieee_terms": {
                "terms": ["Torque", "Rotors", "Equations", "Stator windings", "Computational modeling", "Permanent magnet motors", "Reluctance motors"]
            }
        }, 'terms': {"Torque", "Rotors", "Equations", "Stator windings", "Computational modeling", "Permanent magnet motors", "Reluctance motors"}, 'sources': ['ieee']},
        {'indexTerms': {
            "ieee_terms": {
                "terms": ["Saturation magnetization", "Rotors", "Current measurement", "Torque", "Magnetic analysis", "Reluctance motors", "Stators"]
            },
            "author_terms": {
                "terms": ["Modeling",  "Identification", "Saturation", "Synchronous Reluctance Motor", "Signal injection"]
            }
        }, 'terms': {"Modeling",  "Identification", "Saturation", "Synchronous Reluctance Motor", "Signal injection", "Saturation magnetization", "Rotors", "Current measurement", "Torque", "Magnetic analysis", "Reluctance motors", "Stators"}, 'sources': ['ieee', 'author']},
    ])
    def testIndexTerms(self, indexTerms, terms, sources):
        result = Result({'index_terms': indexTerms})
        self.assertIn('index_terms', result)
        self.assertEqual(len(result['index_terms']), len(terms))
        self.assertSetEqual(set(result['index_terms']), terms)

        for s in sources:
            self.assertIn(s, result['index_terms'])
            self.assertEqual(result['index_terms'][s], indexTerms[s + '_terms']['terms'])

    @TestData([
        {
            'authors': {
                "authors": [
                    {
                        "affiliation": "Affiliation 1",
                        "authorUrl": "https://ieeexplore.ieee.org/author/123456789",
                        "id": 123456789,
                        "full_name": "Author 1",
                        "author_order": 1
                    },
                    {
                        "affiliation": "Affilation 2, Pays",
                        "authorUrl": "https://ieeexplore.ieee.org/author/987654321",
                        "id": 987654321,
                        "full_name": "Author 2",
                        "author_order": 2
                    },
                ]
            },
            'names': ["1", "2"],
            'forenames': [["Author"], ["Author"]],
        },
        {
            "authors": {
                "authors": [
                    {
                        "full_name": "Author1 name1",
                        "author_order": 1
                    },
                    {
                        "full_name": "Author2 name2",
                        "author_order": 2
                    }
                ]
            },
            'names': ["name1", "name2"],
            'forenames': [["Author1"], ["Author2"]],
        },
    ])
    def testAuthors(self, authors, names, forenames):
        result = Result({'authors': authors})
        self.assertEqual(len(result['authors']), len(authors['authors']))
        for author, expected in zip(result['authors'], authors['authors']):
            for k, v in author:
                self.assertIn(k, expected)
                self.assertEqual(v, expected[k])
            for k, v in expected.items():
                self.assertIn(k, author)
                self.assertEqual(author[k], v)
        for author, expectedName in zip(result['authors'], names):
            self.assertEqual(author['name'], expectedName)
        for author, expectedForenames in zip(result['authors'], forenames):
            self.assertEqual(author['forenames'], expectedForenames)

    @TestData([
        {'name': 'conference_dates', 'value': '11 Mar. 1989',               'begin': date(1989, 3, 11), 'end': date(1989, 3, 11)},
        {'name': 'conference_dates', 'value': '10-12 Mar. 1989',            'begin': date(1989, 3, 10), 'end': date(1989, 3, 12)},
        {'name': 'conference_dates', 'value': '10 Feb.-12 Apr. 1989',       'begin': date(1989, 2, 10), 'end': date(1989, 4, 12)},
        {'name': 'conference_dates', 'value': '10 Feb. 1988-12 Apr. 1990',  'begin': date(1988, 2, 10), 'end': date(1990, 4, 12)},
        {'name': 'publication_date', 'value': '11 Mar. 1989',               'begin': date(1989, 3, 11), 'end': date(1989, 3, 11)},
        {'name': 'publication_date', 'value': '10-12 Mar. 1989',            'begin': date(1989, 3, 10), 'end': date(1989, 3, 12)},
        {'name': 'publication_date', 'value': '10 Feb.-12 Apr. 1989',       'begin': date(1989, 2, 10), 'end': date(1989, 4, 12)},
        {'name': 'publication_date', 'value': '10 Feb. 1988-12 Apr. 1990',  'begin': date(1988, 2, 10), 'end': date(1990, 4, 12)},
    ])
    def testDates(self, name, value, begin, end):
        result = Result({name: value})
        self.assertIn(name, result)
        self.assertEqual(result[name].begin, begin)
        self.assertEqual(result[name].end, end)


    @TestData([
        {'name': 'conference_dates', 'value': '0 Mar. 1989' },
        {'name': 'conference_dates', 'value': '11 Juny 1989'},
        {'name': 'conference_dates', 'value': '11 May. 1989'},
        {'name': 'conference_dates', 'value': '32 Mar. 1989'},

        {'name': 'publication_date', 'value': '0 Mar. 1989' },
        {'name': 'publication_date', 'value': '11 Juny 1989'},
        {'name': 'publication_date', 'value': '11 May. 1989'},
        {'name': 'publication_date', 'value': '32 Mar. 1989'},
    ])
    def testInvalidDates(self, name, value):
        with warnings.catch_warnings(record=True) as warns:
            result = Result({name: value})

            self.assertEqual(len(warns), 1)
            self.assertTrue(issubclass(warns[0].category, UserWarning))
            self.assertEqual(str(warns[0].message), f"Value for result field \"{name}\" has bad type: {value}")

        self.assertNotIn(name, result)

if __name__ == '__main__':
    unittest.main(verbosity=2)
