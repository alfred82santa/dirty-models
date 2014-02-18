from unittest import TestCase
from dirty_models.models import BaseModel, DynamicModel
from dirty_models.fields import BaseField, IntegerField, FloatField, StringField, DateTimeField, ModelField, ArrayField, \
    BooleanField
from datetime import datetime


INITIAL_DATA = {
    'testField1': 'testValue1',
    'testField2': 'testValue2'
}


class TestModels(TestCase):

    def setUp(self):
        class FakeModel(BaseModel):
            testField1 = BaseField()

        self.model = FakeModel()
        self.model._original_data = INITIAL_DATA

    def tearDown(self):
        self.model.clear()

    def test_object_creation_test(self):

        class FakeModel(BaseModel):
            testField1 = BaseField()
            testField3 = BaseField()

        data = {'testField1': 'Value1', 'testField2': 'No matters'}
        model_object = FakeModel(
            data, testField3='Value3', testField4='No matters')
        self.assertEqual(model_object.testField1, 'Value1')
        self.assertFalse(hasattr(model_object, 'testField2'))
        self.assertEqual(model_object.testField3, 'Value3')
        self.assertFalse(hasattr(model_object, 'testField4'))

    def test_set_initial_value(self):
        self.model._original_data = {}
        self.model.set_field_value('testField1', 'whatever')
        self.assertIsNone(self.model._original_data.get('testField1'))
        self.assertEqual('whatever', self.model._modified_data['testField1'])

    def test_set_value_to_modify(self):
        self.model.set_field_value('testField1', 'whatever')
        self.assertEqual(INITIAL_DATA['testField1'],
                         self.model._original_data['testField1'])
        self.assertEqual('whatever', self.model._modified_data['testField1'])

    def test_set_value_already_modified_with_previous_value(self):
        self.model._modified_data = {'testField1': 'modifiedValue1'}
        self.model.set_field_value('testField1', INITIAL_DATA['testField1'])
        self.assertEquals(self.model._original_data['testField1'],
                          INITIAL_DATA['testField1'])
        self.assertEquals({}, self.model._modified_data)

    def test_delete_value(self):
        self.model.delete_field_value('testField1')
        self.assertEqual(INITIAL_DATA['testField1'],
                         self.model._original_data['testField1'])
        self.assertTrue('testField1' in self.model._deleted_fields)

    def test_set_value_deleted(self):
        self.model.delete_field_value('testField1')
        self.assertTrue('testField1' in self.model._deleted_fields)
        self.model.set_field_value('testField1', 'undelete')
        self.assertFalse('testField1' in self.model._deleted_fields)
        self.assertEquals('undelete', self.model._modified_data['testField1'])

    def test_delete_modified_value(self):
        self.model._modified_data = {'testField1': 'modifiedValue1'}
        self.model.delete_field_value('testField1')
        self.assertEquals({}, self.model._modified_data)
        self.assertTrue('testField1' in self.model._deleted_fields)

    def test_get_deleted_value(self):
        self.model.delete_field_value('testField1')
        self.assertIsNone(self.model.get_field_value('testField1'))

    def test_get_modified_value(self):
        self.model.set_field_value('testField1', 'modifiedValue')
        self.assertEquals('modifiedValue',
                          self.model.get_field_value('testField1'))

    def test_import_data(self):
        self.model.import_data(INITIAL_DATA)
        self.assertTrue(hasattr(self.model, 'testField1'))
        self.assertFalse(hasattr(self.model, 'testField2'))

    def _get_test_model_instance(self):

        class TestExportModel(BaseModel):
            testField1 = BaseField()
            testField2 = BaseField()
            testField3 = BaseField()

        return TestExportModel()

    def test_export_data(self):

        model_field = self._get_test_model_instance()
        model_field._original_data = {'testField1': 'Field Value1',
                                      'testField2': 'Field Value2'}
        model_field._modified_data = {'testField2': 'Field Value2 Modified'}

        self.model._modified_data = {'testField1': 'Value1Modified',
                                     'testField2': 'Value2Modified',
                                     'testField3': 'Value3',
                                     'testField4': model_field}
        self.model._deleted_fields = ['testField2', 'testField3']
        exported_data = self.model.export_data()
        self.assertEqual(exported_data, {'testField1': 'Value1Modified',
                                         'testField4':
                                         {'testField2':
                                          'Field Value2 Modified',
                                             'testField1': 'Field Value1'}})

    def test_export_modified(self):

        model_field = self._get_test_model_instance()
        model_field._original_data = {
            'testField1': 'Field Value1', 'testField2': 'Field Value2',
            'testField3': 'Field Value3'}
        model_field._modified_data = {'testField2': 'Field Value2 Modified'}
        model_field._deleted_fields = ['testField3']

        self.model._modified_data = {'testField1': 'Value1Modified',
                                     'testField3': 'Value3',
                                     'testField4': model_field}
        self.model._deleted_fields = ['testField3']
        exported_data = self.model.export_modified_data()
        self.assertEqual(exported_data, {'testField1': 'Value1Modified',
                                         'testField3': None,
                                         'testField4': {
                                             'testField2':
                                             'Field Value2 Modified',
                                             'testField3': None}})

    def test_flat_data(self):
        model_field = self._get_test_model_instance()
        model_field._original_data = {'testField1': 'Field Value1',
                                      'testField2': 'Field Value2'}
        model_field._modified_data = {'testField2': 'Field Value2 Modified'}

        self.model._modified_data = {'testField1': 'Value1Modified',
                                     'testField2': 'Value2Modified',
                                     'testField3': 'Value3',
                                     'testField4': model_field}
        self.model._deleted_fields = ['testField2', 'testField3']
        self.model.flat_data()
        self.assertEqual(self.model._deleted_fields, [])
        self.assertEqual(self.model._modified_data, {})

        self.assertEqual(set(self.model._original_data.keys()),
                         set(['testField1', 'testField4']))
        self.assertEqual(
            self.model._original_data['testField1'], 'Value1Modified')
        self.assertEqual(
            self.model._original_data['testField4']._original_data,
            {'testField1': 'Field Value1',
             'testField2': 'Field Value2 Modified'})

    def test_dirty_model_meta_field(self):

        class TestIntegerField(BaseField):
            pass

        class TestStringField(BaseField):
            pass

        class CarModel(BaseModel):
            wheels = TestIntegerField(name='other_wheel_name')
            colour = TestStringField()

        self.assertTrue(hasattr(CarModel, 'other_wheel_name'))

        test_car = CarModel()
        test_car.wheels = 12
        self.assertEqual(test_car.other_wheel_name, 12)


class TestDynamicModel(TestCase):

    def setUp(self):
        self.model = DynamicModel()

    def tearDown(self):
        self.model.clear()

    def test_set_int_value(self):
        self.model.test1 = 1
        self.assertEqual(self.model.test1, 1)
        self.assertIsInstance(self.model.__class__.__dict__['test1'], IntegerField)

        newmodel = DynamicModel()
        newmodel.test1 = "aaaa"
        self.assertEqual(newmodel.test1, "aaaa")

    def test_set_float_value(self):
        self.model.test2 = 1.0
        self.assertEqual(self.model.test2, 1.0)
        self.assertIsInstance(self.model.__class__.__dict__['test2'], FloatField)

    def test_set_bool_value(self):
        self.model.test2 = True
        self.assertTrue(self.model.test2)
        self.assertIsInstance(self.model.__class__.__dict__['test2'], BooleanField)

    def test_set_str_value(self):
        self.model.test3 = "aass"
        self.assertEqual(self.model.test3, "aass")
        self.assertIsInstance(self.model.__class__.__dict__['test3'], StringField)

    def test_set_datetime_value(self):
        self.model.test4 = datetime(year=2014, month=11, day=1)
        self.assertEqual(self.model.test4, datetime(year=2014, month=11, day=1))
        self.assertIsInstance(self.model.__class__.__dict__['test4'], DateTimeField)

    def test_load_from_dict_value(self):
        self.model.import_data({"aa": "aaaaaa"})
        self.assertEqual(self.model.export_data(), {"aa": "aaaaaa"})
        self.assertIsInstance(self.model.__class__.__dict__['aa'], StringField)

    def test_set_dict_value(self):
        self.model.test1 = {"aa": "aaaaaa"}
        self.assertEqual(self.model.export_data(), {"test1": {"aa": "aaaaaa"}})
        self.assertIsInstance(self.model.__class__.__dict__['test1'], ModelField)
        self.assertEqual(self.model.__class__.__dict__['test1'].model_class, DynamicModel)

    def test_set_model_value(self):
        class FakeModel(BaseModel):
            test2 = IntegerField()
        self.model.test1 = FakeModel({"test2": 23})
        self.assertEqual(self.model.export_data(), {"test1": {"test2": 23}})
        self.assertIsInstance(self.model.__class__.__dict__['test1'], ModelField)
        self.assertEqual(self.model.__class__.__dict__['test1'].model_class, FakeModel)

    def test_set_list_value(self):
        self.model.test1 = ["aa", "aaaaaa"]
        self.assertEqual(self.model.export_data(), {"test1": ["aa", "aaaaaa"]})
        self.assertIsInstance(self.model.__class__.__dict__['test1'], ArrayField)

    def test_set_invalid_type_field_fail(self):
        with self.assertRaisesRegexp(TypeError, "Invalid parameter: test34. Type not supported."):
            self.model.test34 = (2, 2)

    def test_delete_field(self):
        self.model.test1 = 1
        self.assertEqual(self.model.test1, 1)
        self.assertIsInstance(self.model.__class__.__dict__['test1'], IntegerField)

        del self.model.test1
        self.assertIsNone(self.model.test1)

    def test_delete_protected_field(self):
        self.model._test1 = 1
        self.assertEqual(self.model._test1, 1)
        del self.model._test1
