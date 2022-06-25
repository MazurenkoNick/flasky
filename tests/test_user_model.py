import unittest
from app.models import User


class UserModelTestCase(unittest.TestCase):
    def test_no_password_getter(self):
        u = User(username='Ivan')
        u.password = 'cat'

        with self.assertRaises(AttributeError):
            self.u.password

    def test_assert_verivication(self):
        u = User(username='Ivan')
        u.password = 'cat'

        self.assertTrue(u.verify_password('cat'))
        self.assertFalse(u.verify_password('dog'))
        self.assertFalse(u.verify_password('cAt'))