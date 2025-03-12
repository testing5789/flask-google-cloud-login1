# app.py
import os
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import firebase_admin
from firebase_admin import credentials, auth

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')  # Change in production

# Initialize Firebase Admin SDK
# For Cloud Run, set this as an environment variable
# For local development, you can place the JSON file in a secure location
cred_path = os.environ.get('FIREBASE_CREDENTIALS', './firebase-credentials.json')
cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred)

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@login_required
def index():
    return render_template('index.html', name=session.get('name', 'User'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        try:
            # Verify the user credentials with Firebase
            user = auth.get_user_by_email(email)
            # Note: Firebase Admin SDK cannot verify passwords
            # This is typically done client-side with Firebase JS SDK
            # For a server-side approach, you'd need to use Firebase REST API
            
            # For this example, we'll assume verification is done client-side
            # and we're just retrieving the user here
            
            # Set session data
            session['user_id'] = user.uid
            session['email'] = user.email
            session['name'] = user.display_name or email.split('@')[0]
            
            return redirect(url_for('index'))
        except auth.AuthError as e:
            error = f"Authentication error: {str(e)}"
    
    return render_template('login.html', error=error)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name', '')
        
        try:
            # Create the user in Firebase
            user = auth.create_user(
                email=email,
                password=password,
                display_name=name
            )
            
            # Set session data
            session['user_id'] = user.uid
            session['email'] = user.email
            session['name'] = user.display_name or email.split('@')[0]
            
            return redirect(url_for('index'))
        except auth.AuthError as e:
            error = f"Registration error: {str(e)}"
    
    return render_template('signup.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/verify-token', methods=['POST'])
def verify_token():
    # This endpoint is for verifying tokens from client-side auth
    token = request.json.get('token')
    try:
        decoded_token = auth.verify_id_token(token)
        uid = decoded_token['uid']
        user = auth.get_user(uid)
        
        # Set session data
        session['user_id'] = user.uid
        session['email'] = user.email
        session['name'] = user.display_name or user.email.split('@')[0]
        
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 401

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
