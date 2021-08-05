from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

#########################################################
""" Remove it later """
import os

DB_PATH = os.path.abspath(os.getcwd() + "/src/temp.db")
#########################################################

app = Flask(__name__)
app.config["SECRET_KEY"] = "NnuUKdVF71sppI6cia7XXf386_AbYUnnXnmdaOW_PRy_sGawZXfScC_DoGNAO0r6H4WgNwGGeCnaXxevUapfyw"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + DB_PATH
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)

from src.models import User
@login_manager.user_loader
def load_user(username):
    return User.query.get(username)

from src import routes