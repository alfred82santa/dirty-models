from unittest.case import TestCase

from dirty_models.utils import underscore_to_camel


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
