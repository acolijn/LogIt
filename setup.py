from setuptools import setup, find_packages

setup(
    name='LogIt',
    version='0.1',
    packages=find_packages(where='app/routes'),
    package_dir={'': 'app/routes'},  # This tells it that the packages are in src/
)

# if __name__ == "__main__":
#     from app import create_app, mongo  # Move the imports here to avoid breaking setup
#     from werkzeug.security import generate_password_hash
#     import getpass
    
#     def create_admin():
#         username = input("Enter admin username: ")
#         password = getpass.getpass("Enter admin password: ")
        
#         hashed_password = generate_password_hash(password, method='scrypt')
#         admin = {
#             "username": username,
#             "password": hashed_password,
#             "is_admin": True
#         }
        
#         # Insert the admin user into the 'users' collection
#         result = mongo.db.users.insert_one(admin)
#         if result:
#             print(f"Admin user created with ID: {result.inserted_id}")
#         else:
#             print("Error creating admin user.")

#     # Initialize the Flask app
#     app = create_app('config.Config')
    
#     # Use the app's context to ensure the MongoDB connection is active
#     with app.app_context():
#         create_admin()
