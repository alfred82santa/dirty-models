from unittest import TestCase
from dirty_models.fields import (IntegerField, StringField, BooleanField, ModelField, FloatField, ArrayField)
from dirty_models.models import BaseModel
from dirty_models.types import ListModel


class TestFields(TestCase):

    def test_int_field_using_int(self):
        field = IntegerField()
        self.assertTrue(field.check_value(3))
        self.assertEqual(field.use_value(3), 3)

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

    def test_array_field(self):

        class TestModel(BaseModel):
            field_name_1 = ModelField()
            field_name_2 = StringField()

        class ArrayModel(BaseModel):
            array_field = ArrayField(model_object=ModelField(model_class=TestModel))

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
            array_field = ArrayField(model_object=ModelField(model_class=TestModel))

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
            array_field = ArrayField(model_object=ModelField(model_class=TestModel))

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
            array_field = ArrayField(model_object=ModelField(model_class=TestModel))

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
            array_field = ArrayField(model_object=ModelField(model_class=TestModel))

        array_model = ArrayModel()
        array_model.array_field = ["Unexpected string", TestModel()]

        self.assertEqual(1, len(array_model.array_field))

    def test_array_field_not_iterable(self):

        class ArrayModel(BaseModel):
            array_field = ArrayField(model_object=BooleanField())

        model = ArrayModel()
        model.array_field = "This is not a list"
        self.assertIsNone(model.array_field)

    def test_array_field_list_invalid_types(self):
        class ArrayModel(BaseModel):
            array_field = ArrayField(model_object=IntegerField())

        model = ArrayModel()
        model.array_field = ["This is not a list", "This neither"]
        self.assertIsNone(model.array_field)

    def test_array_field_conversion(self):

        class ArrayModel(BaseModel):
            array_field = ArrayField(model_object=IntegerField())

        model = ArrayModel()
        model.array_field = ["This is not a list", "2"]
        self.assertEquals(model.array_field[0], 2)

    def test_array_set_value_list_field(self):

        class ArrayModel(BaseModel):
            array_field = ArrayField(model_object=IntegerField())

        model = ArrayModel()
        model.array_field = ListModel(["this is not an integer"], field_type=IntegerField())
        self.assertEqual(0, len(model.array_field))

    def test_array_set_value_list_field_valid_and_convertible(self):
        class ArrayModel(BaseModel):
            array_field = ArrayField(model_object=IntegerField())

        model = ArrayModel()
        model.array_field = ListModel(["3"], field_type=IntegerField())
        self.assertEqual(1, len(model.array_field))

    def test_array_del(self):
        class TestModel(BaseModel):
            field_name_1 = ModelField()
            field_name_2 = StringField()

        class ArrayModel(BaseModel):
            array_field = ArrayField(model_object=ModelField(model_class=TestModel))

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
            array_field = ArrayField(model_object=ModelField(model_class=TestModel))

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
            array_field = ArrayField(model_object=IntegerField())

        model = ArrayModel()
        model.array_field = ["3", 4]

        self.assertEqual({"array_field": [3, 4]}, model.export_data())

    def test_array_model_export_data_not_modified(self):
        class TestModel(BaseModel):
            field_name_1 = ModelField()
            field_name_2 = StringField()

        class ArrayModel(BaseModel):
            array_field = ArrayField(model_object=ModelField(model_class=TestModel))

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
            array_field = ArrayField(model_object=IntegerField())

        model = ArrayModel()
        model.array_field = ["3", 4]
        model.array_field.clear()

        self.assertEqual({"array_field": []}, model.export_data())

    def test_array_model_export_modified_data(self):
        class TestModel(BaseModel):
            field_name_1 = ModelField()
            field_name_2 = StringField()

        class ArrayModel(BaseModel):
            array_field = ArrayField(model_object=ModelField(model_class=TestModel))

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
            array_field = ArrayField(model_object=ModelField(model_class=TestModel))

        array_model = ArrayModel()

        test_model_1 = TestModel()
        test_model_1.field_name_1 = TestModel()
        test_model_1.field_name_2 = "Test model 1"

        test_model_2 = TestModel()
        test_model_2.field_name_1 = TestModel()
        test_model_2.field_name_2 = "Test model 2"

        array_model.array_field = [test_model_1, test_model_2]

        expected_data = {
            "array_field": [{"field_name_1": {}},
                            {"field_name_1": {}}]
        }
        array_model.flat_data()
        self.assertEqual(expected_data, array_model.export_modified_data())

    def test_array_model_export_modified_data_integers(self):
        class ArrayModel(BaseModel):
            array_field = ArrayField(model_object=IntegerField())

        model = ArrayModel()
        model.array_field = ["3", 4]

        self.assertEqual({"array_field": [3, 4]}, model.export_modified_data())

    def test_array_model_export_modified_data_unitialised(self):
        class ArrayModel(BaseModel):
            array_field = ArrayField(model_object=IntegerField())

        model = ArrayModel()
        model.array_field = ["3", 4]
        model.array_field.clear()

        self.assertEqual({"array_field": []}, model.export_modified_data())

    def test_array_model_import_data(self):
        class ArrayModel(BaseModel):
            array_field = ArrayField(model_object=IntegerField())

        array_model = ArrayModel()
        array_model.import_data({"array_field": [1, 2, 3, 4]})
        self.assertEqual(4, len(array_model.array_field))
