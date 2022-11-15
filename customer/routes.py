#Import Flask Library
from flask import Blueprint, render_template, session, request, url_for, redirect
from app_global import *
from app_public_views import *
import datetime

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


#XXX: may need to define a new route just to create a form
#Define route for purchase ticket
@customer_bp.route('/purchaseTicket', methods=['GET', 'POST'])
def purchaseTicket():
	#grabs information from the forms
	card_type = request.form['card_type']
	name_on_card = request.form['name_on_card']
	card_number = request.form['card_number']
	expiration_date = request.form['expiration_date']

	purchase_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

	customer_email = session['user']

	# TODO: set airline_name, flight_num and departure_timestamp
	'''
	airline_name = 
	flight_num =
	departure_timestamp = 
	'''
	
	#check if user is logged in
	if not customer_email:
		error = "Cannot proceed with action. User not logged in."
		#TODO change html
		return render_template('.html', error = error)

	#TODO insert ticket
	query = "INSERT INTO Ticket VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
	#TODO render template or redirect


#Define route for cancel ticket
#TODO
@customer_bp.route('/cancelTicket', methods=['GET', 'POST'])
def cancelTicket():
	query = "DELETE FROM Ticket WHERE ticket_id = %s"
	pass


#Define route for give ratings
#TODO
@customer_bp.route('/rate', methods=['GET', 'POST'])
def rate():
	#grabs information from the form
	rating = request.form['rating']
	comment = request.form['comment']

	email = session['user']

	#TODO get airline_name, flight_num and departure_timestamp
	'''
	airline_name =
	flight_num = 
	departure_timestamp =
	'''

	#TODO check if user is logged in

	#TODO render template


#Define route for Track Spending
#TODO
@customer_bp.route('/trackSpending')
def trackSpending():
	#query for total spending in last year
	query = "SELECT SUM(sold_price) AS total_spending"\
			" FROM Ticket"\
			" WHERE customer_email = %s AND purchase_timestamp >= DATEADD(year, -1, CURRENT_TIMESTAMP())"
	total_spending = fetchone(query, (session['user']))

	#query for spending in each month in the last 6 months
	query = "SELECT MONTH(purchase_timestamp) AS month, SUM(sold_price) AS total_spending"\
			" FROM Ticket"\
			" WHERE customer_email = %s AND purchase_timestamp >= DATEADD(month, -6, CURRENT_TIMESTAMP())"\
			" GROUP BY MONTH(purchase_timestamp)"
	chart_data = fetchall(query, (session['user']))

	return render_template("track_spending.html", total_spending = total_spending, chart_data = chart_data) #NOTE change name if needed

#Define route for Track Spending Requests (given date)
#TODO
@customer_bp.route('/trackSpendingReq', methods = ['GET', 'POST'])
def trackSpendingReq():
	#grabs information from the form
	start_date = request.form['start_date']
	end_date = request.form['end_date']

	#query for total spending in between the time range given
	query = "SELECT SUM(sold_price) AS total_spending"\
			" FROM Ticket"\
			" WHERE customer_email = %s AND"\
			" DATE(purchase_timestamp) BETWEEN %s AND %s"
	total_spending = fetchone(query, (session['user']))

	#query for spending in each month in time range given
	query = "SELECT MONTH(purchase_timestamp) AS month, SUM(sold_price) AS total_spending"\
			" FROM Ticket"\
			" WHERE customer_email = %s AND"\
			" DATE(purchase_timestamp) BETWEEN %s AND %s"\
			" GROUP BY MONTH(purchase_timestamp)"
	chart_data = fetchall(query, (session['user']))

	return render_template("track_spending.html", total_spending = total_spending, chart_data = chart_data) #NOTE change name if needed


#Define route for logout
@customer_bp.route('/logout')
def logout():
	session.pop('user')
	return redirect('/')