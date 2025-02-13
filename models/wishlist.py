from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

from . import db

class Wishlist(db.Model):
    __tablename__ = 'wishlist'  # Table name is 'wishlist'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)  # Foreign key to products
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Foreign key to users (assuming you have a User model)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Define relationships back to Product and User models
    product = db.relationship('Product', backref='wishlist_items', lazy=True)
    
    # Change the backref name to avoid conflict with the existing 'user' attribute in User model
    user = db.relationship('User', backref='wishlist_entries', lazy=True)

    def __repr__(self):
        return f'<Wishlist {self.product.name} added by User {self.user_id}>'
