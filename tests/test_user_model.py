import unittest
from app.models import User
from app import db


class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        db.session.query(User).delete()

    def test_password_setter(self):
        u = User(username='Y')
        u.password = 'cat'
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self):
        u = User(username='Ivan')
        u.password = 'cat'

        with self.assertRaises(AttributeError):
            self.u.password

    def test_password_verivication(self):
        u = User(username='Ivan')
        u.password = 'cat'

        self.assertTrue(u.verify_password('cat'))
        self.assertFalse(u.verify_password('dog'))
        self.assertFalse(u.verify_password('cAt'))

    def test_password_salts_are_random(self):
        u1 = User(username='Ivan')
        u1.password = 'cat'
        u2 = User(username='Taras')
        u2.password = 'cat'

        self.assertTrue(u1.password_hash != u2.password_hash)

    def test_token_confirmation(self):
        u1 = User(email='smth@gmail.com', username='Ivan')
        u1.password = 'cat'
        u2 = User(email='smth2@gmail.cpm', username='ivan')
        u2.password = 'cat'
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()

        token1 = u1.generete_confirmation_token()
        token2 = u2.generete_confirmation_token()

        self.assertTrue(u1.confirm(token1))
        self.assertTrue(u2.confirm(token2))
        self.assertEquals(u1.confirm(token2), False)