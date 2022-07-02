import datetime
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask import current_app
from . import db, login_manager


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    # to many. users & role will not be in a database, but 
    # we have access to it in Python.
    users = db.relationship('User', backref='role')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(UserMixin, db.Model):
    __tablenames__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), index=True)
    # one.  This is a foreign from table 'roles' and with a field 'id'
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return '<Role %r>' % self.username

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def get_id(self):
        return str(self.user_id)


class UserAuthentificationManager:
    def __init__(self, user):
        self.user = user

    def verify_password(self, password):
        return check_password_hash(self.user.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        reset_token = jwt.encode(
            {
                'confirm': self.user.user_id,
                'exp': datetime.datetime.now(tz=datetime.timezone.utc)
                        + datetime.timedelta(seconds=expiration)
            },
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )
        return reset_token

    def confirm(self, token):
        try:
            data = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                # token will be available for 10 sec. after expiration:
                leeway=10,
                algorithms=['HS256']
            )
        except:
            return False

        if data.get('confirm') != self.user.user_id:
            # user will be deleted from the database if
            # confirmation isn't successfull
            db.session.delete(self.user)
            db.session.commit()
            return False
        self.user.confirmed = True
        db.session.commit()
        return True


@login_manager.user_loader
def load_user(id):
    return User.query.filter_by(user_id=id).first()
