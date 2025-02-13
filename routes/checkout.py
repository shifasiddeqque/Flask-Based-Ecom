from flask import Blueprint, jsonify, request, render_template, redirect, url_for, flash
from app.models import db, Cart, Order, Product, ProductVariant
from flask_login import login_required, current_user
from app.models.customer import Customer
from app.models.order import Order, OrderProduct, OrderPayment
from app.models.cart import CartItem
from flask_mail import Message
from app.utils import send_email
from app.forms.checkout_form import CheckoutForm
import random
import string
from datetime import datetime
from decimal import Decimal
from app.config.config import Config

checkout_bp = Blueprint('checkout', __name__)

@checkout_bp.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if not current_user.is_authenticated:
        print("User is not authenticated!")
        return redirect(url_for('auth.login'))

    # Initialize the form
    form = CheckoutForm()

    # Get the cart for the logged-in user
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    if not cart or not cart.items:
        flash("Your cart is empty!", 'warning')
        return redirect(url_for('cart.view_cart'))

    # Ensure that the customer has filled out all required details (phone, name, and address_1)
    customer = Customer.query.filter_by(user_id=current_user.id).first()
    if not all([customer.first_name, customer.last_name, customer.phone, customer.address_line1]):
        flash('Please complete your profile with your name, phone, and address before checking out.', 'warning')
        return redirect(url_for('auth.update_profile'))

    # Calculate total amount and individual item prices
    total_amount = 0
    for item in cart.items:
        images = item.product.images
        if images:
            item.product.main_image_url = images[0].image_url
        if item.variant_id:
            # If variant_id exists, retrieve variant price
            variant = ProductVariant.query.filter_by(id=item.variant_id).first()
            if variant:
                vp = variant.sale_price if variant.sale_price else variant.price
                total_amount += Decimal(vp) * item.quantity
                item.unit_price = vp
            else:
                total_amount += item.product.sale_price if item.product.sale_price else item.product.price * item.quantity  # Fallback to product price if no variant found
                item.unit_price = item.product.sale_price if item.product.sale_price else item.product.price  # Update individual item price to product price
        else:
            # If no variant, use product price
            total_amount += item.product.price * item.quantity
            item.unit_price = item.product.sale_price if item.product.sale_price else item.product.price  # Update individual item price to product price
    # Handle payment method (COD for now)
    shipping_fee = Config.flat_shipping_rate if hasattr(Config, 'flat_shipping_rate') else 0
    tax =  Decimal(Config.flat_tax_rate if hasattr(Config, 'flat_tax_rate') else 0)
    tax_amount = round((total_amount * tax/100), 2)
    over_alltotal_amount = round(total_amount + tax_amount + shipping_fee, 2)
    #total_amount = total_amount + tax + shipping_fee
    if request.method == 'POST':
        payment_method = request.form.get('payment_method')
        
        if payment_method == 'COD':
            # Generate order number (e.g., combining date with random string)
            order_number = generate_order_number()

            # Create the order
            order = Order(
                user_id=current_user.id,
                order_number=order_number,
                status='pending',
                total_amount=total_amount,
                shipping_address=customer.address_line1,  # Add customer shipping address
                billing_address=customer.address_line1,  # You can adjust this as needed
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.session.add(order)
            db.session.commit()

            # Create the order items
            for item in cart.items:
                # Use the unit price that was updated above
                order_item = OrderProduct(
                    order_id=order.id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    unit_price=item.unit_price,  # Use the updated unit price
                    subtotal=item.unit_price * item.quantity  # Correct subtotal calculation
                )
                db.session.add(order_item)

            # Create the order payment (Cash on Delivery)
            order_payment = OrderPayment(order_id=order.id, payment_method='COD', amount=over_alltotal_amount, status='Pending')
            db.session.add(order_payment)

            # Clear the user's cart
            for item in cart.items:
                db.session.delete(item)  # Delete CartItems from the cart

            db.session.delete(cart)  # Delete Cart
            db.session.commit()

            # Send an email upon order placement (optional)
            # send_order_confirmation_email(order)

            flash("Your order has been placed successfully!", 'success')
            return redirect(url_for('order.view_orders'))

    return render_template('checkout/checkout.html', form=form, cart=cart, total_amount=total_amount, customer=customer, shipping_fee=shipping_fee, tax_amount=tax_amount )

# def checkout():
#     if not current_user.is_authenticated:
#         print("User is not authenticated!")
#         return redirect(url_for('auth.login'))

#     # Initialize the form
#     form = CheckoutForm()

#     # Get the cart for the logged-in user
#     cart = Cart.query.filter_by(user_id=current_user.id).first()
#     if not cart or not cart.items:
#         flash("Your cart is empty!", 'warning')
#         return redirect(url_for('cart.view_cart'))

#     # Ensure that the customer has filled out all required details (phone, name, and address_1)
#     customer = Customer.query.filter_by(user_id=current_user.id).first()
#     if not all([customer.first_name, customer.last_name, customer.phone, customer.address_line1]):
#         flash('Please complete your profile with your name, phone, and address before checking out.', 'warning')
#         return redirect(url_for('auth.update_profile'))

#     total_amount = sum([item.product.price * item.quantity for item in cart.items])


#     # Handle payment method (COD for now)
#     if request.method == 'POST':
#         payment_method = request.form.get('payment_method')
        
#         if payment_method == 'COD':
#             # Generate order number (e.g., combining date with random string)
#             order_number = generate_order_number()

#             # Create the order
#             order = Order(
#                 user_id=current_user.id,
#                 order_number=order_number,
#                 status='pending',
#                 total_amount=total_amount,
#                 shipping_address=customer.address_line1,  # Add customer shipping address
#                 billing_address=customer.address_line1,  # You can adjust this as needed
#                 created_at=datetime.utcnow(),
#                 updated_at=datetime.utcnow()
#             )
#             db.session.add(order)
#             db.session.commit()

#             # Create the order items
#             for item in cart.items:
#                 order_item = OrderProduct(order_id=order.id, product_id=item.product_id, quantity=item.quantity, unit_price=item.product.price, subtotal=item.product.price * item.quantity)
#                 db.session.add(order_item)

#             # Create the order payment (Cash on Delivery)
#             order_payment = OrderPayment(order_id=order.id, payment_method='COD', amount=total_amount, status='Pending')
#             db.session.add(order_payment)

#             # Clear the user's cart
#             for item in cart.items:
#                 db.session.delete(item)  # Delete CartItems from the cart

#             db.session.delete(cart)
#             db.session.commit()

#             # Send an email upon order placement
#             #send_order_confirmation_email(order)

#             flash("Your order has been placed successfully!", 'success')
#             return redirect(url_for('order.view_orders'))

#     return render_template('checkout/checkout.html', form=form, cart=cart, total_amount=total_amount, customer=customer)

def generate_order_number():
    """
    Generate a unique order number.
    You can customize this as needed.
    """
    return f"ORD-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}"


def send_order_confirmation_email(order):
    """Send an order confirmation email to the customer."""
    subject = "Order Confirmation"
    recipient = current_user.email
    body = f"Dear {current_user.username},\n\nYour order with ID {order.id} has been successfully placed.\n\nTotal Amount: ${order.total_amount}\n\nThank you for shopping with us."

    msg = Message(subject, recipients=[recipient], body=body)
    send_email(msg)















# @checkout_bp.route('/checkout', methods=['POST'])
# @login_required
# def create_order():
#     # Get user's cart
#     cart = Cart.query.filter_by(user_id=current_user.id).first()
#     if not cart or not cart.items:
#         return jsonify({'message': 'Cart is empty'}), 400

#     # Verify stock availability and calculate total
#     total = 0
#     for item in cart.items:
#         if item.product.stock < item.quantity:
#             return jsonify({
#                 'message': f'Not enough stock for {item.product.name}',
#                 'available': item.product.stock
#             }), 400
#         total += item.quantity * item.product.price

#     # Create order
#     order = Order(
#         user_id=current_user.id,
#         total=total,
#         status='pending'
#     )
#     db.session.add(order)

#     # Create order items and update product stock
#     for cart_item in cart.items:
#         order_item = OrderItem(
#             order_id=order.id,
#             product_id=cart_item.product_id,
#             quantity=cart_item.quantity,
#             price=cart_item.product.price
#         )
#         db.session.add(order_item)
        
#         # Reduce product stock
#         cart_item.product.stock -= cart_item.quantity

#     # Clear cart
#     CartItem.query.filter_by(cart_id=cart.id).delete()
    
#     db.session.commit()
    
#     return jsonify({
#         'message': 'Order created successfully',
#         'order_id': order.id
#     })

# @checkout_bp.route('/orders', methods=['GET'])
# @login_required
# def get_user_orders():
#     orders = Order.query.filter_by(user_id=current_user.id).all()
#     return jsonify([{
#         'id': order.id,
#         'total': order.total,
#         'status': order.status,
#         'created_at': order.created_at.isoformat(),
#         'items': [{
#             'product_id': item.product_id,
#             'quantity': item.quantity,
#             'price': item.price
#         } for item in order.items]
#     } for order in orders])

# @checkout_bp.route('/orders/<int:id>', methods=['GET'])
# @login_required
# def get_order_details(id):
#     order = Order.query.filter_by(id=id, user_id=current_user.id).first_or_404()
#     return jsonify({
#         'id': order.id,
#         'total': order.total,
#         'status': order.status,
#         'created_at': order.created_at.isoformat(),
#         'items': [{
#             'product_id': item.product_id,
#             'product_name': item.product.name,
#             'quantity': item.quantity,
#             'price': item.price
#         } for item in order.items]
#     })
