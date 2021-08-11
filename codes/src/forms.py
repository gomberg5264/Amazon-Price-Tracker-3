from flask import flash
from flask_wtf import FlaskForm
import re
from src.scraper import url_checker
from wtforms import StringField, PasswordField, SubmitField, IntegerField
from wtforms.fields.html5 import EmailField, URLField
from wtforms.widgets.html5 import NumberInput
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, url, NumberRange

REGEX = """Must contain
- atleast one lowercase letter
- atleast one uppercase letter
- atleast one digit
- at least one symbol
"""
VALID_USERNAMES = re.compile(r"[a-zA-Z0-9@_.]+")
VALID_PASSWORDS = re.compile(r"^(?=.*[@_.#!^$])(?=.*[0-9])(?=.*[a-zA-Z])([a-zA-Z0-9_@#.$^!]+)$")

#Login form structure
class LoginFormUsername(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('LOGIN')

class LoginFormEmail(FlaskForm):
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
    
#Profile form structure
class ProfileForm(FlaskForm):
    first_name = StringField('First Name')
    last_name = StringField('Last Name')
    email = EmailField('Email', validators=[Email("Please check your email again.")])
    submit = SubmitField('SAVE')
    cancel = SubmitField("CANCEL")

#Form structure to add items
class ItemForm(FlaskForm):
    url = URLField('Link of the item', default="", validators=[DataRequired(), url()])
    price = IntegerField('Price', default=0, validators=[NumberRange(min=0, max=10000000000)], widget=NumberInput())
    add = SubmitField('ADD')

    def validate_url(form, field):
        valid, _, _ = url_checker(str(field.data))
        if not valid:
            flash("Not an amazon website.")
            raise ValidationError("Not a valid product URL")

#Password Reset form structure
class PasswordReset(FlaskForm):
    old_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=8, max=20, message="Length of password should be between 8 and 20 characters")])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('new_password', message="Passwords not matching")])
    submit = SubmitField('Change')

    def validate_new_password(form, field):
        """
        Validates the password format. Checks whether it follows a certain format or not.
        """
        match = re.match(VALID_PASSWORDS, field.data)
        if not match:
            raise ValidationError(REGEX)

#Forgot password form structure
class ForgotPassword(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email("Please check your email again.")])
    reset = SubmitField("Reset Password")

class ResetPassword(FlaskForm):
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=8, max=20, message="Length of password should be between 8 and 20 characters")])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('new_password', message="Passwords not matching")])
    submit = SubmitField('Change')

    def validate_new_password(form, field):
        """
        Validates the password format. Checks whether it follows a certain format or not.
        """
        match = re.match(VALID_PASSWORDS, field.data)
        if not match:
            raise ValidationError(REGEX)