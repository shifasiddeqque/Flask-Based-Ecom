from flask import Blueprint, jsonify, request, render_template, redirect, url_for, session
from app.models import Product, ProductCategory, ProductImage, RelatedProduct, ProductDetail, Wishlist
from flask_login import login_required, current_user

product_bp = Blueprint('product', __name__)

@product_bp.route('/products', methods=['GET'])
def get_products():
    category_id = request.args.get('category_id', type=int)
    search = request.args.get('search', '')
    sort = request.args.get('sort', 'name')
    
    query = Product.query
    
    if category_id:
        query = query.filter_by(category_id=category_id)
        
    if search:
        query = query.filter(Product.name.ilike(f'%{search}%'))
        
    if sort == 'price_low':
        query = query.order_by(Product.price.asc())
    elif sort == 'price_high':
        query = query.order_by(Product.price.desc())
    else:
        query = query.order_by(Product.name.asc())
        
    products = query.all()
    
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'description': p.description,
        'price': p.price,
        'stock': p.stock,
        'category_id': p.category_id,
        'image_url': p.image_url
    } for p in products])

@product_bp.route('/products/<int:id>', methods=['GET'])
def get_product(id):
    product = Product.query.get_or_404(id)
    return jsonify({
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': product.price,
        'stock': product.stock,
        'category_id': product.category_id,
        'category_name': product.category.name,
        'image_url': product.image_url,
        'specifications': product.specifications,
        'created_at': product.created_at.isoformat()
    })

@product_bp.route('/categories', methods=['GET'])
def get_categories():
    categories = Category.query.all()
    return jsonify([{
        'id': c.id,
        'name': c.name,
        'description': c.description,
        'product_count': len(c.products)
    } for c in categories])

@product_bp.route('/categories/<int:id>', methods=['GET'])
def get_category(id):
    category = Category.query.get_or_404(id)
    return jsonify({
        'id': category.id,
        'name': category.name,
        'description': category.description,
        'products': [{
            'id': p.id,
            'name': p.name,
            'price': p.price,
            'stock': p.stock,
            'image_url': p.image_url
        } for p in category.products]
    })

@product_bp.route('/products/featured', methods=['GET'])
def get_featured_products():
    featured_products = Product.query.filter_by(is_featured=True).limit(6).all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'price': p.price,
        'image_url': p.image_url,
        'category_name': p.category.name
    } for p in featured_products])

@product_bp.route('/products/new', methods=['GET'])
def get_new_products():
    new_products = Product.query.order_by(Product.created_at.desc()).limit(8).all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'price': p.price,
        'image_url': p.image_url,
        'category_name': p.category.name
    } for p in new_products])