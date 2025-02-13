from flask import Blueprint, render_template, request, current_app, session
from app.models import db, Product, ProductImage, ProductDetail, ProductVariant
from flask_login import login_required
from flask import flash, redirect, url_for


shop_bp = Blueprint('shop', __name__)

@shop_bp.route('/')

def index():
    per_page = current_app.config.get('PER_PAGE', 10)  # Default to 10 items per page
    
    # Get the current page from the request arguments (defaults to 1 if not provided)
    page = request.args.get('page', 1, type=int)
    
    # Get the paginated products
    products = Product.query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Loop through products and their images
    for product in products.items:
        product.variants = ProductVariant.query.filter_by(product_id=product.id).all()
        images = product.images  # Get associated images for the product
        if images:
            # Assuming the first image is the main image for the product
            product.main_image_url = images[0].image_url  # Assuming `image_url` is the field storing the image path
    
    # Return the rendered template with paginated products and pagination info
    return render_template('shop/index.html', products=products.items, pagination=products)
@shop_bp.route('/category/<int:category_id>')
@login_required
def category(category_id):
    """Show products filtered by category"""
    products = Product.query.filter_by(category_id=category_id).all()
    return render_template('shop/index.html', products=products)

@shop_bp.route('/search')
def search():
    """Search products"""
    per_page = current_app.config.get('PER_PAGE', 10)  # Default to 10 items per page
    
    # Get the current page from the request arguments (defaults to 1 if not provided)
    page = request.args.get('page', 1, type=int)

    query = request.args.get('q', '')

   # Assuming `query` is the search term from the user input
    products_query = Product.query.filter(Product.name.ilike(f'%{query}%'))

    # Apply pagination to the filtered query
    products = products_query.paginate(page=page, per_page=per_page, error_out=False)


    print("diss",products)
    return render_template('shop/index.html', products=products, pagination=products)
@shop_bp.route('/product/<int:product_id>')
def product_detail(product_id):
    # Query the product
    product = Product.query.get_or_404(product_id)

    # Fetch related products (based on category_id or other criteria)
    related_products = Product.query.filter(Product.category_id == product.category_id).limit(4).all()

    # Fetch product images
    product_images = ProductImage.query.filter_by(product_id=product_id).order_by(ProductImage.display_order).all()
    
    # Fetch the primary image (the one with is_primary = 1)
    primary_image = next((img for img in product_images if img.is_primary), None)

    # Pass the data to the template
    data = {
        "product": product, 
        "product_images": product_images, 
        "primary_image": primary_image,
        "related_products": related_products
    }

    return render_template('shop/product_detail.html', **data)


