import pickle
from datetime import date, datetime, time, timedelta
from unittest import TestCase

from enum import Enum
from functools import partial

from dirty_models.base import Unlocker
from dirty_models.fields import ArrayField, BaseField, BooleanField, DateField, DateTimeField, EnumField, FloatField, \
    HashMapField, IntegerField, ModelField, MultiTypeField, StringField, TimeField, TimedeltaField
from dirty_models.models import BaseModel, CamelCaseMeta, DynamicModel, FastDynamicModel, HashMapModel
from dirty_models.utils import factory

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
        self.model.__original_data__ = INITIAL_DATA

    def tearDown(self):
        self.model.clear_all()

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

        self.assertEqual(str(model_object), "FakeModel('testField1': 'Value1','testField3': 'Value3')")

    def test_set_initial_value(self):
        self.model.__original_data__ = {}
        self.model.set_field_value('testField1', 'whatever')
        self.assertIsNone(self.model.__original_data__.get('testField1'))
        self.assertEqual('whatever', self.model.__modified_data__['testField1'])

    def test_set_value_to_modify(self):
        self.model.set_field_value('testField1', 'whatever')
        self.assertEqual(INITIAL_DATA['testField1'],
                         self.model.__original_data__['testField1'])
        self.assertEqual('whatever', self.model.__modified_data__['testField1'])

    def test_set_value_already_modified_with_previous_value(self):
        self.model.__modified_data__ = {'testField1': 'modifiedValue1'}
        self.model.set_field_value('testField1', INITIAL_DATA['testField1'])
        self.assertEquals(self.model.__original_data__['testField1'],
                          INITIAL_DATA['testField1'])
        self.assertEquals({}, self.model.__modified_data__)

    def test_delete_value(self):
        self.model.delete_field_value('testField1')
        self.assertEqual(INITIAL_DATA['testField1'],
                         self.model.__original_data__['testField1'])
        self.assertTrue('testField1' in self.model.__deleted_fields__)

    def test_set_value_deleted(self):
        self.model.delete_field_value('testField1')
        self.assertTrue('testField1' in self.model.__deleted_fields__)
        self.model.set_field_value('testField1', 'undelete')
        self.assertFalse('testField1' in self.model.__deleted_fields__)
        self.assertEquals('undelete', self.model.__modified_data__['testField1'])

    def test_delete_modified_value(self):
        self.model.__modified_data__ = {'testField1': 'modifiedValue1'}
        self.model.delete_field_value('testField1')
        self.assertEquals({}, self.model.__modified_data__)
        self.assertTrue('testField1' in self.model.__deleted_fields__)

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

    def test_import_nulled_data(self):
        self.model.import_data(INITIAL_DATA)
        self.assertTrue(hasattr(self.model, 'testField1'))

        self.model.import_data({'testField1': None})
        self.assertIsNone(self.model.testField1)

    def test_import_invalid_data(self):
        with self.assertRaises(TypeError):
            self.model.import_data('invalid data')

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
            test_field4 = BaseField(name="testField4")
            testFieldModel = ModelField()

        return TestExportModel()

    def test_export_data(self):
        model_field = self._get_test_model_instance()
        model_field.__original_data__ = {'testField1': 'Field Value1',
                                         'testField2': 'Field Value2'}
        model_field.__modified_data__ = {'testField2': 'Field Value2 Modified'}

        self.model.__modified_data__ = {'testField1': 'Value1Modified',
                                        'testField2': 'Value2Modified',
                                        'testField3': 'Value3',
                                        'testField4': model_field}
        self.model.__deleted_fields__ = ['testField2', 'testField3']
        exported_data = self.model.export_data()
        self.assertEqual(exported_data, {'testField1': 'Value1Modified',
                                         'testField4':
                                             {'testField2': 'Field Value2 Modified',
                                              'testField1': 'Field Value1'}})

    def test_export_modified(self):
        model_field = self._get_test_model_instance()
        model_field.__original_data__ = {
            'testField1': 'Field Value1', 'testField2': 'Field Value2',
            'testField3': 'Field Value3'}
        model_field.__modified_data__ = {'testField2': 'Field Value2 Modified'}
        model_field.__deleted_fields__ = ['testField3']

        self.model.__modified_data__ = {'testField1': 'Value1Modified',
                                        'testField3': 'Value3',
                                        'testField4': model_field}
        self.model.__deleted_fields__ = ['testField3']
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

        deleted_fields = ['field_1', 'field_fake', 'field_2.0.field_2']
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

        self.assertIsNone(model.get_original_field_value('foo'))

    def test_flat_data(self):
        model_field = self._get_test_model_instance()
        model_field.__original_data__ = {'testField1': 'Field Value1',
                                         'testField2': 'Field Value2'}
        model_field.__modified_data__ = {'testField2': 'Field Value2 Modified'}

        self.model.__modified_data__ = {'testField1': 'Value1Modified',
                                        'testField2': 'Value2Modified',
                                        'testField3': 'Value3',
                                        'testField4': model_field}
        self.model.__deleted_fields__ = ['testField2', 'testField3']
        self.assertTrue(model_field.is_modified())
        self.model.flat_data()
        self.assertEqual(self.model.__deleted_fields__, [])
        self.assertEqual(self.model.__modified_data__, {})
        self.assertFalse(self.model.is_modified())

        self.assertEqual(set(self.model.__original_data__.keys()),
                         set(['testField1', 'testField4']))
        self.assertEqual(
            self.model.__original_data__['testField1'], 'Value1Modified')
        self.assertEqual(
            self.model.__original_data__['testField4'].__original_data__,
            {'testField1': 'Field Value1',
             'testField2': 'Field Value2 Modified'})

    def test_clear(self):
        model_field = self._get_test_model_instance()
        model_field.__original_data__ = {'testField1': 'Field Value1',
                                         'testField2': 'Field Value2'}
        model_field.__modified_data__ = {'testField2': 'Field Value2 Modified'}

        model_field.__modified_data__ = {'testField1': 'Value1Modified',
                                         'testField2': 'Value2Modified',
                                         'testField3': 'Value3',
                                         'testField4': model_field}
        model_field.__deleted_fields__ = ['testField2', 'testField3']
        self.assertTrue(model_field.is_modified())
        model_field.clear()
        self.assertTrue(model_field.is_modified())
        self.assertEqual(sorted(model_field.__deleted_fields__), sorted(['testField1', 'testField2']))
        self.assertEqual(model_field.__modified_data__, {})
        self.assertEqual(model_field.__original_data__, {'testField1': 'Field Value1',
                                                         'testField2': 'Field Value2'})

    def test_clear_all(self):
        model_field = self._get_test_model_instance()
        model_field.__original_data__ = {'testField1': 'Field Value1',
                                         'testField2': 'Field Value2'}
        model_field.__modified_data__ = {'testField2': 'Field Value2 Modified'}

        model_field.__modified_data__ = {'testField1': 'Value1Modified',
                                         'testField2': 'Value2Modified',
                                         'testField3': 'Value3',
                                         'testField4': model_field}
        model_field.__deleted_fields__ = ['testField2', 'testField3']
        self.assertTrue(model_field.is_modified())
        model_field.clear_all()
        self.assertFalse(model_field.is_modified())
        self.assertEqual(model_field.__deleted_fields__, [])
        self.assertEqual(model_field.__modified_data__, {})
        self.assertEqual(model_field.__original_data__, {})

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
        model.test_field4 = 'd'

        model.flat_data()

        self.assertFalse(model.is_modified_field('testField1'))
        self.assertFalse(model.is_modified_field('testField2'))
        self.assertFalse(model.is_modified_field('testField3'))
        self.assertFalse(model.is_modified_field('test_field4'))

        model.testField3 = 'cccc'
        model.test_field4 = 'dddd'
        self.assertTrue(model.is_modified_field('testField3'))
        self.assertTrue(model.is_modified_field('test_field4'))

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

    def test_fields_nulled_data(self):
        model = self._get_test_model_instance()
        model.testField1 = 'a'
        model.testField2 = 'b'
        model.testField3 = 'c'

        model.flat_data()

        model.testField2 = None

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
                alias=[
                    'alias_1_test_field_1',
                    'alias_2_test_field_1'
                ]
            )

        data = {'testField1': 'Value1'}
        model_object = FakeModel(data)
        self.assertEqual(model_object.testField1, 'Value1')
        self.assertEqual(model_object.alias_1_test_field_1, 'Value1')
        self.assertEqual(model_object.alias_2_test_field_1, 'Value1')

    def test_object_creation_test_with_getter(self):
        def getter_function(self, instance, value):
            return 'getter_function'

        class FakeModel(BaseModel):
            testField1 = BaseField(
                getter=getter_function
            )

        data = {'testField1': 'Value1'}
        model_object = FakeModel(data)
        self.assertEqual(model_object.testField1, 'getter_function')

    def test_object_creation_test_with_setter(self):
        def setter_function(self, instance, value):
            self.set_value(instance, self.use_value('setter_function'))

        class FakeModel(BaseModel):
            testField1 = BaseField(
                setter=setter_function
            )

        data = {'testField1': 'Value1'}
        model_object = FakeModel(data)

        self.assertEqual(model_object.testField1, 'setter_function')

    def test_object_model_field_creation_test_with_setter(self):
        def setter_function(self, instance, value):
            data = {'testBaseField1': 'setter_function'}
            super(ModelField, self).__set__(instance, data)

        class FakeBaseModel(BaseModel):
            testBaseField1 = BaseField()

        class FakeModel(BaseModel):
            testField1 = ModelField(
                model_class=FakeBaseModel,
                setter=setter_function
            )

        data = {'testBaseField1': 'Value1'}
        model_base_object = FakeBaseModel(data)

        data = {'testField1': model_base_object}
        model_object = FakeModel(data)

        self.assertEqual(model_object.testField1.testBaseField1, 'setter_function')

    def test_object_model_field_with_on_set_callback(self):
        def update_testField2(model_object, field_name):
            model_object.testField2 = field_name

        class FakeModel(BaseModel):
            testField1 = BaseField(on_set=update_testField2)
            testField2 = BaseField()

        model_object = FakeModel()
        self.assertIsNone(model_object.testField2)
        model_object.testField1 = "Value1"
        self.assertEqual(model_object.testField2, "testField1")

    def test_get_field_obj(self):
        class FakeModel(BaseModel):
            testField1 = BaseField()

        data = {'testField1': 'Value1'}
        model_object = FakeModel(data)

        test_field_obj = model_object.get_field_obj('testField1')

        self.assertIsInstance(test_field_obj, BaseField)

    def test_delete_attr_by_path(self):
        class FakeBaseModel(BaseModel):
            testBaseField1 = BaseField()
            testBaseField2 = IntegerField()

        class FakeModel(BaseModel):
            testField1 = ModelField(model_class=FakeBaseModel)
            testField2 = IntegerField()

        data = {'testBaseField1': 'Value1', 'testBaseField2': 19}
        model_base_object = FakeBaseModel(data)

        data = {'testField1': model_base_object, 'testField2': 11}
        model_object = FakeModel(data)

        self.assertIsNotNone(model_object.testField1.testBaseField2)
        model_object.delete_attr_by_path('testField1.testBaseField2')
        self.assertIsNone(model_object.testField1.testBaseField2)

    def test_delete_attr_by_path_with_list_model(self):
        class EvenMoreFakeBaseModel(BaseModel):
            bruceWayneField = IntegerField()

        class FakeBaseModel(BaseModel):
            testBaseField1 = BaseField()
            testBaseField2 = IntegerField()
            testBaseField3 = ArrayField(field_type=IntegerField())
            testBaseField4 = ArrayField(field_type=ModelField(model_class=EvenMoreFakeBaseModel))

        class FakeModel(BaseModel):
            testField1 = ModelField(model_class=FakeBaseModel)
            testField2 = IntegerField()

        data = {'bruceWayneField': 45}
        model_1 = EvenMoreFakeBaseModel(data)

        data = {'testBaseField1': 'Value1', 'testBaseField2': 19, 'testBaseField3': [11, 12, 14, 'paco'],
                'testBaseField4': [model_1]}
        model_2 = FakeBaseModel(data)

        data = {'testField1': model_2, 'testField2': 11}
        model_object = FakeModel(data)
        self.assertIsNotNone(model_object.testField1.testBaseField2)
        self.assertIsNotNone(model_object.testField1.testBaseField3[2])
        self.assertIsNotNone(model_object.testField1.testBaseField4[0].bruceWayneField)
        model_object.delete_attr_by_path('testField1.testBaseField2')
        model_object.delete_attr_by_path('testField1.testBaseField3.2')
        model_object.delete_attr_by_path('testField1.testBaseField4.*.bruceWayneField')
        model_object.delete_attr_by_path('testField1.testBaseField3.*.nonExistingField')
        self.assertIsNone(model_object.testField1.testBaseField2)
        self.assertRaises(IndexError, model_object.testField1.testBaseField3.__getitem__, 2)
        self.assertIsNone(model_object.testField1.testBaseField4[0].bruceWayneField)
        self.assertIsNone(model_object.testField1.testBaseField4[0].bruceWayneField)

    def test_delete_attr_by_path_with_list_model_empty_list(self):
        class FakeBaseModel(BaseModel):
            testBaseField1 = BaseField()
            testBaseField2 = IntegerField()
            testBaseField3 = ArrayField(field_type=IntegerField())

        class FakeModel(BaseModel):
            testField1 = ModelField(model_class=FakeBaseModel)
            testField2 = IntegerField()

        data = {'testBaseField1': 'Value1', 'testBaseField2': 19, 'testBaseField3': []}
        model_2 = FakeBaseModel(data)

        data = {'testField1': model_2, 'testField2': 11}
        model_object = FakeModel(data)

        self.assertIsNotNone(model_object.testField1.testBaseField3)
        model_object.delete_attr_by_path('testField1.testBaseField3.*')
        self.assertIsNotNone(model_object.testField1.testBaseField3)

    def test_delete_attr_by_path_whole_list(self):
        class EvenMoreFakeBaseModel(BaseModel):
            bruceWayneField = IntegerField()

        class FakeBaseModel(BaseModel):
            testBaseField1 = BaseField()
            testBaseField2 = IntegerField()
            testBaseField3 = ArrayField(field_type=IntegerField())
            testBaseField4 = ArrayField(field_type=ModelField(model_class=EvenMoreFakeBaseModel))

        class FakeModel(BaseModel):
            testField1 = ModelField(model_class=FakeBaseModel)
            testField2 = IntegerField()

        data = {'bruceWayneField': 45}
        model_1 = EvenMoreFakeBaseModel(data)

        data = {'testBaseField1': 'Value1', 'testBaseField2': 19, 'testBaseField3': [11, 12, 14, 'paco'],
                'testBaseField4': [model_1]}
        model_2 = FakeBaseModel(data)

        data = {'testField1': model_2, 'testField2': 11}
        model_object = FakeModel(data)
        self.assertIsNotNone(model_object.testField1.testBaseField3[2])
        self.assertIsNotNone(model_object.testField1.testBaseField4[0].bruceWayneField)
        model_object.delete_attr_by_path('testField1.testBaseField3.*')
        model_object.delete_attr_by_path('testField1.testBaseField4.0.bruceWayneField')
        model_object.delete_attr_by_path('testField1.testBaseField4.3.bruceWayneField')

        with self.assertRaises(IndexError):
            model_object.testField1.testBaseField3[2]

        self.assertIsNone(model_object.testField1.testBaseField4[0].bruceWayneField)

    def test_reset_attr_by_path_with_lists(self):
        class EvenMoreFakeBaseModel(BaseModel):
            bruceWayneField = IntegerField()

        class FakeBaseModel(BaseModel):
            testBaseField1 = BaseField()
            testBaseField2 = IntegerField()
            testBaseField3 = ArrayField(field_type=IntegerField())
            testBaseField4 = ArrayField(field_type=ModelField(model_class=EvenMoreFakeBaseModel))

        class FakeModel(BaseModel):
            testField1 = ModelField(model_class=FakeBaseModel)
            testField2 = IntegerField()

        data = {'bruceWayneField': 45}
        model_1 = EvenMoreFakeBaseModel(data)

        data = {'testBaseField1': 'Value1', 'testBaseField2': 19, 'testBaseField3': [11, 12, 14, 'paco'],
                'testBaseField4': [model_1]}
        model_2 = FakeBaseModel(data)

        data = {'testField1': model_2, 'testField2': 11}
        model_object = FakeModel(data)

        model_object.flat_data()

        model_object.testField1.testBaseField3[2] = 25
        model_object.testField1.testBaseField4[0].bruceWayneField = 22
        self.assertEqual(model_object.testField1.testBaseField3[2], 25)
        self.assertEqual(model_object.testField1.testBaseField4[0].bruceWayneField, 22)
        model_object.reset_attr_by_path('testField1.testBaseField4.*.bruceWayneField')
        model_object.reset_attr_by_path('testField1.testBaseField3.2')
        self.assertEqual(model_object.testField1.testBaseField3[2], 25)
        self.assertEqual(model_object.testField1.testBaseField4[0].bruceWayneField, 45)

    def test_reset_attr_by_path(self):
        class FakeBaseModel(BaseModel):
            testBaseField1 = BaseField()
            testBaseField2 = IntegerField()

        class FakeModel(BaseModel):
            testField1 = ModelField(model_class=FakeBaseModel)
            testField2 = IntegerField()

        data = {'testBaseField1': 'Value1', 'testBaseField2': 19}
        model_base_object = FakeBaseModel(data)

        data = {'testField1': model_base_object, 'testField2': 11}
        model_object = FakeModel(data)
        model_object.flat_data()

        model_object.testField1.testBaseField2 = 22

        self.assertEqual(model_object.testField1.testBaseField2, 22)
        model_object.reset_attr_by_path('testField1.testBaseField2')
        self.assertEqual(model_object.testField1.testBaseField2, 19)

    def test_reset_attr_by_path_with_flag(self):
        class FakeBaseModel(BaseModel):
            testBaseField1 = BaseField()
            testBaseField2 = IntegerField()

        class FakeModel(BaseModel):
            testField1 = ModelField(model_class=FakeBaseModel)
            testField2 = IntegerField()

        data = {'testBaseField1': 'Value1', 'testBaseField2': 19}
        model_base_object = FakeBaseModel(data)

        data = {'testField1': model_base_object, 'testField2': 11}
        model_object = FakeModel(data)
        model_object.flat_data()

        model_object.testField1.testBaseField2 = 22
        model_object.testField1.testBaseField1 = 'Value2'
        model_object.testField2 = 22

        self.assertEqual(model_object.testField2, 22)
        self.assertEqual(model_object.testField1.testBaseField1, 'Value2')
        self.assertEqual(model_object.testField1.testBaseField2, 22)
        model_object.reset_attr_by_path('testField1.*')
        model_object.reset_attr_by_path('testField2.*')
        self.assertEqual(model_object.testField2, 22)
        self.assertEqual(model_object.testField1.testBaseField2, 19)
        self.assertEqual(model_object.testField1.testBaseField1, 'Value1')

    def test_to_str(self):
        class TestModel(BaseModel):
            field_1 = IntegerField()
            field_2 = ArrayField(field_type=ModelField(model_class=PicklableModel))
            field_3 = ArrayField(field_type=IntegerField())

        model = TestModel()
        model.import_data({'field_1': '23', 'field_2': [{'field_2': 12, 'field_1': {'field_2': 122}}],
                           'field_3': [12, '23']})

        self.assertEqual(str(model), "TestModel('field_1': 23,'field_2': [PicklableModel('field_1': PicklableModel("
                                     "'field_2': 122),'field_2': 12)],'field_3': [12, 23])")

    def test_get_structure(self):
        model = self._get_test_model_instance()

        s = model.get_structure()

        self.assertIn('testField1', s)
        self.assertIsInstance(s['testField1'], BaseField)

        self.assertIn('testField2', s)
        self.assertIsInstance(s['testField2'], BaseField)

        self.assertIn('testField3', s)
        self.assertIsInstance(s['testField3'], BaseField)

        self.assertIn('testField4', s)
        self.assertIsInstance(s['testField4'], BaseField)

        self.assertIn('testFieldModel', s)
        self.assertIsInstance(s['testFieldModel'], ModelField)


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

    def test_import_delete_fields_readonly(self):
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

        model.testFieldModel.import_deleted_fields(['testField1'])
        self.assertEqual(model.testFieldModel.testField1, 61)

    def test_documentation_default(self):
        class TestModel(BaseModel):
            field_1 = IntegerField()
            field_2 = IntegerField(read_only=True)
            field_3 = ArrayField(field_type=ModelField(model_class=IntegerField))

        self.assertEqual(TestModel.field_1.__doc__, 'IntegerField field')
        self.assertEqual(TestModel.field_2.__doc__, 'IntegerField field [READ ONLY]')
        self.assertEqual(TestModel.field_3.__doc__,
                         'Array of ModelField field (:class:`dirty_models.fields.IntegerField`)')

    def test_import_data_readonly(self):
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

        model.testFieldModel.import_data({'testField1': 2})
        self.assertEqual(model.testFieldModel.testField1, 61)


class TestDynamicModel(TestCase):

    def setUp(self):
        self.model = DynamicModel()
        self.dict_model = DynamicModel

    def tearDown(self):
        self.model.clear_all()

    def _get_field_type(self, name):
        try:
            return self.model.get_field_obj(name)
        except KeyError:
            return None

    def test_set_int_value(self):
        self.model.test1 = 1
        self.assertEqual(self.model.test1, 1)
        self.assertIsInstance(self._get_field_type('test1'), IntegerField)

        newmodel = DynamicModel()
        newmodel.test1 = "aaaa"
        self.assertEqual(newmodel.test1, "aaaa")

    def test_set_none_value(self):
        self.model.test1 = None
        self.assertIsNone(self._get_field_type('test1'))

    def test_set_float_value(self):
        self.model.test2 = 1.0
        self.assertEqual(self.model.test2, 1.0)
        self.assertIsInstance(self._get_field_type('test2'), FloatField)

    def test_set_bool_value(self):
        self.model.test2 = True
        self.assertTrue(self.model.test2)
        self.assertIsInstance(self._get_field_type('test2'), BooleanField)

    def test_set_str_value(self):
        self.model.test3 = "aass"
        self.assertEqual(self.model.test3, "aass")
        self.assertIsInstance(self._get_field_type('test3'), StringField)

    def test_set_datetime_value(self):
        self.model.test4 = datetime(year=2014, month=11, day=1)
        self.assertEqual(self.model.test4, datetime(year=2014, month=11, day=1))
        self.assertIsInstance(self._get_field_type('test4'), DateTimeField)

    def test_set_date_value(self):
        self.model.test4 = date(year=2014, month=11, day=1)
        self.assertEqual(self.model.test4, date(year=2014, month=11, day=1))
        self.assertIsInstance(self._get_field_type('test4'), DateField)

    def test_set_time_value(self):
        self.model.test4 = time(hour=23, minute=43, second=11)
        self.assertEqual(self.model.test4, time(hour=23, minute=43, second=11))
        self.assertIsInstance(self._get_field_type('test4'), TimeField)

    def test_set_timedelta_value(self):
        self.model.test4 = timedelta(seconds=3223)
        self.assertEqual(self.model.test4, timedelta(seconds=3223))
        self.assertIsInstance(self._get_field_type('test4'), TimedeltaField)

    def test_load_from_dict_value(self):
        self.model.import_data({"aa": "aaaaaa"})
        self.assertEqual(self.model.export_data(), {"aa": "aaaaaa"})
        self.assertIsInstance(self._get_field_type('aa'), StringField)

    def test_set_dict_value(self):
        self.model.test1 = {"aa": "aaaaaa"}
        self.assertEqual(self.model.export_data(), {"test1": {"aa": "aaaaaa"}})
        self.assertIsInstance(self._get_field_type('test1'), ModelField)
        self.assertEqual(self._get_field_type('test1').model_class, self.dict_model)

    def test_set_model_value(self):
        class FakeModel(BaseModel):
            test2 = IntegerField()

        self.model.test1 = FakeModel({"test2": 23})
        self.assertEqual(self.model.export_data(), {"test1": {"test2": 23}})
        self.assertIsInstance(self._get_field_type('test1'), ModelField)
        self.assertEqual(self._get_field_type('test1').model_class, FakeModel)

    def test_set_list_value(self):
        self.model.test1 = ["aa", "aaaaaa"]
        self.assertEqual(self.model.export_data(), {"test1": ["aa", "aaaaaa"]})
        self.assertIsInstance(self._get_field_type('test1'), ArrayField)
        self.assertIsInstance(self._get_field_type('test1').field_type, StringField)

    def test_set_enum_value(self):
        class TestEnum(Enum):
            value_1 = 1

        self.model.test1 = TestEnum.value_1
        self.assertEqual(self.model.export_data(), {"test1": TestEnum.value_1})
        self.assertIsInstance(self._get_field_type('test1'), EnumField)
        self.assertEqual(self._get_field_type('test1').enum_class, TestEnum)

    def test_set_empty_list_value(self):
        self.model.test1 = []

        self.assertIsNone(self.model.test1)

    def test_set_invalid_type_field_fail(self):
        with self.assertRaisesRegexp(TypeError, "Invalid parameter: test34. Type not supported."):
            self.model.test34 = (2, 2)

    def test_delete_field(self):
        self.model.test1 = 1
        self.assertEqual(self.model.test1, 1)
        self.assertIsInstance(self._get_field_type('test1'), IntegerField)

        del self.model.test1
        self.assertIsNone(self.model.test1)

    def test_nulled_field(self):
        self.model.test1 = 1
        self.assertEqual(self.model.test1, 1)
        self.assertIsInstance(self._get_field_type('test1'), IntegerField)

        self.model.test1 = None
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

    def test_is_modified_value(self):
        self.model.test3 = "aass"
        self.assertEqual(self.model.test3, "aass")
        self.assertTrue(self.model.is_modified())
        self.assertIsInstance(self._get_field_type('test3'), StringField)
        field_type = self._get_field_type('test3')
        self.model.flat_data()
        self.assertFalse(self.model.is_modified())
        self.model.test3 = "dddd"
        self.assertEqual(self.model.test3, "dddd")
        self.assertEqual(self._get_field_type('test3'), field_type)
        self.assertTrue(self.model.is_modified())
        self.assertTrue(self.model.is_modified_field('test3'))

    def test_import_none(self):
        self.model.import_data({'test': None})
        self.assertIsNone(self.model.test)


class TestFastDynamicModel(TestDynamicModel):

    def setUp(self):
        self.model = FastDynamicModel()
        self.dict_model = FastDynamicModel

    def _get_field_type(self, name):
        try:
            return self.model.__field_types__[name]
        except KeyError:
            return None


class FastDynamicModelExtraFields(FastDynamicModel):
    testField1 = StringField()


class TestFastDynamicModelExtraFields(TestDynamicModel):

    def setUp(self):
        self.model = FastDynamicModelExtraFields()
        self.dict_model = FastDynamicModel

    def _get_field_type(self, name):
        try:
            return self.model.__field_types__[name]
        except KeyError:
            return None

    def test_dyn_fields(self):
        self.model.testField2 = '1'
        self.model.testField3 = 1
        self.model.testField4 = 21
        self.model.testField5 = '212'
        self.assertEqual(self.model.testField2, '1')
        self.assertEqual(self.model.testField3, 1)
        self.assertEqual(self.model.testField4, 21)
        self.assertEqual(self.model.testField5, '212')

    def test_multi_fields(self):
        self.model.testField1 = 'aaaa'
        self.model.testField2 = '1'
        self.model.testField3 = 1
        self.model.testField4 = 21
        self.model.testField5 = '212'
        self.assertEqual(self.model.testField1, 'aaaa')
        self.assertEqual(self.model.testField2, '1')
        self.assertEqual(self.model.testField3, 1)
        self.assertEqual(self.model.testField4, 21)
        self.assertEqual(self.model.testField5, '212')

    def test_modified_fields(self):
        self.model.testField1 = 'aaaa'
        self.model.testField2 = '1'
        self.model.testField3 = 1
        self.model.testField4 = 21
        self.model.testField5 = '212'

        self.assertTrue(self.model.is_modified())
        self.model.flat_data()
        self.assertFalse(self.model.is_modified())
        self.model.testField4 = 21
        self.assertFalse(self.model.is_modified())
        self.model.testField4 = '241'
        self.assertTrue(self.model.is_modified())
        self.assertTrue(self.model.is_modified_field('testField4'))
        self.assertEqual(self.model.testField1, 'aaaa')
        self.assertEqual(self.model.testField2, '1')
        self.assertEqual(self.model.testField3, 1)
        self.assertEqual(self.model.testField4, 241)
        self.assertEqual(self.model.testField5, '212')

    def test_fail_type(self):
        self.model.testField2 = '1'
        self.assertTrue(self.model.is_modified())
        self.model.flat_data()
        self.assertFalse(self.model.is_modified())
        self.model.testField2 = {}
        self.assertFalse(self.model.is_modified())
        self.assertEqual(self.model.testField2, '1')

    def test_delete_fields(self):
        self.model.testField1 = 'aaaa'
        self.model.testField2 = '1'
        self.model.testField3 = 1
        self.model.testField4 = 21
        self.model.testField5 = '212'

        self.assertTrue(self.model.is_modified())
        self.model.flat_data()
        self.assertFalse(self.model.is_modified())
        self.model.testField4 = 21
        self.assertFalse(self.model.is_modified())
        del self.model.testField1
        del self.model.testField4
        self.assertTrue(self.model.is_modified())
        self.assertTrue(self.model.is_modified_field('testField4'))
        self.assertIsNone(self.model.testField1)
        self.assertEqual(self.model.testField2, '1')
        self.assertEqual(self.model.testField3, 1)
        self.assertIsNone(self.model.testField4)
        self.assertEqual(self.model.testField5, '212')

    def test_get_structure(self):
        self.model.testField1 = 'aaaa'
        self.model.testField2 = 1

        s = self.model.get_current_structure()

        self.assertIn('testField1', s)
        self.assertIsInstance(s['testField1'], StringField)
        self.assertIn('testField1', s)
        self.assertIsInstance(s['testField2'], IntegerField)


class PickableHashMapModel(HashMapModel):
    testField1 = StringField()


class TestHashMapModel(TestCase):

    def setUp(self):
        self.model = PickableHashMapModel(field_type=IntegerField())

    def test_fixed_fields(self):
        self.model.testField1 = 'aaaa'
        self.assertEqual(self.model.testField1, 'aaaa')

    def test_dyn_fields(self):
        self.model.testField2 = '1'
        self.model.testField3 = 1
        self.model.testField4 = 21
        self.model.testField5 = '212'
        self.assertEqual(self.model.testField2, 1)
        self.assertEqual(self.model.testField3, 1)
        self.assertEqual(self.model.testField4, 21)
        self.assertEqual(self.model.testField5, 212)

    def test_multi_fields(self):
        self.model.testField1 = 'aaaa'
        self.model.testField2 = '1'
        self.model.testField3 = 1
        self.model.testField4 = 21
        self.model.testField5 = '212'
        self.assertEqual(self.model.testField1, 'aaaa')
        self.assertEqual(self.model.testField2, 1)
        self.assertEqual(self.model.testField3, 1)
        self.assertEqual(self.model.testField4, 21)
        self.assertEqual(self.model.testField5, 212)

    def test_modified_fields(self):
        self.model.testField1 = 'aaaa'
        self.model.testField2 = '1'
        self.model.testField3 = 1
        self.model.testField4 = 21
        self.model.testField5 = '212'

        self.assertTrue(self.model.is_modified())
        self.model.flat_data()
        self.assertFalse(self.model.is_modified())
        self.model.testField4 = 21
        self.assertFalse(self.model.is_modified())
        self.model.testField4 = 241
        self.assertTrue(self.model.is_modified())
        self.assertTrue(self.model.is_modified_field('testField4'))
        self.assertEqual(self.model.testField1, 'aaaa')
        self.assertEqual(self.model.testField2, 1)
        self.assertEqual(self.model.testField3, 1)
        self.assertEqual(self.model.testField4, 241)
        self.assertEqual(self.model.testField5, 212)

    def test_delete_fields(self):
        self.model.testField1 = 'aaaa'
        self.model.testField2 = '1'
        self.model.testField3 = 1
        self.model.testField4 = 21
        self.model.testField5 = '212'

        self.assertTrue(self.model.is_modified())
        self.model.flat_data()
        self.assertFalse(self.model.is_modified())
        self.model.testField4 = 21
        self.assertFalse(self.model.is_modified())
        del self.model.testField1
        del self.model.testField4
        self.assertTrue(self.model.is_modified())
        self.assertTrue(self.model.is_modified_field('testField4'))
        self.assertIsNone(self.model.testField1)
        self.assertEqual(self.model.testField2, 1)
        self.assertEqual(self.model.testField3, 1)
        self.assertIsNone(self.model.testField4)
        self.assertEqual(self.model.testField5, 212)

    def test_nulled_fields(self):
        self.model.testField1 = 'aaaa'
        self.model.testField2 = '1'
        self.model.testField3 = 1
        self.model.testField4 = 21
        self.model.testField5 = '212'

        self.assertTrue(self.model.is_modified())
        self.model.flat_data()
        self.assertFalse(self.model.is_modified())
        self.model.testField4 = 21
        self.assertFalse(self.model.is_modified())
        self.model.testField1 = None
        self.model.testField4 = None
        self.assertTrue(self.model.is_modified())
        self.assertTrue(self.model.is_modified_field('testField4'))
        self.assertIsNone(self.model.testField1)
        self.assertEqual(self.model.testField2, 1)
        self.assertEqual(self.model.testField3, 1)
        self.assertIsNone(self.model.testField4)
        self.assertEqual(self.model.testField5, 212)

    def test_wrong_value(self):
        self.model.testField2 = 'aaaaa'
        self.assertIsNone(self.model.testField1)

    def test_pickle(self):
        self.model.testField1 = 'aaaa'
        self.model.testField2 = '1'
        self.model.testField3 = 1
        self.model.testField4 = 21
        self.model.testField5 = '212'
        self.model.flat_data()

        del self.model.testField2
        self.model.testField4 = 241

        model_unpickled = pickle.loads(pickle.dumps(self.model))
        self.assertNotEqual(id(self.model), id(model_unpickled))
        self.assertEqual(model_unpickled.export_data(), self.model.export_data())
        self.assertEqual(model_unpickled.export_original_data(), self.model.export_original_data())
        self.assertEqual(model_unpickled.export_modified_data(), self.model.export_modified_data())
        self.assertEqual(model_unpickled.export_deleted_fields(), self.model.export_deleted_fields())
        self.assertEqual(type(model_unpickled.get_field_type()), type(self.model.get_field_type()))
        self.assertEqual(model_unpickled.get_field_type().export_definition(),
                         self.model.get_field_type().export_definition())

    def test_copy_model(self):
        self.model.field1 = '1'
        self.model.field2 = '3'
        model2 = self.model.copy()
        self.model.field2 = '5'

        self.assertEqual(self.model.field1, model2.field1)
        self.assertNotEqual(self.model.field2, model2.field2)
        self.assertNotEqual(id(self.model), id(model2))

    def test_no_type_def(self):
        model = PickableHashMapModel()
        model.field1 = 'sdsd'
        self.assertEqual(model.field1, 'sdsd')

    def test_import_model(self):
        model = FastDynamicModel(data={'test1': 'test_string'})
        self.model.import_data(model)
        self.assertEqual(model.test1, 'test_string')


class SecondaryModel(BaseModel):
    field_integer = IntegerField(default=2)
    field_string = StringField(default='test')


class ModelDefaultValues(BaseModel):
    field_integer = IntegerField(default=1)
    field_string = StringField(default='foobar')
    field_boolean = BooleanField(default=True)
    field_float = FloatField(default=0.1)
    field_date = DateField(default=date(2016, 11, 23))
    field_time = TimeField(default=time(23, 56, 59))
    field_datetime = DateTimeField(default=datetime(2016, 11, 23, 23, 56, 59))
    field_array_integer = ArrayField(field_type=IntegerField(), default=[1, 3, 4])
    field_model = ModelField(model_class=SecondaryModel, default={"field_integer": 5})
    field_hashmap = HashMapField(field_type=StringField(), default={"item1": "aaaa",
                                                                    "item2": "bbbb"})


class TestDefaultValues(TestCase):

    def test_field_default_value(self):
        model = ModelDefaultValues()

        self.assertEqual(model.field_integer, 1)
        self.assertEqual(model.field_string, 'foobar')
        self.assertEqual(model.field_boolean, True)
        self.assertEqual(model.field_float, 0.1)
        self.assertEqual(model.field_date, date(2016, 11, 23))
        self.assertEqual(model.field_time, time(23, 56, 59))
        self.assertEqual(model.field_datetime, datetime(2016, 11, 23, 23, 56, 59))
        self.assertEqual(model.field_array_integer.export_data(), [1, 3, 4])
        self.assertEqual(model.field_model.export_data(), {"field_integer": 5,
                                                           "field_string": "test"})
        self.assertEqual(model.field_hashmap.export_data(), {"item1": "aaaa",
                                                             "item2": "bbbb"})

    def test_original_data(self):
        model = ModelDefaultValues()
        self.assertEqual(model.export_original_data(), {})

    def test_modified_data(self):
        model = ModelDefaultValues()
        self.assertEqual(model.export_modified_data(), {'field_array_integer': [1, 3, 4],
                                                        'field_boolean': True,
                                                        'field_date': date(2016, 11, 23),
                                                        'field_datetime': datetime(2016, 11, 23, 23, 56, 59),
                                                        'field_float': 0.1,
                                                        'field_hashmap': {'item1': 'aaaa', 'item2': 'bbbb'},
                                                        'field_integer': 1,
                                                        'field_model': {'field_integer': 5, 'field_string': 'test'},
                                                        'field_string': 'foobar',
                                                        'field_time': time(23, 56, 59)})

    def test_modify_model(self):
        model = ModelDefaultValues()
        del model.field_model
        del model.field_hashmap

        model.field_integer = 4
        model.field_string = 'test'

        self.assertEqual(model.export_modified_data(), {'field_array_integer': [1, 3, 4],
                                                        'field_boolean': True,
                                                        'field_date': date(2016, 11, 23),
                                                        'field_datetime': datetime(2016, 11, 23, 23, 56, 59),
                                                        'field_float': 0.1,
                                                        'field_integer': 4,
                                                        'field_string': 'test',
                                                        'field_time': time(23, 56, 59)})


class ModelGeneralDefault(ModelDefaultValues):
    __default_data__ = {'field_array_integer': [20, 30, 40],
                        'field_boolean': False,
                        'field_datetime': datetime(2017, 11, 23, 23, 56, 59),
                        'field_float': 1.1,
                        'field_hashmap': {'item3': 'cccc', 'item4': 'dddd'},
                        'field_integer': 9,
                        'field_model': {'field_integer': 6, 'field_string': 'tost'},
                        'field_string': 'barfoo',
                        'field_time': time(13, 56, 59)}


class TestGeneralDefaultValues(TestCase):

    def test_field_default_value(self):
        model = ModelGeneralDefault()

        self.assertEqual(model.field_integer, 9)
        self.assertEqual(model.field_string, 'barfoo')
        self.assertEqual(model.field_boolean, False)
        self.assertEqual(model.field_float, 1.1)
        self.assertEqual(model.field_date, date(2016, 11, 23))
        self.assertEqual(model.field_time, time(13, 56, 59))
        self.assertEqual(model.field_datetime, datetime(2017, 11, 23, 23, 56, 59))
        self.assertEqual(model.field_array_integer.export_data(), [20, 30, 40])
        self.assertEqual(model.field_model.export_data(), {"field_integer": 6,
                                                           "field_string": "tost"})
        self.assertEqual(model.field_hashmap.export_data(), {"item3": "cccc",
                                                             "item4": "dddd"})

    def test_original_data(self):
        model = ModelGeneralDefault()
        self.assertEqual(model.export_original_data(), {})

    def test_modified_data(self):
        model = ModelGeneralDefault()

        self.assertEqual(model.export_modified_data(), {'field_array_integer': [20, 30, 40],
                                                        'field_boolean': False,
                                                        'field_date': date(2016, 11, 23),
                                                        'field_datetime': datetime(2017, 11, 23, 23, 56, 59),
                                                        'field_float': 1.1,
                                                        'field_hashmap': {'item3': 'cccc', 'item4': 'dddd'},
                                                        'field_integer': 9,
                                                        'field_model': {'field_integer': 6, 'field_string': 'tost'},
                                                        'field_string': 'barfoo',
                                                        'field_time': time(13, 56, 59)})

    def test_modify_model(self):
        model = ModelGeneralDefault()
        del model.field_model
        del model.field_hashmap

        model.field_integer = 4
        model.field_string = 'test'

        self.assertEqual(model.export_modified_data(), {'field_array_integer': [20, 30, 40],
                                                        'field_boolean': False,
                                                        'field_date': date(2016, 11, 23),
                                                        'field_datetime': datetime(2017, 11, 23, 23, 56, 59),
                                                        'field_float': 1.1,
                                                        'field_integer': 4,
                                                        'field_string': 'test',
                                                        'field_time': time(13, 56, 59)})


class CamelCaseMetaclassTests(TestCase):

    def test_camelcase_fields(self):
        class TestModel(BaseModel, metaclass=CamelCaseMeta):
            test_field_1 = StringField()
            test_field2 = StringField()
            testField_3 = StringField()
            testField4 = StringField(name='test_field_4')

        model = TestModel(data={'testField_1': 'foo',
                                'testField2': 'bar',
                                'testField_3': 'tor',
                                'test_field_4': 'pir'})

        self.assertEqual(model.test_field_1, 'foo')
        self.assertEqual(model.testField_1, 'foo')
        self.assertEqual(model.test_field2, 'bar')
        self.assertEqual(model.testField2, 'bar')
        self.assertEqual(model.testField_3, 'tor')
        self.assertEqual(model.testField4, 'pir')
        self.assertEqual(model.test_field_4, 'pir')
        self.assertEqual(model.export_data(), {'testField_1': 'foo',
                                               'testField2': 'bar',
                                               'testField_3': 'tor',
                                               'test_field_4': 'pir'})


class AliasTests(TestCase):

    def test_field_alias(self):
        class Model(BaseModel):
            integer_field = IntegerField(name='scalar_field', alias=['int_field', 'number_field'])
            string_field = StringField(name='text_field')

        self.assertEqual(Model.get_structure()['scalar_field'].alias, ['integer_field', 'int_field', 'number_field'])
        self.assertEqual(Model.get_structure()['text_field'].alias, ['string_field'])


class StructureTests(TestCase):

    def test_simple_structure(self):
        class Model(BaseModel):
            integer_field = IntegerField(name='scalar_field', alias=['int_field', 'number_field'])
            string_field = StringField(name='text_field')

        self.assertEqual(len(Model.get_structure()), 2)
        self.assertIn('scalar_field', Model.get_structure())
        self.assertIsInstance(Model.get_structure()['scalar_field'], IntegerField)
        self.assertIn('text_field', Model.get_structure())
        self.assertIsInstance(Model.get_structure()['text_field'], StringField)

    def test_inherit_structure(self):
        class Model(BaseModel):
            integer_field = IntegerField(name='scalar_field', alias=['int_field', 'number_field'])
            string_field = StringField(name='text_field')

        class InheritModel(Model):
            integer_field = IntegerField(name='scalar_field', alias=['int_field', 'number_field'])
            float_field = FloatField()

        self.assertEqual(len(InheritModel.get_structure()), 3)
        self.assertIn('scalar_field', InheritModel.get_structure())
        self.assertIsInstance(InheritModel.get_structure()['scalar_field'], IntegerField)
        self.assertIn('text_field', InheritModel.get_structure())
        self.assertIsInstance(InheritModel.get_structure()['text_field'], StringField)
        self.assertIn('float_field', InheritModel.get_structure())
        self.assertIsInstance(InheritModel.get_structure()['float_field'], FloatField)


class FieldInconsistenceTests(TestCase):

    def test_override_field(self):
        with self.assertRaises(RuntimeError):
            class Model(BaseModel):
                test_field_1 = StringField(alias=['text_field'])
                test_field_2 = IntegerField(alias=['test_field_1'])


class GetAttributeByPathTests(TestCase):

    def setUp(self):
        class InnerModel(BaseModel):
            test_field_1 = IntegerField()
            test_field_2 = StringField()

        class Model(BaseModel):
            test_field_1 = IntegerField()
            test_list = ArrayField(field_type=ModelField(model_class=InnerModel))
            test_model = ModelField(model_class=InnerModel)
            test_list_int = ArrayField(field_type=IntegerField())

        self.model = Model(data={'test_field_1': 1,
                                 'test_list': [{'test_field_1': 2, 'test_field_2': 'string'},
                                               {'test_field_1': 3}],
                                 'test_model': {'test_field_1': 4, 'test_field_2': 'string2'},
                                 'test_list_int': [1, 2, 3]})

    def test_simple(self):
        self.assertEqual(self.model.get_attrs_by_path('test_field_1'), [1])

    def test_simple_path(self):
        self.assertEqual(self.model.get_attrs_by_path('test_model.test_field_1'), [4])
        self.assertEqual(self.model.get_attrs_by_path('test_model.test_field_2'), ['string2'])

    def test_simple_path_no_field(self):
        self.assertIsNone(self.model.get_attrs_by_path('test_model.test_field_3'))

    def test_simple_path_no_struct(self):
        self.assertIsNone(self.model.get_attrs_by_path('test_field_1.test_field_3'))

    def test_simple_path_no_value(self):
        self.assertIsNone(self.model.get_attrs_by_path('test_list.1.test_field_2'))

    def test_simple_path_list(self):
        self.assertEqual(self.model.get_attrs_by_path('test_list.0.test_field_1'), [2])
        self.assertEqual(self.model.get_attrs_by_path('test_list.0.test_field_2'), ['string'])

    def test_wildcard_path_list_inner(self):
        self.assertEqual(self.model.get_attrs_by_path('test_list.*.test_field_1'), [2, 3])
        self.assertEqual(self.model.get_attrs_by_path('test_list.*.test_field_2'), ['string'])

    def test_wildcard_path_all(self):
        self.assertEqual(set(self.model.get_attrs_by_path('*')), {1, self.model.test_list,
                                                                  self.model.test_model,
                                                                  self.model.test_list_int})

    def test_wildcard_path_list(self):
        self.assertEqual(set(self.model.get_attrs_by_path('test_list.*')), {self.model.test_list[0],
                                                                            self.model.test_list[1]})

    def test_first_simple(self):
        self.assertEqual(self.model.get_1st_attr_by_path('test_field_1'), 1)

    def test_first_simple_path(self):
        self.assertEqual(self.model.get_1st_attr_by_path('test_model.test_field_1'), 4)
        self.assertEqual(self.model.get_1st_attr_by_path('test_model.test_field_2'), 'string2')

    def test_first_simple_path_no_field(self):
        with self.assertRaises(AttributeError):
            self.model.get_1st_attr_by_path('test_model.test_field_3')

    def test_first_simple_path_no_field_with_default(self):
        self.assertEqual(self.model.get_1st_attr_by_path('test_model.test_field_3', default=4), 4)

    def test_first_simple_path_no_value(self):
        with self.assertRaises(AttributeError):
            self.model.get_1st_attr_by_path('test_list.1.test_field_2')

    def test_first_simple_path_no_value_with_default(self):
        self.assertEqual(self.model.get_1st_attr_by_path('test_list.1.test_field_2', default=4), 4)

    def test_first_simple_path_list(self):
        self.assertEqual(self.model.get_1st_attr_by_path('test_list.0.test_field_1'), 2)
        self.assertEqual(self.model.get_1st_attr_by_path('test_list.0.test_field_2'), 'string')

    def test_first_wildcard_path_list_inner(self):
        self.assertEqual(self.model.get_1st_attr_by_path('test_list.*.test_field_1'), 2)
        self.assertEqual(self.model.get_1st_attr_by_path('test_list.*.test_field_2'), 'string')

    def test_first_wildcard_path_all(self):
        self.assertIn(self.model.get_1st_attr_by_path('*'), [1, self.model.test_list,
                                                             self.model.test_model, self.model.test_list_int])

    def test_first_wildcard_path_list(self):
        self.assertEqual(self.model.get_1st_attr_by_path('test_list.*'), self.model.test_list[0])

    def test_list_first_simple_path_list(self):
        self.assertEqual(self.model.test_list.get_1st_attr_by_path('0.test_field_1'), 2)
        self.assertEqual(self.model.test_list.get_1st_attr_by_path('0.test_field_2'), 'string')

    def test_list_first_simple_path_list_no_field(self):
        with self.assertRaises(AttributeError):
            self.model.test_list.get_1st_attr_by_path('0.test_field_3')

    def test_list_first_simple_path_list_no_field_default(self):
        self.assertEqual(self.model.test_list.get_1st_attr_by_path('0.test_field_3', default=2), 2)

    def test_list_first_simple_path_list_no_value(self):
        with self.assertRaises(AttributeError):
            self.model.test_list.get_1st_attr_by_path('1.test_field_2')

    def test_list_first_simple_path_list_no_value_default(self):
        self.assertEqual(self.model.test_list.get_1st_attr_by_path('1.test_field_2', default=2), 2)

    def test_list_first_wildcard_path_list(self):
        self.assertEqual(self.model.test_list.get_1st_attr_by_path('*.test_field_1'), 2)
        self.assertEqual(self.model.test_list.get_1st_attr_by_path('*.test_field_2'), 'string')

    def test_dict_like_simple(self):
        self.assertEqual(self.model['test_field_1'], 1)

    def test_dict_like_simple_path(self):
        self.assertEqual(self.model['test_model.test_field_1'], 4)
        self.assertEqual(self.model['test_model.test_field_2'], 'string2')

    def test_dict_like_simple_path_no_field(self):
        with self.assertRaises(KeyError):
            self.model['test_model.test_field_3']

    def test_dict_like_simple_path_no_value(self):
        with self.assertRaises(KeyError):
            self.model['test_list.1.test_field_2']

    def test_dict_like_simple_path_list(self):
        self.assertEqual(self.model['test_list.0.test_field_1'], 2)
        self.assertEqual(self.model['test_list.0.test_field_2'], 'string')

    def test_dict_like_wildcard_path_list_inner(self):
        self.assertEqual(self.model['test_list.*.test_field_1'], 2)
        self.assertEqual(self.model['test_list.*.test_field_2'], 'string')

    def test_dict_like_wildcard_path_all(self):
        self.assertIn(self.model['*'], [1, self.model.test_list,
                                        self.model.test_model, self.model.test_list_int])

    def test_dict_like_wildcard_path_list(self):
        self.assertEqual(self.model['test_list.*'], self.model.test_list[0])

    def test_list_dict_like_simple_path_list(self):
        self.assertEqual(self.model.test_list['0.test_field_1'], 2)
        self.assertEqual(self.model.test_list['0.test_field_2'], 'string')

    def test_list_dict_like_simple_path_list_no_field(self):
        with self.assertRaises(KeyError):
            self.model.test_list['0.test_field_3']

    def test_list_dict_like_simple_path_list_no_value(self):
        with self.assertRaises(KeyError):
            self.model.test_list['1.test_field_2']

    def test_list_dict_like_wildcard_path_list(self):
        self.assertEqual(self.model.test_list['*.test_field_1'], 2)
        self.assertEqual(self.model.test_list['*.test_field_2'], 'string')

    def test_list_invalid_path_list(self):
        self.assertIsNone(self.model.get_attrs_by_path('test_list_int.*.test'))


class GetAttributeByPathDynamicModelTests(GetAttributeByPathTests):

    def setUp(self):
        self.model = DynamicModel(data={'test_field_1': 1,
                                        'test_list': [{'test_field_1': 2, 'test_field_2': 'string'},
                                                      {'test_field_1': 3}],
                                        'test_model': {'test_field_1': 4, 'test_field_2': 'string2'},
                                        'test_list_int': [1, 2, 3]})


class GetAttributeByPathFastDynamicModelTests(GetAttributeByPathTests):

    def setUp(self):
        self.model = FastDynamicModel(data={'test_field_1': 1,
                                            'test_list': [{'test_field_1': 2, 'test_field_2': 'string'},
                                                          {'test_field_1': 3}],
                                            'test_model': {'test_field_1': 4, 'test_field_2': 'string2'},
                                            'test_list_int': [1, 2, 3]})


class AvoidInternalAttributesTests(TestCase):

    def test_hashmap_import_double_underscore(self):
        class Model(HashMapModel):
            test_field = IntegerField()

        model = Model(field_type=ModelField(model_class=FastDynamicModel))
        model.import_data({'__structure__': {}})
        self.assertNotEqual(model.__structure__, {})

    def test_dynmodel_import_double_underscore(self):
        model = DynamicModel()
        model.import_data({'__class__': 'test_class'})
        self.assertNotEqual(model.__class__, 'test_class')

    def test_fastdynmodel_import_double_underscore(self):
        model = FastDynamicModel()
        model.import_data({'__class__': 'test_class'})
        self.assertNotEqual(model.__class__, 'test_class')


class ContainsAttributeRegularModelTests(TestCase):

    class Model(HashMapModel):
        test_field = IntegerField()

    def test_contains_attribute_original_data(self):
        model = self.Model(test_field=1, flat=True)
        self.assertTrue('test_field' in model)

    def test_not_contains_attribute(self):
        model = self.Model()

        self.assertFalse('test_field' in model)

    def test_not_contains_attribute_original_deleted(self):
        model = self.Model(test_field=1, flat=True)

        del model.test_field

        self.assertFalse('test_field' in model)

    def test_contains_attribute_modified_data(self):
        model = self.Model(test_field=1)
        self.assertTrue('test_field' in model)

    def test_contains_attribute_modified_deleted(self):
        model = self.Model(test_field=1)

        del model.test_field

        self.assertFalse('test_field' in model)


class ContainsAttributeDynamicModelTests(ContainsAttributeRegularModelTests):
    Model = DynamicModel


class ContainsAttributeFastDynamicModelTests(ContainsAttributeRegularModelTests):
    Model = FastDynamicModel


class ContainsAttributeHashMapModelTests(ContainsAttributeRegularModelTests):
    Model = partial(HashMapModel, field_type=IntegerField())


class ExportModificationsTests(TestCase):

    class Model(BaseModel):
        test_field_int = IntegerField()
        test_array_int = ArrayField(field_type=IntegerField())
        test_array_model = ArrayField(field_type=MultiTypeField(field_types=[IntegerField(),
                                                                             ModelField()]))
        test_array_array_model = ArrayField(field_type=ArrayField(field_type=ModelField()))
        test_model = ModelField()

    def test_simple_modified_value(self):
        model = self.Model()
        model.test_field_int = 3

        self.assertEqual(model.export_modifications(), {'test_field_int': 3})

    def test_simple_value(self):
        model = self.Model()
        model.test_field_int = 3

        model.flat_data()

        self.assertEqual(model.export_modifications(), {})

    def test_simple_deleted_value(self):
        model = self.Model()
        model.test_field_int = 3

        model.flat_data()
        del model.test_field_int

        self.assertEqual(model.export_modifications(), {})

    def test_inner_model_modified_model(self):
        model = self.Model()
        model.test_model = {'test_field_int': 3}

        self.assertEqual(model.export_modifications(), {'test_model': {'test_field_int': 3}})

    def test_inner_model_modified_value(self):
        model = self.Model()
        model.test_model = {'test_field_int': 3}
        model.flat_data()
        model.test_model.test_field_int = 4

        self.assertEqual(model.export_modifications(), {'test_model.test_field_int': 4})

    def test_inner_model_value(self):
        model = self.Model()
        model.test_model = {'test_field_int': 3}
        model.flat_data()

        self.assertEqual(model.export_modifications(), {})

    def test_inner_model_deleted_value(self):
        model = self.Model()
        model.test_model = {'test_field_int': 3}
        model.flat_data()
        del model.test_model.test_field_int

        self.assertEqual(model.export_modifications(), {})

    def test_list_int_modified(self):
        model = self.Model({'test_array_int': [3, 4]})

        self.assertEqual(model.export_modifications(), {'test_array_int': [3, 4]})

    def test_list_int_original(self):
        model = self.Model({'test_array_int': [3, 4]})
        model.flat_data()

        self.assertEqual(model.export_modifications(), {})

    def test_list_int_append_item(self):
        model = self.Model({'test_array_int': [3, 4]})
        model.flat_data()
        model.test_array_int.append(5)

        self.assertEqual(model.export_modifications(), {'test_array_int': [3, 4, 5]})

    def test_list_model_modified(self):
        model = self.Model({'test_array_model': [{'test_field_int': 3},
                                                 {'test_field_int': 4}]})

        self.assertEqual(model.export_modifications(), {'test_array_model': [{'test_field_int': 3},
                                                                             {'test_field_int': 4}]})

    def test_list_model_original(self):
        model = self.Model({'test_array_model': [{'test_field_int': 3},
                                                 {'test_field_int': 4}]})

        model.flat_data()

        self.assertEqual(model.export_modifications(), {})

    def test_list_model_inner_modified(self):
        model = self.Model({'test_array_model': [{'test_field_int': 3},
                                                 {'test_field_int': 4},
                                                 6]})

        model.flat_data()
        model.test_array_model[1].test_field_int = 5

        self.assertEqual(model.export_modifications(), {'test_array_model.1.test_field_int': 5})

    def test_list_model_append_item(self):
        model = self.Model({'test_array_model': [{'test_field_int': 3},
                                                 {'test_field_int': 4}]})

        model.flat_data()
        model.test_array_model[0].test_field_int = 2
        model.test_array_model[1].test_field_int = 5
        model.test_array_model.append({'test_field_int': 6})

        self.assertEqual(model.export_modifications(), {'test_array_model': [{'test_field_int': 2},
                                                                             {'test_field_int': 5},
                                                                             {'test_field_int': 6}]})

    def test_list_inner_list_model_modified(self):
        model = self.Model({'test_array_array_model': [[{'test_field_int': 3},
                                                        {'test_field_int': 4}]]})

        self.assertEqual(model.export_modifications(), {'test_array_array_model': [[{'test_field_int': 3},
                                                                                    {'test_field_int': 4}]]})

    def test_list_inner_list_model_original(self):
        model = self.Model({'test_array_array_model': [[{'test_field_int': 3},
                                                        {'test_field_int': 4}]]})

        model.flat_data()

        self.assertEqual(model.export_modifications(), {})

    def test_list_inner_list_model_inner_modified(self):
        model = self.Model({'test_array_array_model': [[{'test_field_int': 3},
                                                        {'test_field_int': 4}]]})

        model.flat_data()
        model.test_array_array_model[0][1].test_field_int = 5

        self.assertEqual(model.export_modifications(), {'test_array_array_model.0.1.test_field_int': 5})

    def test_list_inner_list_model_append_item(self):
        model = self.Model({'test_array_array_model': [[{'test_field_int': 3},
                                                        {'test_field_int': 4}]]})

        model.flat_data()
        model.test_array_array_model[0].append({'test_field_int': 6})

        self.assertEqual(model.export_modifications(), {'test_array_array_model.0': [{'test_field_int': 3},
                                                                                     {'test_field_int': 4},
                                                                                     {'test_field_int': 6}]})


class IterFactory:

    def __init__(self):
        self.i = 0

    def __call__(self):
        self.i += 1
        return self.i


class DefaultValueFactoryTests(TestCase):

    class Model(BaseModel):
        __default_data__ = {'test_field_float': factory(IterFactory())}

        test_field_int = IntegerField(default=factory(IterFactory()))
        test_field_string = StringField(default=factory(IterFactory()))
        test_field_float = FloatField()

    def test_default_value_factory(self):
        model = self.Model()

        self.assertEquals(model.test_field_int, 1)
        self.assertEquals(model.test_field_string, '1')
        self.assertEquals(model.test_field_float, 1.0)

        model = self.Model()

        self.assertEquals(model.test_field_int, 2)
        self.assertEquals(model.test_field_string, '2')
        self.assertEquals(model.test_field_float, 2.0)


class DefaultValueFactoryDateTimeTests(TestCase):

    class Model(BaseModel):
        __default_data__ = {'test_field_2': factory(datetime.now)}

        test_field_1 = DateTimeField(default=factory(datetime.now))
        test_field_2 = DateTimeField()
        test_field_float = FloatField()

    def test_default_value_factory(self):
        model = self.Model()

        self.assertIsInstance(model.test_field_1, datetime)
        self.assertIsInstance(model.test_field_2, datetime)
