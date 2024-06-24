import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, current_user
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static/uploads')
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mov'}
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024  # Set maximum file size to 200MB

db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from app import routes

# Error handling for large files
from flask import request, flash, redirect

@app.errorhandler(413)
def request_entity_too_large(error):
    flash('File is too large. Maximum size is 16MB.', 'danger')
    return redirect(request.url)

# Custom context processor
@app.context_processor
def inject_is_admin():
    def is_admin():
        return current_user.is_authenticated and current_user.username == 'dalton'
    return dict(is_admin=is_admin)