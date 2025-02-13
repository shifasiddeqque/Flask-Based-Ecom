from app.routes.product import product_bp
from app.routes.cart import cart_bp
from app.routes.checkout import checkout_bp
from app.routes.shop import shop_bp
from app.routes.auth.auth import auth_bp
from app.routes.admin import admin_bp
from app.routes.payment import payment_bp
from app.routes.wishlist import wishlist_bp
from app.routes.auth.auth import auth_bp
from app.routes.auth.customer import customer_bp
from app.routes.order import order_bp

def register_blueprints(app):
    """Register all blueprints"""
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(product_bp, url_prefix='/product')
    app.register_blueprint(cart_bp, url_prefix='/cart')
    app.register_blueprint(checkout_bp, url_prefix='/checkout') 
    app.register_blueprint(shop_bp, url_prefix='')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(payment_bp, url_prefix='/payment')
    app.register_blueprint(wishlist_bp, url_prefix='')
    app.register_blueprint(customer_bp, url_prefix='/customer')
    app.register_blueprint(order_bp, url_prefix='/order')