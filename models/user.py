from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask import current_app
from itsdangerous import SignatureExpired, BadSignature, TimedSerializer as Serializer
from flask_login import UserMixin


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128))
    is_active = db.Column(db.Boolean, default=True)
    role = db.Column(db.String(50), nullable=False, default='customer')
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    # Relationships
    carts = db.relationship('Cart', back_populates='user')
    orders = db.relationship('Order', back_populates='customer')
    customer_profile = db.relationship('Customer', backref='user', uselist=False)
    wishlist = db.relationship('Wishlist', backref='wishlist_entries', lazy=True)

    # Ensure these methods are implemented for Flask-Login to work correctly
    def get_id(self):
        return str(self.id)  # or self.id based on how you manage user IDs

    def generate_reset_token(self, expires_in=600):
        """Generate a reset password token."""
        s = Serializer(current_app.config['SECRET_KEY'], expires_in)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        """Verify the reset password token."""
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except (SignatureExpired, BadSignature):
            return None
        return User.query.get(data['user_id'])