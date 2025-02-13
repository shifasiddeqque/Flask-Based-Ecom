from flask import jsonify, request, flash, redirect, url_for
from app.models import db, Admin
from app.routes.auth.auth import auth_bp
from datetime import datetime
from flask_login import logout_user

@auth_bp.route('/logout')
def logout():
    logout_user()  # This will log the user out and clear the session
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))  # Redirect to the login page

# @auth_bp.route('/logout', methods=['POST'])
# def logout():
#     # Get the user ID from the request
#     user_id = request.get_json().get('user_id')
    
#     if user_id:
#         # Update last logout time for admin users
#         admin = Admin.query.filter_by(user_id=user_id).first()
#         if admin:
#             admin.last_login_at = datetime.utcnow()
#             db.session.commit()
    
#     return jsonify({'message': 'Successfully logged out'}), 200
