from datetime import datetime, timezone
from . import db

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    sale_price = db.Column(db.Numeric(10, 2), default=price)
    stock = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    category_id = db.Column(db.Integer, db.ForeignKey('product_categories.id'))
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    stock = db.Column(db.Integer, default=0)
    unit = db.Column(db.String(10), default='pcs')

    # Relationships
    category = db.relationship('ProductCategory', back_populates='products')
    details = db.relationship('ProductDetail', back_populates='product', cascade='all, delete-orphan')
    images = db.relationship('ProductImage', back_populates='product', cascade='all, delete-orphan')
    related = db.relationship('RelatedProduct', back_populates='product', foreign_keys='[RelatedProduct.product_id]', cascade='all, delete-orphan')
    variants = db.relationship('ProductVariant', backref='product', lazy=True)

    def get_available_stock(self):
        if self.variants:
            # If variants exist, return stock for each variant
            total_stock = sum(variant.stock for variant in self.variants)
            return total_stock
        else:
            # If no variants, return stock from the product itself
            return self.stock
    def get_price_range(self):
        """Returns the minimum and maximum price of the product's variants."""
        if not self.variants:
            return (0, 0)  # Return zero range if no variants
        
        prices = [variant.price for variant in self.variants]
        return (min(prices), max(prices))

class ProductCategory(db.Model):
    __tablename__ = 'product_categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    parent_id = db.Column(db.Integer, db.ForeignKey('product_categories.id'))
    
    # Relationships
    products = db.relationship('Product', back_populates='category')
    subcategories = db.relationship('ProductCategory', backref=db.backref('parent', remote_side=[id]))

class ProductDetail(db.Model):
    __tablename__ = 'product_details'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    key = db.Column(db.String(100), nullable=False)
    value = db.Column(db.String(200), nullable=False)

    # Relationships
    product = db.relationship('Product', back_populates='details')

class ProductImage(db.Model):
    __tablename__ = 'product_images'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    alt_text = db.Column(db.String(200))
    is_primary = db.Column(db.Boolean, default=False)
    display_order = db.Column(db.Integer, default=0)

    # Relationships
    product = db.relationship('Product', back_populates='images')

class RelatedProduct(db.Model):
    __tablename__ = 'related_products'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    related_product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    relationship_type = db.Column(db.String(50), nullable=False)  # similar, accessory, cross-sell
    display_order = db.Column(db.Integer, default=0)

    # Relationships
    product = db.relationship('Product', foreign_keys=[product_id], back_populates='related')
    related_product = db.relationship('Product', foreign_keys=[related_product_id])

class ProductVariant(db.Model):
    __tablename__ = 'product_variants'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)  # Foreign Key Reference to Product Table
    size = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    sale_price = db.Column(db.Numeric(10, 2), default=price)
    color = db.Column(db.String(50), nullable=False)
    stock = db.Column(db.Integer, default=0)  # Stock at the variant level
