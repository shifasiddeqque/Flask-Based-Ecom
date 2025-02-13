# appmodels/__init__.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .cart import Cart, CartItem
from .product import Product, ProductImage, ProductDetail, RelatedProduct, ProductCategory, ProductVariant
from .payment import Payment
from .user import User
from .admin import Admin, AdminActionLog
from .customer import Customer
from .order import Order, OrderHistory, OrderProductHistory
from .wishlist import Wishlist

