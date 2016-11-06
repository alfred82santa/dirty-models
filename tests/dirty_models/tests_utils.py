from datetime import datetime, date, timedelta
from enum import Enum
from json import dumps, loads
from unittest.case import TestCase

from dirty_models.fields import StringIdField, IntegerField, DateTimeField, ArrayField, MultiTypeField, ModelField, \
    HashMapField, DateField, TimedeltaField, EnumField
from dirty_models.models import BaseModel, DynamicModel, FastDynamicModel
from dirty_models.utils import underscore_to_camel, ModelFormatterIter, ListFormatterIter, JSONEncoder


class UnderscoreToCamelTests(TestCase):

    def test_no_underscore(self):
        self.assertEqual(underscore_to_camel('foobar'), 'foobar')

    def test_underscore(self):
        self.assertEqual(underscore_to_camel('foo_bar'), 'fooBar')

    def test_underscore_multi(self):
        self.assertEqual(underscore_to_camel('foo_bar_tor_pir'), 'fooBarTorPir')

    def test_underscore_number(self):
        self.assertEqual(underscore_to_camel('foo_bar_1'), 'fooBar_1')

    def test_underscore_multi_number(self):
        self.assertEqual(underscore_to_camel('foo_bar_tor_pir_1'), 'fooBarTorPir_1')


class TestModel(BaseModel):

    class TestEnum(Enum):
        value_1 = 1
        value_2 = '2'
        value_3 = date(year=2015, month=7, day=30)

    test_string_field_1 = StringIdField(name='other_field')
    test_int_field_1 = IntegerField()
    test_datetime = DateTimeField(parse_format="%Y-%m-%dT%H:%M:%S")
    test_array_datetime = ArrayField(field_type=DateTimeField(parse_format="%Y-%m-%dT%H:%M:%S"))
    test_array_multitype = ArrayField(field_type=MultiTypeField(field_types=[IntegerField(),
                                                                             DateTimeField(
                                                                                 parse_format="%Y-%m-%dT%H:%M:%S"
    )]))
    test_model_field_1 = ArrayField(field_type=ArrayField(field_type=ModelField()))
    test_hash_map = HashMapField(field_type=DateField(parse_format="%Y-%m-%d date"))
    test_timedelta = TimedeltaField()
    test_enum = EnumField(enum_class=TestEnum)
    test_multi_field = MultiTypeField(field_types=[IntegerField(),
                                                   DateField(parse_format="%Y-%m-%d multi date")])


class ModelFormatterIterTests(TestCase):

    def test_model_formatter(self):
        model = TestModel(data={'test_string_field_1': 'foo',
                                'test_int_field_1': 4,
                                'test_datetime': datetime(year=2016, month=5, day=30,
                                                          hour=22, minute=22, second=22),
                                'test_array_datetime': [datetime(year=2015, month=5, day=30,
                                                                 hour=22, minute=22, second=22),
                                                        datetime(year=2015, month=6, day=30,
                                                                 hour=22, minute=22, second=22)],
                                'test_array_multitype': [datetime(year=2015, month=5, day=30,
                                                                  hour=22, minute=22, second=22),
                                                         4, 5],
                                'test_model_field_1': [[{'test_datetime': datetime(year=2015, month=7, day=30,
                                                                                   hour=22, minute=22, second=22)}]],
                                'test_hash_map': {'foo': date(year=2015, month=7, day=30)},
                                'test_timedelta': timedelta(seconds=32.1122),
                                'test_enum': TestModel.TestEnum.value_3,
                                'test_multi_field': date(year=2015, month=7, day=30)})

        formatter = ModelFormatterIter(model)
        data = {k: v for k, v in formatter}
        self.assertEqual(data['other_field'], 'foo')
        self.assertEqual(data['test_int_field_1'], 4)
        self.assertEqual(data['test_datetime'], '2016-05-30T22:22:22')
        self.assertIsInstance(data['test_array_datetime'], ListFormatterIter)
        self.assertEqual(list(data['test_array_datetime']), ['2015-05-30T22:22:22', '2015-06-30T22:22:22'])
        self.assertIsInstance(data['test_array_multitype'], ListFormatterIter)
        self.assertEqual(list(data['test_array_multitype']), ['2015-05-30T22:22:22', 4, 5])
        self.assertIsInstance(data['test_model_field_1'], ListFormatterIter)
        self.assertIsInstance(list(data['test_model_field_1'])[0], ListFormatterIter)
        self.assertEqual({k: v for k, v in list(list(data['test_model_field_1'])[0])[0]},
                         {'test_datetime': '2015-07-30T22:22:22'})
        self.assertIsInstance(data['test_hash_map'], ModelFormatterIter)
        self.assertEqual({k: v for k, v in data['test_hash_map']}, {'foo': '2015-07-30 date'})
        self.assertEqual(data['test_timedelta'], 32.1122)
        self.assertEqual(data['test_enum'], str(date(year=2015, month=7, day=30)))
        self.assertEqual(data['test_multi_field'], '2015-07-30 multi date')

    def test_dynamic_model_formatter(self):
        model = DynamicModel(data={'test_string_field_1': 'foo',
                                   'test_int_field_1': 4,
                                   'test_datetime': datetime(year=2016, month=5, day=30,
                                                             hour=22, minute=22, second=22),
                                   'test_array_datetime': [datetime(year=2015, month=5, day=30,
                                                                    hour=22, minute=22, second=22),
                                                           datetime(year=2015, month=6, day=30,
                                                                    hour=22, minute=22, second=22)],
                                   'test_model_field_1': [[{'test_datetime': datetime(year=2015, month=7, day=30,
                                                                                      hour=22, minute=22, second=22)}]],
                                   'test_hash_map': {'foo': date(year=2015, month=7, day=30)},
                                   'test_timedelta': timedelta(seconds=32.1122),
                                   'test_enum': TestModel.TestEnum.value_1,
                                   'test_multi_field': date(year=2015, month=7, day=30)})

        formatter = ModelFormatterIter(model)
        data = {k: v for k, v in formatter}
        print(data)
        self.assertEqual(data['test_int_field_1'], 4)
        self.assertEqual(data['test_datetime'], '2016-05-30 22:22:22')
        self.assertIsInstance(data['test_array_datetime'], ListFormatterIter)
        self.assertEqual(list(data['test_array_datetime']), ['2015-05-30 22:22:22', '2015-06-30 22:22:22'])
        self.assertIsInstance(data['test_model_field_1'], ListFormatterIter)
        self.assertIsInstance(list(data['test_model_field_1'])[0], ListFormatterIter)
        self.assertEqual({k: v for k, v in list(list(data['test_model_field_1'])[0])[0]},
                         {'test_datetime': '2015-07-30 22:22:22'})
        self.assertIsInstance(data['test_hash_map'], ModelFormatterIter)
        self.assertEqual({k: v for k, v in data['test_hash_map']}, {'foo': '2015-07-30'})
        self.assertEqual(data['test_timedelta'], 32.1122)

    def test_fast_dynamic_model_formatter(self):
        model = FastDynamicModel(data={'test_string_field_1': 'foo',
                                       'test_int_field_1': 4,
                                       'test_datetime': datetime(year=2016, month=5, day=30,
                                                                 hour=22, minute=22, second=22),
                                       'test_array_datetime': [datetime(year=2015, month=5, day=30,
                                                                        hour=22, minute=22, second=22),
                                                               datetime(year=2015, month=6, day=30,
                                                                        hour=22, minute=22, second=22)],
                                       'test_model_field_1': [[{'test_datetime': datetime(year=2015, month=7, day=30,
                                                                                          hour=22, minute=22,
                                                                                          second=22)}]],
                                       'test_hash_map': {'foo': date(year=2015, month=7, day=30)},
                                       'test_timedelta': timedelta(seconds=32.1122),
                                       'test_enum': TestModel.TestEnum.value_1,
                                       'test_multi_field': date(year=2015, month=7, day=30)})

        formatter = ModelFormatterIter(model)
        data = {k: v for k, v in formatter}
        self.assertEqual(data['test_int_field_1'], 4)
        self.assertEqual(data['test_datetime'], '2016-05-30 22:22:22')
        self.assertIsInstance(data['test_array_datetime'], ListFormatterIter)
        self.assertEqual(list(data['test_array_datetime']), ['2015-05-30 22:22:22', '2015-06-30 22:22:22'])
        self.assertIsInstance(data['test_model_field_1'], ListFormatterIter)
        self.assertIsInstance(list(data['test_model_field_1'])[0], ListFormatterIter)
        self.assertEqual({k: v for k, v in list(list(data['test_model_field_1'])[0])[0]},
                         {'test_datetime': '2015-07-30 22:22:22'})
        self.assertIsInstance(data['test_hash_map'], ModelFormatterIter)
        self.assertEqual({k: v for k, v in data['test_hash_map']}, {'foo': '2015-07-30'})
        self.assertEqual(data['test_timedelta'], 32.1122)
        self.assertEqual(data['test_multi_field'], '2015-07-30')


class JSONEncoderTests(TestCase):

    def test_model_json(self):
        model = TestModel(data={'test_string_field_1': 'foo',
                                'test_int_field_1': 4,
                                'test_datetime': datetime(year=2016, month=5, day=30,
                                                          hour=22, minute=22, second=22),
                                'test_array_datetime': [datetime(year=2015, month=5, day=30,
                                                                 hour=22, minute=22, second=22),
                                                        datetime(year=2015, month=6, day=30,
                                                                 hour=22, minute=22, second=22)],
                                'test_array_multitype': [datetime(year=2015, month=5, day=30,
                                                                  hour=22, minute=22, second=22),
                                                         4, 5],
                                'test_model_field_1': [[{'test_datetime': datetime(year=2015, month=7, day=30,
                                                                                   hour=22, minute=22, second=22)}]],
                                'test_hash_map': {'foo': date(year=2015, month=7, day=30)},
                                'test_timedelta': timedelta(seconds=32.1122),
                                'test_enum': TestModel.TestEnum.value_1,
                                'test_multi_field': date(year=2015, month=7, day=30)})

        json_str = dumps(model, cls=JSONEncoder)

        data = {'other_field': 'foo',
                'test_int_field_1': 4,
                'test_datetime': '2016-05-30T22:22:22',
                'test_array_datetime': ['2015-05-30T22:22:22',
                                        '2015-06-30T22:22:22'],
                'test_array_multitype': ['2015-05-30T22:22:22', 4, 5],
                'test_model_field_1': [[{'test_datetime': '2015-07-30T22:22:22'}]],
                'test_hash_map': {'foo': '2015-07-30 date'},
                'test_timedelta': 32.1122,
                'test_enum': 1,
                'test_multi_field': '2015-07-30 multi date'}

        self.assertEqual(loads(json_str), data)

    def test_general_use_json(self):
        data = {'foo': 3, 'bar': 'str'}
        json_str = dumps(data, cls=JSONEncoder)
        self.assertEqual(loads(json_str), data)
