from flask_login import login_user, logout_user, login_required, current_user
from flask import render_template, redirect, request, url_for, flash, session
from app import db
from ..models import User, Role, UserAuthentificationManager
from ..email import send_email
from .forms import LoginForm, RegistrationForm
from . import auth


@auth.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        auth_manager = UserAuthentificationManager(user)

        if user is not None and auth_manager.verify_password(form.password.data):
            login_user(user, form.remember_me.data)     
            
            # The URL in next is validated to make sure it is a relative URL, 
            # to prevent a malicious user from using this argument to redirect 
            # unsuspecting users to another site.
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = url_for('main.index')
            return redirect(next)

        flash('Invalid username or password.')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You\'ve been logged out!')
    return redirect(url_for('main.index'))


# USER REGISTRATION
@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    user_role = Role.query.filter_by(name='user').first()

    if form.validate_on_submit():
        # add user to db. If user won't confirm the 
        # registration, he we'll be deleted from db
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data,
                    role=user_role)
        db.session.add(user)
        db.session.commit()
        # automatically log in a new (registered) user
        login_user(user)
        auth_manager = UserAuthentificationManager(user)

        token = auth_manager.generate_confirmation_token()
        send_email(user.email, 'Confirm Your Account',
                    'auth/email/confirm', user=user, token=token)
        flash('A confirmation email has been sent to you by email.')
        return redirect(url_for('main.index'))

    return render_template('auth/register.html', form=form)


# CONFIRM USER REGISTRATION
@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    auth_manager = UserAuthentificationManager(current_user)
    if current_user.confirmed:
        flash('Your account is already confirmed.')
        return redirect(url_for('main.index'))
    if auth_manager.confirm(token):
        current_user.confirmed = True
        db.session.commit()
        flash('You have confirmed your account. Thanks!')
    else:
        flash('''The confirmation link is invalid or has expired.
        Your account will be deleted! Register again, please.''')
        User.query.filter_by(username=current_user.username).delete()
        db.session.commit()
    return redirect(url_for('main.index'))


@auth.before_app_request
def before_request():
    # user is logged in & not confirmed &
    # the request is outside auth blueprint
    if current_user.is_authenticated \
        and not current_user.confirmed \
        and request.blueprint != 'auth' \
        and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))


# UNCONFIRMED PAGE & RESEND CONFIRMATION HANDLER
# Unconfirmed user can only use this view on the site:
@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/resend_confirmation')
@login_required
def resend_confirmation():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))

    auth_manager = UserAuthentificationManager(current_user)
    token = auth_manager.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account',
                'auth/email/confirm', user=current_user, token=token)
    flash('A new confirmation has just been sent to you by email!')
    return redirect(url_for('main.index'))        