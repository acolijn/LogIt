import os

from flask import Blueprint, render_template, request, redirect, url_for, current_app, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from datetime import datetime
import pytz

from app import mongo


main = Blueprint('main', __name__)

# Your file upload and logbook entry handling goes here:
UPLOAD_FOLDER = 'app/static/upload/' 
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main.route('/add-entry', methods=['GET'])
@login_required
def add_entry_form():
    """Show the add entry form.

    Returns: 
        HTML page -- The add entry form.

    """	
    print("add_entry_form")
    return render_template('add_entry.html')

@main.route('/add-entry', methods=['POST'])
@login_required
def handle_entry():
    """Handle the add entry form.

    Returns:
        HTML page -- The add entry form.

    """
    # Extract data from form

    print("handle_entry")
    text = request.form['text']
    keywords = request.form.getlist('keywordSelect[]')

    # Handle image upload
    print('static folder = ', current_app.static_folder )   
    image_filename = None
    if 'image' in request.files:
        image = request.files['image']
        if image.filename != '' and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(UPLOAD_FOLDER, filename))
            image_filename = filename
    
    # Store the data in MongoDB
    entry = {
        "timestamp": datetime.utcnow(),
        "text": text,
        "keywords": keywords,
        "image": image_filename,   # store the path or filename to the uploaded image
        "user": current_user.username   # this should come from your user management system
    }

    mongo.db.entries.insert_one(entry)
    
    # return redirect(url_for('main.add_entry_form'))
    return redirect(url_for('main.show_entries'))


from math import ceil


@main.route('/entries')
@login_required
def show_entries():
    search_term = request.args.get('search_term', '')
    keyword_filter = request.args.get('keyword_filter', None)

    query = {}
    if search_term:
        query["text"] = {"$regex": search_term, "$options": "i"}
    if keyword_filter:
        query["keywords"] = keyword_filter

    per_page = 5
    page_number = int(request.args.get('page', 1))

    skip_entries = (page_number - 1) * per_page

    entries_cursor = mongo.db.entries.find(query).sort("timestamp", -1).skip(skip_entries).limit(per_page)
    
    # Convert UTC timestamp to Amsterdam local time
    amsterdam_tz = pytz.timezone('Europe/Amsterdam')
    entries = []
    for entry in entries_cursor:
        entry['timestamp'] = entry['timestamp'].replace(tzinfo=pytz.utc).astimezone(amsterdam_tz)
        entries.append(entry)

    # Calculate the total number of entries matching the query
    if query:
        total_entries = mongo.db.entries.count_documents(query)
    else:
        total_entries = mongo.db.entries.count_documents({})
    total_pages = ceil(total_entries / per_page)

    return render_template('show_entries.html', entries=entries, 
                           page_number=page_number, total_pages=total_pages, 
                           search_term=search_term, keyword_filter=keyword_filter)

@main.route('/test-mongo')
@login_required
def test_mongo():
    """Test the connection to MongoDB.

    Returns:
        str: Success or failure message.

    """
    print(current_app.config['MONGO_URI'])
    print("MongoDB:", mongo.db)
    return "Check the logs!"

@main.route('/add-keyword', methods=['POST'])
@login_required
def add_keyword():
    """Add a new keyword to the allowed list in MongoDB.

    Returns:
        str: Success or failure message.

    """
    keyword = request.form.get('keyword')  # Get the keyword from the form data
    if not keyword:
        return "Keyword not provided", 400

    # Add the new keyword to the list of allowed keywords in the database
    result = mongo.db.allowed_keywords.update_one({}, {"$addToSet": {"keywords": keyword}})
    
    if result.modified_count:
        return f"Keyword '{keyword}' added successfully!", 200
    else:
        return f"Keyword '{keyword}' already exists or there was an error!", 400

@main.route('/remove-keyword', methods=['POST'])
@login_required
def remove_keyword():
    """Remove a keyword from the allowed list in MongoDB.

    Returns:
        str: Success or failure message.

    """
    keyword = request.form.get('keyword')  # Get the keyword from the form data
    if not keyword:
        return "Keyword not provided", 400

    # Remove the keyword from the list of allowed keywords in the database
    result = mongo.db.allowed_keywords.update_one({}, {"$pull": {"keywords": keyword}})
    
    if result.modified_count:
        return f"Keyword '{keyword}' removed successfully!", 200
    else:
        return f"Keyword '{keyword}' doesn't exist or there was an error!", 400

@main.route('/keywords')
@login_required
def show_keywords():
    """Show the list of allowed keywords.

    Returns:
        HTML page -- The keywords page.

    """
    keyword_data = mongo.db.allowed_keywords.find_one()
    if not keyword_data:
        # If no keyword data exists, initialize it with an empty list
        mongo.db.allowed_keywords.insert_one({"keywords": []})
        keywords = []
    else:
        keywords = keyword_data.get('keywords', [])
    return render_template('keywords.html', keywords=keywords)

@main.route('/get-keywords')
@login_required
def get_keywords():
    """Get the list of allowed keywords.

    Returns:
        JSON -- The list of allowed keywords.

    """ 
    keyword_data = mongo.db.allowed_keywords.find_one()
    if not keyword_data:
        return jsonify(keywords=[])
    else:
        print(keyword_data)
        return jsonify(keywords=keyword_data.get('keywords', []))

