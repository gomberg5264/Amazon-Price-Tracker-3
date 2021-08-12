from flask import render_template, url_for, redirect, request, session, flash
from flask_login import login_user, logout_user, current_user, login_required
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer 
from src import app, db, send_mail, async_mail
from src.forms import LoginFormUsername, LoginFormEmail, RegisterForm, ProfileForm, ItemForm, PasswordReset, ForgotPassword, ResetPassword
from src.models import User, Products
from src.scraper import extract_product_details, get_html
import threading
from werkzeug.security import generate_password_hash

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home', methods=['GET', 'POST'])
@login_required
def home(): 
    form = ItemForm(request.form)
    if request.method == 'POST' and form.validate_on_submit():
        if form.url.data is None or form.url.data.strip() == "":
            flash("URL is empty. Please enter valid URL.")
            return redirect(url_for('home'))
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
    return render_template('home.html', form=form)

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

@app.route('/remove/<item_id>', methods=["GET"])
@login_required
def remove(item_id: str):
    Products.query.filter_by(product_id=item_id, user_id=current_user.username).delete()
    db.session.commit()
    return redirect(url_for('home'))   

@app.route('/password_change/<username>', methods=["GET", "POST"])
@login_required
def reset_password(username: str):
    form = PasswordReset(request.form)
    if request.method == 'POST' and form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            print("valid")
            new_pwd_hash = generate_password_hash(form.new_password.data)
            current_user.password = new_pwd_hash
            db.session.commit()
            return redirect(url_for("home"))
        flash("Wrong current password.")
    return render_template("reset_password.html", form=form)

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = ForgotPassword(request.form)
    if request.method == "POST" and form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            subject = "Reset Password"
            body = 'Link to reset your password. Link expires in 10 minutes.\n{}\n\n'.format(url_for('set_new_pass', token=user.get_reset_token(), _external=True))
            body += 'If you did not make this request, ignore this mail.'
            msg = send_mail(subject=subject, body=body, recipient=user.email)

            mail_thread = threading.Thread(target=async_mail, args=(msg, ))
            mail_thread.start()
            flash("An email has been sent to your account.")
        else:
            flash("An account with that email does not exist.")
        return redirect(url_for("forgot_password"))
    return render_template('forgot_password.html', form=form)

@app.route('/reset_password/<token>', methods=['POST', 'GET', 'POST'])
def set_new_pass(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    serializer = Serializer(app.config["SECRET_KEY"])
    try:
        user_name = serializer.loads(token)["user_name"]
    except Exception as e:
        user_name = None

    user = User.query.filter_by(username=user_name).first()
    if user is None:
        flash("Token invalid or has expired.")
        return redirect(url_for('login_username'))
    
    form = ResetPassword(request.form)
    if request.method == 'POST' and form.validate_on_submit():
        new_pwd_hash = generate_password_hash(form.new_password.data)
        user.password = new_pwd_hash
        db.session.commit()
        return redirect(url_for('login_username'))
    return render_template("forgot_password_reset.html", form=form, password=user.password)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login_username'))
