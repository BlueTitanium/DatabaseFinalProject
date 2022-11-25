#Import Flask Library
from flask import Blueprint, render_template, session, request, url_for, redirect
from app_global import *
from app_public_views import *
import datetime

customer_bp = Blueprint('customer_bp', __name__, template_folder='templates')

#Define route for home
@customer_bp.route('/home')
def home():
	user = session['customer']
	return render_template('home.html', user = user)


#Define route for View Future Flights use case (Customer 1)
# Default - show future flights only
@customer_bp.route('/viewFlights')
def viewFlights():
	#XXX may have to get Ticket information such as ID as well -- need to change query in this case
	query = "SELECT *"\
			" FROM Flight"\
			" WHERE (airline_name, flight_num, departure_timestamp) IN ("\
				" SELECT airline_name, flight_num, departure_timestamp"\
				" FROM Customer JOIN Ticket ON (Customer.email = Ticket.customer_email)"\
				" WHERE Customer.email = %s AND departure_timestamp > CURRENT_TIMESTAMP()"\
			")"
	
	data = fetchall(query, (session['customer']))

	return render_template("view.html", flights = data)

#Define route for View Future Flights use case (Customer 1)
# Show all flights
@ customer_bp.route('/viewAllFlights')
def viewAllFlights():
	#XXX may have to get Ticket information such as ID as well -- need to change query in this case
	query = "SELECT *"\
			" FROM Flight"\
			" WHERE (airline_name, flight_num, departure_timestamp) IN ("\
				" SELECT airline_name, flight_num, departure_timestamp"\
				" FROM Customer JOIN Ticket ON (Customer.email = Ticket.customer_email)"\
				" WHERE Customer.email = %s"\
			")"

	data = fetchall(query, (session['customer']))
	return render_template("view.html", flights = data)


#Define route for Search Future Flights use case (Customer 2, Public Info)
@customer_bp.route('/searchFlights')
def searchFlights():
	return render_template("search.html")
# Define route for Search Future Flights requests
'''
@customer_bp.route('/searchFlightsReq', methods = ['GET', 'POST'])
def searchFlightsReq():
	# See dispatch_request(self) in app_public_views.SearchFlightView
	pass
'''
customer_bp.add_url_rule("/searchFlightsReq", view_func = SearchFlightsView.as_view("searchFlightsReq", "search.html"), methods = ['GET', 'POST'])


#Define route for View Flight Status use case (Public Info)
#TODO: add route to reach page
# Define route for View Flight Status Requests
#TODO: change .html
customer_bp.add_url_rule("/flightStatus", view_func = FlightStatusView.as_view("flightStatus", ".html"), methods = ['GET', 'POST'])


#Define route for form to purchase ticket
@customer_bp.route('/purchaseTicket')
def purchaseTicket(airline_name, flight_num, departure_timestamp):
	query = "SELECT * FROM Flight WHERE airline_name = %s AND flight_num = %s AND departure_timestamp = %s"
	data = fetchone(query, (airline_name, flight_num, departure_timestamp))

	query = "SELECT COUNT(ticket_id)"\
			" FROM Ticket"\
			" WHERE airline_name = %s AND flight_num = %s AND departure_timestamp = %s"
	curr_num_tickets = fetchone(query, (airline_name, flight_num, departure_timestamp))

	query = "SELECT num_seats"\
			" FROM Airplane JOIN Flight ON (Airplane.id = Flight.airplane_id AND Airplane.name = Flight.airline_name)"\
			" WHERE airline_name = %s AND flight_num = %s AND departure_timestamp = %s"
	num_seats = fetchone(query, (airline_name, flight_num, departure_timestamp))

	error = None
	# check if flight exists
	if not data:
		error = "Flight does not exist"

	# check if flight has already departed
	if (datetime.strptime(departure_timestamp, "%Y-%m-%d %H:%M:%S") >= datetime.now()):
		error = "Flight has already departed"

	# check if flight is cancelled
	#TODO check if this works
	elif data['status'] == 'canceled':
		error = "Flight is canceled"
 
	# check if there are still seats
	#TODO check if this works (check if curr_num_tickets and num_seats are of type int)
	elif not (curr_num_tickets < num_seats):
		error = "Flight is full"

	if error:
		return render_template("purchase.html", error = error)

	# calculate sold_price
	sold_price = data['base_price']
	if (0.6*num_seats <= curr_num_tickets):
		sold_price *= 1.25

	return render_template("purchase.html", flight = data, sold_price = sold_price)

#Define route for Purchase Ticket Request
@customer_bp.route('/purchaseTicketReq', methods=['GET', 'POST'])
def purchaseTicketReq(airline_name, flight_num, departure_timestamp):	
	customer_email = session['customer']
	
	#check if user is logged in
	if not customer_email:
		error = "Cannot proceed with action. User not logged in."
		return render_template('purchase.html', error = error)


	query = "SELECT * FROM Flight WHERE airline_name = %s AND flight_num = %s AND departure_timestamp = %s"
	data = fetchone(query, (airline_name, flight_num, departure_timestamp))

	query = "SELECT COUNT(ticket_id)"\
			" FROM Ticket"\
			" WHERE airline_name = %s AND flight_num = %s AND departure_timestamp = %s"
	curr_num_tickets = fetchone(query, (airline_name, flight_num, departure_timestamp))

	query = "SELECT num_seats"\
			" FROM Airplane JOIN Flight ON (Airplane.id = Flight.airplane_id AND Airplane.name = Flight.airline_name)"\
			" WHERE airline_name = %s AND flight_num = %s AND departure_timestamp = %s"
	num_seats = fetchone(query, (airline_name, flight_num, departure_timestamp))

	error = None
	# check if flight exists
	if not data:
		error = "Flight does not exist"

	# check if flight has already departed
	if (datetime.strptime(departure_timestamp, "%Y-%m-%d %H:%M:%S") >= datetime.now()):
		error = "Flight has already departed"

	# check if flight is cancelled
	#TODO check if this works
	elif data['status'] == 'canceled':
		error = "Flight is canceled"
 
	# check if there are still seats
	#TODO check if this works (check if curr_num_tickets and num_seats are of type int)
	elif not (curr_num_tickets < num_seats):
		error = "Flight is full"

	if error:
		return render_template("purchase.html", error = error)

	#grabs information from the forms
	card_type = request.form['card_type']
	name_on_card = request.form['name_on_card']
	card_number = request.form['card_number']
	expiration_date = request.form['expiration_date']

	purchase_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

	# calculate sold_price
	sold_price = data['base_price']
	if (0.6*num_seats <= curr_num_tickets):
		sold_price *= 1.25

	#TODO insert ticket
	query = "INSERT INTO Ticket (sold_price, card_type, name_on_card, card_number, expiration_date, purchase_timestamp, customer_email, airline_name, flight_num, departure_timestamp) VALUES(%.2f, %s, %s, %s, %s, %s, %s, %s, %s)"
	

	#TODO render template or redirect


#Define route for cancel ticket request
#TODO
@customer_bp.route('/cancelTicket', methods=['GET', 'POST'])
def cancelTicket(ticket_id):
	#check if user is authorized
	customer_email = session['user']
	query = "SELECT * FROM Ticket WHERE customer_email = %s AND ticket_id = %s"
	data = fetchone(query, (customer_email, ticket_id))

	if not data:
		error = "You are not authorized to cancel this ticket"
		return render_template("cancel.html", error = error)

	query = "DELETE FROM Ticket WHERE ticket_id = %s"
	modify(query, (ticket_id))

	#TODO render some page (confirmation page or user home screen on success)
	pass


#Define route for Give Ratings
#TODO
@customer_bp.route('/rate', methods=['GET', 'POST'])
def rate(airline_name, flight_num, departure_timestamp):
	#grabs information from the form
	rating = request.form['rating']
	comment = request.form['comment']

	email = session['customer']
	#TODO check if user is logged in
	if not email:
		error = "You need to be logged in to rate a flight"
		return render_template("rate.html", error = error)

	query = "INSERT INTO Rate VALUES(%s, %s, %s, %s, %d, %s)"
	modify(query, (email, airline_name, flight_num, departure_timestamp, rating, comment))

	#TODO render template
	pass


#Define route for Track Spending
#TODO
@customer_bp.route('/trackSpending')
def trackSpending():
	#query for total spending in last year
	query = "SELECT SUM(sold_price) AS total_spending"\
			" FROM Ticket"\
			" WHERE customer_email = %s AND purchase_timestamp >= DATEADD(year, -1, CURRENT_TIMESTAMP())"
	total_spending = fetchone(query, (session['customer']))
	#NOTE if last year does not mean last 365 days, solely Last Year, have to compare YEAR(purchase_timestamp) >= YEAR(DATEADD(year, -1, CURRENT_TIMESTAMP()))

	#query for spending in each month in the last 6 months
	query = "SELECT MONTH(purchase_timestamp) AS month, SUM(sold_price) AS total_spending"\
			" FROM Ticket"\
			" WHERE customer_email = %s AND purchase_timestamp >= DATEADD(month, -6, CURRENT_TIMESTAMP())"\
			" GROUP BY MONTH(purchase_timestamp)"
	chart_data = fetchall(query, (session['customer']))

	return render_template("spending.html", total_spending = total_spending, chart_data = chart_data) #NOTE change name if needed

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
	total_spending = fetchone(query, (session['customer']))

	#query for spending in each month in time range given
	query = "SELECT MONTH(purchase_timestamp) AS month, SUM(sold_price) AS total_spending"\
			" FROM Ticket"\
			" WHERE customer_email = %s AND"\
			" DATE(purchase_timestamp) BETWEEN %s AND %s"\
			" GROUP BY MONTH(purchase_timestamp)"
	chart_data = fetchall(query, (session['customer']))

	return render_template("spending.html", total_spending = total_spending, chart_data = chart_data) #NOTE change name if needed


#Define route for logout
@customer_bp.route('/logout')
def logout():
	session.pop('customer')
	return redirect('/')