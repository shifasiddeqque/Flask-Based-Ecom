from flask_wtf import FlaskForm
from wtforms import RadioField, SubmitField
from flask_wtf.csrf import CSRFProtect

# FlaskForm to handle CSRF and form elements
class CheckoutForm(FlaskForm):
    payment_method = RadioField('Payment Method', choices=[('COD', 'Cash on Delivery (COD)')], default='COD')
    submit = SubmitField('Place Order')
