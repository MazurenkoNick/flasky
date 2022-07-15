from flask import render_template, session
from ..models import User 
from . import main


@main.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html', name=session.get('name'))


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)