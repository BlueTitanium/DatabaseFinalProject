#Import Flask Library
from flask import Blueprint, render_template, session, request, url_for, redirect
from app_global import *
from app_public_views import *
from datetime import datetime, timedelta

customer_bp = Blueprint('customer_bp', __name__, template_folder='templates')

#Define route for home
@customer_bp.route('/home')
def home():
	user = session['customer']
	return render_template('customer/home.html', user = user)


#Define route for View Future Flights use case (Customer 1)
# Default - show future flights only
@customer_bp.route('/viewFlights')
def viewFlights():
	'''
	# this query retrieves only flight information
	query = "SELECT *"\
			" FROM Flight"\
			" WHERE (airline_name, flight_num, departure_timestamp) IN ("\
				" SELECT airline_name, flight_num, departure_timestamp"\
				" FROM Customer JOIN Ticket ON (Customer.email = Ticket.customer_email)"\
				" WHERE Customer.email = %s AND departure_timestamp > CURRENT_TIMESTAMP()"\
			")"
	'''

	query = "SELECT Flight.*, ticket_id, sold_price"\
			" FROM Flight NATURAL JOIN Ticket"\
			" WHERE customer_email = %s AND departure_timestamp > CURRENT_TIMESTAMP()"
	
	data = fetchall(query, (session['customer']))

	return render_template("customer/view.html", flights = data)

#Define route for View My Flights use case (Customer 1)
# Show all flights (including past flights)
@customer_bp.route('/viewAllFlights')
def viewAllFlights():
	query = "SELECT Flight.*, ticket_id, sold_price"\
			" FROM Flight NATURAL JOIN Ticket"\
			" WHERE customer_email = %s"

	data = fetchall(query, (session['customer']))
	return render_template("customer/view.html", flights = data)



#Define route for Search Future Flights use case (Customer 2, Public Info)
@customer_bp.route('/searchFlightsPage')
def searchFlightsPage():
	return render_template("customer/search.html")
# Define route for Search Future Flights requests
'''
@customer_bp.route('/searchFlights', methods = ['GET', 'POST'])
def searchFlights():
	# See dispatch_request(self) in app_public_views.SearchFlightView
	pass
'''
customer_bp.add_url_rule("/searchFlights", view_func = SearchFlightsView.as_view("searchFlights", "customer/search.html"), methods = ['GET', 'POST'])



#Define route for View Flight Status use case (Public Info)
@customer_bp.route('/findFlightStatusPage')
def findFlightStatusPage():
	return render_template("customer/status.html")
# Define route for View Flight Status Requests
customer_bp.add_url_rule("/flightStatus", view_func = FlightStatusView.as_view("flightStatus", "customer/status.html"), methods = ['GET', 'POST'])



#Define route for Purchase Ticket use case (Customer 3)
@customer_bp.route('/purchaseTicketPage')
def purchaseTicketPage():
	return render_template("customer/purchase.html")
#Define route for showing all purchaseable tickets
customer_bp.add_url_rule("/searchPurchaseTickets", view_func = SearchFlightsView.as_view("searchPurchaseTickets", "customer/purchase.html"), methods = ['GET', 'POST'])

#Define route for form to purchase ticket
@customer_bp.route('/purchaseTicket', methods=['GET', 'POST'])
def purchaseTicket():
	airline_name = request.args['airline_name']
	flight_num = request.args['flight_num']
	departure_timestamp = request.args['departure_timestamp']

	query = "WITH FlightTicketCount AS ("\
				" SELECT airline_name, flight_num, departure_timestamp, COUNT(ticket_id) AS ticket_count"\
				" FROM Ticket"\
				" GROUP BY airline_name, flight_num, departure_timestamp"\
			")"\
			" SELECT *, CASE"\
				" WHEN ticket_count >= 0.6*num_seats THEN ROUND(base_price * 1.25, 2)"\
				" ELSE base_price"\
			" END AS sell_price"\
			" FROM Flight AS F NATURAL JOIN FlightTicketCount JOIN Airplane ON (F.airline_name = Airplane.name AND F.airplane_id = Airplane.id)"\
			" WHERE airline_name = %s AND flight_num = %s AND departure_timestamp = %s"
	data = fetchone(query, (airline_name, flight_num, departure_timestamp))

	error = None
	# check if flight exists
	if not data:
		error = "Flight does not exist"

	# check if flight has already departed
	if (datetime.strptime(departure_timestamp, "%Y-%m-%d %H:%M:%S") <= datetime.now()):
		error = "Flight has already departed"

	# check if flight is cancelled
	elif data['status'] == 'canceled':
		error = "Flight is canceled"
 
	# check if there are still seats
	elif not (data['ticket_count'] < data['num_seats']):
		error = "Flight is full"

	if error:
		return render_template("customer/purchase.html", error = error)

	return render_template("customer/purchaseExactTicket.html", flight_data = data)

#Define route for Purchase Ticket Request
@customer_bp.route('/purchaseTicketReq', methods=['GET', 'POST'])
def purchaseTicketReq():
	airline_name = request.args['airline_name']
	flight_num = request.args['flight_num']
	departure_timestamp = request.args['departure_timestamp']


	customer_email = session['customer']
	
	#check if user is logged in
	if not customer_email:
		error = "Cannot proceed with action. User not logged in."
		return render_template('customer/purchase.html', error = error)


	query = "WITH FlightTicketCount AS ("\
				" SELECT airline_name, flight_num, departure_timestamp, COUNT(ticket_id) AS ticket_count"\
				" FROM Ticket"\
				" GROUP BY airline_name, flight_num, departure_timestamp"\
			")"\
			" SELECT *, CASE"\
				" WHEN ticket_count >= 0.6*num_seats THEN ROUND(base_price * 1.25, 2)"\
				" ELSE base_price"\
			" END AS sell_price"\
			" FROM Flight AS F NATURAL JOIN FlightTicketCount JOIN Airplane ON (F.airline_name = Airplane.name AND F.airplane_id = Airplane.id)"\
			" WHERE airline_name = %s AND flight_num = %s AND departure_timestamp = %s"
	data = fetchone(query, (airline_name, flight_num, departure_timestamp))

	error = None
	# check if flight exists
	if not data:
		error = "Flight does not exist"

	# check if flight has already departed
	if (datetime.strptime(departure_timestamp, "%Y-%m-%d %H:%M:%S") <= datetime.now()):
		error = "Flight has already departed"

	# check if flight is cancelled
	elif data['status'] == 'canceled':
		error = "Flight is canceled"
 
	# check if there are still seats
	elif not (data['ticket_count'] < data['num_seats']):
		error = "Flight is full"

	if error:
		return render_template("customer/purchaseExactTicket.html", flight_data = data, error = error)

	#grabs information from the forms
	card_type = request.form['card_type']
	name_on_card = request.form['name_on_card']
	card_number = request.form['card_number']
	expiration_date = request.form['expiration_date']

	# check card has not expired
	if (datetime.strptime(expiration_date, "%Y-%m-%d") < datetime.now()):
		error = "Card has already expired"
		return render_template("customer/purchaseExactTicket.html", flight_data = data, error = error)

	purchase_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

	#insert ticket
	ins_query = "INSERT INTO Ticket (sold_price, card_type, name_on_card, card_number, expiration_date, purchase_timestamp, customer_email, airline_name, flight_num, departure_timestamp) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
	ins_data = (data['sell_price'], card_type, name_on_card, card_number, expiration_date, purchase_timestamp, customer_email, airline_name, flight_num, departure_timestamp)
	modify(ins_query, ins_data)

	#redirect to View Flights Page
	return redirect(url_for('.viewFlights'))



#Define route for Cancel Ticket Page (Customer 4)
@customer_bp.route('/cancelTripPage')
def cancelTripPage():
	query = "SELECT Flight.*, ticket_id, sold_price"\
			" FROM Flight NATURAL JOIN Ticket"\
			" WHERE customer_email = %s AND departure_timestamp > (CURRENT_TIMESTAMP() + INTERVAL 24 HOUR)"
	data = fetchall(query, (session['customer']))

	return render_template("customer/cancel.html", cancellable_flights_data = data)
	
#Define route for cancel ticket request
@customer_bp.route('/cancelTicket', methods=['GET', 'POST'])
def cancelTicket():
	ticket_id = request.args['ticket_id']

	#check if user is authorized
	customer_email = session['customer']
	query = "SELECT * FROM Ticket WHERE customer_email = %s AND ticket_id = %s"
	data = fetchone(query, (customer_email, ticket_id))

	error = None
	if not data:
		error = "You are not authorized to cancel this ticket"

	#check that ticket is still cancelable
	elif (data['departure_timestamp'] <= (datetime.now() + timedelta(hours=24))):
		error = "Flight departs in 24 hours or less, cannot be cancelled"

	if error:
		query = "SELECT Flight.*, ticket_id, sold_price"\
				" FROM Flight NATURAL JOIN Ticket"\
				" WHERE customer_email = %s AND departure_timestamp > (CURRENT_TIMESTAMP() + INTERVAL 24 HOUR)"
		data = fetchall(query, (session['customer']))

		# re-render template with cancellable flights data and error
		return render_template("customer/cancel.html", cancellable_flights_data = data, error = error)


	query = "DELETE FROM Ticket WHERE ticket_id = %s"
	modify(query, (ticket_id))

	#redirect to Cancel Trip Page route
	return redirect(url_for(".cancelTripPage"))



#Define route for Give Ratings use case (Customer 5)
@customer_bp.route('/ratePreviousFlightsPage')
def ratePreviousFlightsPage():
	query = "SELECT Flight.*, ticket_id, sold_price"\
			" FROM Flight NATURAL JOIN Ticket"\
			" WHERE customer_email = %s AND arrival_timestamp < CURRENT_TIMESTAMP()"
	data = fetchall(query, (session['customer']))

	return render_template("customer/rate.html", previous_flights = data)

#Define route for Rating Specific Flight
@customer_bp.route('/rateFlight')
def rateFlight():
	airline_name = request.args['airline_name']
	flight_num = request.args['flight_num']
	departure_timestamp = request.args['departure_timestamp']

	query = "SELECT Flight.*, ticket_id, sold_price"\
			" FROM Flight NATURAL JOIN Ticket"\
			" WHERE customer_email = %s AND airline_name = %s AND flight_num = %s AND departure_timestamp = %s"
	data = fetchone(query, (session['customer'], airline_name, flight_num, departure_timestamp))

	return render_template("customer/rateExactFlight.html", flight_data = data)

#Define route for Give Ratings Request
@customer_bp.route('/rate', methods=['GET', 'POST'])
def rate():
	airline_name = request.args['airline_name']
	flight_num = request.args['flight_num']
	departure_timestamp = request.args['departure_timestamp']

	#grabs information from the form
	rating = request.form['rating']
	comment = request.form['comment']

	email = session['customer']


	# check customer has flown the flight
	query = "SELECT Flight.*, ticket_id, sold_price"\
			" FROM Flight NATURAL JOIN Ticket"\
			" WHERE customer_email = %s AND airline_name = %s AND flight_num = %s AND departure_timestamp = %s"
	data = fetchone(query, (email, airline_name, flight_num, departure_timestamp))

	if not data:
		error = "You have not flown this flight before."
		return render_template("customer/rateExactFlight.html", flight_data = data, error = error)


	# check the flight is a previous flight
	if (data['arrival_timestamp'] > datetime.now()):
		error = "This flight is not a previous flight (has not arrived)."
		return render_template("customer/rateExactFlight.html", flight_data = data, error = error)


	query = "INSERT INTO Rate VALUES(%s, %s, %s, %s, %s, %s)"
	modify(query, (email, airline_name, flight_num, departure_timestamp, rating, comment))

	#redirect to rate flights page on success
	return redirect(url_for(".ratePreviousFlightsPage"))



#Define route for Track Spending (Customer 6)
@customer_bp.route('/trackSpending')
def trackSpending():
	#query for total spending in last year
	query = "SELECT SUM(sold_price) AS total_spending"\
			" FROM Ticket"\
			" WHERE customer_email = %s AND DATE(purchase_timestamp) >= DATE((CURRENT_TIMESTAMP() - INTERVAL 1 YEAR))" # DATE(DATE_ADD(CURRENT_TIMESTAMP(), INTERVAL -1 YEAR))
	total_spending_data = fetchone(query, (session['customer']))
	#NOTE if last year does not mean last 365 days, solely Last Year, have to compare YEAR(purchase_timestamp) >= YEAR(DATE_ADD(CURRENT_TIMESTAMP(), INTERVAL -1 YEAR))

	#query for spending in each month in the last 6 months
	query = "SELECT YEAR(purchase_timestamp) AS year, MONTH(purchase_timestamp) AS month, SUM(sold_price) AS total_spending"\
			" FROM Ticket"\
			" WHERE customer_email = %s AND"\
				" YEAR(purchase_timestamp) >= YEAR((CURRENT_TIMESTAMP() - INTERVAL 6 MONTH)) AND"\
				" MONTH(purchase_timestamp) >= MONTH((CURRENT_TIMESTAMP() - INTERVAL 6 MONTH))"\
			" GROUP BY year, month" # DATE(DATE_ADD(month, -6, CURRENT_TIMESTAMP()))
	chart_data = fetchall(query, (session['customer']))

	# render template
	return render_template("customer/spending.html", 
		total_spending_header = "in the last year", total_spending_data = total_spending_data, 
		chart_data_header = "In the Last 6 Months (Default)", chart_data = chart_data)

#Define route for Track Spending Requests (given date range)
@customer_bp.route('/trackSpendingReq', methods = ['GET', 'POST'])
def trackSpendingReq():
	#grabs information from the form
	start_date = request.form['start_date']
	end_date = request.form['end_date']

	#query for total spending in between the date range given
	query = "SELECT SUM(sold_price) AS total_spending"\
			" FROM Ticket"\
			" WHERE customer_email = %s AND"\
				" DATE(purchase_timestamp) BETWEEN %s AND %s"
	total_spending_data = fetchone(query, (session['customer'], start_date, end_date))

	#query for spending in each month in date range given
	query = "SELECT YEAR(purchase_timestamp) AS year, MONTH(purchase_timestamp) AS month, SUM(sold_price) AS total_spending"\
			" FROM Ticket"\
			" WHERE customer_email = %s AND"\
				" DATE(purchase_timestamp) BETWEEN %s AND %s"\
			" GROUP BY year, month"
	chart_data = fetchall(query, (session['customer'], start_date, end_date))


	# set headers
	total_spending_header = "from " + start_date + " to " + end_date 
	chart_data_header = "From " + start_date + " To " + end_date 


	# render template
	return render_template("customer/spending.html", 
		total_spending_header = total_spending_header, total_spending_data = total_spending_data, 
		chart_data_header = chart_data_header, chart_data = chart_data)



#Define route for logout (Customer 7)
@customer_bp.route('/logout')
def logout():
	session.pop('customer')
	return redirect(url_for('general_bp.customerLogin'))