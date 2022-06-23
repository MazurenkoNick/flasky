from flask import current_app, render_template, session, flash, redirect, url_for
from .forms import NameForm
from . import main
from .. import db
from ..models import User, Role
from ..email import send_email


@main.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user_role = Role.query.filter_by(name='user').first() 
        user = User.query.filter_by(username=form.name.data).first()

        if user is None:
            user = User(username=form.name.data, role=user_role)
            db.session.add(user)
            db.session.commit()
            session['known'] = False
            flash('Looks like you\'ve been successfully registered!')
            send_email('mazurenkonick1@gmail.com', ' New User', 
                            'mail/new_user', user=user)
        else:
            session['known'] = True
            flash('You were successfully logged in!')
        
        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('.index'))

    return render_template('index.html', 
                            form=form,
                            name=session.get('name'),
                            known=session.get('known', False))