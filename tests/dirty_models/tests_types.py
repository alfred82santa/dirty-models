from unittest import TestCase
from dirty_models.model_types import ListModel
from dirty_models.fields import StringField
from dirty_models.fields import IntegerField


class TestTypes(TestCase):

    def test_list_model(self):

        test_list = ListModel()
        test_list.append(7)

        self.assertEqual(test_list._modified_data, [7])
        self.assertEqual(test_list._original_data, None)
        test_list.append(6)
        test_list.insert(1, 3)
        self.assertEqual(test_list._modified_data, [7, 3, 6])

    def test_list_model_iteration(self):

        test_list = ListModel([2, 4, 5])
        for val in test_list:
            self.assertEqual(val, test_list._modified_data[test_list.index(val)])

    def test_list_remove_field(self):
        test_list = ListModel([2, 4, 5])
        test_list.append(7)
        test_list.remove(4)
        self.assertEqual(test_list._modified_data, [2, 5, 7])

    def test_list_field_conversion(self):
        test_list = ListModel([2, 3, "4", 6], field_type=StringField())

        self.assertEqual(test_list._modified_data, ["2", "3", "4", "6"])

    def test_extend_with_invalid_elements(self):
        test_list = ListModel([2, 3, "4", 6], field_type=StringField())
        test_list.extend([{}, 3.4])
        self.assertEqual(test_list._modified_data, ["2", "3", "4", "6", "3.4"])

    def test_set_initialised_list(self):
        test_list = ListModel([2, 3, "4", 6], field_type=StringField())
        test_list[2] = {}
        test_list[3] = "hi"
        test_list.append("hi")
        self.assertEqual(test_list._modified_data, ["2", "3", "4", "hi", "hi"])

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

    def test_clear_list(self):
        test_list = ListModel([2, 3, "4", 6])

        test_list.flat_data()
        test_list.append(1)
        self.assertEqual(test_list._modified_data, [2, 3, "4", 6, 1])
        self.assertEqual(test_list._original_data, [2, 3, "4", 6])
        test_list.clear()
        self.assertEqual(test_list._modified_data, None)
        self.assertEqual(test_list._original_data, None)

    def test_pop_element(self):
        test_list = ListModel([2, 3, "4", 6], field_type=StringField())
        test_list.pop(1)
        self.assertEqual(test_list._modified_data, ["2", "4", "6"])
        test_list.flat_data()
        test_list.pop(1)
        self.assertEqual(test_list._modified_data, ["2", "6"])
        self.assertEqual(test_list._original_data, ["2", "4", "6"])

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
