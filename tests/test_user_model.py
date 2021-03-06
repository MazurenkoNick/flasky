import unittest
from app.models import User, UserAuthentificationManager, Permission, AnonymousUser
from app import db


class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        db.create_all()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()

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
        auth_manager = UserAuthentificationManager(u)

        self.assertTrue(auth_manager.verify_password('cat'))
        self.assertFalse(auth_manager.verify_password('dog'))
        self.assertFalse(auth_manager.verify_password('cAt'))

    def test_password_salts_are_random(self):
        u1 = User(username='Ivan')
        u1.password = 'cat'
        u2 = User(username='Taras')
        u2.password = 'cat'

        self.assertTrue(u1.password_hash != u2.password_hash)

    def test_token_confirmation(self):
        u1 = User(email='smth@gmail.com', username='Ivan')
        u1.password = 'cat'
        u2 = User(email='smth2@gmail.com', username='ivan')
        u2.password = 'cat'
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()

        auth_manager1 = UserAuthentificationManager(u1)
        auth_manager2 = UserAuthentificationManager(u2)
        token1 = auth_manager1.generate_user_confirmation_token()
        token2 = auth_manager2.generate_user_confirmation_token()

        self.assertTrue(auth_manager1.confirm_user(token1))
        self.assertTrue(auth_manager2.confirm_user(token2))
        self.assertEquals(auth_manager1.confirm_user(auth_manager2), False)

def test_user_role(self):
    u = User(email='john@example.com', password='cat')
    self.assertTrue(u.can(Permission.FOLLOW))
    self.assertTrue(u.can(Permission.COMMENT))
    self.assertTrue(u.can(Permission.WRITE))
    self.assertFalse(u.can(Permission.MODERATE))
    self.assertFalse(u.can(Permission.ADMIN))

def test_anonymous_user(self):
    u = AnonymousUser()
    self.assertFalse(u.can(Permission.FOLLOW))
    self.assertFalse(u.can(Permission.COMMENT))
    self.assertFalse(u.can(Permission.WRITE))
    self.assertFalse(u.can(Permission.MODERATE))
    self.assertFalse(u.can(Permission.ADMIN))
    