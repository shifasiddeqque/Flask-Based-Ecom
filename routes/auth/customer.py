from flask import render_template, Blueprint, request, redirect, url_for, flash
from app.models import db
from flask_login import login_required, current_user, logout_user
from app.models import User, Customer  # Import your user model
from app.forms.customer_form import CustomerForm



customer_bp = Blueprint('customer', __name__)

@customer_bp.route('/account', methods=['GET', 'POST'])
@login_required  # Ensure the user is logged in
def account():
    # Query the customer's existing data
    customer = Customer.query.filter_by(user_id=current_user.id).first()

    if not customer:
        return redirect(url_for('customer.create_account'))
    
    form = CustomerForm(obj=customer)
    if form.validate_on_submit():  # Check if the form is being submitted and is valid
        #customer.user_id = current_user.id
        customer.first_name = form.first_name.data
        customer.last_name = form.last_name.data
        customer.phone = form.phone.data
        customer.address_line1 = form.address_line1.data
        customer.address_line2 = form.address_line2.data
        customer.city = form.city.data
        customer.state = form.state.data
        customer.postal_code = form.postal_code.data
        customer.country = form.country.data
        print("fff", customer)
        # Commit the changes to the database
        db.session.commit()

        flash('Account updated successfully!', 'success')
        return redirect(url_for('customer.account'))

    # If it's a GET request or the form isn't valid
    return render_template('customer/account.html', form=form, customer=customer)

@customer_bp.route('/create_account', methods=['GET', 'POST'])
@login_required  # Ensure the user is logged in
def create_account():
    # Create a new customer profile if it doesn't exist
    form = CustomerForm()

    if form.validate_on_submit():
        # Create new customer record
        customer = Customer(
            user_id=current_user.id,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            phone=form.phone.data,
            address_line1=form.address_line1.data,
            address_line2=form.address_line2.data,
            city=form.city.data,
            state=form.state.data,
            postal_code=form.postal_code.data,
            country=form.country.data
        )
        
        db.session.add(customer)
        db.session.commit()

        return redirect(url_for('customer.account'))

    return render_template('customer/create_account.html', form=form)




