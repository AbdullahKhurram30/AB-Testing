import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

# configuring the database
project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "database.db"))
# configuring the app
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = database_file
app.config['SECRET_KEY'] = 'secret_key'
# initializing the database
db = SQLAlchemy()
db.init_app(app)
bcrypt = Bcrypt(app)
# initializing the login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
# importing the routes
from app import routes