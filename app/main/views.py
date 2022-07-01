from flask import current_app, render_template, session, flash, redirect, url_for
from . import main
from .. import db
from ..models import User, Role
from ..email import send_email


@main.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html', name=session.get('name'))