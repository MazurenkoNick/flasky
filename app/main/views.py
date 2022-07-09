from flask import render_template, session
from . import main


@main.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html', name=session.get('name'))