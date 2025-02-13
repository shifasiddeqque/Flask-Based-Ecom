from flask import Blueprint, jsonify, request, render_template, session, url_for, redirect, g
from app.models import db, Cart, Product, CartItem, ProductVariant
from flask_login import login_required, current_user
from app.extensions.loginmanager import login_manager
from flask_wtf.csrf import CSRFProtect
from decimal import Decimal
from app.config.config import Config

cart_bp = Blueprint('cart', __name__)

@cart_bp.route('/cart')
def view_cart():
    total_price = Decimal(0)  # Initialize total_price as Decimal
    cart_items = []

    # For logged-in users, fetch the cart from the database
    if current_user.is_authenticated:
        cart = Cart.query.filter_by(user_id=current_user.id).first()
        if cart:
            # Fetch cart items along with their variants (if any)
            cart_items = (
                db.session.query(CartItem)
                .join(ProductVariant, isouter=True)  # Left join with Variant to handle products without variants
                .filter(CartItem.cart_id == cart.id)
                .all()
            )

            # Calculate total price
            for item in cart_items:
                product = item.product
                variant = item.variant
                images = item.product.images
                if images:
                    product.main_image_url = images[0].image_url

                # Handle product with or without a variant
                if variant:
                    price = Decimal(variant.sale_price if variant.sale_price else variant.price)  # Ensure variant price is Decimal
                else:
                    price = Decimal(product.sale_price if product.sale_price else product.price)  # Use product price if there's no variant

                total_price += price * Decimal(item.quantity) 
        else:
            cart_items = []
            total_price = Decimal(0)  # Reset total price if no cart found

    # For guests, fetch cart items from session
    else:
        if 'cart' in session:
            for item in session['cart']:
                product = Product.query.get(item['product_id'])
                if not product:
                    continue  # Skip invalid product

                # Get the product's image (if available)
                images = product.images
                if images:
                    product.main_image_url = images[0].image_url

                variant = ProductVariant.query.get(item['variant_id'])  # Fetch the variant based on variant_id
                if product and variant:  # Ensure both product and variant exist
                    cart_items.append({'product': product, 'variant': variant, 'quantity': item['quantity']})

                    # Ensure that variant price is Decimal and multiply with quantity
                    total_price += Decimal(variant.price) * Decimal(item['quantity'])  # Convert quantity to Decimal
                elif product:  # In case no variant, use the product price
                    cart_items.append({'product': product, 'variant': None, 'quantity': item['quantity']})

                    # Ensure that product price is Decimal and multiply with quantity
                    total_price += Decimal(product.price) * Decimal(item['quantity'])  # Convert quantity to Decimal

    # Return the template with cart items and total price
    return render_template('cart/cart.html', cart_items=cart_items, total_price=total_price)

@cart_bp.route('/add_to_cart/', methods=['POST'])
def add_to_cart():

    product_id = request.args.get('product_id')  # Get product_id from URL
    quantity = int(request.form.get('quantity', 1))  # Get quantity from form data
    variant_id = request.form.get('variant_id')  # Get selected variant ID from form data
    csrf_token = request.form['csrf_token']

    # Fetch the product based on product_id
    product = Product.query.get(product_id)

    if not product:
        return "Product not found", 404

    # If variant_id is provided, attempt to fetch the variant
    variant = None
    variant_price = product.price  # Default to product price (if no variant exists)
    if variant_id:
        variant = ProductVariant.query.get(variant_id)
        if variant:
            variant_price = variant.price  # If a valid variant is found, use its price
        else:
            # If an invalid variant_id is provided, return an error
            return "Variant not found", 404

    # Case where no variant is selected (variant is None)
    if not variant:
        # No variant selected or valid variant was found, use the product price
        variant_id = None  # Set variant_id to None for products without variants

    # Check if the user is authenticated
    if current_user.is_authenticated:
        # For authenticated users, we store the cart in the database
        cart = Cart.query.filter_by(user_id=current_user.id).first()
        if not cart:
            cart = Cart(user_id=current_user.id)
            db.session.add(cart)

        # Check if the product (with or without variant) is already in the cart
        cart_item = CartItem.query.filter_by(cart_id=cart.id, product_id=product.id, variant_id=variant_id).first()
        if cart_item:
            # Increase the quantity if the item already exists in the cart
            cart_item.quantity += quantity
        else:
            # Add the new product (with or without variant) to the cart
            cart_item = CartItem(cart_id=cart.id, product_id=product.id, quantity=quantity, variant_id=variant_id)
            db.session.add(cart_item)

        db.session.commit()
        return redirect(url_for('cart.view_cart'))  # Redirect to the cart page

    else:
        # For guests (unauthenticated users), we store the cart in the session
        if 'cart' not in session:
            session['cart'] = []

        # Check if the product with the same variant (or no variant) is already in the cart
        item_exists = False
        for item in session['cart']:
            if item['product_id'] == product.id and item['variant_id'] == variant_id:
                item['quantity'] += quantity  # Increase the quantity of the existing item
                item_exists = True
                break

        if not item_exists:
            # Add new item to the cart session (with the variant or product)
            session['cart'].append({'product_id': product.id, 'quantity': quantity, 'variant_id': variant_id})

        session.modified = True  # Mark session as modified to ensure updates are saved
        return redirect(url_for('cart.view_cart'))  # Redirect to the cart page


@cart_bp.route('/remove_from_cart', methods=['POST', 'GET'])
def remove_from_cart(): 
    try:
        # Get the item ID from the request body
        item_id = request.get_json()
        print("nischal item_id",item_id)
        if not item_id or 'itemId' not in item_id:
            return jsonify({'message': 'Item ID is required'}), 400
        print("nischals item_id",item_id)
        # Retrieve the cart item
        cart_item = CartItem.query.get_or_404(item_id['itemId'])
        print("nischals cart_item",cart_item)
        # Ensure the current user is the owner of the cart
        if cart_item.cart.user_id != current_user.id:
            return jsonify({'message': 'Unauthorized'}), 403

        # Delete the cart item and commit the changes to the database
        db.session.delete(cart_item)
        db.session.commit()
        print("nischal cart_item",cart_item)            
        # Optionally, you can return updated cart totals or other relevant info
        updated_totals = get_updated_cart_totals(current_user.id)
        
        return jsonify({'status': 'success', 'message': 'Item removed from cart', 'product_name': cart_item.product.name, 'updated_totals': updated_totals}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'An error occurred while removing the item from the cart'}), 500

def get_updated_cart_totals(user_id):
    print("inside user", user_id)
    # Get the cart associated with the current user
    cart = Cart.query.filter_by(user_id=user_id).first()
    
    if not cart:
        return {'subtotal': 0, 'tax': 0, 'total': 0}  # Empty cart or no cart found

    # Initialize variables for total calculations
    subtotal = 0
    tax_rate = 0.07  # Example: 7% tax rate

    for cart_item in cart.items:  # Assuming a one-to-many relationship between Cart and CartItem
        subtotal += cart_item.price * cart_item.quantity

    # Calculate tax
    tax = subtotal * tax_rate

    # Total after tax
    total = subtotal + tax

    # Return the updated totals as a dictionary
    return {
        'subtotal': round(subtotal, 2),
        'tax': round(tax, 2),
        'total': round(total, 2)
    }


@cart_bp.route('/cart/clear', methods=['POST'])
@login_required
def clear_cart():
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    if cart:
        CartItem.query.filter_by(cart_id=cart.id).delete()
        db.session.commit()
    return jsonify({'message': 'Cart cleared'})

@cart_bp.before_request
def cart_count():
    # This function will run before every request to update cart count
    if current_user.is_authenticated:
        # If the user is logged in, count the items from the database
        cart = Cart.query.filter_by(user_id=current_user.id).first()
        if cart:
            cart_items = CartItem.query.filter_by(cart_id=cart.id).all()
            total_count = sum(item.quantity for item in cart_items)
        else:
            total_count = 0
    else:
        # If the user is not logged in, count the items from the session
        total_count = 0
        if 'cart' in session:
            total_count = sum(item['quantity'] for item in session['cart'])

    # Store the cart count in g (global context for each request)
    g.cart_count = total_count

@cart_bp.route('/update_cart', methods=['POST'])
def update_cart():
    try:
        product_id = int(request.form['product_id'])
        action = request.form['action']
        csrf_token = request.form['csrf_token']

        if current_user.is_authenticated:
            cart = Cart.query.filter_by(user_id=current_user.id).first()
            if cart and hasattr(cart, 'items'):
                
                cart_item = CartItem.query.filter_by(cart_id=cart.id, product_id=product_id).first()

                if cart_item:
                    print("cart_item", cart_item)
                    if action == 'increase':
                        cart_item.quantity += 1
                    elif action == 'decrease':
                        if cart_item.quantity > 1:
                            cart_item.quantity -= 1
                        else:
                            # Remove item from cart if quantity is 1 or less
                            db.session.delete(cart_item)
                    db.session.commit()

                total_price = 0
                for item in cart.items:
                    variant = ProductVariant.query.get(item.variant_id)

                    if variant:
                        item_price = variant.sale_price if variant.sale_price else variant.price
                    else:
                        product = Product.query.get(item.product_id)  # Fetch the product based on product_id
                        item_price = product.sale_price if product.sale_price else product.price
                    total_price += float(item.quantity) * float(item_price)

                    cart_count = len(cart.items)
    
                    return jsonify({
                        'updated_quantity': cart_item.quantity,
                        'product_price': float(item_price),
                        'total_price': total_price,
                        'cart_count': cart_count
                    })

        else:  # For guest users
           if 'cart' in session:
            cart = session['cart']
            item_found = False
            updated_item = None  # Store the updated item to track its new quantity

            # Loop through the cart to find the item and modify its quantity
            for item in cart:
                if item['product_id'] == product_id:
                    item_found = True
                    if action == 'increase':
                        item['quantity'] += 1
                    elif action == 'decrease':
                        if item['quantity'] > 1:
                            item['quantity'] -= 1
                        else:
                            cart.remove(item)  # Remove the item if quantity reaches 0
                    updated_item = item  # Store the updated item
                    break
            
            # If item quantity is 0 or less, remove it from the cart
            if item_found and updated_item and updated_item['quantity'] <= 0:
                cart.remove(updated_item)

            session.modified = True  # Mark session as modified

            # Recalculate the total price and cart count
            total_price = 0
            cart_count = len(cart)  # Get the current number of items in the cart
            updated_product_total = 0  # This will hold the updated total for the modified product

            # Loop through the cart to calculate the total price and individual item totals
            for item in cart:
                variant = ProductVariant.query.get(item['variant_id'])  # Fetch the variant based on variant_id
                if variant:
                    #need to change sale price
                    individual_product_total = float(variant.sale_price if variant.sale_price else variant.price) * item['quantity']
                    total_price += individual_product_total
                    if item == updated_item:
                        updated_product_total = individual_product_total  # Track the updated product total
                else:
                    product = Product.query.get(item['product_id'])
                    if product:
                        individual_product_total = float(product.price) * item['quantity']
                        total_price += individual_product_total
                        if item == updated_item:
                            updated_product_total = individual_product_total  # Track the updated product total
            # Return the updated cart information
            return jsonify({
                'updated_quantity': updated_item['quantity'] if updated_item else 0,  # Show updated quantity for the item
                'product_price': float(Product.query.get(product_id).price),
                'total_price': total_price,
                'cart_count': cart_count,
                'updated_product_total': float(updated_product_total)  # Return the updated individual product total
            })
    except Exception as e:
        error_message = str(e)
        print(f"Error updating cart: {e}")
        return jsonify({
                 'success': False,
                 'error': True,
                 'error_message': error_message
            })


    # If no cart found or other error
    return jsonify({'error': 'Cart update failed.'}), 400

def merge_session_cart_into_user_cart():
    # Check if there's a cart in the session and user is authenticated
    
    if 'cart' in session and current_user.is_authenticated:
        session_cart_items = session['cart']
        #user_cart = Cart.query.filter_by(user_id=current_user.id, is_active=True).first()
        user_cart = Cart.query.filter_by(user_id=current_user.id).first()

        if not user_cart:
            user_cart = Cart(user_id=current_user.id)
            db.session.add(user_cart)
            db.session.commit()

        # Merge session cart items into user's cart
        for item in session_cart_items:
            # Look for the product in the user's cart (considering variant_id as well)
            existing_item = CartItem.query.filter_by(cart_id=user_cart.id, product_id=item['product_id'], variant_id=item.get('variant_id')).first()
            
            if existing_item:
                # If item exists in the cart, update the quantity
                existing_item.quantity += item['quantity']
            else:
                # If item doesn't exist in the cart, add a new CartItem
                new_item = CartItem(
                    cart_id=user_cart.id, 
                    product_id=item['product_id'], 
                    quantity=item['quantity'], 
                    variant_id=item.get('variant_id')  # Include variant_id if available
                )
                db.session.add(new_item)
                print(f"Added new item: {new_item}")  # Debugging
        
        # Commit the changes and clear the session cart
        db.session.commit()
        session.pop('cart', None)  # Remove cart from session to prevent re-adding it
# Helper function to calculate cart totals
def calculate_cart_totals(cart_id):
   
    cart_items = CartItem.query.filter_by(cart_id=cart_id).all()

    subtotal = 0
    for item in cart_items:
        # If the item has a variant (variant_id is not None), we check the price and sale price for that variant
        if item.variant_id:
            variant = item.variant  # Assuming item.variant is an object, not a dictionary
            # Access variant's price or sale_price directly
            variant_price = variant.sale_price if variant.sale_price else variant.price
        else:
            # No variant, use product price or sale price
            variant_price = item.product.sale_price if item.product.sale_price else item.product.price
        
        # If no valid price was found, default to 0
        if variant_price is None:
            variant_price = 0
        
        # Add the calculated price for the item to the subtotal (considering quantity)
        subtotal += item.quantity * variant_price

    # Assuming a flat shipping rate is available in Config
    tax =  Decimal(Config.flat_tax_rate if hasattr(Config, 'flat_tax_rate') else 0)
    tax_amount = round((subtotal * tax/100), 2)
    shipping_fee = Config.flat_shipping_rate if hasattr(Config, 'flat_shipping_rate') else 0
    # Calculate total with shipping fee
    total = subtotal + shipping_fee + tax_amount

    # Return values
    return subtotal, total, tax_amount



@cart_bp.route('/update_cart_checkout', methods=['POST'])
def update_cart_checkout():
    try:
        data = request.get_json()  # Get JSON data from the request
        print(f"Received data: {data}")  # Log the incoming data for debugging

        if 'cart' not in data:
            return jsonify({'status': 'error', 'message': "'cart' missing in request"}), 400
        
        cart = data['cart']  # Assuming the User model has a relationship to Cart
        if not cart:
            return jsonify({'status': 'error', 'message': 'Cart not found for this user'})  # Extract the cart data
        items = cart.get('items', [])

        if not items:
            return jsonify({'status': 'error', 'message': "'items' missing in 'cart'"}), 400
        
        for item in items:
            # Log the entire item to verify its structure
            item_id = item.get('itemId') 
            new_quantity = item.get('quantity')
            unit_price = item.get('unit_price')
            variant_id = item.get('variant_id')

            # Validation for item fields
            if not item_id or not new_quantity or not unit_price:
                return jsonify({'status': 'error', 'message': 'Missing itemId, quantity, or unit_price'}), 400

            # Retrieve the user's cart
            cartid = Cart.query.filter_by(user_id=current_user.id).first()

            if not cartid:
                return jsonify({'status': 'error', 'message': 'Cart not found for the user'}), 400

            item_found = False  # Reset flag for each item iteration

            if variant_id:
                
                # Try to find the item by variant_id and item_id
                cart_item = CartItem.query.filter_by(cart_id=cartid.id, product_id=item_id, variant_id=variant_id).first()
            else:
                # If no variant_id, look for the product by item_id
                cart_item = CartItem.query.filter_by(cart_id=cartid.id, product_id=item_id).first()
            if cart_item:
                # Update existing cart item
                cart_item.quantity = new_quantity
                #cart_item.price = unit_price  # Ensure price is a valid number
                cart_item.variant_id = variant_id
                db.session.add(cart_item)
                item_found = True
            else:
                # If item doesn't exist in cart, add it
                if variant_id:
                    new_cart_item = CartItem(cart_id=cartid.id, product_id=item_id, quantity=new_quantity, variant_id=variant_id)
                else:
                    new_cart_item = CartItem(cart_id=cartid.id, product_id=item_id, quantity=new_quantity, variant_id='')
                db.session.add(new_cart_item)
                item_found = True
        # If no items were found or updated/added, return an error message
        if not item_found:
            return jsonify({'status': 'error', 'message': 'Item not found in cart'}), 400

        # Commit the transaction if everything is successful
        db.session.commit()

        
        subtotal, total, tax_amount = calculate_cart_totals(cartid.id)

        # Return updated cart and totals to frontend
        return jsonify({
            'status': 'success',
            'subtotal': subtotal,
            'cartTotal': total,
            'tax_amount': tax_amount
        })

    except Exception as e:
        print(f"Error occurred: {e}")  # Print error for debugging
        return jsonify({'status': 'error', 'message': str(e)}), 400







# def update_cart():
#     product_id = request.form['product_id']
#     action = request.form['action']  # Can be 'increase' or 'decrease'
#     csrf_token = request.form['csrf_token']

#     # For logged-in users, handle cart update in the database
#     if current_user.is_authenticated:
#         cart = Cart.query.filter_by(user_id=current_user.id).first()
#         if cart:
#             # Find the cart item associated with the product
#             cart_item = CartItem.query.filter_by(cart_id=cart.id, product_id=product_id).first()
#             if cart_item:
#                 # Update the quantity based on action
#                 if action == 'increase':
#                     cart_item.quantity += 1
#                 elif action == 'decrease' and cart_item.quantity > 1:
#                     cart_item.quantity -= 1
#                 db.session.commit()  # Commit the changes to the database

#                 # Calculate the new total price for the cart
#                 total_price = sum(item.quantity * item.product.price for item in cart.cart_items)
#                 cart_count = len(cart.cart_items)  # Correct cart count

#                 return jsonify({
#                     'updated_quantity': cart_item.quantity,
#                     'product_price': cart_item.product.price,
#                     'total_price': total_price,
#                     'cart_count': cart_count
#                 })

#     # For guests (unauthenticated users), handle cart update in the session
#     else:
#         if 'cart' in session:
#            # cart = session['cart']
#             cart = session.get('cart', [])
#             product = next((item for item in cart if item['product_id'] == product_id), None)
#             if product is None:
#                 return jsonify({'error': 'Product not found in cart'}), 404
#              # Update the quantity based on the action
#             if action == 'increase':
#                 product['quantity'] += 1
#             elif action == 'decrease' and product['quantity'] > 1:
#                 product['quantity'] -= 1

#             # Recalculate the total price for that specific product
#             updated_quantity = product['quantity']
#             product_price = product['price']
#             total_price = updated_quantity * product_price
#             # Recalculate overall cart totals
#             total_cart_price = sum(item['quantity'] * item['price'] for item in cart)
#             cart_count = sum(item['quantity'] for item in cart)
#             return jsonify({
#                 'updated_quantity': updated_quantity,
#                 'product_price': product_price,
#                 'total_price': total_cart_price,
#                 'cart_count': cart_count
#             })

#     return jsonify({'error': 'Unable to update cart'}), 400
