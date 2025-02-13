from flask import render_template, Blueprint, abort, redirect, url_for
from flask_login import login_required, current_user
from app.models import Order  # Import your order model
from app.models import db

order_bp = Blueprint('order', __name__)

@order_bp.route('/orders')
def view_orders():
    # Query all orders for the current logged-in user
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()

    return render_template('order/orders.html', orders=orders)

@order_bp.route('/order/<int:order_id>')
def view_order(order_id):
    # Query the order by ID and make sure it belongs to the current user
    order = Order.query.filter_by(user_id=current_user.id, id=order_id).first()

    if not order:
        abort(404, description="Order not found or does not belong to the user.")
    
    return render_template('order/order_list.html', order=order)


@order_bp.route('/orders/<int:order_id>/cancel', methods=['POST'])
def cancel_order(order_id):
    order = Order.query.filter_by(user_id=current_user.id, id=order_id).first()
    if not order:
        abort(404)  # If the order doesn't exist or doesn't belong to the user
    order.status = 'cancelled'
    db.session.commit()
    return redirect(url_for('order.view_orders'))

def customer_orders():
    orders = Order.query.filter_by(user_id=current_user.id).all()
    return render_template('order/order.html', orders=orders)




