from flask import render_template, url_for, redirect, request, session, flash
from flask_login import login_user, logout_user, current_user, login_required
from src import app, db
from src.forms import LoginFormUsername, LoginFormEmail, RegisterForm
from src.models import User

@app.route('/')
def index():
    return redirect(url_for('login_username'))

@app.route('/home')
@login_required
def home(): 
    return render_template('index.html', user=session.get('user'))

@app.route('/login/username', methods=['GET', 'POST'])
def login_username():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginFormUsername(request.form)
    if request.method == "POST" and form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.verify_password(form.password.data):
            session["user"] = user.username
            login_user(user)
            return redirect(url_for('home'))
        flash("Wrong credentials. Please enter again.")
    return render_template('login_username.html', form=form)

@app.route('/login/email', methods=['GET', 'POST'])
def login_email():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginFormEmail(request.form)
    if request.method == "POST" and form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.verify_password(form.password.data):
            session["user"] = user.username
            login_user(user)
            return redirect(url_for('home'))
        flash("Wrong credentials. Please enter again.")
    return render_template('login_email.html', form=form)

@app.route('/register', methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate_on_submit():
        username = User.query.filter_by(username=form.username.data).first()
        email = User.query.filter_by(email=form.email.data).first()

        print(username, email) 

        if username:
            flash("Username already exists. Please enter different username.")
            return render_template('registration.html', form=form)
        if email:
            flash("Email already exists. Please enter different username.")
            return render_template('registration.html', form=form)
        
        user = User(1, form.first_name.data, form.last_name.data, form.username.data, form.email.data, form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Account created successfully. Please login.")
        return redirect(url_for('login_username'))
    return render_template('registration.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login_username'))