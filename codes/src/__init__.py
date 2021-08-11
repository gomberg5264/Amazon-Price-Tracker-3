from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
import json
import os

dir = "/".join(__file__.split("/")[:-1])
with open(os.path.join(dir, 'flask-configs.json')) as f:
    js_file = json.load(f)

app = Flask(__name__)
app.config["SECRET_KEY"] = js_file["SECRET_KEY"]
app.config["SQLALCHEMY_DATABASE_URI"] = js_file["SQLALCHEMY_DATABASE_URI"]
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = js_file["SQLALCHEMY_TRACK_MODIFICATIONS"]
app.config["MAIL_SERVER"] = js_file["MAIL_SERVER"]
app.config["MAIL_PORT"] = js_file["MAIL_PORT"]
app.config["MAIL_SSL"] = js_file["MAIL_SSL"]
app.config["MAIL_USE_TLS"] = js_file["MAIL_USE_TLS"]
app.config["MAIL_USERNAME"] = js_file["MAIL_USERNAME"]
app.config["MAIL_PASSWORD"] = js_file["MAIL_PASSWORD"]
app.config["MAIL_SENDER"] = js_file["MAIL_SENDER"]

db = SQLAlchemy(app)
login_manager = LoginManager(app)
mail = Mail(app)

from src.models import User
@login_manager.user_loader
def load_user(username):
    return User.query.get(username)

def async_mail(msg):
    with app.app_context() as context:
        try:
            mail.send(msg)
        except Exception as e:
            pass

def send_mail(subject, recipient, body, html=None):
    msg = Message(subject = subject,
        recipients = [recipient],
        sender = app.config["MAIL_SENDER"],
        body = body,
        html = html)
    return msg

from src import routes