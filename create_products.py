import os

config_mapping = {
    'development': 'app.config.config.DevelopmentConfig',
    'production': 'app.config.config.ProductionConfig',
    'testing': 'app.config.config.TestingConfig'
}

from flask import Flask
from app.models import db
from app.models import Product, ProductCategory, ProductImage, ProductDetail, RelatedProduct  # Adjust path
from faker import Faker
from datetime import datetime

# Initialize Flask App (Ensure this points to your actual app)
app = Flask(__name__)
config_type = os.environ.get('FLASK_ENV', 'development')
config_class = config_mapping.get(config_type, 'app.config.config.DevelopmentConfig')
app.config.from_object(config_class)

# Create the database and models (if necessary)
db.init_app(app)

# Initialize Faker
fake = Faker()

with app.app_context():  # Run within app context to use db
    # Step 1: Create Product Categories
    categories = ["Electronics", "Apparel", "Home & Kitchen", "Sports & Outdoors", "Books"]
    category_objects = []
    for category_name in categories:
        category = ProductCategory(name=category_name, slug=fake.slug())
        db.session.add(category)
        category_objects.append(category)
    db.session.commit()

    # Step 2: Generate 100 Dummy Products
    products = []
    for _ in range(100):  # Create 100 dummy products
        category = fake.random_element(category_objects)  # Randomly select a category
        product = Product(
            name=fake.company(),
            slug=fake.slug(),
            description=fake.text(),
            price=fake.random_number(digits=3),
            stock=fake.random_int(min=1, max=100),
            category_id=category.id,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.session.add(product)
        products.append(product)
    db.session.commit()

    # Step 3: Generate Product Details (Key-Value pairs for each product)
    product_details = []
    for product in products:
        details = [
            ProductDetail(product_id=product.id, key="Color", value=fake.color_name()),
            ProductDetail(product_id=product.id, key="Size", value=fake.random_element(["S", "M", "L", "XL"])),
            ProductDetail(product_id=product.id, key="Material", value=fake.word())
        ]
        product_details.extend(details)
    db.session.add_all(product_details)
    db.session.commit()

    # Step 4: Generate Product Images (At least one image per product)
    product_images = []
    for product in products:
        image_url = f"https://via.placeholder.com/150?text={product.name.replace(' ', '+')}"
        image = ProductImage(
            product_id=product.id,
            image_url=image_url,
            alt_text=f"{product.name} Image",
            is_primary=True,
            display_order=0
        )
        product_images.append(image)
    db.session.add_all(product_images)
    db.session.commit()

    # Step 5: Generate Related Products (At least one related product per product)
    related_products = []
    for product in products:
        # Pick a random related product (make sure it's not the same product)
        related_product = fake.random_element([p for p in products if p.id != product.id])
        related = RelatedProduct(
            product_id=product.id,
            related_product_id=related_product.id,
            relationship_type=fake.random_element(["similar", "accessory", "cross-sell"]),
            display_order=0
        )
        related_products.append(related)
    db.session.add_all(related_products)
    db.session.commit()

    print("100 dummy products with associated data (categories, details, images, related products) created successfully.")
