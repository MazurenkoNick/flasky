from flask_login import login_required, current_user
from flask import redirect, render_template, session, flash, url_for
from app.decorators import admin_required
from ..models import User, Role
from .. import db
from .forms import EditProfileAdminForm, EditProfileForm
from . import main


@main.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html', name=session.get('name'))


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)


@main.route('/edit-profile', methods=['POST', 'GET'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('main.user', username=current_user.username))
    
    # renders the values in the form to see the current values
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required 
def edif_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user)
    if form.validate_on_submit():
        user.email = form.email.data 
        user.username = form.username.data 
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data) 
        user.name = form.name.data 
        user.location = form.location.data 
        user.about_me = form.about_me.data 

        db.session.add(user)
        db.session.commit()
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))

    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form)