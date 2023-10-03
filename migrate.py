from app import create_app, mongo
from werkzeug.security import generate_password_hash
import getpass

def migrate():
    xams_logbook_id = mongo.db.logbooks.find_one({"name": "xams"})["_id"]  # Fetch the ID of the xams logbook

    # Update all entries to be associated with the xams logbook
    mongo.db.entries.update_many({}, {"$set": {"logbook": xams_logbook_id}})

if __name__ == "__main__":
    # Initialize the Flask app
    app = create_app('config.Config')  # replace 'config_filename' with your actual config module or filename
    
    # Use the app's context to ensure the MongoDB connection is active
    with app.app_context():
        migrate()

