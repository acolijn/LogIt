from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import mongo


class User(UserMixin):
    """User Class"""	
    # Initialization
    def __init__(self, _id=None, username=None, password=None, is_admin=False):
        self._id = _id
        self.username = username
        self.password = password
        self.is_admin = is_admin

    @classmethod
    def find_by_username(cls, username):
        user_data = mongo.db.users.find_one({"username": username})
        print("Retrieved user_data from MongoDB:", user_data)
        if user_data:
            user_data['password'] = user_data.pop('password')  # This line is changed
            return cls(**user_data)
        else:
            return None

    # Save the user to the database
    def save(self):
        data_to_save = self.__dict__.copy()
        if data_to_save["_id"] is None:
            del data_to_save["_id"]
        mongo.db.users.insert_one(data_to_save)

    # Method to set the hashed password
    @staticmethod
    def set_password(password):
        return generate_password_hash(password, method='scrypt')

    # Method to check the password
    def check_password(self, password):
        return check_password_hash(self.password, password)

    # Required by Flask-Login
    def get_id(self):
        return str(self._id)

