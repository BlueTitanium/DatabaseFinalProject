#Import Flask Library
from flask import Blueprint, render_template, session, request, url_for, redirect
from app_global import *
from app_public_views import *

airlinestaff_bp = Blueprint('airlinestaff_bp', __name__, template_folder='templates')

#Define route for home
@airlinestaff_bp.route('/home')
def home():
    user = session['user']
    return render_template('home.html', user = user)


#Define route for Search Future Flights use case (Public Info)
airlinestaff_bp.add_url_rule("/searchFlights", view_func = SearchFlightsView.as_view("searchFlights", "home.html"), methods = ['GET', 'POST'])


#Define route for View Flight Status use case (Public Info)
#TODO: change index.html if necessary
airlinestaff_bp.add_url_rule("/flightStatus", view_func = FlightStatusView.as_view("flightStatus", "index.html"), methods = ['GET', 'POST'])


#Define route for View Future Flights use case (AirlineStaff 1)
# Shows default - flight the staff works for for the next 30 days
#TODO
@airlinestaff_bp.route('/viewFlights')
def viewFlights():
    query = "SELECT *"\
            " FROM Flight"\
            " WHERE airline_name = ("\
                " SELECT airline_name FROM AirlineStaff WHERE username = %s"\
            ") AND departure_timestamp BETWEEN CURRENT_TIMESTAMP() AND DATEADD(day, 30, CURRENT_TIMESTAMP())"
    pass



#Define route for logout
@airlinestaff_bp.route('/logout')
def logout():
	session.pop('user')
	return redirect('/')