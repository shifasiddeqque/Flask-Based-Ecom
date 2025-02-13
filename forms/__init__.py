from flask_wtf import FlaskForm
from wtforms import StringField, SelectField
from wtforms.validators import DataRequired

class CheckoutForm(FlaskForm):
    shipping_address = StringField('Shipping Address', validators=[DataRequired()])
    billing_address = StringField('Billing Address', validators=[DataRequired()])
    payment_method = SelectField('Payment Method', 
                               choices=[
                                   ('credit_card', 'Credit Card'),
                                   ('debit_card', 'Debit Card'),
                                   ('paypal', 'PayPal')
                               ],
                               validators=[DataRequired()])
