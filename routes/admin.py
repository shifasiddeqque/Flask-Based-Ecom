from flask import Blueprint, jsonify, request, render_template, redirect, url_for, flash
from app.models import db, Admin, User, Product, Order, OrderProductHistory, AdminActionLog
from datetime import datetime
from functools import wraps
from flask_login import login_required, current_user

admin_bp = Blueprint('admin', __name__)
@admin_bp.route('/admin')
@login_required
def admin():
    if current_user.role != 'admin':
        flash('You are not authorized to access this page.', 'danger')
        return redirect(url_for('shop.index.html'))  # Redirect to customer home if not admin
    return render_template('adin/dasboard.html')  # Admin dashboard page
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get admin from request context
        admin = Admin.query.filter_by(user_id=request.user_id).first()
        if not admin or not admin.is_active:
            return jsonify({'message': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

def check_permission(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            admin = Admin.query.filter_by(user_id=request.user_id).first()
            if not admin or permission not in admin.permissions:
                return jsonify({'message': 'Permission denied'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Product Management
@admin_bp.route('/products', methods=['GET'])
@admin_required
def get_products():
    products = Product.query.all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'price': p.price,
        'category_id': p.category_id,
        'stock': p.stock
    } for p in products])

@admin_bp.route('/products', methods=['POST'])
@admin_required
@check_permission('product_create')
def create_product():
    data = request.get_json()
    product = Product(**data)
    db.session.add(product)
    
    log = AdminActionLog(
        admin_id=request.admin.id,
        action='create',
        entity_type='product',
        entity_id=product.id,
        details=data
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({'message': 'Product created successfully'})

@admin_bp.route('/products/<int:id>', methods=['PUT'])
@admin_required
@check_permission('product_edit')
def update_product(id):
    product = Product.query.get_or_404(id)
    data = request.get_json()
    for key, value in data.items():
        setattr(product, key, value)
    
    log = AdminActionLog(
        admin_id=request.admin.id,
        action='update',
        entity_type='product',
        entity_id=id,
        details=data
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({'message': 'Product updated successfully'})

@admin_bp.route('/products/<int:id>', methods=['DELETE'])
@admin_required
@check_permission('product_delete')
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    
    log = AdminActionLog(
        admin_id=request.admin.id,
        action='delete',
        entity_type='product',
        entity_id=id
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({'message': 'Product deleted successfully'})

@admin_bp.route('/orders/<int:id>', methods=['GET'])
@admin_required
def get_order_details(id):
    order = Order.query.get_or_404(id)
    return jsonify({
        'id': order.id,
        'user_id': order.user_id,
        'status': order.status,
        'total': order.total,
        'items': order.items,
        'created_at': order.created_at
    })

@admin_bp.route('/orders/<int:id>/status', methods=['PUT'])
@admin_required
@check_permission('order_edit')
def update_order_status(id):
    order = Order.query.get_or_404(id)
    data = request.get_json()
    order.status = data['status']
    
    log = AdminActionLog(
        admin_id=request.admin.id,
        action='update_status',
        entity_type='order',
        entity_id=id,
        details={'status': data['status']}
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({'message': 'Order status updated successfully'})

# Customer Management
@admin_bp.route('/customers', methods=['GET'])
@admin_required
def get_customers():
    users = User.query.filter(User.id.notin_(
        db.session.query(Admin.user_id)
    )).all()
    return jsonify([{
        'id': u.id,
        'email': u.email,
        'name': u.name,
        'created_at': u.created_at
    } for u in users])

@admin_bp.route('/customers/<int:id>', methods=['PUT'])
@admin_required
@check_permission('customer_edit')
def update_customer(id):
    user = User.query.get_or_404(id)
    data = request.get_json()
    for key, value in data.items():
        setattr(user, key, value)
    
    log = AdminActionLog(
        admin_id=request.admin.id,
        action='update',
        entity_type='customer',
        entity_id=id,
        details=data
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({'message': 'Customer updated successfully'})

@admin_bp.route('/customers/<int:id>', methods=['DELETE'])
@admin_required
@check_permission('customer_delete')
def delete_customer(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    
    log = AdminActionLog(
        admin_id=request.admin.id,
        action='delete',
        entity_type='customer',
        entity_id=id
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({'message': 'Customer deleted successfully'})

# Category Management
@admin_bp.route('/categories', methods=['POST'])
@admin_required
@check_permission('category_create')
def create_category():
    data = request.get_json()
    category = Category(**data)
    db.session.add(category)
    
    log = AdminActionLog(
        admin_id=request.admin.id,
        action='create',
        entity_type='category',
        entity_id=category.id,
        details=data
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({'message': 'Category created successfully'})

# New User Creation
@admin_bp.route('/users', methods=['POST'])
@admin_required
@check_permission('user_create')
def create_user():
    data = request.get_json()
    user = User(**data)
    db.session.add(user)
    
    log = AdminActionLog(
        admin_id=request.admin.id,
        action='create',
        entity_type='user',
        entity_id=user.id,
        details=data
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({'message': 'User created successfully'})

@admin_bp.route('/orders', methods=['GET'])
@admin_required
def get_orders():
    orders = Order.query.all()
    return jsonify([{
        'id': o.id,
        'user_id': o.user_id,
        'total': o.total,
        'status': o.status,
        'created_at': o.created_at.isoformat()
    } for o in orders])

@admin_bp.route('/orders/<int:id>', methods=['PUT']) 
@admin_required
@check_permission('order_edit')
def update_order(id):
    order = Order.query.get_or_404(id)
    data = request.get_json()
    
    for key, value in data.items():
        setattr(order, key, value)
        
    log = AdminActionLog(
        admin_id=request.admin.id,
        action='update',
        entity_type='order',
        entity_id=id,
        details=data
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({'message': 'Order updated successfully'})

@admin_bp.route('/orders/<int:id>', methods=['DELETE'])
@admin_required
@check_permission('order_delete') 
def delete_order(id):
    order = Order.query.get_or_404(id)
    db.session.delete(order)
    
    log = AdminActionLog(
        admin_id=request.admin.id,
        action='delete',
        entity_type='order',
        entity_id=id
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({'message': 'Order deleted successfully'})

