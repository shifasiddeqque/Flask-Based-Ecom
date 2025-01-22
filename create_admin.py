from app.models.user import User
from app.models.admin import Admin
from app.models import db
from datetime import datetime, timezone

def create_admin_user(username, email, password):
    """
    Create a new admin user by creating both User and Admin records
    """
    # Create the user first
    user = User(
        username=username,
        email=email,
        is_active=True,
        created_at = datetime.now(timezone.utc)
    )
    user.set_password(password)
    
    # Create the associated admin record
    admin = Admin(
        user=user,
        is_active=True,
        created_at=datetime.utcnow()
    )
    
    # Add and commit both records
    try:
        db.session.add(user)
        db.session.add(admin)
        db.session.commit()
        return admin
    except Exception as e:
        db.session.rollback()
        raise e

if __name__ == '__main__':
    # Example usage
    try:
        admin = create_admin_user(
            username='admin',
            email='admin@example.com',
            password='securepassword123'
        )
        print(f"Admin user created successfully with ID: {admin.id}")
    except Exception as e:
        print(f"Error creating admin user: {str(e)}")
