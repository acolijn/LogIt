from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import mongo


class User(UserMixin):
    """User Class"""	
    # Initialization
    def __init__(self, _id=None, username=None, email=None, password=None, is_admin=False, 
                 auth_method='local', sso_id=None, sso_name=None, allowed_logbooks=None):
        self._id = _id
        self.username = username
        self.email = email
        self.password = password
        self.is_admin = is_admin
        self.auth_method = auth_method  # 'local' or 'sso'
        self.sso_id = sso_id  # Unique SSO identifier (sub claim)
        self.sso_name = sso_name  # Display name from SSO
        self.allowed_logbooks = allowed_logbooks if allowed_logbooks is not None else []

    @classmethod
    def find_by_username(cls, username):
        user_data = mongo.db.users.find_one({"username": username})
        print("Retrieved user_data from MongoDB:", user_data)
        if user_data:
            user_data['password'] = user_data.pop('password')  # This line is changed
            return cls(**user_data)
        else:
            return None

    @classmethod
    def find_by_sso_id(cls, sso_id):
        """Find user by SSO ID"""
        user_data = mongo.db.users.find_one({"sso_id": sso_id})
        if user_data:
            return cls(**user_data)
        return None

    # Save the user to the database
    def save(self):
        data_to_save = self.__dict__.copy()
        if data_to_save["_id"] is None:
            del data_to_save["_id"]
        mongo.db.users.insert_one(data_to_save)

    # Update user in database
    def update(self):
        """Update existing user in database"""
        if self._id is None:
            raise ValueError("Cannot update user without _id")
        data_to_save = self.__dict__.copy()
        from bson.objectid import ObjectId
        user_id = data_to_save.pop("_id")
        mongo.db.users.update_one(
            {"_id": ObjectId(user_id) if not isinstance(user_id, ObjectId) else user_id},
            {"$set": data_to_save}
        )

    # Method to set the hashed password
    @staticmethod
    def set_password(password):
        return generate_password_hash(password, method='scrypt')

    # Method to check the password
    def check_password(self, password):
        if self.auth_method == 'sso':
            return False  # SSO users don't have passwords
        return check_password_hash(self.password, password)
    
    def has_logbook_access(self, logbook_name):
        """Check if user has access to a specific logbook"""
        if self.is_admin:
            return True  # Admins have access to all logbooks
        return logbook_name in self.allowed_logbooks

    # Required by Flask-Login
    def get_id(self):
        return str(self._id)


