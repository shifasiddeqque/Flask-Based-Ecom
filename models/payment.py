from datetime import datetime
from . import db

class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    transaction_id = db.Column(db.String(100), unique=True)
    status = db.Column(db.String(20), nullable=False, default='pending')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    order = db.relationship('Order', backref=db.backref('payment', uselist=False))

    def __init__(self, order_id, amount, payment_method, transaction_id=None):
        self.order_id = order_id
        self.amount = amount
        self.payment_method = payment_method
        self.transaction_id = transaction_id

    def update_status(self, new_status):
        self.status = new_status
        self.updated_at = datetime.utcnow()

    def __repr__(self):
        return f'<Payment {self.id} for Order {self.order_id}>'
