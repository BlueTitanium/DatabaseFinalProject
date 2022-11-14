#Import Flask Library
from flask import Blueprint, render_template, session, request, url_for, redirect
from app_global import *

customer_bp = Blueprint('customer_bp', __name__, template_folder='templates')

#Define route for home
@customer_bp.route('/home')
def home():
    user = session['user']
    return render_template('home.html', user = user)

#Define route for viewing future flights
@customer_bp.route('/viewFlights')
def viewFlights():
    user = session['user']
    '''
    SELECT *
    FROM FLIGHT
    WHERE (flight_num, departure_timestamp) IN (
        SELECT flight_num, departure_timestamp
        FROM Customer JOIN Ticket ON (Customer.email = Ticket.customer_email)
        WHERE Customer.email = %s AND departure_timestamp > CURRENT_TIMESTAMP()
    )
    '''

#Define route for logout
@customer_bp.route('/logout')
def logout():
	session.pop('user')
	return redirect('/')