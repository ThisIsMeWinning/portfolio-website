from app import app, db
from app.models import User

with app.app_context():
    # Retrieve the user by username
    user = User.query.filter_by(username='dalton').first()
    if user:
        user.is_admin = True
        db.session.commit()
        print("User 'dalton' has been promoted to admin.")
    else:
        print("User 'dalton' not found.")
