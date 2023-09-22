from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user,login_required, logout_user, current_user

from app import mongo, login_manager
from app.models.User import User
from app.models.Registration import RegistrationForm
from bson.objectid import ObjectId

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    print("login")
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.find_by_username(username)
        if user and user.check_password(password):
            login_user(user)  # This is the important part
            flash('Logged in successfully!')
            return redirect(url_for('main.show_entries'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')
#    return "Login Route"

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@login_manager.user_loader
def load_user(user_id):
    user_data = mongo.db.users.find_one({"_id": ObjectId(user_id)})
    if user_data:
        user_data['password'] = user_data.pop('password', None)  # Rename the key
        return User(**user_data)    
    return None

@auth.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    # Ensure only admin can access
    if not current_user.is_admin:
        flash('Access denied!', 'danger')
        return redirect(url_for('main.show_entries'))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = User.set_password(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        new_user.save()
        flash('New user registered successfully!', 'success')
        return redirect(url_for('main.show_entries'))
    return render_template('register.html', form=form)


# I need a function to get alist o users. no render_template needed
@auth.route('/users')
@login_required
def users():
    # Ensure only admin can access
    if not current_user.is_admin:
        flash('Access denied!', 'danger')
        return redirect(url_for('main.show_entries'))

    users = User.get_all()
    return users

@auth.route('/')
def index():
    return redirect(url_for('auth.login'))