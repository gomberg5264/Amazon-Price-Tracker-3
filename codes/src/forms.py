from flask_wtf import FlaskForm
import re
from wtforms import StringField, PasswordField, SubmitField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError

REGEX = """Must contain
- atleast one lowercase letter
- atleast one uppercase letter
- atleast one digit
- at least one symbol
"""
VALID_USERNAMES = re.compile(r"[a-zA-Z0-9@_.]+")
VALID_PASSWORDS = re.compile(r"^(?=.*[@_.#!^$])(?=.*[0-9])(?=.*[a-zA-Z])([a-zA-Z0-9_@#.$^!]+)$")

#Login form structure
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('LOGIN')


#Registration form structure
class RegisterForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name')
    username = StringField('Username', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(), Email("Please check your email again.")])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message="Passwords not matching")])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=20, message="Length of password should be between 8 and 20 characters")])
    submit = SubmitField('REGISTER')

    def validate_username(form, field):
        """
        Validates the format of usernames. Allows only certain characters.
        """
        match = re.match(VALID_USERNAMES, field.data)
        if match.end() - match.start() != len(field.data):
            raise ValidationError("Unwanted characters in username. Please Enter again.")
    
    def validate_password(form, field):
        """
        Validates the password format. Checks whether it follows a certain format or not.
        """
        match = re.match(VALID_PASSWORDS, field.data)
        if not match:
            raise ValidationError(REGEX)