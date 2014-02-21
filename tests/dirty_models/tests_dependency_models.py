from unittest import TestCase
from dirty_models.models import BaseModel, DynamicModel
from dirty_models.fields import (BaseField, IntegerField, FloatField,
                                 StringField, DateTimeField, ModelField,
                                 ArrayField, BooleanField)
from dirty_models.dependency_models import DependencyBaseModel

class TestDependencyBaseModel(TestCase):


    def setUp(self):
        self.model = DependencyBaseModel()

    def test_dependencies(self):

        class SimpleModel(DependencyBaseModel):
            simple_field_1 = IntegerField()
            simple_field_2 = StringField()

        class TestModel(DependencyBaseModel):
            field_1 = StringField()
            field_2 = BooleanField()
            field_3 = ArrayField(field_type=ModelField(model_class=SimpleModel))
            dependencies = [("field_1", "field_3.simple_field_1")]


        model = TestModel()
        model.field_1 = "a"
        model.field_2 = True
        simple_model_1 = SimpleModel()
        simple_model_2 = SimpleModel()
        simple_model_1.simple_field_1 = 23
        simple_model_1.simple_field_2 = "simple_model_1_field_2"
        simple_model_2.simple_field_1 = 34
        simple_model_2.simple_field_2 = "simple_model_2_field_2"

        model.field_3 = [simple_model_1, simple_model_2, "should not be here"]
        expected_data = {'field_1': 'a', 'field_2': True,
                         'field_3': [{'simple_field_2': 'simple_model_1_field_2','simple_field_1': 23},
                                     {'simple_field_2': 'simple_model_2_field_2', 'simple_field_1': 34}]}
        self.assertEqual(expected_data, model.export_modified_data())

        model.flat_data()
        self.assertEqual({'field_3': [{}, {}]}, model.export_modified_data())

        model.field_3[0].simple_field_1 = 12
        expected_data = {'field_1': 'a', 'field_3': [{'simple_field_1': 12}, {'simple_field_1': 34}]}
        self.assertEqual(expected_data, model.export_modified_data())

        model.flat_data()
        model_to_add_1 = SimpleModel()
        model_to_add_1.simple_field_2 = "This one should not affect the other fields"
        model.field_3.append(model_to_add_1)
        expected_data = {'field_3': [{}, {}, {'simple_field_2': 'This one should not affect the other fields'}]}
        self.assertEqual(expected_data, model.export_modified_data())

        model_to_add_2 = SimpleModel()
        model_to_add_2.simple_field_1 = 111
        model_to_add_2.simple_field_2 = "Should affect"
        model.field_3.append(model_to_add_2)
        expected_data = {'field_1': 'a',
                         'field_3': [{'simple_field_1': 12}, {'simple_field_1': 34},
                                     {'simple_field_2': 'This one should not affect the other fields'},
                                     {'simple_field_2': 'Should affect', 'simple_field_1': 111}]}
        self.assertEqual(expected_data, model.export_modified_data())


