from flask import flash, redirect, render_template, session, url_for, request
from flask_login import current_user, login_required
from app import db
from ..auth.forms import LoginForm
from ..models import UserAuthentificationManager, User
from ..email import send_email
from . import settings
from .forms import PasswordForm, EmailForm, ResetForm


# CHANGE PASSWORD
@settings.route('/changepassword', methods=['GET','POST'])
@login_required
def change_password():
    form = PasswordForm()

    if form.validate_on_submit():
        password = form.new_password.data
        current_user.password = password
        db.session.commit()
        flash('Your password has been changed successfully!')
        return redirect(url_for('main.index'))

    return render_template('settings/changepassword.html', form=form)


# RESET PASSWORD
@settings.route('/resetpassword', methods=['GET', 'POST'])
def send_reset_confirmation():
    form = EmailForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        auth_manager = UserAuthentificationManager(user)
        token = auth_manager.generate_confirmation_token()

        flash('Confirmation email has been sent!')
        send_email(user.email, 'Confirm Reset Password', 
                    '/settings/email/resetconfrimation', 
                    user=user, 
                    token=token)
        # add user email to session to have access to it in confirm_reset view
        session['user_email'] = form.email.data
        return redirect(url_for('main.index'))
    return render_template('settings/sendresetpassword.html', form=form)
    

@settings.route("/resetpassword/<token>", methods=['GET','POST'])
def reset_password(token):
    # if user exists, than user uses the same session as when he sended an email  
    user = User.query.filter_by(email=session.get('user_email')).first()
    auth_manager = UserAuthentificationManager(user)

    if user is None or current_user.is_authenticated or not auth_manager.confirm(token):
        flash('''Confirmation wasn't successfull. 
        Make sure you use the same browser and divice between requests.''')
        return redirect(url_for('main.index'))

    form = ResetForm()
    if form.validate_on_submit():
        user.password = form.password1.data
        db.session.commit()
        flash('Password has been successfully changed!')
        return redirect(url_for('auth.login'))

    return render_template('settings/reset_password.html', form=form)

