import os
import secrets
from flask import render_template, url_for, flash, redirect, request, abort
from app import app, db, bcrypt
from app.models import User, Post
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.forms import RegistrationForm, LoginForm, PostForm, UpdateProfileForm

# Helper function to check if the current user is an admin
def is_admin():
    return current_user.is_authenticated and current_user.is_admin

# Admin route to view and manage users
@app.route("/admin/manage_users")
@login_required
def manage_users():
    if not is_admin():
        abort(403)
    users = User.query.all()
    return render_template('admin_users.html', title='Manage Users', users=users)

# Admin route to delete a user
@app.route("/admin/manage_users/<int:user_id>/delete", methods=['POST'])
@login_required
def delete_user(user_id):
    if not is_admin():
        abort(403)
    user = User.query.get_or_404(user_id)
    if user.username == 'dalton':
        flash('Cannot delete the admin account.', 'danger')
        return redirect(url_for('manage_users'))
    # Ensure to handle posts authored by the user before deleting
    for post in user.posts:
        db.session.delete(post)
    db.session.delete(user)
    db.session.commit()
    flash('User has been deleted.', 'success')
    return redirect(url_for('manage_users'))

# Admin route to promote a user to admin
@app.route("/admin/manage_users/<int:user_id>/promote", methods=['POST'])
@login_required
def promote_user(user_id):
    if not is_admin():
        abort(403)
    user = User.query.get_or_404(user_id)
    user.is_admin = True
    db.session.commit()
    flash('User has been promoted to admin.', 'success')
    return redirect(url_for('manage_users'))

# Admin route to demote a user from admin
@app.route("/admin/manage_users/<int:user_id>/demote", methods=['POST'])
@login_required
def demote_user(user_id):
    if not is_admin():
        abort(403)
    user = User.query.get_or_404(user_id)
    user.is_admin = False
    db.session.commit()
    flash('User has been demoted from admin.', 'success')
    return redirect(url_for('manage_users'))

@app.route("/admin/users/new", methods=['GET', 'POST'])
@login_required
def create_user():
    if not is_admin():
        abort(403)
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('The account has been created!', 'success')
        return redirect(url_for('admin_users'))
    return render_template('create_user.html', title='Create User', form=form)

