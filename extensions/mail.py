# app/extensions/mail.py

from flask_mail import Mail

mail = Mail()

def init_mail(app):
    """
    Initialize the Flask-Mail extension with the app.
    """
    mail.init_app(app)
