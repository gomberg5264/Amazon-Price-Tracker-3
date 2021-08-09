from flask_login import UserMixin
from src import db, app
from werkzeug.security import generate_password_hash, check_password_hash
from jwt import encode
from time import time

#User table
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    # id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100))
    username = db.Column(db.String(20), unique=True, nullable=False, primary_key=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    products = db.relationship('Products', backref='products', lazy=True)

    def __repr__(self):
        """
        Details of the user instance
        """
        return "username - {}".format(self.username)

    def __init__(self, id, first_name, last_name, username, email, password):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.email = email
        self.password = self.hashed_password(password)
    
    def get_id(self):
        return self.username

    def hashed_password(self, password):
        pwd_hash = generate_password_hash(password)
        return pwd_hash

    def verify_password(self, password):
        return check_password_hash(self.password, password)

    def get_reset_token(self):
        return encode({'reset_password': self.username, 'exp': time() + 600}, key=app.config["SECRET_KEY"])


#Products table
class Products(UserMixin, db.Model):
    __tablename__ = 'products'
    product_id = db.Column(db.String(20), primary_key=True)
    product_name = db.Column(db.String(200), nullable=False)
    url = db.Column(db.String(400), nullable=False)
    product_price = db.Column(db.BigInteger)
    expected_price = db.Column(db.BigInteger, nullable=False)
    availability = db.Column(db.Boolean, default=True, nullable=False)
    last_check = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.String(20), db.ForeignKey('users.username'), primary_key=True, nullable=False)

    def __repr__(self):
        """
        Details of the user instance
        """
        return "username - {}, product_id - {}".format(self.user_id, self.product_id)

    def __init__(self, product_id, product_name, url, product_price, expected_price, availability, last_check, user_id):
        self.product_id = product_id
        self.product_name = product_name
        self.url = url
        self.product_price = product_price
        self.expected_price = expected_price
        self.availability = availability
        self.last_check = last_check
        self.user_id = user_id


#Creating the databases
db.create_all()