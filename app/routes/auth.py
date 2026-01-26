import os
from authlib.integrations.flask_client import OAuth

from flask import Blueprint, render_template, redirect, url_for, request, flash, session, current_app
from flask_login import login_user,login_required, logout_user, current_user

from app import mongo, login_manager
from app.models.User import User
from app.models.Registration import RegistrationForm
from app.models.LogBookForm import LogbookForm, AddUsersToLogbookForm, RemoveUsersFromLogbookForm, DeleteUserForm, ManageUserLogbooksForm
from bson.objectid import ObjectId
from app.routes.main import UPLOAD_FOLDER

auth = Blueprint('auth', __name__)

# Initialize OAuth
oauth = OAuth()

def init_oauth(app):
    """Initialize OAuth with the Flask app"""
    oauth.init_app(app)
    if app.config.get('OIDC_ENABLED'):
        oauth.register(
            name='nikhef',
            client_id=app.config['OIDC_CLIENT_ID'],
            client_secret=app.config['OIDC_CLIENT_SECRET'],
            server_metadata_url=app.config['OIDC_DISCOVERY_URL'],
            client_kwargs={
                'scope': app.config['OIDC_SCOPES']
            }
        )

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
            session['logbook_name'] = logbook['name']

            flash('You are successfully logged in!', 'success')
            return redirect(url_for('main.show_entries'))
        elif user and user.check_password(password) and user._id not in logbook['users']:
            flash('User not in logbook!', 'danger')
        elif user and not user.check_password(password):
            flash('Invalid password!', 'danger')
        else:
            flash('Invalid username!', 'danger')

    logbooks = list(mongo.db.logbooks.find())
    oidc_enabled = current_app.config.get('OIDC_ENABLED', False)
    return render_template('login.html', logbooks=logbooks, oidc_enabled=oidc_enabled)

@auth.route('/login/sso')
def login_sso():
    """Initiate SSO login"""
    if not current_app.config.get('OIDC_ENABLED'):
        flash('SSO is not enabled!', 'danger')
        return redirect(url_for('auth.login'))
    
    # Store the selected logbook in session before redirecting to SSO
    chosen_logbook = request.args.get('logbook')
    if chosen_logbook:
        session['pending_logbook'] = chosen_logbook
    
    redirect_uri = url_for('auth.callback', _external=True)
    return oauth.nikhef.authorize_redirect(redirect_uri)

@auth.route('/auth/callback')
def callback():
    """Handle SSO callback"""
    if not current_app.config.get('OIDC_ENABLED'):
        flash('SSO is not enabled!', 'danger')
        return redirect(url_for('auth.login'))
    
    try:
        token = oauth.nikhef.authorize_access_token()
        
        # Explicitly fetch userinfo from userinfo endpoint (not from token)
        userinfo = oauth.nikhef.userinfo(token=token)
        
        # Extract user information
        sso_id = userinfo.get('sub')
        
        # Extract email - prefer direct email claim
        email = userinfo.get('email')
        if not email:
            # Try eduperson_principal_name (might be a list)
            eppn = userinfo.get('eduperson_principal_name')
            if eppn:
                email = eppn[0] if isinstance(eppn, list) else eppn
            else:
                # Fallback to preferred_username
                preferred = userinfo.get('preferred_username')
                if preferred:
                    email = preferred[0] if isinstance(preferred, list) else preferred
                else:
                    email = sso_id
        
        name = userinfo.get('name', 
                           userinfo.get('displayName',
                                      userinfo.get('cn',
                                                 userinfo.get('givenName', email))))
        
        # Debug: log what we received
        print(f"SSO Login - userinfo: {userinfo}")
        print(f"SSO Login - sso_id: {sso_id}, email: {email}, name: {name}")
        print(f"SSO Login - Available claims: {list(userinfo.keys())}")
        
        # Check group membership
        group_claim = current_app.config.get('OIDC_GROUP_CLAIM', 'groups')
        user_groups = userinfo.get(group_claim, [])
        allowed_groups = current_app.config.get('OIDC_ALLOWED_GROUPS', [])
        
        # Debug: log group information
        print(f"SSO Login - Group claim config: '{group_claim}'")
        print(f"SSO Login - User groups from '{group_claim}': {user_groups}")
        print(f"SSO Login - Allowed groups config: {allowed_groups}")
        
        # Check if there are any group-related claims in userinfo
        group_related_claims = {k: v for k, v in userinfo.items() if 'group' in k.lower() or 'entitlement' in k.lower() or 'affiliation' in k.lower()}
        print(f"SSO Login - Group-related claims found: {group_related_claims}")
        
        # If allowed_groups is configured, check membership
        if allowed_groups:
            has_access = any(group in allowed_groups for group in user_groups)
            if not has_access:
                flash(f'Access denied! You must be a member of one of these groups: {", ".join(allowed_groups)}', 'danger')
                return redirect(url_for('auth.login'))
        
        # Find or create user
        user = User.find_by_sso_id(sso_id)
        
        if not user:
            # Create new SSO user with default logbooks
            default_logbooks = current_app.config.get('DEFAULT_LOGBOOKS', ['xams'])
            user = User(
                username=email,
                email=email,
                auth_method='sso',
                sso_id=sso_id,
                sso_name=name,
                is_admin=False,
                allowed_logbooks=default_logbooks
            )
            user.save()
            flash(f'Welcome! Your account has been created with access to: {", ".join(default_logbooks)}', 'success')
        else:
            # Update user info
            user.sso_name = name
            user.email = email
            user.update()
        
        # Handle logbook selection
        pending_logbook = session.pop('pending_logbook', None)
        if pending_logbook:
            logbook = mongo.db.logbooks.find_one({"_id": ObjectId(pending_logbook)})
            if logbook:
                # Check if user has access to this logbook
                if user.has_logbook_access(logbook['name']):
                    session['logbook'] = str(pending_logbook)
                    session['logbook_name'] = logbook['name']
                    login_user(user)
                    flash('You are successfully logged in via SSO!', 'success')
                    return redirect(url_for('main.show_entries'))
                else:
                    flash(f'You do not have access to the {logbook["name"]} logbook. Please contact an administrator.', 'danger')
                    return redirect(url_for('auth.login'))
        
        # If no logbook selected, try to use first allowed logbook
        if user.allowed_logbooks:
            first_logbook_name = user.allowed_logbooks[0]
            first_logbook = mongo.db.logbooks.find_one({"name": first_logbook_name})
            if first_logbook:
                session['logbook'] = str(first_logbook['_id'])
                session['logbook_name'] = first_logbook['name']
                login_user(user)
                flash('You are successfully logged in via SSO!', 'success')
                return redirect(url_for('main.show_entries'))
        
        # No logbook access
        flash('You do not have access to any logbooks. Please contact an administrator.', 'danger')
        return redirect(url_for('auth.login'))
        
    except Exception as e:
        print(f"SSO login error: {str(e)}")
        flash(f'SSO login failed: {str(e)}', 'danger')
        return redirect(url_for('auth.login'))

@auth.route('/logout')
@login_required
def logout():
    """Logout the current user."""	
    session.clear()
    logout_user()
    return redirect(url_for('auth.login'))

@login_manager.user_loader
def load_user(user_id):
    """Check if user is logged-in on every page load."""
    if not user_id or user_id == 'None':
        return None
    try:
        user_data = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        if user_data:
            user_data['password'] = user_data.pop('password', None)  # Rename the key
            return User(**user_data)
    except Exception as e:
        print(f"Error loading user {user_id}: {e}")
        return None
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
    - Manage SSO user logbook permissions
    
    Accessible only to admin users.
    """
    if not current_user.is_admin:
        flash('Access denied!', 'danger')
        return redirect(url_for('main.show_entries'))

    logbook_form = LogbookForm()
    user_form = AddUsersToLogbookForm()
    delete_user_form = DeleteUserForm()
    registration_form = RegistrationForm()
    manage_logbooks_form = ManageUserLogbooksForm()

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
    
    # Set choices for delete user form - exclude admin users
    all_users = mongo.db.users.find({"is_admin": {"$ne": True}})
    delete_user_form.user_select.choices = [('', 'Select User')] + [(str(user['_id']), user['username']) for user in all_users]
    
    # Set choices for manage logbooks form
    all_logbooks = list(mongo.db.logbooks.find())
    all_users_for_mgmt = list(mongo.db.users.find())
    manage_logbooks_form.user_select.choices = [('', 'Select User')] + [(str(user['_id']), f"{user['username']} ({'SSO' if user.get('auth_method') == 'sso' else 'Local'})") for user in all_users_for_mgmt]
    manage_logbooks_form.logbook_access.choices = [(logbook['name'], logbook['name']) for logbook in all_logbooks]

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

    # Handle deleting user completely
    if 'delete_user' in request.form:
        if delete_user_form.validate_on_submit():
            user_id = ObjectId(delete_user_form.user_select.data)
            user = mongo.db.users.find_one({"_id": user_id})
            
            if user:
                # Prevent deletion of admin users
                if user.get('is_admin', False):
                    flash('Cannot delete admin users!', 'danger')
                    return redirect(url_for('auth.admin_page'))
                
                # Remove user from all logbooks
                mongo.db.logbooks.update_many(
                    {"users": user_id},
                    {"$pull": {"users": user_id}}
                )
                
                # Delete the user
                mongo.db.users.delete_one({"_id": user_id})
                
                flash(f"User '{user['username']}' deleted successfully from all logbooks!", 'success')
                return redirect(url_for('auth.admin_page'))
            else:
                flash('User not found!', 'danger')
    
    # Handle managing user logbook permissions
    if 'manage_user_logbooks' in request.form:
        if manage_logbooks_form.validate_on_submit():
            user_id = ObjectId(manage_logbooks_form.user_select.data)
            user = mongo.db.users.find_one({"_id": user_id})
            
            if user:
                # Get selected logbooks
                selected_logbooks = manage_logbooks_form.logbook_access.data
                
                # Update user's allowed_logbooks
                mongo.db.users.update_one(
                    {"_id": user_id},
                    {"$set": {"allowed_logbooks": selected_logbooks}}
                )
                
                flash(f"Logbook permissions updated for user '{user['username']}'!", 'success')
                return redirect(url_for('auth.admin_page'))
            else:
                flash('User not found!', 'danger')

    return render_template('admin.html', logbook_form=logbook_form, user_form=user_form, 
                         delete_user_form=delete_user_form, registration_form=registration_form,
                         manage_logbooks_form=manage_logbooks_form)

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

@auth.route('/get-logbook-users/<logbook_id>')
def get_logbook_users(logbook_id):
    # Get the current users in the logbook
    logbook = mongo.db.logbooks.find_one({"_id": ObjectId(logbook_id)})
    if not logbook:
        return jsonify(users=[])
    
    current_user_ids = logbook.get('users', [])
    
    # Fetch users in the logbook
    logbook_users = mongo.db.users.find({'_id': {'$in': current_user_ids}})
    
    # Convert users to list of dicts to send as JSON
    user_list = [{'id': str(user['_id']), 'name': user['username']} for user in logbook_users]

    return jsonify(users=user_list)

@auth.route('/get-user-logbooks/<user_id>')
def get_user_logbooks(user_id):
    """Get the logbooks a user has access to"""
    user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        return jsonify(logbooks=[])
    
    allowed_logbooks = user.get('allowed_logbooks', [])
    return jsonify(logbooks=allowed_logbooks)