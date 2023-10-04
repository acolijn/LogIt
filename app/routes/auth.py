import os

from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_user,login_required, logout_user, current_user

from app import mongo, login_manager
from app.models.User import User
from app.models.Registration import RegistrationForm
from app.models.LogBookForm import LogbookForm, AddUsersToLogbookForm
from bson.objectid import ObjectId
from app.routes.main import UPLOAD_FOLDER

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """For GET requests, display the login form.
    For POSTS, login the current user by processing the form.
    """
    print("login ..... ")
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        chosen_logbook = request.form.get('logbook')

        user = User.find_by_username(username)

        # check if the user is in the list of users for the logbook
        logbook = mongo.db.logbooks.find_one({"_id": ObjectId(chosen_logbook)})
        if user and user.check_password(password) and user._id in logbook['users']:
            # Log in the user
            login_user(user)
            # session variable to store the logbook id
            session['logbook'] = str(chosen_logbook)
            flash('You are successfully logged in!', 'success')
            return redirect(url_for('main.show_entries'))
        elif user and user.check_password(password) and user._id not in logbook['users']:
            flash('User not in logbook!', 'danger')
        elif user and not user.check_password(password):
            flash('Invalid password!', 'danger')
        else:
            flash('Invalid username!', 'danger')

    logbooks = mongo.db.logbooks.find()  # Assuming db is your MongoDB database instance.
    return render_template('login.html', logbooks=logbooks)

@auth.route('/logout')
@login_required
def logout():
    """Logout the current user."""	
    logout_user()
    return redirect(url_for('auth.login'))

@login_manager.user_loader
def load_user(user_id):
    """Check if user is logged-in on every page load."""	
    user_data = mongo.db.users.find_one({"_id": ObjectId(user_id)})
    if user_data:
        user_data['password'] = user_data.pop('password', None)  # Rename the key
        return User(**user_data)    
    return None

@auth.route('/')
def index():
    """Redirect to login page."""	
    return redirect(url_for('main.show_entries'))

@auth.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_page():
    """Admin page.
    
    - Create logbooks
    - Add users to logbooks
    - Register new users
    
    Accessible only to admin users.
    """
    if not current_user.is_admin:
        flash('Access denied!', 'danger')
        return redirect(url_for('main.show_entries'))

    logbook_form = LogbookForm()
    user_form = AddUsersToLogbookForm()
    registration_form = RegistrationForm()

    # Dynamically set choices for the logbook dropdown
    logbooks = mongo.db.logbooks.find()

    # New code to populate users
    users = mongo.db.users.find()

    # i want to select the users from the database that are currently not in the list of users for the logbook
    # users = mongo.db.users.find({"_id": {"$nin": logbook['users']}})
    # and 
    user_form.logbook_select.choices = [(str(logbook['_id']), logbook['name']) for logbook in logbooks]
    user_form.user_select.choices = [(str(user['_id']), user['username']) for user in users]
    # user_form.logbook_select.choices = [(str(logbook['_id']), logbook['name']) for logbook in logbooks]

    # Handle logbook creation
    if 'create_logbook' in request.form:
        if logbook_form.validate_on_submit():
            # Split the allowed keywords by comma, but if there are no elements in the list, set it to an empty list
            keywords = [keyword.strip() for keyword in logbook_form.allowed_keywords.data.split(',')] if logbook_form.allowed_keywords.data else []
            #keywords = [keyword.strip() for keyword in logbook_form.allowed_keywords.data.split(',')]
            mongo.db.logbooks.insert_one({"name": logbook_form.logbook_name.data, "allowed_keywords": keywords, "users": []})
            # create subdirectory in the UPLOAD_FOLDER for the logbook. but firs check if the directpry already exists
            if not os.path.exists(os.path.join(UPLOAD_FOLDER, logbook_form.logbook_name.data)):
                os.mkdir(os.path.join(UPLOAD_FOLDER, logbook_form.logbook_name.data))
            flash('Logbook created successfully!', 'success')
            return redirect(url_for('auth.admin_page'))

    # Handle adding user to logbook
    if 'add_user_to_logbook' in request.form:
        if user_form.validate_on_submit():
            # user = mongo.db.users.find_one({"username": user_form.username.data})
            user = mongo.db.users.find_one({"_id": ObjectId(user_form.user_select.data)})
            if user:
                # Fetch the logbook based on the selected logbook's ID
                logbook = mongo.db.logbooks.find_one({"_id": ObjectId(user_form.logbook_select.data)})
                
                if logbook:
                    # Check if the user's ID exists within the users array of the logbook
                    if user['_id'] in logbook['users']:
                        flash('User already in logbook!', 'danger')
                        return redirect(url_for('auth.admin_page'))
                    else:
                        mongo.db.logbooks.update_one({"_id": ObjectId(user_form.logbook_select.data)}, {"$push": {"users": user['_id']}})
                        flash('User added to logbook!', 'success')
                else:
                    flash('Logbook not found!', 'danger')
            else:
                flash('User not found!', 'danger')

    # Handle user registration
    if 'register_user' in request.form:
        if registration_form.validate_on_submit():
            hashed_password = User.set_password(registration_form.password.data)
            new_user = User(username=registration_form.username.data, email=registration_form.email.data, password=hashed_password)
            new_user.save()
            flash('New user registered successfully!', 'success')
            return redirect(url_for('auth.admin_page'))
        elif request.method == 'POST':  # Check if the form was submitted
            for field, errors in registration_form.errors.items():
                for error in errors:
                    flash(f"Error in the {getattr(registration_form, field).label.text} field - {error}", 'danger')

    return render_template('admin.html', logbook_form=logbook_form, user_form=user_form, registration_form=registration_form)

from flask import jsonify
@auth.route('/get-available-users/<logbook_id>')
def get_available_users(logbook_id):
    # Get the current users in the logbook
    logbook = mongo.db.logbooks.find_one({"_id": ObjectId(logbook_id)})
    current_users = logbook['users']

    # Fetch users not in the logbook
    available_users = mongo.db.users.find({'_id': {'$nin': current_users}})
    
    # Convert users to list of dicts to send as JSON
    user_list = [{'id': str(user['_id']), 'name': user['username']} for user in available_users]

    return jsonify(users=user_list)