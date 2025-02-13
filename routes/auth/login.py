from flask import jsonify, request, current_app, render_template, redirect, url_for, flash, session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta
import jwt
from app.models import db, User, Admin
from app.routes.auth.auth import auth_bp
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import flash
from app.forms.login_form import LoginForm
from flask_login import login_required, current_user
from app.utils import send_email
from flask_login import login_user
from app.routes.cart import merge_session_cart_into_user_cart

@auth_bp.route('/debug_session')
def debug_session():
    return f'Session data: {session} | current_user: {current_user}, Is Authenticated: {current_user.is_authenticated}'
    # In the login function, print current_user data

@auth_bp.route('/login', methods=['GET','POST'])
def login():    
    if current_user.is_authenticated:
        flash('You are already logged in.', 'info')
        if current_user.role == 'admin':
            return redirect(url_for('admin'))  # Admin dashboard
        else:
            return redirect(url_for('shop.index'))  # Customer home page
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user and check_password_hash(user.password, form.password.data):
            # Login logic (using Flask-Login or custom session management)
            login_user(user)
            merge_session_cart_into_user_cart()
            flash(f'Welcome {user.username}!', 'success')

            if user.role == 'admin':
                return redirect(url_for('admin'))  # Admin dashboard
            else:
                return redirect(url_for('shop.index'))  # Customer home page

        flash('Invalid username or password', 'danger')

    return render_template('auth/login.html', form=form)

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    
    if not data or not data.get('email'):
        return jsonify({'message': 'Email is required'}), 400

    user = User.query.filter_by(email=data['email']).first()
    
    if not user:
        return jsonify({'message': 'If the email exists, a reset link will be sent'}), 200

    # Generate reset token
    reset_token = secrets.token_urlsafe(32)
    user.reset_token = reset_token
    user.reset_token_expires = datetime.utcnow() + timedelta(hours=24)
    db.session.commit()

    # Send reset email
    try:
        reset_url = f"{request.host_url}reset-password/{reset_token}"
        body = f"Click the following link to reset your password: {reset_url}\n\nThis link will expire in 24 hours."
        send_email('Password Reset Request', user.email, body)
        return jsonify({'message': 'If the email exists, a reset link will be sent'}), 200

    except Exception as e:
        return jsonify({'message': 'Error sending reset email'}), 500

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password_request():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        if user:
            # Generate token for resetting password
            token = user.generate_reset_token()
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            # Send reset email
            send_email('Password Reset Request', user.email, reset_url)
            flash('A password reset link has been sent to your email.', 'info')
        else:
            flash('No account with that email address.', 'danger')
        return redirect(url_for('auth.reset_password_request'))
    
    return render_template('auth.reset_password_request.html')

@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = User.verify_reset_token(token)
    if not user:
        flash('The reset link is invalid or has expired.', 'danger')
        return redirect(url_for('auth.reset_password_request'))

    if request.method == 'POST':
        new_password = request.form['password']
        user.password = generate_password_hash(new_password)
        db.session.commit()
        flash('Your password has been updated!', 'success')
        return redirect(url_for('login'))  # Redirect to login page after successful password reset
    
    return render_template('auth.reset_password.html', token=token)

from flask_login import logout_user



#@auth_bp.route('/login', methods=['GET','POST'])
# def login():
#     data = request.get_json()
    
#     if not data or not data.get('email') or not data.get('password'):
#         return jsonify({'message': 'Missing email or password'}), 400

#     user = User.query.filter_by(email=data['email']).first()

#     if not user:
#         return jsonify({'message': 'Invalid email or password'}), 401

#     if not check_password_hash(user.password, data['password']):
#         return jsonify({'message': 'Invalid email or password'}), 401

#     # Generate JWT token
#     token = jwt.encode({
#         'user_id': user.id,
#         'exp': datetime.utcnow() + timedelta(days=1)
#     }, current_app.config['SECRET_KEY'])

#     # Update last login for admin users
#     admin = Admin.query.filter_by(user_id=user.id).first()
#     if admin:
#         admin.last_login_at = datetime.utcnow()
#         db.session.commit()

#     return jsonify({
#         'token': token,
#         'user_id': user.id,
#         'email': user.email
#     })