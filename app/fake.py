from random import randint
from sqlalchemy.exc import IntegrityError
from faker import Faker
from . import db
from .models import User, Post


def users(count=100):
    fake = Faker()
    i = 0

    while i < count:
        try:
            u = User(
                username=fake.name(),
                email=fake.email(),
                password='password',
                confirmed=True,
                name=fake.name(),
                location=fake.city(),
                about_me=fake.text(),
                member_since=fake.past_date()
            )
            db.session.add(u)
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()


def posts(count=100):
    fake = Faker()
    user_count = User.query.count()

    for i in range(100):
        u = User.query.get(randint(1,user_count))
        p = Post(
            body=fake.text(),
            timestamp=fake.past_date(),
            author=u
            )
        db.session.add(p)
    db.session.commit()