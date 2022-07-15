import datetime
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import AnonymousUserMixin, UserMixin
from flask import current_app
from . import db, login_manager


class Permission:
    FOLLOW = 1
    COMMENT = 2
    WRITE = 4
    MODERATE = 8
    ADMIN = 16


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    # to many. users & role will not be in a database, but 
    # we have access to it in Python.
    users = db.relationship('User', backref='role')

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    def __repr__(self):
        return f'<Role {self.name}>'

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm
    
    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm

    @staticmethod
    def insert_roles():
        roles = {
            'User': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE],
            'Moderator': [
                Permission.FOLLOW, Permission.COMMENT, 
                Permission.WRITE, Permission.MODERATE],
            'Administrator': [
                Permission.FOLLOW, Permission.COMMENT, 
                Permission.WRITE, Permission.MODERATE, Permission.ADMIN]
        }
        default_role = 'User'
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)

            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name == default_role)

            db.session.add(role)
        db.session.commit()


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), index=True)
    # one.  This is a foreign from table 'roles' and with a field 'id'
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.datetime.utcnow)


    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config.get('FLASKY_ADMIN'):
                self.role = Role.query.filter_by(name='Administrator').first()
            else:
                self.role = Role.query.filter_by(default=True).first()

    def __repr__(self):
        return f'<User {self.username}>'

    def ping(self):
        """sets current 'last seen' time"""
        self.last_seen = datetime.datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self):
        return self.can(Permission.ADMIN)

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

    def reset_password(self, token, new_password):
        try: 
            data = jwt.decode(
                token, 
                current_app.config['SECRET_KEY'],
                leeway=10,
                algorithms=['HS256']
            )
        except:
            return False
        
        user = User.query.filter_by(user_id=data.get('confirm')).first()
        if user is None:
            return False
        user.password = new_password
        db.session.commit()
        return True

    def generate_user_confirmation_token(self, expiration=3600):
        token = jwt.encode(
            {
                'confirm': self.user.user_id,
                'exp': datetime.datetime.now(tz=datetime.timezone.utc)
                        + datetime.timedelta(seconds=expiration)
            },
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )
        return token

    def confirm_user(self, token):
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
            return False
        return True

    def generate_new_email_token(self, new_email, expiration=3600):
        email_token = jwt.encode(
            {
                'user_id': self.user.user_id,
                'email': self.user.email,
                'new_email': new_email,
                'exp': datetime.datetime.now(tz=datetime.timezone.utc) 
                        + datetime.timedelta(seconds=expiration) 
            },
            current_app.config['SECRET_KEY'], 
            algorithm="HS256"
        )
        return email_token

    def change_email(self, token):
        try:
            data = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                leeway=10,
                algorithms=['HS256']
            )
        except:
            return False
        
        user = User.query.filter_by(email=data.get('email')).first()
        if user:
            user.email = data.get('new_email')
            db.session.commit()
            return True
        else:
            return False


class AnonymousUser(AnonymousUserMixin):
    def can(self, perm):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser

@login_manager.user_loader
def load_user(id):
    return User.query.filter_by(user_id=id).first()
