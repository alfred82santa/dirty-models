from unittest import TestCase

from dirty_models import AccessMode


class AccessModeTests(TestCase):

    def test_and_base_READ_AND_WRITE(self):
        self.assertEqual(AccessMode.READ_AND_WRITE & AccessMode.WRITABLE_ONLY_ON_CREATION,
                         AccessMode.WRITABLE_ONLY_ON_CREATION)
        self.assertEqual(AccessMode.READ_AND_WRITE & AccessMode.READ_ONLY, AccessMode.READ_ONLY)
        self.assertEqual(AccessMode.READ_AND_WRITE & AccessMode.HIDDEN, AccessMode.HIDDEN)

    def test_and_base_WRITABLE_ONLY_ON_CREATION(self):
        self.assertEqual(AccessMode.WRITABLE_ONLY_ON_CREATION & AccessMode.READ_ONLY, AccessMode.READ_ONLY)
        self.assertEqual(AccessMode.WRITABLE_ONLY_ON_CREATION & AccessMode.HIDDEN, AccessMode.HIDDEN)

    def test_and_base_READ_ONLY(self):
        self.assertEqual(AccessMode.READ_ONLY & AccessMode.HIDDEN, AccessMode.HIDDEN)

    def test_or_base_READ_AND_WRITE(self):
        self.assertEqual(AccessMode.READ_AND_WRITE | AccessMode.WRITABLE_ONLY_ON_CREATION, AccessMode.READ_AND_WRITE)
        self.assertEqual(AccessMode.READ_AND_WRITE | AccessMode.READ_ONLY, AccessMode.READ_AND_WRITE)
        self.assertEqual(AccessMode.READ_AND_WRITE | AccessMode.HIDDEN, AccessMode.READ_AND_WRITE)

    def test_or_base_WRITABLE_ONLY_ON_CREATION(self):
        self.assertEqual(AccessMode.WRITABLE_ONLY_ON_CREATION | AccessMode.READ_ONLY,
                         AccessMode.WRITABLE_ONLY_ON_CREATION)
        self.assertEqual(AccessMode.WRITABLE_ONLY_ON_CREATION | AccessMode.HIDDEN,
                         AccessMode.WRITABLE_ONLY_ON_CREATION)

    def test_or_base_READ_ONLY(self):
        self.assertEqual(AccessMode.READ_ONLY | AccessMode.HIDDEN, AccessMode.READ_ONLY)
