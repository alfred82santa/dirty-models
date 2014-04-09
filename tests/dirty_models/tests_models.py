import pickle
from unittest import TestCase
from dirty_models.models import BaseModel, DynamicModel
from dirty_models.fields import (BaseField, IntegerField, FloatField,
                                 StringField, DateTimeField, ModelField,
                                 ArrayField, BooleanField)

from datetime import datetime
from dirty_models.base import Unlocker


INITIAL_DATA = {
    'testField1': 'testValue1',
    'testField2': 'testValue2'
}


class PicklableModel(BaseModel):

    field_1 = ModelField()
    field_2 = IntegerField()


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

    def test_import_data_from_model(self):
        class FakeModel(BaseModel):
            testField1 = BaseField()
            testField3 = BaseField()

        data = {'testField1': 'Value1', 'testField3': 'No matters'}
        model1 = FakeModel(data)

        model2 = FakeModel()

        model2.import_data(model1)

        self.assertDictEqual(model1.export_data(), model2.export_data())

    def test_copy_model(self):
        class FakeModel(BaseModel):
            testField1 = BaseField()
            testField3 = BaseField()

        data = {'testField1': 'Value1', 'testField3': 'No matters'}
        model1 = FakeModel(data)

        model2 = model1.copy()

        self.assertDictEqual(model1.export_data(), model2.export_data())
        self.assertNotEqual(id(model1), id(model2))

    def _get_test_model_instance(self):

        class TestExportModel(BaseModel):
            testField1 = BaseField()
            testField2 = BaseField()
            testField3 = BaseField()
            testFieldModel = ModelField()

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

    def test_export_deleted_fields_1st_level(self):

        model_field = self._get_test_model_instance()
        model_field.import_data({
            'testField1': 'Field Value1', 'testField2': 'Field Value2',
            'testField3': 'Field Value3',
            'testFieldModel': {'testField3': 'Field Value3'}})

        model_field.flat_data()

        del model_field.testField1
        del model_field.testField2

        self.assertEqual(model_field.export_deleted_fields(), ['testField1', 'testField2'])

    def test_export_deleted_fields_2nd_level(self):

        model_field = self._get_test_model_instance()
        model_field.import_data({
            'testField1': 'Field Value1', 'testField2': 'Field Value2',
            'testField3': 'Field Value3',
            'testFieldModel': {'testField3': 'Field Value3'}})

        model_field.flat_data()

        del model_field.testField1
        del model_field.testField2
        del model_field.testFieldModel.testField3

        self.assertEqual(model_field.export_deleted_fields(), ['testField1', 'testField2',
                                                               'testFieldModel.testField3'])

    def test_export_deleted_with_array_fields(self):

        class TestModel(BaseModel):

            field_1 = IntegerField()
            field_2 = ArrayField(field_type=ModelField(model_class=PicklableModel))
            field_3 = ArrayField(field_type=IntegerField())

        model = TestModel()
        model.import_data({'field_1': '23', 'field_2': [{'field_2': 12, 'field_1': {'field_2': 122}}],
                           'field_3': [12, '23']})
        model.flat_data()
        del model.field_1
        del model.field_2[0].field_2
        del model.field_3[1]
        self.assertEqual(model.export_deleted_fields(), ['field_1', 'field_2.0.field_2'])

    def test_import_deleted_fields(self):

        class TestModel(BaseModel):

            field_1 = IntegerField()
            field_2 = ArrayField(field_type=ModelField(model_class=PicklableModel))
            field_3 = ArrayField(field_type=IntegerField())

        model = TestModel()
        model.import_data({'field_1': '23', 'field_2': [{'field_2': 12, 'field_1': {'field_2': 122}}],
                           'field_3': [12, '23']})

        deleted_fields = ['field_1', 'field_2.0.field_2']
        model.import_deleted_fields(deleted_fields)
        self.assertEqual(model.export_data(), {'field_2': [{'field_1': {'field_2': 122}}], 'field_3': [12, 23]})

    def test_export_original_data(self):

        class TestModel(BaseModel):

            field_1 = IntegerField()
            field_2 = ArrayField(field_type=ModelField(model_class=PicklableModel))
            field_3 = ArrayField(field_type=IntegerField())

        model = TestModel()
        model.import_data({'field_1': '23', 'field_2': [{'field_2': 12, 'field_1': {'field_2': 122}}],
                           'field_3': [12, '23']})
        model.flat_data()

        model.field_1 = 123
        model.field_3.append(124)
        del model.field_2[0].field_2
        model.field_2.append({'field_2': 234134})
        self.assertEqual(model.export_original_data(), {'field_1': 23,
                                                        'field_2': [{'field_2': 12, 'field_1': {'field_2': 122}}],
                                                        'field_3': [12, 23]})

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
        self.assertTrue(self.model.is_modified())
        self.model.flat_data()
        self.assertEqual(self.model._deleted_fields, [])
        self.assertEqual(self.model._modified_data, {})
        self.assertFalse(self.model.is_modified())

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

    def test_fields_empty(self):
        model = self._get_test_model_instance()

        self.assertEqual(model.get_fields(), [])

    def test_fields_modified_data(self):
        model = self._get_test_model_instance()
        model.testField1 = 'a'
        model.testField2 = 'b'
        model.testField3 = 'c'

        self.assertEqual(sorted(model.get_fields()), ['testField1', 'testField2', 'testField3'])

    def test_reset_field_value(self):
        model = self._get_test_model_instance()
        model.testField1 = 'a'
        model.testField2 = 'b'
        model.testField3 = 'c'

        model.flat_data()

        self.assertEqual(model.testField3, 'c')
        model.testField3 = 'cccc'
        self.assertEqual(model.testField3, 'cccc')
        model.reset_field_value('testField3')
        self.assertEqual(model.testField3, 'c')
        del model.testField3

        model.reset_field_value('testField3')
        self.assertEqual(model.testField3, 'c')

    def test_is_modified_field(self):
        model = self._get_test_model_instance()
        model.testField1 = 'a'
        model.testField2 = 'b'
        model.testField3 = 'c'

        model.flat_data()

        self.assertFalse(model.is_modified_field('testField1'))
        self.assertFalse(model.is_modified_field('testField2'))
        self.assertFalse(model.is_modified_field('testField3'))

        model.testField3 = 'cccc'
        self.assertTrue(model.is_modified_field('testField3'))

    def test_fields_original_data(self):
        model = self._get_test_model_instance()
        model.testField1 = 'a'

        model.flat_data()

        model.testField3 = 'c'

        self.assertEqual(sorted(model.get_fields()), ['testField1', 'testField3'])

    def test_fields_deleted_data(self):
        model = self._get_test_model_instance()
        model.testField1 = 'a'
        model.testField2 = 'b'
        model.testField3 = 'c'

        model.flat_data()

        del model.testField2

        self.assertEqual(sorted(model.get_fields()), ['testField1', 'testField3'])

    def test_iter_model(self):
        class FakeModel(BaseModel):
            testField1 = BaseField()
            testField3 = BaseField()

        data = {'testField1': 'Value1', 'testField3': 'No matters'}
        model = FakeModel(data)

        for t in model:
            self.assertIsInstance(t, tuple)
            self.assertEqual(len(t), 2)
            self.assertIsInstance(t[0], str)
            self.assertIn(t[0], data.keys(), "Field name " + t[0])
            del data[t[0]]

        self.assertEqual(data, {}, "Empty data")

    def test_pickle(self):
        model = PicklableModel()
        model.field_2 = 23
        model.field_1 = {'field_2': 122}
        model.flat_data()
        del model.field_2
        model.field_1.field_2 = 133
        model_unpickled = pickle.loads(pickle.dumps(model))
        self.assertNotEqual(id(model), id(model_unpickled))
        self.assertEqual(model_unpickled.export_data(), model.export_data())
        self.assertEqual(model_unpickled.export_original_data(), model.export_original_data())
        self.assertEqual(model_unpickled.export_modified_data(), model.export_modified_data())
        self.assertEqual(model_unpickled.export_deleted_fields(), model.export_deleted_fields())

    def test_object_creation_test_with_alias(self):

        class FakeModel(BaseModel):
            testField1 = BaseField(
                alias={
                    'alias_1_test_field_1',
                    'alias_2_test_field_1'
                }
            )

        data = {'testField1': 'Value1'}
        model_object = FakeModel(data)
        self.assertEqual(model_object.testField1, 'Value1')
        self.assertEqual(model_object.alias_1_test_field_1, 'Value1')
        self.assertEqual(model_object.alias_2_test_field_1, 'Value1')


class ModelReadOnly(BaseModel):
    testField1 = BaseField()
    testField2 = BaseField(read_only=True)
    testField3 = BaseField()
    testFieldModel = ModelField(read_only=True)
    testFieldList = ArrayField(read_only=True, field_type=IntegerField())
    testFieldModelList = ArrayField(read_only=True, field_type=ModelField())


class TestModelReadOnly(TestCase):

    def test_no_writing(self):
        data = {
            'testField1': 1, 'testField2': 2, 'testField3': 3,
            'testFieldList': [45, 56, 23, 676, 442, 242],
            'testFieldModel': {'testField1': 61, 'testField2': 51, 'testField3': 41,
                               'testFieldList': [5, 6, 3, 66, 42, 22]},
            'testFieldModelList': [{'testField1': 61, 'testField2': 51, 'testField3': 41,
                                    'testFieldList': [5, 6, 3, 66, 42, 22]},
                                   {'testField1': 61, 'testField2': 51, 'testField3': 41,
                                    'testFieldList': [5, 6, 3, 66, 42, 22]}]
        }

        model = ModelReadOnly(data)
        model.flat_data()

        model.testField2 = 99
        self.assertEqual(model.testField2, 2, 'Read only simple field')
        self.assertFalse(model.is_modified())
        self.assertTrue(model.is_locked())

        model.testFieldModel.testField1 = 99
        self.assertEqual(model.testFieldModel.testField1, 61, 'Read only embedded field')
        self.assertFalse(model.is_modified())

        model.testFieldModel.testFieldList.append(99)
        self.assertEqual(model.testFieldModel.testFieldList.export_data(),
                         [5, 6, 3, 66, 42, 22], 'Read only list field')
        self.assertFalse(model.is_modified())

        model.testFieldModelList[0].testField1 = 99
        print(model.testFieldModelList.get_read_only())
        self.assertEqual(model.testFieldModelList[0].testField1, 61, 'Read only inside list field')
        self.assertFalse(model.is_modified())

    def test_unlock_writing(self):
        data = {
            'testField1': 1, 'testField2': 2, 'testField3': 3,
            'testFieldList': [45, 56, 23, 676, 442, 242],
            'testFieldModel': {'testField1': 61, 'testField2': 51, 'testField3': 41,
                               'testFieldList': [5, 6, 3, 66, 42, 22]},
            'testFieldModelList': [{'testField1': 61, 'testField2': 51, 'testField3': 41,
                                    'testFieldList': [5, 6, 3, 66, 42, 22]},
                                   {'testField1': 61, 'testField2': 51, 'testField3': 41,
                                    'testFieldList': [5, 6, 3, 66, 42, 22]}]
        }

        model = ModelReadOnly(data)
        model.flat_data()

        model.unlock()

        model.testField2 = 99
        self.assertEqual(model.testField2, 99, 'Read only simple field')
        self.assertTrue(model.is_modified())

        model.testField2 = 2
        self.assertFalse(model.is_modified())

        model.testFieldModel.testField1 = 99
        self.assertEqual(model.testFieldModel.testField1, 99, 'Read only embedded field')
        self.assertTrue(model.is_modified())

        model.testFieldModel.testField1 = 61
        self.assertFalse(model.is_modified())

        model.testFieldModelList[0].testField1 = 99
        self.assertEqual(model.testFieldModelList[0].testField1, 99, 'Read only inside list field')
        self.assertTrue(model.is_modified())

        model.testFieldModelList[0].testField1 = 61
        self.assertFalse(model.is_modified())

        model.testFieldModel.testFieldList.append(99)
        self.assertEqual(model.testFieldModel.testFieldList.export_data(),
                         [5, 6, 3, 66, 42, 22, 99], 'Read only list field')
        self.assertTrue(model.is_modified())

        self.assertFalse(model.is_locked())

    def test_unlocklocker(self):
        data = {
            'testField1': 1, 'testField2': 2, 'testField3': 3,
            'testFieldList': [45, 56, 23, 676, 442, 242],
            'testFieldModel': {'testField1': 61, 'testField2': 51, 'testField3': 41,
                               'testFieldList': [5, 6, 3, 66, 42, 22]},
            'testFieldModelList': [{'testField1': 61, 'testField2': 51, 'testField3': 41,
                                    'testFieldList': [5, 6, 3, 66, 42, 22]},
                                   {'testField1': 61, 'testField2': 51, 'testField3': 41,
                                    'testFieldList': [5, 6, 3, 66, 42, 22]}]
        }

        model = ModelReadOnly(data)
        model.flat_data()

        with Unlocker(model):

            model.testField2 = 99
            self.assertEqual(model.testField2, 99, 'Read only simple field')
            self.assertTrue(model.is_modified())

            model.testField2 = 2
            self.assertFalse(model.is_modified())

            model.testFieldModel.testField1 = 99
            self.assertEqual(model.testFieldModel.testField1, 99, 'Read only embedded field')
            self.assertTrue(model.is_modified())

            model.testFieldModel.testField1 = 61
            self.assertFalse(model.is_modified())

            model.testFieldModelList[0].testField1 = 99
            self.assertEqual(model.testFieldModelList[0].testField1, 99, 'Read only inside list field')
            self.assertTrue(model.is_modified())

            model.testFieldModelList[0].testField1 = 61
            self.assertFalse(model.is_modified())

            model.testFieldModel.testFieldList.append(99)
            self.assertEqual(model.testFieldModel.testFieldList.export_data(),
                             [5, 6, 3, 66, 42, 22, 99], 'Read only list field')
            self.assertTrue(model.is_modified())

            self.assertFalse(model.is_locked())

        self.assertTrue(model.is_locked())


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
        self.assertIsInstance(self.model.__class__.__dict__['test1'].field_type, StringField)

    def test_set_empty_list_value(self):
        self.model.test1 = []

        with self.assertRaises(AttributeError):
            self.model.test1

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

    def test_pickle(self):
        self.model.test1 = 1
        pickled = pickle.dumps(self.model)
        self.assertEqual(pickle.loads(pickled).export_data(), self.model.export_data())

    def test_copy_model(self):

        self.model.field1 = 'field1'
        self.model.field2 = 'field2'
        model2 = self.model.copy()
        self.model.field2 = 'field2modified'

        self.assertEqual(self.model.field1, model2.field1)
        self.assertNotEqual(self.model.field2, model2.field2)
        self.assertNotEqual(id(self.model), id(model2))

    def test_documentation_default(self):
        class DeviceModel(BaseModel):
            field_1 = IntegerField()
            field_2 = IntegerField(read_only=True)
            field_3 = ArrayField(field_type=ModelField(model_class=IntegerField))

        self.assertEqual(DeviceModel.field_1.__doc__, 'IntegerField field')
        self.assertEqual(DeviceModel.field_2.__doc__, 'IntegerField field [READ ONLY]')
        self.assertEqual(DeviceModel.field_3.__doc__,
                         'Array of ModelField field (:class:`dirty_models.fields.IntegerField`)')
