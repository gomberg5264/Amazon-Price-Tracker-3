from flask import render_template, url_for, redirect, request, session, flash
from flask_login import login_user, logout_user, current_user, login_required
from src import app, db
from src.forms import LoginFormUsername, LoginFormEmail, RegisterForm, ProfileForm, ItemForm
from src.models import User, Products
from src.scraper import extract_product_details, get_html

@app.route('/')
def index():
    return redirect(url_for('login_username'))

@app.route('/home', methods=['GET', 'POST'])
@login_required
def home(): 
    form = ItemForm(request.form)
    if request.method == 'POST' and form.validate_on_submit():
        details = extract_product_details(get_html(form.url.data))
        user_products = Products.query.filter_by(product_id=details["asin"], user_id=current_user.username).first()
        if user_products:
            flash("Product already exists in list.")        
            return redirect(url_for('home'))   
        product = Products(details["asin"], details["name"], details["url"], details["price"],\
            form.price.data, details["availability"], details["last-check"], current_user.username)
        db.session.add(product)
        db.session.commit()
        flash("Product added to the list!")
        return redirect(url_for('home'))   
    return render_template('index.html', form=form)

@app.route('/profile/<username>', methods=['GET', 'POST'])
@login_required
def profile(username: str):
    form = ProfileForm(request.form)
    old = {'first': current_user.first_name, 'last': current_user.last_name, 'email': current_user.email}
    flag = False

    if form.cancel.data:
        return redirect(url_for('home'))
    if request.method == 'POST' and form.validate_on_submit():
        form_data = {'first': form.first_name.data, 'last': form.last_name.data, 'email': form.email.data}
        for field in old:
            if old[field] != form_data[field] and field != 'email':
                flag = not flag
                if field == 'first':
                    current_user.first_name =  form_data[field]
                else:
                    current_user.last_name = form_data[field]
                continue
            elif old[field] != form_data[field]:
                if User.query.filter_by(email=form.email.data).first():
                    flash("An account with that email already exists.")
                    return redirect(url_for('profile', username=current_user.username))
                
                flag = not flag
                current_user.email = form_data[field]
            else:
                continue
        db.session.commit()
        if flag:
            print("Changed")
            flash("Profile details changed successfully.")
        return redirect(url_for('home'))
    return render_template('profile.html', form=form)

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