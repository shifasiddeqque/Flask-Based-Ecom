from flask import jsonify
from sqlalchemy import text  # Import the text() function from sqlalchemy
from app.models import db
from app.routes.auth.auth import auth_bp

@auth_bp.route('/check_db_connection', methods=['GET'])
def check_db_connection():
   try:
       # Use the `text()` function to explicitly declare the raw SQL query
       db.session.execute(text('SELECT 1'))
       return jsonify({'status': 'success', 'message': 'Database connection successful'})
   except Exception as e:
       return jsonify({'status': 'error', 'message': f'Database connection failed: {str(e)}'}), 500
