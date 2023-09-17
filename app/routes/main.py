from flask import Blueprint, render_template, request, redirect, url_for, current_app
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from app import mongo

main = Blueprint('main', __name__)

# ... (Other routes and functionalities for the main blueprint) ...

# Your file upload and logbook entry handling goes here:
UPLOAD_FOLDER = 'static/upload/' 
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main.route('/add-entry', methods=['GET'])
def add_entry_form():
    print("add_entry_form")
    return render_template('add_entry.html')

@main.route('/add-entry', methods=['POST'])
def handle_entry():
    # Extract data from form

    print("handle_entry")
    text = request.form['text']
    keywords = request.form['keywords'].split(',')
    
    image_filename = None
    if 'image' in request.files:
        image = request.files['image']
        if image.filename != '' and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(UPLOAD_FOLDER, filename))
            image_filename = filename
    
    # Store the data in MongoDB
    entry = {
        "text": text,
        "keywords": keywords,
        "image": image_filename,   # store the path or filename to the uploaded image
        "user": "UsernameHere",   # this should come from your user management system
        "timestamp": datetime.utcnow()
    }

    print(entry)

    mongo.db.entries.insert_one(entry)
    
    return redirect(url_for('main.add_entry_form'))

@main.route('/entries')
def show_entries():
    entries = mongo.db.entries.find({})
    return render_template('show_entries.html', entries=entries)

@main.route('/test-mongo')
def test_mongo():
    print(current_app.config['MONGO_URI'])
    print("MongoDB:", mongo.db)
    return "Check the logs!"


@main.route('/test_image')
def test_image():
    return current_app.send_static_file('upload/IMG_9404.JPG')

from flask import send_from_directory

@main.route('/direct_image')
def direct_image():
    return send_from_directory('static/upload/', 'IMG_9404.JPG')
