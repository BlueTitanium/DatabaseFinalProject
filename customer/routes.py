#Import Flask Library
from flask import Blueprint, render_template, session, request, url_for, redirect
from app_global import *

customer_bp = Blueprint('customer_bp', __name__, template_folder='templates')

#Define route for home
@customer_bp.route('/home')
def home():
    user = session['user']
    return render_template('home.html', user = user)