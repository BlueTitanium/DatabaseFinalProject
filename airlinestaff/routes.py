#Import Flask Library
from flask import Blueprint, render_template, session, request, url_for, redirect
from app_global import *

airlinestaff_bp = Blueprint('airlinestaff_bp', __name__, template_folder='templates')

#Define route for home
@airlinestaff_bp.route('/home')
def home():
    user = session['user']
    return render_template('home.html', user = user)

#Define route for logout
@customer_bp.route('/logout')
def logout():
	session.pop('user')
	return redirect('/')