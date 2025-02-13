# app/middleware/auth.py

from flask import session, request, redirect, url_for, g

def check_user_logged_in(app):
    """
    This function runs before every request. It checks if the user is logged in.
    If not, it redirects to the login page.
    """
    @app.before_request
    def before_request():
       # Ensure 'cart' is initialized in session if not already
        if 'cart' not in session:
            session['cart'] = []  # Initialize the cart if it doesn't exist
        # Set the global cart count for the current request
        g.cart_count = len(session['cart'])  # Set cart count
        print(f"Cart count: {g.cart_count}")
        if 'admin_id' not in session and request.endpoint not in ['auth.login', 'static', 'auth.check_db_connection']:
            print('redirecting sid...',request)
            return redirect(url_for('auth.login'))
        


