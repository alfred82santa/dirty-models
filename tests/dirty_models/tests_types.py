from unittest import TestCase
from dirty_models.model_types import ListModel
from dirty_models.fields import StringField, ArrayField, ModelField, MultiTypeField
from dirty_models.fields import IntegerField
from dirty_models.models import BaseModel


class TestTypes(TestCase):

    def test_list_model(self):

        test_list = ListModel()
        test_list.append(7)

        self.assertEqual(test_list.__modified_data__, [7])
        self.assertEqual(test_list.__original_data__, [])
        test_list.append(6)
        test_list.insert(1, 3)
        self.assertEqual(test_list.__modified_data__, [7, 3, 6])

    def test_list_model_iteration(self):

        test_list = ListModel([2, 4, 5])
        for val in test_list:
            self.assertEqual(val, test_list.__modified_data__[test_list.index(val)])

    def test_list_remove_field(self):
        test_list = ListModel([2, 4, 5])
        test_list.append(7)
        test_list.remove(4)
        self.assertEqual(test_list.__modified_data__, [2, 5, 7])

    def test_list_field_conversion(self):
        test_list = ListModel([2, 3, "4", 6], field_type=StringField())

        self.assertEqual(test_list.__modified_data__, ["2", "3", "4", "6"])

    def test_extend_with_invalid_elements(self):
        test_list = ListModel([2, 3, "4", 6], field_type=StringField())
        test_list.extend([{}, 3.4])
        self.assertEqual(test_list.__modified_data__, ["2", "3", "4", "6", "3.4"])

    def test_set_initialised_list(self):
        test_list = ListModel([2, 3, "4", 6], field_type=StringField())
        test_list[2] = {}
        test_list[3] = "hi"
        test_list.append("hi")
        self.assertEqual(test_list.__modified_data__, ["2", "3", "4", "hi", "hi"])

    def test_index_exception(self):
        test_list = ListModel([2, 3, "4", 6], field_type=StringField())
        self.assertRaises(ValueError, test_list.index, 7)

    def test_index_exception_not_initialised(self):
        test_list = ListModel()
        self.assertRaises(ValueError, test_list.index, 0)

    def test_get_items(self):
        test_list = ListModel([2, 3, "4", 6], field_type=StringField())
        self.assertEqual(test_list[0], "2")

    def test_get_items_flattered_list(self):
        test_list = ListModel([2, 3, "4", 6], field_type=StringField())
        test_list.flat_data()
        self.assertEqual(test_list[0], "2")

    def test_delete_item(self):
        test_list = ListModel([2, 3, "4", 6], field_type=StringField())
        del test_list[0]
        test_list.flat_data()
        self.assertEqual(test_list[0], "3")

    def test_delete_item_flattered(self):
        test_list = ListModel([2, 3, "4", 6], field_type=StringField())
        test_list.flat_data()
        del test_list[0]
        self.assertEqual(test_list[0], "3")

    def test_iter_not_initialised_goes_ok(self):
        test_list = ListModel()
        iterations = 0
        for x in test_list:
            iterations += 1
        self.assertEqual(iterations, 0)

    def test_iter_flattered(self):
        initial_list = [2, 3, "4", 6]
        test_list = ListModel(initial_list, field_type=StringField())
        test_list.flat_data()
        for x in test_list:
            self.assertEquals(x, str(initial_list[test_list.index(x)]))

    def test_clear_all_list(self):
        test_list = ListModel([2, 3, "4", 6])

        test_list.flat_data()
        test_list.append(1)
        self.assertEqual(test_list.__modified_data__, [2, 3, "4", 6, 1])
        self.assertEqual(test_list.__original_data__, [2, 3, "4", 6])
        test_list.clear_all()
        self.assertEqual(test_list.__modified_data__, None)
        self.assertEqual(test_list.__original_data__, [])

    def test_clear_list(self):
        test_list = ListModel([2, 3, "4", 6])

        test_list.flat_data()
        test_list.append(1)
        self.assertEqual(test_list.__modified_data__, [2, 3, "4", 6, 1])
        self.assertEqual(test_list.__original_data__, [2, 3, "4", 6])
        test_list.clear()
        self.assertIsNone(test_list.__modified_data__)
        self.assertEqual(test_list.__original_data__, [2, 3, "4", 6])

    def test_export_data_after_clear_all(self):
        test_list = ListModel([2, 3, "4", 6])

        test_list.flat_data()
        test_list.append(1)
        self.assertEqual(test_list.__modified_data__, [2, 3, "4", 6, 1])
        self.assertEqual(test_list.__original_data__, [2, 3, "4", 6])
        test_list.clear_all()
        self.assertEqual(test_list.export_data(), [])

    def test_export_modified_data_after_clear_all(self):
        test_list = ListModel([2, 3, "4", 6])

        test_list.flat_data()
        test_list.append(1)
        self.assertEqual(test_list.__modified_data__, [2, 3, "4", 6, 1])
        self.assertEqual(test_list.__original_data__, [2, 3, "4", 6])
        test_list.clear_all()
        self.assertEqual(test_list.export_modified_data(), [])

    def test_pop_element(self):
        test_list = ListModel([2, 3, "4", 6], field_type=StringField())
        test_list.pop(1)
        self.assertEqual(test_list.__modified_data__, ["2", "4", "6"])
        test_list.flat_data()
        test_list.pop(1)
        self.assertEqual(test_list.__modified_data__, ["2", "6"])
        self.assertEqual(test_list.__original_data__, ["2", "4", "6"])

    def test_pop_unitialised(self):
        test_list = ListModel()
        self.assertRaises(IndexError, test_list.pop, 0)

    def test_count_elements(self):
        test_list = ListModel([2, 3, "4", 6])
        self.assertEqual(test_list.count(3), 1)
        test_list.pop(1)
        test_list.flat_data()
        self.assertEqual(test_list.count(3), 0)

    def test_count_unitialised(self):
        test_list = ListModel()
        self.assertEqual(test_list.count("whatever"), 0)

    def test_length_unitialised(self):
        test_list = ListModel()
        self.assertEqual(0, len(test_list))

    def test_reverse(self):
        test_list = ListModel(["one", "two", "three", []], field_type=StringField())
        test_list.reverse()
        self.assertEqual(["three", "two", "one"], list(test_list))

    def test_sort(self):
        test_list = ListModel(["one", "two", 1, 2, 9, 3, "three", []], field_type=IntegerField())
        test_list.sort()
        self.assertEqual([1, 2, 3, 9], list(test_list))

    def test_length_initialised(self):
        test_list = ListModel([2, 3, "4", 6])
        self.assertEqual(4, len(test_list))

    def test_length_initialised_flattered(self):
        test_list = ListModel([2, 3, "4", 6])
        test_list.flat_data()
        self.assertEqual(4, len(test_list))
        self.assertEqual(4, len(test_list))

    def test_import_data(self):
        test_list = ListModel()
        test_list.import_data(set([1, 2]))
        self.assertTrue(1 in test_list)

    def test_invalid_index(self):
        test_list = ListModel([2, 4, 5])

        with self.assertRaises(TypeError):
            test_list[23.12]

    def test_out_of_bounds_index(self):
        test_list = ListModel([2, 4, 5])

        with self.assertRaises(IndexError):
            test_list[23]


class ContainsItemTests(TestCase):

    def test_contains_item_original_data(self):

        list_model = ListModel([1])
        list_model.flat_data()

        self.assertTrue(1 in list_model)

    def test_contains_item_modified_data(self):
        list_model = ListModel([1])

        self.assertTrue(1 in list_model)

    def test_not_contains_item_original_data(self):
        list_model = ListModel([2])
        list_model.flat_data()

        self.assertFalse(1 in list_model)

    def test_not_contains_item_modified_data(self):
        list_model = ListModel([1, 2])
        list_model.flat_data()
        list_model.pop(0)
        self.assertFalse(1 in list_model)


class ExportDeletedFieldsTests(TestCase):

    class Model(BaseModel):
        test_int = IntegerField()
        test_array = ArrayField(field_type=MultiTypeField(field_types=[IntegerField(),
                                                                       ModelField()]))

    def test_inner_model_deleted_field(self):

        model = self.Model({'test_array': [{'test_int': 1},
                                           {'test_int': 2},
                                           3]})

        model.flat_data()

        del model.test_array[1].test_int
        self.assertEqual(model.export_deleted_fields(), ['test_array.1.test_int'])
