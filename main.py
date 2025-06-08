# Project: OTP Authentication Web App (Flask)

# -------------------
# File: main.py
# -------------------

from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Email
from flask_sqlalchemy import SQLAlchemy
import smtplib
import random
from functools import wraps
from flask import make_response

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
# Set session to be more secure
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access to session cookie
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Restrict cookie sending to same-site requests
app.config['PERMANENT_SESSION_LIFETIME'] = 1800  # Session expires after 30 minutes of inactivity
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

csrf = CSRFProtect(app)
db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    surname = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True, nullable=False)

# OTP store (in-memory)
otp_store = {}

# Forms
class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    surname = StringField('Surname', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Send OTP')

class OTPForm(FlaskForm):
    email = HiddenField('Email', validators=[DataRequired(), Email()])
    otp = StringField('OTP', validators=[DataRequired()])
    submit = SubmitField('Submit OTP')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Send OTP')

# Login required decorator

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_email' not in session:
            return redirect(url_for('login'))
        # Make sure the user still exists in the database
        user = User.query.filter_by(email=session['user_email']).first()
        if not user:
            session.clear()
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.before_request
def create_tables():
    if not hasattr(app, 'db_initialized'):
        db.create_all()
        app.db_initialized = True

@app.route('/')
def home():
    response = render_template('home.html')
    response = add_no_cache_headers(response)
    return response

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        name = form.name.data
        surname = form.surname.data
        email = form.email.data
        otp = str(random.randint(10000, 99999))
        otp_store[email] = {'otp': otp, 'name': name, 'surname': surname}
        send_email(email, otp, name)
        flash('OTP sent to your email.')
        otp_form = OTPForm()
        otp_form.email.data = email
        return render_template('register.html', form=form, otp_form=otp_form, show_otp=True)
    return render_template('register.html', form=form, show_otp=False)

@app.route('/verify_signup', methods=['POST'])
def verify_signup():
    otp_form = OTPForm()
    if otp_form.validate_on_submit():
        email = otp_form.email.data
        otp_input = otp_form.otp.data
        if email in otp_store and otp_store[email]['otp'] == otp_input:
            name = otp_store[email]['name']
            surname = otp_store[email]['surname']
            if not User.query.filter_by(email=email).first():
                new_user = User(name=name, surname=surname, email=email)
                db.session.add(new_user)
                db.session.commit()
            otp_store.pop(email)
            flash('Account created successfully!')
            return redirect(url_for('login'))
        else:
            flash('Invalid OTP. Please try again.')
    return redirect(url_for('register'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()
        if user:
            otp = str(random.randint(10000, 99999))
            otp_store[email] = {'otp': otp}
            send_email(email, otp, user.name)
            flash('Login OTP sent to your email.')
            otp_form = OTPForm()
            otp_form.email.data = email
            return render_template('login.html', form=form, otp_form=otp_form, show_otp=True)
        else:
            flash('User not found.')
    return render_template('login.html', form=form, show_otp=False)

@app.route('/verify_login', methods=['POST'])
def verify_login():
    otp_form = OTPForm()
    if otp_form.validate_on_submit():
        email = otp_form.email.data
        otp_input = otp_form.otp.data
        if email in otp_store and otp_store[email]['otp'] == otp_input:
            session['user_email'] = email
            otp_store.pop(email)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid OTP. Please try again.')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    user = User.query.filter_by(email=session['user_email']).first()
    response = render_template('dashboard.html', user=user)
    # Add no-cache headers to prevent browser caching
    return add_no_cache_headers(response)

@app.route('/logout')
@login_required
def logout():
    # Clear the entire session instead of just removing one key
    session.clear()
    flash('Logged out successfully.')
    response = redirect(url_for('home'))
    # Add headers to prevent caching
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/page<int:n>')
@login_required
def page(n):
    response = render_template(f'page{n}.html')
    return add_no_cache_headers(response)

def add_no_cache_headers(response):
    """Add headers to prevent caching of sensitive pages."""
    if not isinstance(response, str):
        return response
    
    resp = make_response(response)
    resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'
    return resp

def send_email(to, otp, name):
    sender_email = "smtp.testpersonal2004@gmail.com"
    sender_password = "hikwecnpzjlcgiyt"
    subject = "Your OTP Code"
    body = f"Hi {name},\nYour OTP code is: {otp}"
    message = f"Subject: {subject}\n\n{body}"
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to, message)
    except Exception as e:
        print("Error sending email:", e)

if __name__ == '__main__':
    app.run(debug=True)

# -------------------
# HTML templates should include {{ form.hidden_tag() }} in each <form> block
# Example adjustment for register.html:
# <form method="post">{{ form.hidden_tag() }} ...</form>
# <form method="post" action="/verify_signup">{{ otp_form.hidden_tag() }} ...</form>
