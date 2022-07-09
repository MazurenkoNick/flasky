from flask import flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from app import db
from ..models import UserAuthentificationManager, User
from ..email import send_email
from .forms import ChangePasswordForm, EmailForm, NewEmailForm, ResetPasswordForm
from . import settings


# CHANGE PASSWORD
@settings.route('/changepassword', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()

    if form.validate_on_submit():
        password = form.new_password.data
        current_user.password = password
        db.session.commit()
        flash('Your password has been changed successfully!')
        return redirect(url_for('main.index'))

    return render_template('settings/changepassword.html', form=form)


# RESET PASSWORD
@settings.route('/resetpassword', methods=['GET', 'POST'])
def send_reset_password_confirmation():
    form = EmailForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        auth_manager = UserAuthentificationManager(user)
        token = auth_manager.generate_user_confirmation_token()

        flash('Confirmation email has been sent!')
        send_email(
            user.email, 
            'Confirm Reset Password', 
            '/settings/email/resetconfrimation', 
            user=user, 
            token=token
        )
        return redirect(url_for('main.index'))
    return render_template('settings/sendresetpassword.html', form=form)
    

@settings.route("/resetpassword/<token>", methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        flash('User is logged in')
        return redirect(url_for('main.index'))

    auth_manager = UserAuthentificationManager(current_user)
    form = ResetPasswordForm()
    if form.validate_on_submit():
        if not auth_manager.reset_password(token, form.password1.data):
            flash('Password hasn\'t been changed!')
        else:
            flash('Password has been successfully changed!')
            return redirect(url_for('auth.login'))

    return render_template('settings/reset_password.html', form=form)


# CHANGE EMAIL
@settings.route("/change_email", methods=['GET','POST'])
@login_required
def send_change_email_confirmation():
    form = NewEmailForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=current_user.email).first()
        auth_manager = UserAuthentificationManager(user)
        token = auth_manager.generate_new_email_token(new_email=form.email.data)

        flash('Confirmation email has been sent')
        send_email(
            form.email.data,
            'Confirm Email Change',
            'settings/email/confirm_email_change',
            user=user,
            token=token
        )
        return redirect(url_for('main.index'))
    return render_template('settings/change_email.html', form=form)


@settings.route("/change_email/<token>")
@login_required
def change_email(token):
    auth_manager = UserAuthentificationManager(current_user)
    if auth_manager.change_email(token):
        flash('You\'ve successfully changed your email')
    else:
        flash('We didn\'t manage to change your email')

    return redirect(url_for('main.index'))
