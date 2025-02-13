from flask import Blueprint, jsonify, request
from app.models import db, Order
from flask_login import login_required, current_user

payment_bp = Blueprint('payment', __name__)

@payment_bp.route('/payment/options', methods=['GET'])
@login_required
def get_payment_options():
    return jsonify({
        'payment_methods': [
            {
                'id': 'credit_card',
                'name': 'Credit Card',
                'supported_cards': ['visa', 'mastercard', 'amex']
            },
            {
                'id': 'paypal',
                'name': 'PayPal'
            },
            {
                'id': 'bank_transfer', 
                'name': 'Bank Transfer'
            }
        ]
    })

@payment_bp.route('/payment/process/<int:order_id>', methods=['POST'])
@login_required
def process_payment(order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    
    if order.status != 'pending':
        return jsonify({'message': 'Order cannot be processed'}), 400
        
    data = request.get_json()
    payment_method = data.get('payment_method')
    shipping_address = data.get('shipping_address')
    
    if not payment_method or not shipping_address:
        return jsonify({'message': 'Missing payment method or shipping address'}), 400
    
    # Validate shipping address
    required_fields = ['street', 'city', 'state', 'postal_code', 'country']
    if not all(field in shipping_address for field in required_fields):
        return jsonify({'message': 'Invalid shipping address'}), 400
    
    # Process payment based on method
    try:
        if payment_method == 'credit_card':
            card_details = data.get('card_details')
            if not card_details or not all(k in card_details for k in ['number', 'exp_month', 'exp_year', 'cvv']):
                return jsonify({'message': 'Invalid card details'}), 400
            # Process credit card payment here
            
        elif payment_method == 'paypal':
            paypal_token = data.get('paypal_token')
            if not paypal_token:
                return jsonify({'message': 'Invalid PayPal token'}), 400
            # Process PayPal payment here
            
        elif payment_method == 'bank_transfer':
            bank_details = data.get('bank_details')
            if not bank_details or not all(k in bank_details for k in ['account_number', 'routing_number']):
                return jsonify({'message': 'Invalid bank details'}), 400
            # Process bank transfer here
            
        else:
            return jsonify({'message': 'Unsupported payment method'}), 400
        
        # Update order status and add shipping details
        order.status = 'paid'
        order.shipping_address = shipping_address
        order.payment_method = payment_method
        db.session.commit()
        
        return jsonify({
            'message': 'Payment processed successfully',
            'order_id': order.id,
            'status': order.status
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Payment processing failed: {str(e)}'}), 500

@payment_bp.route('/shipping/calculate', methods=['POST'])
@login_required
def calculate_shipping():
    data = request.get_json()
    shipping_address = data.get('shipping_address')
    order_id = data.get('order_id')
    
    if not shipping_address or not order_id:
        return jsonify({'message': 'Missing shipping address or order ID'}), 400
        
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    
    # Calculate shipping options based on address and order details
    shipping_options = [
        {
            'method': 'standard',
            'price': 10.00,
            'estimated_days': '5-7 business days'
        },
        {
            'method': 'express',
            'price': 25.00,
            'estimated_days': '2-3 business days'
        },
        {
            'method': 'overnight',
            'price': 50.00,
            'estimated_days': '1 business day'
        }
    ]
    
    return jsonify({
        'shipping_options': shipping_options
    })
