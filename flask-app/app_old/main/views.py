from flask import render_template
from app import app
import os

@app.route('/')
def home():
    welcome_message = os.getenv('WELCOME_MESSAGE', 'Welcome to the Flask Demo!')
    return render_template('home.html', welcome_message=welcome_message)

@app.route('/templates/navbar.html')
def navbar():
    return render_template('navbar.html')