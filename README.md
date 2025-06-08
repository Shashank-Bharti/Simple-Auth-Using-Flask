# Flask OTP Authentication System

A simple Flask-based authentication system using One-Time Passwords (OTP) sent via email for secure user verification.

## Features

- User registration with OTP verification
- Secure login using email OTP
- Session management
- Protected routes using decorators
- SQLite database integration

## Prerequisites

- Python 3.7+
- Flask
- Flask-WTF
- Flask-SQLAlchemy
- Email account for sending OTPs

## Installation

1. Clone the repository:
```
https://github.com/Shashank-Bharti/Simple-Auth-Using-Flask.git
```

2. Navigate to the project directory:
```
cd flask-otp-auth
```

3. Install required dependencies:
```
pip install -r requirements.txt
```

## Configuration

Before running the application, you need to configure the email settings for sending OTP codes:

1. Open `main.py` in your editor
2. Locate lines 189-190 containing the email configuration:
```python
sender_email = "smtp.testpersonal2004@gmail.com"
sender_password = "hikwecnpzjlcgiyt"
```
3. Replace these values with your own email address and app password:
   - For Gmail users, you'll need to create an "App Password" in your Google Account settings
   - Go to your Google Account → Security → 2-Step Verification → App passwords
   - Generate a new app password for "Mail"

## Running the Application

After configuration, run the application with:

```
python main.py
```

The server will start on http://127.0.0.1:5000/

## How It Works

1. **Registration**:
   - Enter your name, surname, and email address
   - An OTP will be sent to your email
   - Enter the OTP to complete registration

2. **Login**:
   - Enter your registered email address
   - An OTP will be sent to your email
   - Enter the OTP to log in

3. **Dashboard and Protected Pages**:
   - After successful login, you can access the dashboard
   - Navigate to protected pages using the links
   - Use the logout button to securely end your session

## Security Features

- Secure session management
- CSRF protection
- OTP verification for both registration and login
- Session timeouts
- Anti-caching headers to prevent session issues

## Project Structure

```
main.py              # Main Flask application
requirements.txt     # Python dependencies
instance/
    users.db         # SQLite database
templates/
    dashboard.html   # Dashboard template
    home.html        # Home page template
    login.html       # Login form
    page1.html       # Protected page examples
    page2.html
    page3.html
    page4.html
    page5.html
    register.html    # Registration form
```

## ⚠️ Production Warning

**This application is NOT production-ready** and is intended for demonstration or learning purposes only. 
For production deployment, you would need to implement the following changes:

- Replace SQLite with a more robust database system like PostgreSQL or MySQL:
  - SQLite is not suitable for concurrent access in production environments
  - Enterprise applications should use a client-server database with proper scaling capabilities

- Use a production WSGI server instead of Flask's built-in development server:
  - Deploy with Gunicorn, uWSGI, or a similar WSGI server
  - Configure a reverse proxy like Nginx or Apache in front of the WSGI server

- Implement additional security measures:
  - Rate limiting for OTP requests
  - Proper password hashing for sensitive data
  - HTTPS configuration with valid SSL certificates
  - More robust error handling and logging

Example production deployment command with Gunicorn:
```
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 main:app
```

## Troubleshooting

If you experience issues with login persistence:
- Clear your browser cookies and cache
- Make sure you're using the logout button to end sessions
- Check that your email server is properly configured


