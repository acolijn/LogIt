from flask import Flask
from flask_pymongo import PyMongo
from flask_login import LoginManager

mongo = PyMongo()

login_manager = LoginManager()

def create_app(config_filename):
    print("create_app")
    app = Flask(__name__, static_folder='static')
    app.config.from_object(config_filename)

    print(app.static_folder)
    print("config_filename: ", config_filename)
    print("app.config: ", app.config)

    mongo.init_app(app)
    print('mongo DB =',mongo.db)

    # Register blueprints
    from .routes.main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    from .routes.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    return app
