from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from . import db

class Admin(db.Model):
    __tablename__ = 'admins'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    # Relationships
    user = db.relationship('User', backref='user_admin')

    def __repr__(self):
        return f'<Admin {self.id}>'


class AdminActionLog(db.Model):
    __tablename__ = 'admin_action_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admins.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    entity_type = db.Column(db.String(50), nullable=False)  # user, order, product, etc.
    entity_id = db.Column(db.Integer, nullable=False)
    details = db.Column(db.JSON)
    ip_address = db.Column(db.String(45))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    admin = db.relationship('Admin', backref='action_logs')

    def __repr__(self):
        return f'<AdminActionLog {self.action}>'

class AdminProductManagement(db.Model):
    __tablename__ = 'admin_product_management'
    
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admins.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    action_type = db.Column(db.String(50), nullable=False)  # added_related, added_latest, updated_details, etc
    related_product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    relationship_type = db.Column(db.String(50))  # similar, complementary, accessory
    featured_start_date = db.Column(db.DateTime)
    featured_end_date = db.Column(db.DateTime) 
    display_order = db.Column(db.Integer)
    details = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    admin = db.relationship('Admin', backref='product_management_actions')
    product = db.relationship('Product', foreign_keys=[product_id], backref='admin_management_actions')
    related_product = db.relationship('Product', foreign_keys=[related_product_id])

    def __repr__(self):
        return f'<AdminProductManagement {self.action_type}>'

    def add_related_product(self, related_product_id, relationship_type):
        """Add a related product relationship"""
        self.action_type = 'added_related'
        self.related_product_id = related_product_id
        self.relationship_type = relationship_type
        db.session.add(self)
        db.session.commit()

    def add_latest_product(self, start_date, end_date, display_order=0):
        """Add product to latest products"""
        self.action_type = 'added_latest'
        self.featured_start_date = start_date
        self.featured_end_date = end_date
        self.display_order = display_order
        db.session.add(self)
        db.session.commit()

    def update_product_details(self, details):
        """Update product details"""
        self.action_type = 'updated_details'
        self.details = details
        db.session.add(self)
        db.session.commit()
