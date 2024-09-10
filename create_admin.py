# create_admin.py

from app import create_app, mongo
from werkzeug.security import generate_password_hash
import getpass

def create_admin():
    username = input("Enter admin username: ")
    password = getpass.getpass("Enter admin password: ")
    
    hashed_password = generate_password_hash(password, method='scrypt')
    admin = {
        "username": username,
        "password": hashed_password,
        "is_admin": True
    }
    
    # Insert the admin user into the 'users' collection
    result = mongo.db.users.insert_one(admin)
    if result:
        print(f"Admin user created with ID: {result.inserted_id}")
    else:
        print("Error creating admin user.")

if __name__ == "__main__":
    # Initialize the Flask app
    app = create_app('config.Config')  # Replace with your actual config
    
    # Use the app's context to ensure the MongoDB connection is active
    with app.app_context():
        create_admin()
