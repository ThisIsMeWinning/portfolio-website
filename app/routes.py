import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from app import app, db, bcrypt
from app.forms import RegistrationForm, LoginForm, PostForm, UpdateProfileForm, CreateUserForm
from app.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.utils import secure_filename

def save_file(file, folder, user_id):
    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], str(user_id), folder)
    os.makedirs(user_folder, exist_ok=True)  # Ensure the directory exists
    filename = secure_filename(file.filename)
    filepath = os.path.join(user_folder, filename)
    file.save(filepath)
    return os.path.join('uploads', str(user_id), folder, filename)

def save_picture(form_picture, user_id):
    user_folder = os.path.join(app.root_path, 'static/profile_pics', str(user_id))
    os.makedirs(user_folder, exist_ok=True)  # Ensure the directory exists

    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext.lower()  # Ensure the extension is lowercase
    picture_path = os.path.join(user_folder, picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)

    # Convert image to RGB mode if it is in a different mode
    if i.mode in ("RGBA", "P", "LA"):
        i = i.convert("RGB")
    
    # Crop the image to a square
    width, height = i.size
    if width > height:
        left = (width - height) / 2
        top = 0
        right = (width + height) / 2
        bottom = height
    else:
        left = 0
        top = (height - width) / 2
        right = width
        bottom = (height + width) / 2

    i = i.crop((left, top, right, bottom))
    i.thumbnail(output_size)
    i.save(picture_path)

    return os.path.join('profile_pics', str(user_id), picture_fn)

@app.route("/")
@app.route("/home")
def home():
    return render_template('index.html')

@app.route("/about")
def about():
    return render_template('about.html', title='About')

@app.route("/projects")
def projects():
    return render_template('projects.html', title='Projects')

@app.route("/contact")
def contact():
    return render_template('contact.html', title='Contact')

@app.route("/devlog")
def devlog():
    posts = Post.query.order_by(Post.date_posted.desc()).all()
    return render_template('devlog.html', title='DevLog', posts=posts)

@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        image_file = None
        video_file = None
        if form.image_file.data:
            image_file = save_file(form.image_file.data, 'images', current_user.id)
        if form.video_file.data:
            video_file = save_file(form.video_file.data, 'videos', current_user.id)
        post = Post(title=form.title.data, content=form.content.data, author=current_user, image_file=image_file, video_file=video_file)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('devlog'))
    return render_template('create_post.html', title='New Post', form=form, legend='New Post')

@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        if form.image_file.data:
            post.image_file = save_file(form.image_file.data, 'images', current_user.id)
        if form.video_file.data:
            post.video_file = save_file(form.video_file.data, 'videos', current_user.id)
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('devlog'))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post', form=form, legend='Update Post')

@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user and not is_admin():
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('devlog'))

@app.route("/create_user", methods=['GET', 'POST'])
@login_required
def create_user():
    if not is_admin():
        abort(403)
    form = CreateUserForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('The user has been created!', 'success')
        return redirect(url_for('admin_users'))
    return render_template('create_user.html', title='Create User', form=form)

@app.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():
    form = UpdateProfileForm()
    if form.validate_on_submit():
        if bcrypt.check_password_hash(current_user.password, form.current_password.data):
            if form.picture.data:
                picture_file = save_picture(form.picture.data, current_user.id)
                current_user.image_file = picture_file
            current_user.username = form.username.data
            current_user.email = form.email.data
            if form.new_password.data:
                hashed_password = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
                current_user.password = hashed_password
            db.session.commit()
            flash('Your account has been updated!', 'success')
            return redirect(url_for('profile'))
        else:
            flash('Current password is incorrect.', 'danger')
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename=current_user.image_file)
    return render_template('edit_profile.html', title='Account', image_file=image_file, form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

# Helper function to check if the current user is an admin
def is_admin():
    return current_user.is_authenticated and current_user.is_admin

# Admin route to view and manage users
@app.route("/admin_users")
@login_required
def admin_users():
    if not is_admin():
        abort(403)
    users = User.query.all()
    return render_template('admin_users.html', title='Manage Users', users=users)

# Admin route to delete a user
@app.route("/admin_users/<int:user_id>/delete", methods=['POST'])
@login_required
def delete_user(user_id):
    if not is_admin():
        abort(403)
    user = User.query.get_or_404(user_id)
    if user.username == 'dalton':
        flash('Cannot delete the admin account.', 'danger')
        return redirect(url_for('admin_users'))
    # Ensure to handle posts authored by the user before deleting
    for post in user.posts:
        db.session.delete(post)
    db.session.delete(user)
    db.session.commit()
    flash('User has been deleted.', 'success')
    return redirect(url_for('admin_users'))

# Admin route to promote a user to admin
@app.route("/admin_users/<int:user_id>/promote", methods=['POST'])
@login_required
def promote_user(user_id):
    if not is_admin():
        abort(403)
    user = User.query.get_or_404(user_id)
    user.is_admin = True
    db.session.commit()
    flash('User has been promoted to admin.', 'success')
    return redirect(url_for('admin_users'))

# Admin route to demote a user from admin
@app.route("/admin_users/<int:user_id>/demote", methods=['POST'])
@login_required
def demote_user(user_id):
    if not is_admin():
        abort(403)
    user = User.query.get_or_404(user_id)
    user.is_admin = False
    db.session.commit()
    flash('User has been demoted from admin.', 'success')
    return redirect(url_for('admin_users'))
