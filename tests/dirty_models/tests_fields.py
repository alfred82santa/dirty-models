from datetime import time, date, datetime, timezone, timedelta
from unittest import TestCase

import iso8601
from dateutil import tz

from dirty_models.fields import (IntegerField, StringField, BooleanField,
                                 FloatField, ModelField, TimeField, DateField,
                                 DateTimeField, ArrayField, StringIdField, HashMapField, MultiTypeField, TimedeltaField)
from dirty_models.model_types import ListModel
from dirty_models.models import BaseModel, HashMapModel


class TestFields(TestCase):

    def test_int_field_using_int(self):
        field = IntegerField()
        self.assertTrue(field.check_value(3))
        self.assertEqual(field.use_value(3), 3)

    def test_int_field_desc(self):
        field = IntegerField()
        self.assertEqual(field.export_definition(), {'alias': None,
                                                     'doc': 'IntegerField field',
                                                     'name': None,
                                                     'read_only': False})

    def test_int_field_using_float(self):
        field = IntegerField()
        self.assertFalse(field.check_value(3.0))
        self.assertTrue(field.can_use_value(3.0))
        self.assertEqual(field.use_value(3.0), 3)

    def test_int_field_using_str(self):
        field = IntegerField()
        self.assertFalse(field.check_value("3"))
        self.assertTrue(field.can_use_value("3"))
        self.assertEqual(field.use_value("3"), 3)

    def test_int_field_using_dict(self):
        field = IntegerField()
        self.assertFalse(field.check_value({}))
        self.assertFalse(field.can_use_value({}))

    def test_float_field_using_int(self):
        field = FloatField()
        self.assertFalse(field.check_value(3))
        self.assertTrue(field.can_use_value(3))
        self.assertEqual(field.use_value(3), 3)

    def test_float_field_using_float(self):
        field = FloatField()
        self.assertTrue(field.check_value(3.0))
        self.assertEqual(field.use_value(3.0), 3.0)

    def test_float_field_using_str(self):
        field = FloatField()
        self.assertFalse(field.check_value("3.0"))
        self.assertTrue(field.can_use_value("3.0"))
        self.assertEqual(field.use_value("3.0"), 3.0)

    def test_float_field_using_dict(self):
        field = FloatField()
        self.assertFalse(field.check_value({}))
        self.assertFalse(field.can_use_value({}))

    def test_str_field_using_int(self):
        field = StringField()
        self.assertFalse(field.check_value(3))
        self.assertTrue(field.can_use_value(3))
        self.assertEqual(field.use_value(3), "3")

    def test_str_field_using_float(self):
        field = StringField()
        self.assertFalse(field.check_value(3.0))
        self.assertTrue(field.can_use_value(3.0))
        self.assertEqual(field.use_value(3.0), "3.0")

    def test_str_field_using_str(self):
        field = StringField()
        self.assertTrue(field.check_value("aaasa"))
        self.assertEqual(field.use_value("aaasa"), "aaasa")

    def test_str_field_using_dict(self):
        field = StringField()
        self.assertFalse(field.check_value({}))
        self.assertFalse(field.can_use_value({}))

    def test_bool_field_using_int_any(self):
        field = BooleanField()
        self.assertFalse(field.check_value(3))
        self.assertTrue(field.can_use_value(3))
        self.assertTrue(field.use_value(3))

    def test_bool_field_using_int_0(self):
        field = BooleanField()
        self.assertFalse(field.check_value(0))
        self.assertTrue(field.can_use_value(9))
        self.assertFalse(field.use_value(0))

    def test_bool_field_using_float(self):
        field = BooleanField()
        self.assertFalse(field.check_value(3.0))
        self.assertFalse(field.can_use_value(3.0))

    def test_bool_field_using_str_true(self):
        field = BooleanField()
        self.assertFalse(field.check_value("TrUe "))
        self.assertTrue(field.can_use_value("TrUe "))
        self.assertTrue(field.use_value("TrUe "))

    def test_bool_field_using_str_false(self):
        field = BooleanField()
        self.assertFalse(field.check_value("False"))
        self.assertTrue(field.can_use_value("False"))
        self.assertFalse(field.use_value("False"))

    def test_bool_field_using_str_any(self):
        field = BooleanField()
        self.assertFalse(field.check_value("aaasa"))
        self.assertTrue(field.can_use_value("aaasa"))
        self.assertFalse(field.use_value("aaasa"))

    def test_bool_field_using_dict(self):
        field = BooleanField()
        self.assertFalse(field.check_value({}))
        self.assertFalse(field.can_use_value({}))

    def test_bool_field_using_bool_true(self):
        field = BooleanField()
        self.assertTrue(field.check_value(True))
        self.assertTrue(field.use_value(True))

    def test_bool_field_using_bool_false(self):
        field = BooleanField()
        self.assertTrue(field.check_value(False))
        self.assertFalse(field.use_value(False))

    def test_int_field_on_class_using_int(self):
        class TestModel(BaseModel):
            field_name = IntegerField()

        model = TestModel()
        model.field_name = 3
        self.assertEqual(model.field_name, 3)

    def test_string_field_on_class_using_empty_string(self):
        class TestModel(BaseModel):
            field_name = StringField()

        model = TestModel()
        model.field_name = ""
        self.assertEqual(model.field_name, "")

    def test_string_id_field_on_class_using_string(self):
        class TestModel(BaseModel):
            field_name = StringIdField()

        model = TestModel()
        model.field_name = "id"
        self.assertIsNotNone(model.field_name)

    def test_string_id_field_on_class_using_number(self):
        class TestModel(BaseModel):
            field_name = StringIdField()

        model = TestModel()
        model.field_name = 1
        self.assertIsNotNone(model.field_name)

    def test_string_id_field_on_class_using_empty_string(self):
        class TestModel(BaseModel):
            field_name = StringIdField()

        model = TestModel()
        model.field_name = ""
        self.assertIsNone(model.field_name)

    def test_string_id_field_on_class_using_empty_string_and_delete_value(self):
        class TestModel(BaseModel):
            field_name = StringIdField()

        model = TestModel()
        model.field_name = "name"
        model.field_name = ""
        self.assertIsNone(model.field_name)

    def test_int_field_on_class_using_float(self):
        class TestModel(BaseModel):
            field_name = IntegerField()

        model = TestModel()
        model.field_name = 3.0
        self.assertEqual(model.field_name, 3)

    def test_int_field_on_class_using_str(self):
        class TestModel(BaseModel):
            field_name = IntegerField()

        model = TestModel()
        model.field_name = "3"
        self.assertEqual(model.field_name, 3)

    def test_int_field_on_class_using_dict(self):
        class TestModel(BaseModel):
            field_name = IntegerField()

        model = TestModel()
        model.field_name = {}
        self.assertIsNone(model.field_name)

    def test_float_field_on_class_using_int(self):
        class TestModel(BaseModel):
            field_name = FloatField()

        model = TestModel()
        model.field_name = 3
        self.assertEqual(model.field_name, 3.0)

    def test_float_field_on_class_using_float(self):
        class TestModel(BaseModel):
            field_name = FloatField()

        model = TestModel()
        model.field_name = 3.0
        self.assertEqual(model.field_name, 3.0)

    def test_float_field_on_class_using_str(self):
        class TestModel(BaseModel):
            field_name = FloatField()

        model = TestModel()
        model.field_name = "3.0"
        self.assertEqual(model.field_name, 3.0)

    def test_float_field_on_class_using_dict(self):
        class TestModel(BaseModel):
            field_name = FloatField()

        model = TestModel()
        model.field_name = {}
        self.assertIsNone(model.field_name)

    def test_str_field_on_class_using_int(self):
        class TestModel(BaseModel):
            field_name = StringField()

        model = TestModel()
        model.field_name = 3
        self.assertEqual(model.field_name, "3")

    def test_str_field_on_class_using_float(self):
        class TestModel(BaseModel):
            field_name = StringField()

        model = TestModel()
        model.field_name = 3.0
        self.assertEqual(model.field_name, "3.0")

    def test_str_field_on_class_using_str(self):
        class TestModel(BaseModel):
            field_name = StringField()

        model = TestModel()
        model.field_name = "aaaaa"
        self.assertEqual(model.field_name, "aaaaa")

    def test_str_field_on_class_using_dict(self):
        class TestModel(BaseModel):
            field_name = StringField()

        model = TestModel()
        model.field_name = {}
        self.assertIsNone(model.field_name)

    def test_bool_field_on_class_using_int_true(self):
        class TestModel(BaseModel):
            field_name = BooleanField()

        model = TestModel()
        model.field_name = 3
        self.assertTrue(model.field_name)

    def test_bool_field_on_class_using_int_false(self):
        class TestModel(BaseModel):
            field_name = BooleanField()

        model = TestModel()
        model.field_name = 0
        self.assertFalse(model.field_name)

    def test_bool_field_on_class_using_float(self):
        class TestModel(BaseModel):
            field_name = BooleanField()

        model = TestModel()
        model.field_name = 3.0
        self.assertIsNone(model.field_name)

    def test_bool_field_on_class_using_str_any(self):
        class TestModel(BaseModel):
            field_name = BooleanField()

        model = TestModel()
        model.field_name = "aaaaa"
        self.assertFalse(model.field_name)

    def test_bool_field_on_class_using_str_false(self):
        class TestModel(BaseModel):
            field_name = BooleanField()

        model = TestModel()
        model.field_name = "False"
        self.assertFalse(model.field_name)

    def test_bool_field_on_class_using_str_true(self):
        class TestModel(BaseModel):
            field_name = BooleanField()

        model = TestModel()
        model.field_name = "   tRuE  "
        self.assertTrue(model.field_name)

    def test_bool_field_on_class_using_dict(self):
        class TestModel(BaseModel):
            field_name = BooleanField()

        model = TestModel()
        model.field_name = {}
        self.assertIsNone(model.field_name)

    def test_int_field_delete_value(self):
        class TestModel(BaseModel):
            field_name = IntegerField()

        model = TestModel()
        model.field_name = 3
        self.assertEqual(model.field_name, 3)

        del model.field_name
        self.assertIsNone(model.field_name)

        # Check field descriptor exists
        model.field_name = "3"
        self.assertEqual(model.field_name, 3)

    def test_int_field_bad_definition(self):
        class TestModel():
            field_name = IntegerField()

        model = TestModel()

        with self.assertRaisesRegexp(AttributeError, "Field name must be set"):
            model.field_name = 3

        with self.assertRaisesRegexp(AttributeError, "Field name must be set"):
            model.field_name

        with self.assertRaisesRegexp(AttributeError, "Field name must be set"):
            del model.field_name

    def test_model_field_on_class_using_int(self):
        class TestModel(BaseModel):
            field_name = ModelField()

        model = TestModel()
        model.field_name = 3
        self.assertIsNone(model.field_name)

    def test_model_field_on_class_using_float(self):
        class TestModel(BaseModel):
            field_name = ModelField()

        model = TestModel()
        model.field_name = 3.0
        self.assertIsNone(model.field_name)

    def test_model_field_on_class_using_str(self):
        class TestModel(BaseModel):
            field_name = ModelField()

        model = TestModel()
        model.field_name = "aaaaa"
        self.assertIsNone(model.field_name)

    def test_model_field_on_class_using_dict(self):
        class TestModel(BaseModel):
            field_name_1 = ModelField()
            field_name_2 = StringField()

        model = TestModel()
        model.field_name_1 = {"field_name_2": "ooo"}
        self.assertIsInstance(model.field_name_1, TestModel)
        self.assertEqual(model.field_name_1.field_name_2, "ooo")

    def test_model_field_import_parent(self):
        class TestModel(BaseModel):
            field_name_1 = ModelField()
            field_name_2 = StringField()

        model = TestModel({"field_name_1": {"field_name_2": "eee"},
                           "field_name_2": "ooo"})

        self.assertIsInstance(model.field_name_1, TestModel)
        self.assertEqual(model.field_name_2, "ooo")
        self.assertEqual(model.field_name_1.field_name_2, "eee")

    def test_model_field_on_class_using_model_with_original_data(self):
        class TestModel(BaseModel):
            field_name_1 = ModelField()
            field_name_2 = StringField()

        model = TestModel({"field_name_1": {"field_name_2": "eee"},
                           "field_name_2": "ooo"})

        model.flat_data()
        model.field_name_1 = TestModel({"field_name_2": "aaa"})
        self.assertIsInstance(model.field_name_1, TestModel)
        self.assertEqual(model.field_name_2, "ooo")
        self.assertEqual(model.field_name_1.field_name_2, "aaa")

    def test_model_field_on_class_using_dict_with_original_data(self):
        class TestModel(BaseModel):
            field_name_1 = ModelField()
            field_name_2 = StringField()

        model = TestModel({"field_name_1": {"field_name_2": "eee"},
                           "field_name_2": "ooo"})

        model.flat_data()
        model.field_name_1 = {"field_name_2": "aaa"}
        self.assertIsInstance(model.field_name_1, TestModel)
        self.assertEqual(model.field_name_2, "ooo")
        self.assertEqual(model.field_name_1.field_name_2, "aaa")

    def test_model_field_bad_definition(self):
        class TestModel():
            field_name = ModelField()

        model = TestModel()

        with self.assertRaisesRegexp(AttributeError, "Field name must be set"):
            model.field_name = {}

    def test_time_field_using_int(self):
        field = TimeField()
        self.assertFalse(field.check_value(3333))
        self.assertTrue(field.can_use_value(3333))
        self.assertEqual(field.use_value(3333),
                         datetime(year=1970, month=1,
                                  day=1, hour=0, minute=55,
                                  second=33, tzinfo=timezone.utc).astimezone()
                         .time())

    def test_time_field_desc(self):
        field = TimeField()
        self.assertEqual(field.export_definition(), {'alias': None,
                                                     'doc': 'TimeField field',
                                                     'parse_format': None,
                                                     'name': None,
                                                     'read_only': False})

    def test_time_field_using_float(self):
        field = TimeField()
        self.assertFalse(field.check_value(3.0))
        self.assertFalse(field.can_use_value(3.0))
        self.assertIsNone(field.use_value(3.0))

    def test_time_field_using_str(self):
        field = TimeField(parse_format="%H:%M:%S")
        self.assertFalse(field.check_value("03:13:23"))
        self.assertTrue(field.can_use_value("03:13:23"))
        self.assertEqual(field.use_value("03:13:23"),
                         time(hour=3, minute=13, second=23))

    def test_time_field_desc_w_format(self):
        field = TimeField(parse_format="%H:%M:%S")
        self.assertEqual(field.export_definition(), {'alias': None,
                                                     'doc': 'TimeField field',
                                                     'parse_format': "%H:%M:%S",
                                                     'name': None,
                                                     'read_only': False})

    def test_time_field_using_bad_str(self):
        field = TimeField(parse_format="%H:%M:%S")
        self.assertIsNone(field.use_value("03:13:2334"))

    def test_time_field_using_str_no_parse_format(self):
        field = TimeField()
        self.assertFalse(field.check_value("03:13:23"))
        self.assertTrue(field.can_use_value("03:13:23"))
        self.assertEqual(field.use_value("03:13:23"),
                         time(hour=3, minute=13, second=23))

    def test_time_field_using_list(self):
        field = TimeField()
        self.assertFalse(field.check_value([3, 13, 23]))
        self.assertTrue(field.can_use_value([3, 13, 23]))
        self.assertEqual(field.use_value([3, 13, 23]),
                         time(hour=3, minute=13, second=23))

    def test_time_field_using_dict(self):
        field = TimeField()
        self.assertFalse(field.check_value({"hour": 3, "minute": 13, "second": 23}))
        self.assertTrue(field.can_use_value({"hour": 3, "minute": 13, "second": 23}))
        self.assertEqual(field.use_value({"hour": 3, "minute": 13, "second": 23}),
                         time(hour=3, minute=13, second=23))

    def test_time_field_using_datetime(self):
        field = TimeField()
        dt = datetime(year=1970, month=1, day=1, hour=3, minute=13, second=23)
        self.assertFalse(field.check_value(dt))
        self.assertTrue(field.can_use_value(dt))
        self.assertEqual(field.use_value(dt),
                         time(hour=3, minute=13, second=23))

    def test_time_field_using_time(self):
        field = TimeField()
        t = time(hour=3, minute=13, second=23)
        self.assertTrue(field.check_value(t))
        self.assertEqual(field.use_value(t),
                         time(hour=3, minute=13, second=23))

    def test_date_field_using_int(self):
        field = DateField()
        self.assertFalse(field.check_value(1433333333))
        self.assertTrue(field.can_use_value(1433333333))
        self.assertEqual(field.use_value(1433333333),
                         datetime(year=2015, month=6,
                                  day=3, hour=0, minute=15,
                                  second=33, tzinfo=timezone.utc).astimezone()
                         .date())

    def test_date_field_using_float(self):
        field = DateField()
        self.assertFalse(field.check_value(3.0))
        self.assertFalse(field.can_use_value(3.0))
        self.assertIsNone(field.use_value(3.0))

    def test_date_field_using_str(self):
        field = DateField(parse_format="%d/%m/%Y")
        self.assertFalse(field.check_value("23/03/2015"))
        self.assertTrue(field.can_use_value("23/03/2015"))
        self.assertEqual(field.use_value("23/03/2015"),
                         date(year=2015, month=3, day=23))

    def test_date_field_using_str_no_parse_format(self):
        field = DateField()
        self.assertFalse(field.check_value("23/03/2015"))
        self.assertTrue(field.can_use_value("23/03/2015"))
        self.assertEqual(field.use_value("23/03/2015"),
                         date(year=2015, month=3, day=23))

    def test_date_field_using_non_parseable_str(self):
        field = DateField(parse_format="%Y-%M-%d")
        self.assertIsNone(field.use_value("2013-9-45"))

    def test_date_field_using_list(self):
        field = DateField()
        self.assertFalse(field.check_value([2015, 3, 23]))
        self.assertTrue(field.can_use_value([2015, 3, 23]))
        self.assertEqual(field.use_value([2015, 3, 23]),
                         date(year=2015, month=3, day=23))

    def test_date_field_using_dict(self):
        field = DateField()
        self.assertFalse(field.check_value({"year": 2015, "month": 3, "day": 23}))
        self.assertTrue(field.can_use_value({"year": 2015, "month": 3, "day": 23}))
        self.assertEqual(field.use_value({"year": 2015, "month": 3, "day": 23}),
                         date(year=2015, month=3, day=23))

    def test_date_field_using_datetime(self):
        field = DateField()
        dt = datetime(year=2015, month=3, day=23, hour=3, minute=13, second=23)
        self.assertFalse(field.check_value(dt))
        self.assertTrue(field.can_use_value(dt))
        self.assertEqual(field.use_value(dt),
                         datetime(year=2015, month=3, day=23).date())

    def test_date_field_using_date(self):
        field = DateField()
        d = date(year=2015, month=3, day=23)
        self.assertTrue(field.check_value(d))
        self.assertEqual(field.use_value(d),
                         date(year=2015, month=3, day=23))

    def test_datetime_field_using_int(self):
        field = DateTimeField()
        self.assertFalse(field.check_value(1433333333))
        self.assertTrue(field.can_use_value(1433333333))
        self.assertEqual(field.use_value(1433333333),
                         datetime(year=2015, month=6,
                                  day=3, hour=12, minute=8,
                                  second=53, tzinfo=timezone.utc).astimezone().replace(tzinfo=None))

    def test_datetime_field_using_float(self):
        field = DateTimeField()
        self.assertFalse(field.check_value(3.0))
        self.assertFalse(field.can_use_value(3.0))
        self.assertIsNone(field.use_value(3.0))

    def test_datetime_field_using_str(self):
        field = DateTimeField(parse_format="%d/%m/%Y")
        self.assertFalse(field.check_value("23/03/2015"))
        self.assertTrue(field.can_use_value("23/03/2015"))
        self.assertEqual(field.use_value("23/03/2015"),
                         datetime(year=2015, month=3, day=23))

    def test_datetime_field_using_bad_str(self):
        field = DateTimeField(parse_format="%d/%m/%Y")
        self.assertIsNone(field.use_value("23/44/2015"))

    def test_datetime_field_using_str_no_parse_format(self):
        from dateutil.tz import tzutc
        field = DateTimeField()
        self.assertFalse(field.check_value('2012-09-11T13:02:41Z'))
        self.assertTrue(field.can_use_value('2012-09-11T13:02:41Z'))
        self.assertEqual(field.use_value('2012-09-11T13:02:41Z'),
                         datetime(2012, 9, 11, 13, 2, 41, tzinfo=tzutc()))

    def test_datetime_field_using_list(self):
        field = DateTimeField()
        self.assertFalse(field.check_value([2015, 3, 23]))
        self.assertTrue(field.can_use_value([2015, 3, 23]))
        self.assertEqual(field.use_value([2015, 3, 23]),
                         datetime(year=2015, month=3, day=23))

    def test_datetime_field_using_dict(self):
        field = DateTimeField()
        self.assertFalse(field.check_value({"year": 2015, "month": 3, "day": 23}))
        self.assertTrue(field.can_use_value({"year": 2015, "month": 3, "day": 23}))
        self.assertEqual(field.use_value({"year": 2015, "month": 3, "day": 23}),
                         datetime(year=2015, month=3, day=23))

    def test_datetime_field_using_date(self):
        field = DateTimeField()
        d = date(year=2015, month=3, day=23)
        self.assertFalse(field.check_value(d))
        self.assertTrue(field.can_use_value(d))
        self.assertEqual(field.use_value(d),
                         datetime(year=2015, month=3, day=23))

    def test_datetime_field_using_datetime(self):
        field = DateTimeField()
        d = datetime(year=2015, month=3, day=23,
                     hour=0, minute=15, second=33,
                     tzinfo=timezone.utc)
        self.assertTrue(field.check_value(d))
        self.assertEqual(field.use_value(d),
                         datetime(year=2015, month=3, day=23,
                                  hour=0, minute=15, second=33,
                                  tzinfo=timezone.utc))

    def test_datetime_field_using_iso8061_parser_and_formatter(self):
        field = DateTimeField('iso8061')
        field.date_parsers = {
            'iso8061': {
                'formatter': '%Y-%m-%dT%H:%M:%SZ',
                'parser': iso8601.parse_date
            }
        }
        data = '2012-09-11T13:02:41Z'
        self.assertFalse(field.check_value(data))
        self.assertTrue(field.can_use_value(data))
        self.assertEqual(field.use_value(data), datetime(year=2012, month=9, day=11,
                                                         hour=13, minute=2, second=41,
                                                         tzinfo=timezone.utc))

    def test_datetime_field_using_iso8061_without_formatter(self):
        field = DateTimeField('iso8061')
        field.date_parsers = {
            'iso8061': {
                'parser': 'bruce_wayne'
            }
        }
        data = '2012-09-11T13:02:41Z'
        self.assertFalse(field.check_value(data))
        self.assertTrue(field.can_use_value(data))
        self.assertIsNone(field.use_value(data))

    def test_datetime_field_using_iso8061_without_parser(self):
        field = DateTimeField('iso8061')
        field.date_parsers = {
            'iso8061': {
                'formatter': '%Y-%m-%dT%H:%M:%SZ'
            }
        }
        data = '2012-09-11T13:02:41Z'
        self.assertFalse(field.check_value(data))
        self.assertTrue(field.can_use_value(data))
        self.assertIsNotNone(field.use_value(data))

    def test_datetime_field_using_iso8061_parser_and_def_formatter(self):
        def parser_format(value):
            return datetime.strptime(datetime.strftime(value, '%Y-%m-%dT%H:%M:%SZ'), '%Y-%m-%dT%H:%M:%SZ')

        field = DateTimeField('iso8061')
        field.date_parsers = {
            'iso8061': {
                'formatter': parser_format,
                'parser': iso8601.parse_date
            }
        }
        data = '2012-09-11T13:02:41Z'
        self.assertFalse(field.check_value(data))
        self.assertTrue(field.can_use_value(data))
        self.assertEqual(field.use_value(data), datetime(year=2012, month=9, day=11,
                                                         hour=13, minute=2, second=41,
                                                         tzinfo=timezone.utc))

    def test_datetime_field_using_iso8061_bad_str(self):
        field = DateTimeField('iso8061')
        field.date_parsers = {
            'iso8061': {
                'formatter': '%Y-%m-%dT%H:%M:%SZ',
                'parser': iso8601.parse_date
            }
        }

        data = '2012-09-50T13:02:41Z'
        self.assertFalse(field.check_value(data))
        self.assertTrue(field.can_use_value(data))
        self.assertIsNone(field.use_value(data))

    def test_time_field_using_iso8061(self):
        field = TimeField('iso8061')
        field.date_parsers = {
            'iso8061': {
                'formatter': '%Y-%m-%dT%H:%M:%SZ',
                'parser': iso8601.parse_date
            }
        }

        data = '2012-09-11T13:02:41Z'
        self.assertFalse(field.check_value(data))
        self.assertTrue(field.can_use_value(data))
        self.assertEqual(field.use_value(data), time(hour=13, minute=2, second=41,
                                                     tzinfo=timezone.utc))

    def test_time_field_using_iso8061_bad_str(self):
        field = TimeField('iso8061')
        field.date_parsers = {
            'iso8061': {
                'formatter': '%Y-%m-%dT%H:%M:%SZ',
                'parser': iso8601.parse_date
            }
        }

        data = '2012-09-50T13:02:41Z'
        self.assertFalse(field.check_value(data))
        self.assertTrue(field.can_use_value(data))
        self.assertIsNone(field.use_value(data))

    def test_date_field_using_iso8061(self):
        field = DateField('iso8061')
        field.date_parsers = {
            'iso8061': {
                'formatter': '%Y-%m-%dT%H:%M:%SZ',
                'parser': iso8601.parse_date
            }
        }

        data = '2012-09-11T13:02:41Z'
        self.assertFalse(field.check_value(data))
        self.assertTrue(field.can_use_value(data))
        self.assertEqual(field.use_value(data), date(year=2012, month=9, day=11))

    def test_date_field_using_is8061_bad_str(self):
        field = DateField('iso8061')
        field.date_parsers = {
            'iso8061': {
                'formatter': '%Y-%m-%dT%H:%M:%SZ',
                'parser': iso8601.parse_date
            }
        }

        data = '2012-09-50T13:02:41Z'
        self.assertFalse(field.check_value(data))
        self.assertTrue(field.can_use_value(data))
        self.assertIsNone(field.use_value(data))

    def test_datetime_field_using_iso8061_def_format(self):
        def get_format(value):
            format = '%Y-%m-%dT%H:%M:%SZ'
            return datetime.strftime(value, format)

        field = DateTimeField('iso8061')
        field.date_parsers = {
            'iso8061': {
                'formatter': get_format,
                'parser': iso8601.parse_date
            }
        }

        data = datetime(year=2012, month=9, day=11,
                        hour=13, minute=2, second=41,
                        tzinfo=timezone.utc)
        self.assertEqual(field.get_formatted_value(data), '2012-09-11T13:02:41Z')

    def test_date_field_using_iso8061_bad_format_str(self):
        field = DateTimeField()

        data = datetime(year=2012, month=9, day=11,
                        hour=13, minute=2, second=41,
                        tzinfo=timezone.utc)
        self.assertEqual(field.get_formatted_value(data), '2012-09-11 13:02:41+00:00')

    def test_date_field_using_iso8061_format_str(self):
        field = DateTimeField('iso8061')
        field.date_parsers = {
            'iso8061': {
                'formatter': '%Y-%m-%dT%H:%M:%SZ',
                'parser': iso8601.parse_date
            }
        }

        data = datetime(year=2012, month=9, day=11,
                        hour=13, minute=2, second=41,
                        tzinfo=timezone.utc)
        self.assertEqual(field.get_formatted_value(data), '2012-09-11T13:02:41Z')

    def test_datetime_field_using_parser_as_formatter(self):
        field = DateTimeField('%Y-%m-%dT%H:%M:%SZ-test')

        data = datetime(year=2012, month=9, day=11,
                        hour=13, minute=2, second=41,
                        tzinfo=timezone.utc)
        self.assertEqual(field.get_formatted_value(data), '2012-09-11T13:02:41Z-test')

    def test_datetime_field_using_dict_as_parser(self):
        field = DateTimeField({'parser': '%Y-%m-%dT%H:%M:%SZ-test',
                               'formatter': '%Y-%m-%dT%H:%M:%SZ-test2'})

        data = datetime(year=2012, month=9, day=11,
                        hour=13, minute=2, second=41)
        self.assertEqual(field.get_parsed_value('2012-09-11T13:02:41Z-test'), data)
        self.assertEqual(field.get_formatted_value(data), '2012-09-11T13:02:41Z-test2')

    def test_datetime_field_using_dict_as_parser_default_formatter(self):
        field = DateTimeField({'parser': '%Y-%m-%dT%H:%M:%SZ-test'})

        data = datetime(year=2012, month=9, day=11,
                        hour=13, minute=2, second=41)
        self.assertEqual(field.get_parsed_value('2012-09-11T13:02:41Z-test'), data)
        self.assertEqual(field.get_formatted_value(data), '2012-09-11T13:02:41Z-test')

    def test_datetime_field_using_dict_neither_parser_or_formatter(self):
        field = DateTimeField({})

        data = datetime(year=2012, month=9, day=11,
                        hour=13, minute=2, second=41,
                        tzinfo=timezone.utc)
        self.assertIsNone(field.get_parsed_value('2012-09-11T13:02:41Z-test'))
        self.assertEqual(field.get_formatted_value(data), '2012-09-11 13:02:41+00:00')

    def test_datetime_field_using_default_parser_formatter(self):
        field = DateTimeField()

        data = datetime(year=2012, month=9, day=11,
                        hour=13, minute=2, second=41,
                        tzinfo=timezone.utc)
        self.assertEqual(field.get_parsed_value('2012-09-11T13:02:41Z'), data)
        self.assertEqual(field.get_formatted_value(data), '2012-09-11 13:02:41+00:00')

    def test_model_field_desc(self):
        class TestModel(BaseModel):
            field_name = StringIdField()

        field = ModelField(model_class=TestModel)
        self.assertEqual(field.export_definition(),
                         {'alias': None,
                          'doc': 'ModelField field (:class:`tests.dirty_models.tests_fields.TestModel`)',
                          'model_class': TestModel,
                          'name': None,
                          'read_only': False})

    def test_array_field(self):
        class TestModel(BaseModel):
            field_name_1 = ModelField()
            field_name_2 = StringField()

        class ArrayModel(BaseModel):
            array_field = ArrayField(field_type=ModelField(model_class=TestModel))

        array_model = ArrayModel()

        test_model_1 = TestModel()
        test_model_1.field_name_2 = "hello"
        test_model_1.field_name_1 = TestModel()

        array_model.array_field = set([test_model_1])
        self.assertEqual(ListModel([test_model_1]).export_data(), array_model.array_field.export_data())
        self.assertEqual(test_model_1, array_model.array_field[0])

    def test_array_field_with_ListModel(self):
        class TestModel(BaseModel):
            field_name_1 = ModelField()
            field_name_2 = StringField()

        class ArrayModel(BaseModel):
            array_field = ArrayField(field_type=ModelField(model_class=TestModel))

        array_model = ArrayModel()

        test_model_1 = TestModel()
        test_model_1.field_name_2 = "hello"
        test_model_1.field_name_1 = TestModel()

        array_model.array_field = ListModel([test_model_1])
        self.assertEqual(test_model_1, array_model.array_field[0])

    def test_array_field_extend(self):
        class TestModel(BaseModel):
            field_name_1 = ModelField()
            field_name_2 = StringField()

        class ArrayModel(BaseModel):
            array_field = ArrayField(field_type=ModelField(model_class=TestModel))

        array_model = ArrayModel()

        test_model_1 = TestModel()
        array_model.array_field = ListModel([test_model_1])

        test_model_2 = TestModel()
        array_model.array_field.extend(set([test_model_2]))

        self.assertEqual(test_model_1, array_model.array_field[0])
        self.assertEqual(test_model_2, array_model.array_field[1])

    def test_array_field_invalid_value_to_add(self):
        class TestModel(BaseModel):
            field_name_1 = ModelField()
            field_name_2 = StringField()

        class ArrayModel(BaseModel):
            array_field = ArrayField(field_type=ModelField(model_class=TestModel))

        array_model = ArrayModel()

        test_model_1 = TestModel()
        array_model.array_field = ListModel([test_model_1])

        array_model.array_field.extend(ListModel(["This is not a valid model"]))

        self.assertEqual(test_model_1, array_model.array_field[0])
        self.assertRaises(IndexError, array_model.array_field.__getitem__, 1)

    def test_array_field_invalid_value_set(self):
        class TestModel(BaseModel):
            field_name_1 = ModelField()
            field_name_2 = StringField()

        class ArrayModel(BaseModel):
            array_field = ArrayField(field_type=ModelField(model_class=TestModel))

        array_model = ArrayModel()
        array_model.array_field = ["Unexpected string", TestModel()]

        self.assertEqual(1, len(array_model.array_field))

    def test_array_field_not_iterable(self):
        class ArrayModel(BaseModel):
            array_field = ArrayField(field_type=BooleanField())

        model = ArrayModel()
        model.array_field = "This is not a list"
        self.assertIsNone(model.array_field)

    def test_array_field_list_invalid_types(self):
        class ArrayModel(BaseModel):
            array_field = ArrayField(field_type=IntegerField())

        model = ArrayModel()
        model.array_field = ["This is not a list", "This neither"]
        self.assertIsNone(model.array_field)

    def test_array_field_conversion(self):
        class ArrayModel(BaseModel):
            array_field = ArrayField(field_type=IntegerField())

        model = ArrayModel()
        model.array_field = ["This is not a list", "2"]
        self.assertEquals(model.array_field[0], 2)

    def test_array_set_value_list_field(self):
        class ArrayModel(BaseModel):
            array_field = ArrayField(field_type=IntegerField())

        model = ArrayModel()
        model.array_field = ListModel(["this is not an integer"], field_type=IntegerField())
        self.assertEqual(0, len(model.array_field))

    def test_array_set_value_list_field_valid_and_convertible(self):
        class ArrayModel(BaseModel):
            array_field = ArrayField(field_type=IntegerField())

        model = ArrayModel()
        model.array_field = ListModel(["3"], field_type=IntegerField())
        self.assertEqual(1, len(model.array_field))

    def test_array_del(self):
        class TestModel(BaseModel):
            field_name_1 = ModelField()
            field_name_2 = StringField()

        class ArrayModel(BaseModel):
            array_field = ArrayField(field_type=ModelField(model_class=TestModel))

        array_model = ArrayModel()

        test_model_1 = TestModel()
        array_model.array_field = [test_model_1]
        self.assertEqual(0, array_model.array_field.index(test_model_1))
        del array_model.array_field[0]
        self.assertEqual(0, len(array_model.array_field))

    def test_array_model_export_data(self):
        class TestModel(BaseModel):
            field_name_1 = ModelField()
            field_name_2 = StringField()

        class ArrayModel(BaseModel):
            array_field = ArrayField(field_type=ModelField(model_class=TestModel))

        array_model = ArrayModel()

        test_model_1 = TestModel()
        test_model_1.field_name_1 = TestModel()
        test_model_1.field_name_2 = "Test model 1"

        test_model_2 = TestModel()
        test_model_2.field_name_1 = TestModel()
        test_model_2.field_name_2 = "Test model 2"

        array_model.array_field = [test_model_1, test_model_2]

        expected_data = {
            "array_field": [{"field_name_1": {}, "field_name_2": "Test model 1"},
                            {"field_name_1": {}, "field_name_2": "Test model 2"}]
        }

        self.assertEqual(expected_data, array_model.export_data())

    def test_array_model_export_data_integers(self):
        class ArrayModel(BaseModel):
            array_field = ArrayField(field_type=IntegerField())

        model = ArrayModel()
        model.array_field = ["3", 4]

        self.assertEqual({"array_field": [3, 4]}, model.export_data())

    def test_array_model_export_data_not_modified(self):
        class TestModel(BaseModel):
            field_name_1 = ModelField()
            field_name_2 = StringField()

        class ArrayModel(BaseModel):
            array_field = ArrayField(field_type=ModelField(model_class=TestModel))

        array_model = ArrayModel()

        test_model_1 = TestModel()
        test_model_1.field_name_1 = TestModel()
        test_model_1.field_name_2 = "Test model 1"

        test_model_2 = TestModel()
        test_model_2.field_name_1 = TestModel()
        test_model_2.field_name_2 = "Test model 2"

        array_model.array_field = [test_model_1, test_model_2]
        array_model.flat_data()

        expected_data = {
            "array_field": [{"field_name_1": {}, "field_name_2": "Test model 1"},
                            {"field_name_1": {}, "field_name_2": "Test model 2"}]
        }

        self.assertEqual(expected_data, array_model.export_data())

    def test_array_model_export_data_unitialised(self):
        class ArrayModel(BaseModel):
            array_field = ArrayField(field_type=IntegerField())

        model = ArrayModel()
        model.array_field = ["3", 4]
        model.array_field.clear()

        self.assertEqual({"array_field": []}, model.export_data())

    def test_array_model_export_modified_data(self):
        class TestModel(BaseModel):
            field_name_1 = ModelField()
            field_name_2 = StringField()

        class ArrayModel(BaseModel):
            array_field = ArrayField(field_type=ModelField(model_class=TestModel))

        array_model = ArrayModel()

        test_model_1 = TestModel()
        test_model_1.field_name_1 = TestModel()
        test_model_1.field_name_2 = "Test model 1"

        test_model_2 = TestModel()
        test_model_2.field_name_1 = TestModel()
        test_model_2.field_name_2 = "Test model 2"

        array_model.array_field = [test_model_1, test_model_2]

        expected_data = {
            "array_field": [{"field_name_1": {}, "field_name_2": "Test model 1"},
                            {"field_name_1": {}, "field_name_2": "Test model 2"}]
        }

        self.assertEqual(expected_data, array_model.export_modified_data())

    def test_array_model_export_modified_data_flattered(self):
        class TestModel(BaseModel):
            field_name_1 = ModelField()
            field_name_2 = StringField()

        class ArrayModel(BaseModel):
            array_field = ArrayField(field_type=ModelField(model_class=TestModel))

        array_model = ArrayModel()

        test_model_1 = TestModel()
        test_model_1.field_name_1 = TestModel()
        test_model_1.field_name_2 = "Test model 1"

        test_model_2 = TestModel()
        test_model_2.field_name_1 = TestModel()
        test_model_2.field_name_2 = "Test model 2"

        array_model.array_field = [test_model_1, test_model_2]

        array_model.flat_data()

        self.assertEqual({}, array_model.export_modified_data())

    def test_array_model_export_modified_data_integers(self):
        class ArrayModel(BaseModel):
            array_field = ArrayField(field_type=IntegerField())

        model = ArrayModel()
        model.array_field = ["3", 4]

        self.assertEqual({"array_field": [3, 4]}, model.export_modified_data())

    def test_array_model_export_modified_data_unitialised(self):
        class ArrayModel(BaseModel):
            array_field = ArrayField(field_type=IntegerField())

        model = ArrayModel()
        model.array_field = ["3", 4]
        model.array_field.clear()

        self.assertEqual({"array_field": []}, model.export_modified_data())

    def test_array_model_import_data(self):
        class ArrayModel(BaseModel):
            array_field = ArrayField(field_type=IntegerField())

        array_model = ArrayModel()
        array_model.import_data({"array_field": [1, 2, 3, 4]})
        self.assertEqual(4, len(array_model.array_field))

    def test_array_model_empty(self):
        class ArrayModel(BaseModel):
            array_field = ArrayField(field_type=IntegerField())

        array_model = ArrayModel()
        array_model.array_field = []
        self.assertIsInstance(array_model.array_field, ListModel)
        self.assertListEqual(array_model.array_field.export_data(), [])

    def test_array_model_with_model_field_no_model_class(self):
        class TestModel(BaseModel):
            field_name_1 = ModelField()
            field_name_2 = StringField()

        class ArrayModel(BaseModel):
            array_field = ArrayField(field_type=ModelField(model_class=TestModel))

        array_model = ArrayModel()
        array_model_indented_1 = TestModel({'field_name_2': 'aaaa'})
        array_model_indented_2 = TestModel({'field_name_2': 'bbbb'})
        array_model.array_field = [array_model_indented_1, array_model_indented_2, "not valid :)"]
        self.assertEqual(list(array_model.array_field), [array_model_indented_1, array_model_indented_2])

    def test_array_model_export_modified_data_model_inside(self):
        class TestModel(BaseModel):
            field_name_1 = ModelField()
            field_name_2 = StringField()

        class ArrayModel(BaseModel):
            array_field = ArrayField(field_type=ModelField(model_class=TestModel))

        array_model = ArrayModel()
        array_model_indented_1 = TestModel({'field_name_2': 'aaaa'})
        array_model_indented_2 = TestModel({'field_name_2': 'bbbb'})
        array_model.array_field = [array_model_indented_1, array_model_indented_2]

        array_model.flat_data()
        array_model_indented_1.field_name_2 = 'cccc'

        self.assertDictEqual(array_model.export_modified_data(), {'array_field': [{'field_name_2': 'cccc'}, {}]})

    def test_array_field_desc(self):
        field = ArrayField(field_type=IntegerField(read_only=True))
        self.assertEqual(field.export_definition(), {
            'alias': None,
            'doc': 'Array of IntegerField field [READ ONLY]',
            'field_type': (IntegerField, {'alias': None,
                                          'doc': 'IntegerField field [READ ONLY]',
                                          'name': None,
                                          'read_only': True}),
            'name': None,
            'read_only': False})

    def test_array_field_from_desc(self):
        field = ArrayField(field_type=(IntegerField, {'alias': None,
                                                      'doc': 'IntegerField field [READ ONLY]',
                                                      'name': None,
                                                      'read_only': True}))
        self.assertEqual(field.export_definition(), {
            'alias': None,
            'doc': 'Array of IntegerField field [READ ONLY]',
            'field_type': (IntegerField, {'alias': None,
                                          'doc': 'IntegerField field [READ ONLY]',
                                          'name': None,
                                          'read_only': True}),
            'name': None,
            'read_only': False})

    def test_hashmap_field(self):
        class FakeHashMapModel(HashMapModel):
            field_name_1 = ModelField()
            field_name_2 = StringField()

        class TestModel(BaseModel):
            hashmap_field = HashMapField(field_type=IntegerField(), model_class=FakeHashMapModel)

        hash_model = TestModel()
        hash_model.hashmap_field = {'field_name_1': {'field_name_2': 'aaaa'},
                                    'field_name_2': 'cccc',
                                    'field_hash_1': '34'}

        self.assertIsInstance(hash_model.hashmap_field, FakeHashMapModel)
        self.assertEqual(hash_model.hashmap_field.field_name_1.field_name_2, 'aaaa')
        self.assertEqual(hash_model.hashmap_field.field_name_2, 'cccc')
        self.assertEqual(hash_model.hashmap_field.field_hash_1, 34)

    def test_hashmap_field_dyn(self):
        class TestModel(BaseModel):
            hashmap_field = HashMapField(field_type=IntegerField())

        hash_model = TestModel()
        hash_model.hashmap_field = {'field_name_1': 3,
                                    'field_name_2': 4,
                                    'field_hash_1': '34'}

        self.assertIsInstance(hash_model.hashmap_field, HashMapModel)
        self.assertEqual(hash_model.hashmap_field.field_name_1, 3)
        self.assertEqual(hash_model.hashmap_field.field_name_2, 4)
        self.assertEqual(hash_model.hashmap_field.field_hash_1, 34)


class ArrayOfStringFieldTests(TestCase):

    def setUp(self):
        super(ArrayOfStringFieldTests, self).setUp()

        class ArrayModel(BaseModel):
            array_field = ArrayField(field_type=StringField(), autolist=True)

        self.model = ArrayModel()

    def test_array_field(self):
        self.model.array_field = ['foo', 'bar']
        self.assertEqual(self.model.export_data(), {'array_field': ['foo', 'bar']})

    def test_array_field_tuple(self):
        self.model.array_field = 'foo',
        self.assertEqual(self.model.export_data(), {'array_field': ['foo']})

    def test_array_field_autolist(self):
        self.model.array_field = 'foo'
        self.assertEqual(self.model.export_data(), {'array_field': ['foo']})

    def test_array_field_no_autolist(self):
        self.model.__class__.__dict__['array_field'].autolist = False
        self.model.array_field = 'foo'
        self.assertEqual(self.model.export_data(), {})


class MultiTypeFieldSimpleTypesTests(TestCase):

    def setUp(self):
        super(MultiTypeFieldSimpleTypesTests, self).setUp()

        class MultiTypeModel(BaseModel):
            multi_field = MultiTypeField(field_types=[IntegerField(), StringField()])

        self.model = MultiTypeModel()

    def test_string_field(self):
        self.model.multi_field = 'foo'
        self.assertEqual(self.model.multi_field, 'foo')

    def test_integer_field(self):
        self.model.multi_field = 3
        self.assertEqual(self.model.multi_field, 3)

    def test_update_string_field(self):
        self.model.multi_field = 3
        self.model.flat_data()
        self.model.multi_field = 'foo'
        self.assertEqual(self.model.multi_field, 'foo')

    def test_update_integer_field(self):
        self.model.multi_field = 'foo'
        self.model.flat_data()
        self.model.multi_field = 3
        self.assertEqual(self.model.multi_field, 3)

    def test_no_update_integer_field(self):
        self.model.multi_field = 3
        self.model.flat_data()
        self.model.multi_field = [3, 4]
        self.assertEqual(self.model.multi_field, 3)

    def test_integer_field_use_float(self):
        self.model.multi_field = 3.0
        self.assertEqual(self.model.multi_field, 3)

    def test_string_field_conversion_priority(self):
        self.model.multi_field = '3'
        self.assertEqual(self.model.multi_field, '3')

    def test_multi_field_desc(self):
        self.maxDiff = None
        field = MultiTypeField(field_types=[IntegerField(), StringField()])
        self.assertEqual(field.export_definition(), {
            'alias': None,
            'doc': "\n".join(['Multiple type values are allowed:',
                              '',
                              '* IntegerField field',
                              '',
                              '* StringField field']),
            'field_types': [(IntegerField, {'alias': None,
                                            'doc': 'IntegerField field',
                                            'name': None,
                                            'read_only': False}),
                            (StringField, {'alias': None,
                                           'doc': 'StringField field',
                                           'name': None,
                                           'read_only': False})],
            'name': None,
            'read_only': False})


class MultiTypeFieldComplexTypesTests(TestCase):

    def setUp(self):
        super(MultiTypeFieldComplexTypesTests, self).setUp()

        class MultiTypeModel(BaseModel):
            multi_field = MultiTypeField(field_types=[IntegerField(), (ArrayField, {"field_type": StringField()})])

        self.model = MultiTypeModel()

    def test_integer_field(self):
        self.model.multi_field = 3
        self.assertEqual(self.model.multi_field, 3)

    def test_array_field(self):
        self.model.multi_field = ['foo', 'bar']
        self.assertEqual(self.model.multi_field.export_data(), ['foo', 'bar'])

    def test_update_array_field(self):
        self.model.multi_field = 3
        self.model.flat_data()
        self.model.multi_field = ['foo', 'bar']
        self.assertEqual(self.model.multi_field.export_data(), ['foo', 'bar'])

    def test_update_integer_field(self):
        self.model.multi_field = ['foo', 'bar']
        self.model.flat_data()
        self.model.multi_field = 3
        self.assertEqual(self.model.multi_field, 3)

    def test_get_field_type_by_value(self):
        multi_field = MultiTypeField(field_types=[IntegerField(), (ArrayField, {"field_type": StringField()})])
        self.assertIsInstance(multi_field.get_field_type_by_value(['foo', 'bar']),
                              ArrayField)
        self.assertIsInstance(multi_field.get_field_type_by_value(3),
                              IntegerField)

    def test_get_field_type_by_value_fail(self):
        multi_field = MultiTypeField(field_types=[IntegerField(), (ArrayField, {"field_type": StringField()})])
        with self.assertRaises(TypeError):
            multi_field.get_field_type_by_value({})


class AutoreferenceModelTests(TestCase):

    def setUp(self):
        super(AutoreferenceModelTests, self).setUp()

        class AutoreferenceModel(BaseModel):
            multi_field = MultiTypeField(field_types=[IntegerField(), (ArrayField, {"field_type": ModelField()})])
            array_of_array = ArrayField(field_type=ArrayField(field_type=ModelField()))
            test_field = IntegerField()

        self.model = AutoreferenceModel()

    def test_model_reference(self):
        self.model.import_data({'multi_field': [{'test_field': 1}, {'test_field': 2}],
                                'array_of_array': [[{'test_field': 3}]]})
        self.assertIsInstance(self.model.multi_field[0], self.model.__class__)
        self.assertIsInstance(self.model.multi_field[1], self.model.__class__)
        self.assertIsInstance(self.model.array_of_array[0][0], self.model.__class__)


class TimedeltaFieldTests(TestCase):

    def setUp(self):
        self.field = TimedeltaField()

    def test_check_value_success(self):
        self.assertTrue(self.field.check_value(timedelta(seconds=0)))

    def test_check_value_fail(self):
        self.assertFalse(self.field.check_value(12))

    def test_can_use_value_int(self):
        self.assertTrue(self.field.can_use_value(12))

    def test_can_use_value_float(self):
        self.assertTrue(self.field.can_use_value(12.11))

    def test_can_use_value_fail(self):
        self.assertFalse(self.field.can_use_value('test'))

    def test_convert_value_int(self):
        self.assertTrue(self.field.convert_value(12), timedelta(seconds=12))

    def test_convert_value_float(self):
        self.assertTrue(self.field.convert_value(12.11), timedelta(seconds=12, milliseconds=110))


class DateTimeFieldWithTimezoneTests(TestCase):

    def test_no_timezone_none(self):
        class Model(BaseModel):
            date_time_field = DateTimeField()

        model = Model(date_time_field=datetime(year=2016, month=7, day=21, hour=12, minute=23))

        self.assertEqual(model.date_time_field, datetime(year=2016, month=7, day=21, hour=12, minute=23))
        self.assertIsNone(model.date_time_field.tzinfo)

    def test_no_timezone_europe(self):
        class Model(BaseModel):
            date_time_field = DateTimeField()

        model = Model(date_time_field=datetime(year=2016, month=7, day=21,
                                               hour=12, minute=23, tzinfo=tz.gettz('Europe/Amsterdam')))

        self.assertEqual(model.date_time_field, datetime(year=2016, month=7, day=21, hour=12, minute=23,
                                                         tzinfo=tz.gettz('Europe/Amsterdam')))
        self.assertEqual(model.date_time_field.tzinfo, tz.gettz('Europe/Amsterdam'))

    def test_with_default_timezone_utc(self):
        class Model(BaseModel):
            date_time_field = DateTimeField(default_timezone=timezone.utc)

        model = Model(date_time_field=datetime(year=2016, month=7, day=21, hour=12, minute=23))

        self.assertEqual(model.date_time_field, datetime(year=2016, month=7, day=21,
                                                         hour=12, minute=23, tzinfo=timezone.utc))
        self.assertEqual(model.date_time_field.tzinfo, timezone.utc)

    def test_with_default_timezone_utc_no_changed(self):
        class Model(BaseModel):
            date_time_field = DateTimeField(default_timezone=timezone.utc)

        model = Model(date_time_field=datetime(year=2016, month=7, day=21, hour=12, minute=23,
                                               tzinfo=tz.gettz('Europe/Amsterdam')))

        self.assertEqual(model.date_time_field, datetime(year=2016, month=7, day=21,
                                                         hour=12, minute=23, tzinfo=tz.gettz('Europe/Amsterdam')))
        self.assertEqual(model.date_time_field.tzinfo, tz.gettz('Europe/Amsterdam'))

    def test_with_default_timezone_europe(self):
        class Model(BaseModel):
            date_time_field = DateTimeField(default_timezone=tz.gettz('Europe/Amsterdam'))

        model = Model(date_time_field=datetime(year=2016, month=7, day=21, hour=12, minute=23))

        self.assertEqual(model.date_time_field, datetime(year=2016, month=7, day=21,
                                                         hour=12, minute=23, tzinfo=tz.gettz('Europe/Amsterdam')))
        self.assertEqual(model.date_time_field.tzinfo, tz.gettz('Europe/Amsterdam'))

    def test_with_default_force_timezone_utc(self):
        class Model(BaseModel):
            date_time_field = DateTimeField(default_timezone=timezone.utc, force_timezone=True)

        model = Model(date_time_field=datetime(year=2016, month=7, day=21,
                                               hour=12, minute=23, tzinfo=tz.gettz('Europe/Amsterdam')))

        self.assertEqual(model.date_time_field,
                         datetime(year=2016, month=7, day=21,
                                  hour=12, minute=23,
                                  tzinfo=tz.gettz('Europe/Amsterdam')).astimezone(timezone.utc))
        self.assertEqual(model.date_time_field.tzinfo, timezone.utc)

    def test_export_definition(self):

        field = DateTimeField(name='test_field', alias=[], default_timezone=timezone.utc, force_timezone=True)

        self.assertEqual(field.export_definition(),
                         {'alias': [], 'parse_format': None,
                          'doc': 'DateTimeField field',
                          'force_timezone': True,
                          'default_timezone': timezone.utc,
                          'name': 'test_field', 'read_only': False},
                         field.export_definition())


class TimeFieldWithTimezone(TestCase):

    def test_no_timezone_none(self):
        class Model(BaseModel):
            time_field = TimeField()

        model = Model(time_field=time(hour=12, minute=23))

        self.assertEqual(model.time_field, time(hour=12, minute=23))
        self.assertIsNone(model.time_field.tzinfo)

    def test_no_timezone_europe(self):
        class Model(BaseModel):
            time_field = TimeField()

        model = Model(time_field=time(hour=12, minute=23, tzinfo=tz.gettz('Europe/Amsterdam')))

        self.assertEqual(model.time_field, time(hour=12, minute=23,
                                                tzinfo=tz.gettz('Europe/Amsterdam')))
        self.assertEqual(model.time_field.tzinfo, tz.gettz('Europe/Amsterdam'))

    def test_with_default_timezone_utc(self):
        class Model(BaseModel):
            time_field = TimeField(default_timezone=timezone.utc)

        model = Model(time_field=time(hour=12, minute=23))

        self.assertEqual(model.time_field, time(hour=12, minute=23, tzinfo=timezone.utc))
        self.assertEqual(model.time_field.tzinfo, timezone.utc)

    def test_with_default_timezone_utc_no_changed(self):
        class Model(BaseModel):
            time_field = TimeField(default_timezone=timezone.utc)

        model = Model(time_field=time(hour=12, minute=23,
                                      tzinfo=tz.gettz('Europe/Amsterdam')))

        self.assertEqual(model.time_field, time(hour=12, minute=23, tzinfo=tz.gettz('Europe/Amsterdam')))
        self.assertEqual(model.time_field.tzinfo, tz.gettz('Europe/Amsterdam'))

    def test_export_definition(self):

        field = TimeField(name='test_field', alias=[], default_timezone=timezone.utc)

        self.assertEqual(field.export_definition(),
                         {'alias': [], 'parse_format': None,
                          'doc': 'TimeField field',
                          'default_timezone': timezone.utc,
                          'name': 'test_field', 'read_only': False},
                         field.export_definition())
