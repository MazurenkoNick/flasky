from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, BooleanField, SelectField
from wtforms.validators import Length, DataRequired, Email, Regexp, ValidationError
from ..models import Role, User


class EditProfileForm(FlaskForm):
    name = StringField('Real Name', validators=[Length(0,64)])
    location = StringField('Location', validators=[Length(0,64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')


class EditProfileAdminForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1,64), 
                                            Email()])
    username = StringField('Username', validators=[
        DataRequired(), Length(1, 64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                'Usernames must have only letters, numbers, dots or underscores')])
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce=int)
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) 
                            for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        # only when there's a change, it should ensure that the new value
        # doesn't duplicate another user's email
        if self.user.email != field.data and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('Email is already in use.')
    
    def validate_username(self, field):
        if self.user.username != field.data and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('Username is already in use.')


class PostForm(FlaskForm):
    body = TextAreaField("What's on your mind?", validators=[DataRequired()])
    submit = SubmitField('Submit')