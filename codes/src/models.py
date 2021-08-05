from flask_login import UserMixin
from src import db
from werkzeug.security import generate_password_hash, check_password_hash

#User table
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    # id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100))
    username = db.Column(db.String(20), unique=True, nullable=False, primary_key=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)

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


#Creating the databases
db.create_all()