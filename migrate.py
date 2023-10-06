from app import create_app, mongo
from werkzeug.security import generate_password_hash
import getpass

def migrate():
    # Get the collection
    entries = mongo.db.entries
    
    # Convert 'image' field to an array and store in 'images'
    entries.update_many(
        {"image": {"$exists": True}},
        [
            {
                "$set": {
                    "images": [{"$ifNull": ["$image", []]}]
                }
            },
            {
                "$unset": ["image"]
            }
        ]
    )

    # Flatten nested arrays in 'images'
    entries.update_many(
        {"images.0": {"$type": "array"}},
        [
            {
                "$set": {
                    "images": {"$arrayElemAt": ["$images", 0]}
                }
            }
        ]
    )

    # Remove entries where images field is a string (due to earlier mistake)
    entries.update_many(
        {"images": "$images.0"},
        {
            "$set": {"images": []}
        }
    )



if __name__ == "__main__":
    # Initialize the Flask app
    app = create_app('config.Config')  # replace 'config_filename' with your actual config module or filename
    
    # Use the app's context to ensure the MongoDB connection is active
    with app.app_context():
        migrate()

