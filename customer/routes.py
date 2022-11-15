#Import Flask Library
from flask import Blueprint, render_template, session, request, url_for, redirect
from app_global import *
from app_public_views import *

customer_bp = Blueprint('customer_bp', __name__, template_folder='templates')

#Define route for home
@customer_bp.route('/home')
def home():
    user = session['user']
    return render_template('home.html', user = user)


#Define route for View Future Flights use case (Customer 1)
@customer_bp.route('/viewFlights')
def viewFlights():
    #XXX may have to get Ticket information such as ID as well
    query = "SELECT *"\
            " FROM Flight"\
            " WHERE (airline_name, flight_num, departure_timestamp) IN ("\
                " SELECT airline_name, flight_num, departure_timestamp"\
                " FROM Customer JOIN Ticket ON (Customer.email = Ticket.customer_email)"\
                " WHERE Customer.email = %s AND departure_timestamp > CURRENT_TIMESTAMP()"\
            ")"
    
    data = fetchall(query, (session['user']))

    #TODO render template or redirect


#Define route for Search Future Flights use case (Customer 2, Public Info)
'''
@customer_bp.route('/searchFlights', methods = ['GET', 'POST'])
def searchFlights():
    # See dispatch_request(self) in app_public_views.SearchFlightView
    pass
'''
customer_bp.add_url_rule("/searchFlights", view_func = SearchFlightsView.as_view("searchFlights", "home.html"), methods = ['GET', 'POST'])


#Define route for View Flight Status use case (Public Info)
#TODO: change index.html if necessary
customer_bp.add_url_rule("/flightStatus", view_func = FlightStatusView.as_view("flightStatus", "index.html"), methods = ['GET', 'POST'])


#Define route for logout
@customer_bp.route('/logout')
def logout():
	session.pop('user')
	return redirect('/')