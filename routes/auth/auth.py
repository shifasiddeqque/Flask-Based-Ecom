# app/routes/auth/auth.py
from flask import Blueprint

# Create the blueprint for authentication
auth_bp = Blueprint('auth', __name__)

# Import routes after the blueprint is created
from app.routes.auth.login import login
from app.routes.auth.logout import logout
from app.routes.auth.register import register
from app.routes.auth.check_db_connection import check_db_connection as check_db_connection


@auth_bp.route('/update_profile', methods=['GET', 'POST'])  # Ensure the user is logged in
def update_profile():
    pass