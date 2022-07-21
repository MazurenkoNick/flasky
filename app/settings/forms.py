from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import PasswordField, SubmitField, EmailField
from wtforms.validators import DataRequired, EqualTo, Email, ValidationError
from ..models import UserAuthentificationManager, User


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Enter the current password',
                                     validators=[DataRequired()])
    new_password = PasswordField(
        'Enter a new password',
        validators=[EqualTo(
            'confirm_password',
            message='Passwords must match.')])
    confirm_password = PasswordField('Confrim your new password',
                                     validators=[DataRequired()])
    submit = SubmitField('Submit')

    def validate_current_password(self, field):
        auth_manager = UserAuthentificationManager(current_user)
        if not auth_manager.verify_password(field.data):
            raise ValidationError('You\'ve given a wrong password.')


class EmailForm(FlaskForm):
    email = EmailField('', validators=[DataRequired(), Email()])
    submit = SubmitField('Submit')

    def validate_email(self, field):
        user = User.query.filter_by(email=field.data).first()
        if user is None:
            raise ValidationError('Email doesn\'t exist')


class ResetPasswordForm(FlaskForm):
    password1 = PasswordField(
        'Enter a new password', validators=[
            DataRequired(), EqualTo(
                'password2', 'Passwords must match.')])
    password2 = PasswordField('Repeat again')
    submit = SubmitField('Submit')


class NewEmailForm(FlaskForm):
    email = EmailField('', validators=[DataRequired(), Email()])
    submit = SubmitField('Submit')

    def validate_email(self, field):
        user = User.query.filter_by(email=field.data).first()
        if user is not None:
            raise ValidationError('This email has already been taken')
