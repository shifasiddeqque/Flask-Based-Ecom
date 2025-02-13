# app/extensions/loginmanager.py 
from flask_login import LoginManager
from app.models import User
# Create an instance of LoginManager
login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    # This function tells Flask-Login how to load a user from the session
    return User.query.get(int(user_id))