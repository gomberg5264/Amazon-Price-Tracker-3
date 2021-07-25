from flask import render_template, url_for, redirect, request
from src import app
from src.forms import LoginForm, RegisterForm


@app.route('/')
def index():
    return redirect(url_for('login', username=1))

@app.route('/home')
def home():
    return render_template('index.html', user=True)

@app.route('/login/<int:username>', methods=['GET', 'POST'])
def login(username: int):
    form = LoginForm()
    if form.validate_on_submit():
        print(form.username.data)
    return render_template('login.html', form=form, username=username)

@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate_on_submit():
        return redirect(url_for('home'))
    return render_template('registration.html', form=form)