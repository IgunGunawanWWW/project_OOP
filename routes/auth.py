from flask import Blueprint, redirect, url_for, session, make_response
from flask import render_template

auth_bp = Blueprint('auth',__name__)

@auth_bp.route('/')
def home():
    return render_template('index.html')