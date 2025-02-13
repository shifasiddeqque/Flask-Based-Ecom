from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional

class CustomerForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=1, max=100)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=1, max=100)])
    phone = StringField('Phone', validators=[Optional(), Length(max=20)])
    address_line1 = StringField('Address Line 1', validators=[Optional(), Length(max=200)])
    address_line2 = StringField('Address Line 2', validators=[Optional(), Length(max=200)])
    city = StringField('City', validators=[Optional(), Length(max=100)])
    state = StringField('State', validators=[Optional(), Length(max=100)])
    postal_code = StringField('Postal Code', validators=[Optional(), Length(max=20)])
    country = StringField('Country', validators=[Optional(), Length(max=100)])

    submit = SubmitField('Update Profile')
