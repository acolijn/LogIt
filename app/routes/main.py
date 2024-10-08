import os
import uuid

from flask import Blueprint, render_template, request, redirect, url_for, current_app, jsonify, session
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from datetime import datetime, timedelta
from collections import defaultdict
import pytz

from app import mongo
import html, re

from pathlib import Path

main = Blueprint('main', __name__)

# Define the project home 
project_home = Path(__file__).parent.parent
UPLOAD_FOLDER = project_home / 'static' / 'upload'
print(f"Upload folder ....: {UPLOAD_FOLDER}")  # Debug: print the upload folder path
# Your file upload and logbook entry handling goes here:
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'pdf'}

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

@main.route('/dbactivity.html')
@login_required
def db_activity():
    """
    Renders the 'dbactivity.html' template.

    Returns:
        Response: A Flask response object that renders the 'dbactivity.html' template.
    """
    return render_template('dbactivity.html')

@main.route('/timeline')
@login_required
def timeline():
    """Get the timeline data.
    
    Returns:
        JSON -- The timeline data.

    """
    entries = mongo.db.entries.find()
    
    data = defaultdict(int)
    for entry in entries:
        timestamp = entry['timestamp']
        date = timestamp.date()
        data[date] += 1
    
    dates = sorted(data.keys())
    counts = [data[date] for date in dates]
    
    return jsonify(dates=dates, counts=counts)

@main.route('/save_image')
@login_required
def save_image(image):
    """Save an image to the filesystem.	

    Args:
        image (FileStorage): The image to save.

    Returns:
        str: The filename of the saved image.

    """
    # get the name of the logbook from the session
    logbook_id = ObjectId(session['logbook'])
    logbook = mongo.db.logbooks.find_one({"_id": logbook_id})

    if image and allowed_file(image.filename):
        # Generate a unique filename using UUID and a timestamp
        unique_filename = f"{uuid.uuid4()}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{secure_filename(image.filename)}"
        print('filename =',unique_filename)
        print('logbook name = ', logbook['name'])

        full_path = os.path.join(UPLOAD_FOLDER, logbook['name'], unique_filename)
        find_path = os.path.join(logbook['name'], unique_filename)
        # full_path = os.path.join(logbook['name'], unique_filename)
        
        try:
            image.save(full_path)
            return find_path
        except Exception as e:
            print(f"Error saving image: {e}")
            return None
    else:
        print("Image is not allowed or no image received")
        return None

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
    image_filenames = []

    if 'image' in request.files:
        images = request.files.getlist('image')  # Get list of uploaded images
        image_filenames = [save_image(image) for image in images if image]
        image_filenames = [filename for filename in image_filenames if filename]  # Filter out None values

    # Store the data in MongoDB
    entry = {
        "timestamp": datetime.utcnow(),
        "text": text,
        "keywords": keywords,
        "images": image_filenames,   # store the path or filename to the uploaded image
        "user": current_user.username,   # this should come from your user management system
        "logbook": ObjectId(session['logbook'])  # retrieve logbook id/name from the session, default to None if not set
    }

    # Insert the entry into the database
    mongo.db.entries.insert_one(entry)
    
    # return redirect(url_for('main.add_entry_form'))
    return redirect(url_for('main.show_entries'))

@main.route('/add_images', methods=['POST'])
@login_required
def add_images():
    """
    Handles the addition of images to an existing entry in the database.
    This function performs the following steps:
    1. Retrieves the entry ID from the form data.
    2. Checks if the entry exists in the database.
    3. Fetches the associated logbook document using the entry's logbook ID.
    4. Handles the image upload process, saving the images and collecting their filenames.
    5. Updates the entry in the database with the new image filenames.
    6. Redirects to the entries display page, with appropriate error messages if necessary.
    Returns:
        A redirect response to the entries display page, with error messages if the entry or logbook is not found.
    """
    
    # Retrieve entry_id from form
    entry_id = request.form['entry_id']

    # Check if entry exists
    entry = mongo.db.entries.find_one({"_id": ObjectId(entry_id)})
    if not entry:
        # Handle the case where the entry does not exist. Maybe redirect with an error message.
        return redirect(url_for('main.show_entries', error="Entry not found"))

    # Fetch the logbook document using the ObjectId from the entry
    logbook = mongo.db.logbooks.find_one({"_id": ObjectId(entry['logbook'])})

    # If for some reason the logbook is not found, handle it appropriately.
    if not logbook:
        return redirect(url_for('main.show_entries', error="Logbook not found"))

    # Handle image upload
    image_filenames = []
    if 'newImage' in request.files:
         images = request.files.getlist('newImage')  # Get list of uploaded images
         image_filenames = [save_image(image) for image in images if image]
         image_filenames = [filename for filename in image_filenames if filename]  # Filter out None values

    # Update the entry in MongoDB with new images

    if image_filenames:
        mongo.db.entries.update_one(
            {"_id": ObjectId(entry_id)},
            {"$push": {"images": {"$each": image_filenames}}}
        )

    return redirect(url_for('main.show_entries'))



from math import ceil

@main.route('/entries')
@login_required
def show_entries():
    """Show the logbook entries.

    Returns:
        HTML page -- The logbook entries page.

    """
    logbook_id = ObjectId(session['logbook'])  # retrieve logbook id/name from the session, default to None if not set

    # Extract query parameters
    search_term = request.args.get('search_term', '')
    keyword_filter = request.args.get('keyword_filter', None)
    start_date_str = request.args.get('start_date', None)
    end_date_str = request.args.get('end_date', None)

    query = {}
    # always filter by logbook
    query["logbook"] = logbook_id

    if search_term:
        query["text"] = {"$regex": search_term, "$options": "i"}
        
    if keyword_filter:
        query["keywords"] = keyword_filter
    
    if start_date_str and end_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d') + timedelta(days=1)  # Adding 1 day to include the end date
        query["timestamp"] = {"$gte": start_date, "$lte": end_date}

    per_page = 10
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
    logbook_id = ObjectId(session['logbook'])  # retrieve logbook id/name from the session
    logbook = mongo.db.logbooks.find_one({"_id": logbook_id})

    keyword = request.form.get('keyword')  # Get the keyword from the form data
    if not keyword:
        return "Keyword not provided", 400

    # Add the new keyword to the list of allowed keywords of the specific logbook in the database
    result = mongo.db.logbooks.update_one({"_id": logbook_id}, {"$addToSet": {"allowed_keywords": keyword}})

    if result.modified_count:
        return f"Keyword '{keyword}' added successfully to {logbook['name']} logbook!", 200
    else:
        return f"Keyword '{keyword}' already exists in {logbook['name']} logbook or there was an error!", 400


@main.route('/remove-keyword', methods=['POST'])
@login_required
def remove_keyword():
    """Remove a keyword from the allowed list in MongoDB.

    Returns:
        str: Success or failure message.

    """
    logbook_id = ObjectId(session['logbook'])  # retrieve logbook id/name from the session
    logbook = mongo.db.logbooks.find_one({"_id": logbook_id})

    keyword = request.form.get('keyword')  # Get the keyword from the form data
    if not keyword:
        return "Keyword not provided", 400

    # Remove the keyword from the list of allowed keywords of the specific logbook in the database
    result = mongo.db.logbooks.update_one({"_id": logbook_id}, {"$pull": {"allowed_keywords": keyword}})

    if result.modified_count:
        return f"Keyword '{keyword}' removed successfully from {logbook['name']} logbook!", 200
    else:
        return f"Keyword '{keyword}' doesn't exist in {logbook['name']} logbook or there was an error!", 400


@main.route('/keywords')
@login_required
def show_keywords():
    """Show the list of allowed keywords.

    Returns:
        HTML page -- The keywords page.

    """
    logbook_id = ObjectId(session['logbook'])  # retrieve logbook id/name from the session
    logbook = mongo.db.logbooks.find_one({"_id": logbook_id})

    # Fetch keywords from logbook or default to an empty list if not present
    keywords = logbook.get('allowed_keywords', []) if logbook else []

    # Sort the keywords alphabetically
    keywords = sorted(keywords, key=lambda s: s.lower())

    # Render the keywords page
    return render_template('keywords.html', keywords=keywords)


@main.route('/get-keywords')
@login_required
def get_keywords():
    """Get the list of allowed keywords.

    Returns:
        JSON -- The list of allowed keywords.

    """ 
    logbook_id = ObjectId(session['logbook'])  # retrieve logbook id/name from the session, default to None if not set
    logbook = mongo.db.logbooks.find_one({"_id": logbook_id})

    if 'allowed_keywords' in logbook and logbook['allowed_keywords']:
        keyword_data = logbook['allowed_keywords']
        return jsonify(keywords=sorted(keyword_data))
    else:
        return jsonify(keywords=[])


@main.route('/calendar')
@login_required
def calendar_view():
    """
    Renders the calendar view template with the current date.

    This function retrieves the current date, formats it as 'YYYY-MM-DD',
    and passes it to the 'show_calendar.html' template for rendering.

    Returns:
        str: The rendered HTML content for the calendar view.
    """
    today = datetime.today().strftime('%Y-%m-%d')
    return render_template('show_calendar.html', today=today)


@main.route('/get_calendar_events')
@login_required
def get_calendar_events():
    """Get the calendar events.

    Returns:
        JSON -- The calendar events.

    """
    logbook_id = ObjectId(session['logbook'])  # retrieve logbook id/name from the session, default to None if not set

    start_date_str = request.args.get('start', None)
    end_date_str = request.args.get('end', None)
    
    datetime_format = '%Y-%m-%dT%H:%M:%S%z'
    start_date = datetime.strptime(start_date_str, datetime_format) if start_date_str else None
    end_date = datetime.strptime(end_date_str, datetime_format) if end_date_str else None

    # Fetching entries from MongoDB based on start and end dates if provided

    # shall we also include the logbook id in the query?
    query = {"logbook": logbook_id}
    if start_date and end_date:
        end_date += timedelta(days=1)
        query["timestamp"] = {"$gte": start_date, "$lt": end_date}
        entries_cursor = mongo.db.entries.find(query)
        # entries_cursor = mongo.db.entries.find({"timestamp": {"$gte": start_date, "$lt": end_date}})
    else:
        entries_cursor = mongo.db.entries.find(query)

    # Counting entries per day
    count_per_day = defaultdict(int)
    events_data_per_day = defaultdict(list)
    for entry in entries_cursor:
        date_str = entry['timestamp'].strftime('%Y-%m-%d')
        count_per_day[date_str] += 1
        event_data = {
            'title': entry.get('text', 'No Title'),
            'description': entry.get('description', ''),
        }
        events_data_per_day[date_str].append(event_data)

    # Creating events with title and description
    events = []
    for date, count in count_per_day.items():

        title = "+{}".format(count) if count > 3 else "\n".join(event['title'] for event in events_data_per_day[date])
        title = html.unescape(title)  # Convert HTML entities to their actual characters
        title = re.sub('<[^<]+?>', '', title)  # Remove HTML tags
        title = title.split('\n')[0]
        title = title[:20] + '...' if len(title) > 20 else title  # Truncate the title to 20 characters

        event = {
            'title': title,
            'start': date,  # Since the events are all-day, we only need the date part.
            'allDay': True
        }
        events.append(event)
    
    return jsonify(events)

from bson import ObjectId  # Importing ObjectId from bson

@main.route('/update_entry/<string:entry_id>', methods=['POST'])
@login_required
def update_entry(entry_id):
    """
    Update the text of an existing entry in the database.
    Args:
        entry_id (str): The ID of the entry to be updated.
    Returns:
        Response: A JSON response indicating the success or failure of the update operation.
            - If the entry ID is invalid, returns a 400 status with an error message.
            - If the entry is not found, returns a 404 status with an error message.
            - If the update is successful, returns a 200 status with a success message.
            - If the update fails, returns a 400 status with an error message.
    """

    data = request.json
    updated_text = data.get('updated_text')

    if not ObjectId.is_valid(entry_id):
        return jsonify(success=False, error="Invalid Entry ID"), 400
    
    entry = mongo.db.entries.find_one({"_id": ObjectId(entry_id)})
    if not entry:
        return jsonify(success=False, error="Entry not found"), 404
    
    print(f"Updating entry with ID: {entry_id}"	)
    result = mongo.db.entries.update_one({"_id": ObjectId(entry_id)}, {"$set": {"text": updated_text}})
    
    if result.modified_count > 0:
        return jsonify(success=True), 200
    else:
        return jsonify(success=False, error="Update Failed"), 400
    
# below is the code for updating keywords
@main.route('/update-entry-keywords/<string:entry_id>', methods=['POST'])
@login_required
def update_entry_keywords(entry_id):
    """
    Update the keywords of a specific entry in the database.
    Args:
        entry_id (str): The ID of the entry to update.
    Returns:
        Response: A JSON response indicating success or failure.
            - If the entry ID is invalid, returns a JSON response with success=False and an error message, with a 400 status code.
            - If the update is successful, returns a JSON response with success=True and a 200 status code.
            - If the update fails, returns a JSON response with success=False and an error message, with a 400 status code.
    """
    if not ObjectId.is_valid(entry_id):
        return jsonify(success=False, error="Invalid Entry ID"), 400
    
    data = request.json
    keywords = data.get('keywords', [])
    
    result = mongo.db.entries.update_one({"_id": ObjectId(entry_id)}, {"$set": {"keywords": keywords}})
    
    if result.modified_count > 0:
        return jsonify(success=True), 200
    else:
        return jsonify(success=False, error="Update Failed"), 400

@main.route('/get-entry-keywords/<string:entry_id>', methods=['GET'])
@login_required
def get_entry_keywords(entry_id):
    """
    Retrieve the keywords associated with a specific entry.
    Args:
        entry_id (str): The ID of the entry to retrieve keywords for.
    Returns:
        Response: A JSON response containing the keywords if the entry is found,
                  or an error message if the entry ID is invalid or the entry is not found.
                  The response status code is 200 on success, 400 if the entry ID is invalid,
                  and 404 if the entry is not found.
    """
    if not ObjectId.is_valid(entry_id):
        return jsonify(success=False, error="Invalid Entry ID"), 400
    
    entry = mongo.db.entries.find_one({"_id": ObjectId(entry_id)})
    if not entry:
        return jsonify(success=False, error="Entry not found"), 404
    
    print(entry.get('keywords', []))
    return jsonify(keywords=entry.get('keywords', []))
