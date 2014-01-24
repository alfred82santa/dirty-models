from unittest import TestCase
from dirty_models.fields import *
from dirty_models.models import BaseModel


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
