from flask import render_template, Blueprint
from flask_login import login_required, current_user

from app.models import Wishlist  # Import your wishlist model

wishlist_bp = Blueprint('wishlist', __name__)

@wishlist_bp.route('/wishlist')
@login_required  # Ensure the user is logged in
def view_wishlist():
    # Query the user's wishlist items from the database
    wishlist_items = Wishlist.query.filter_by(user_id=current_user.id).all()
    return render_template('customer/wishlist.html', wishlist_items=wishlist_items)
