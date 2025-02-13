from datetime import datetime, timezone
from sqlalchemy import Column, Integer, ForeignKey, String, DateTime
from sqlalchemy.orm import relationship
from . import db

class Cart(db.Model):
    __tablename__ = 'carts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    # Relationships
    user = db.relationship('User', back_populates='carts')
    items = db.relationship('CartItem', back_populates='cart', cascade='all, delete-orphan')

    @property
    def subtotal(self):
        return sum(item.subtotal for item in self.items)

    @property 
    def total_items(self):
        return sum(item.quantity for item in self.items)

    def add_item(self, product, quantity=1):
        existing_item = CartItem.query.filter_by(
            cart_id=self.id, 
            product_id=product.id
        ).first()

        if existing_item:
            existing_item.quantity += quantity
        else:
            item = CartItem(
                cart=self,
                product=product,
                quantity=quantity
            )
            db.session.add(item)

    def remove_item(self, product_id):
        CartItem.query.filter_by(
            cart_id=self.id,
            product_id=product_id
        ).delete()

    def clear(self):
        CartItem.query.filter_by(cart_id=self.id).delete()

    def __repr__(self):
        return f'<Cart {self.id}>'

class CartItem(db.Model):
    __tablename__ = 'cart_items'
    
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    variant_id = db.Column(db.Integer, db.ForeignKey('product_variants.id'), nullable=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    # Relationships
    cart = db.relationship('Cart', back_populates='items')
    product = db.relationship('Product')
    variant = db.relationship('ProductVariant', backref='cart_items') 

    @property
    def subtotal(self):
        return self.product.price * self.quantity

    def __repr__(self):
        return f'<CartItem {self.id}>'
