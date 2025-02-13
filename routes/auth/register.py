from flask import Blueprint, render_template, redirect, url_for, flash
from app.routes.auth.auth import auth_bp
from app.forms.register_form import RegistrationForm
from app.models.user import User
from app.models import db
from werkzeug.security import generate_password_hash
from app.models.customer import Customer

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if the username or email already exists
        existing_user = User.query.filter((User.username == form.username.data) | (User.email == form.email.data)).first()
        if existing_user:
            flash('Username or Email already exists!', 'danger')
            return redirect(url_for('auth.login'))

        # Hash the password
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        # Create a new user (role is 'customer' by default)
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)

        # Add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        # Create a new customer profile
        new_customer = Customer(
            user_id=new_user.id,
            first_name="",  # Placeholder value
            last_name="",   # Placeholder value
            phone="",
            address_line1="",
            address_line2="",
            city="",
            state="",
            postal_code="",
            country=""
        )
        
        db.session.add(new_customer)
        db.session.commit()

        flash('Account created successfully! You can update your details later.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)