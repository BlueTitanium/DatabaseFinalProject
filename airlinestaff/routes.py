#Import Flask Library
from flask import Blueprint, render_template, session, request, url_for, redirect
from app_global import *
from app_public_views import *
from datetime import datetime

airlinestaff_bp = Blueprint('airlinestaff_bp', __name__, template_folder='templates')

#Define route for home
@airlinestaff_bp.route('/home')
def home():
	user = session['user']
	return render_template('airlinestaff/home.html', user = user)


#Define route for Search Future Flights use case (Public Info)
@airlinestaff_bp.route('/searchFlightsPage')
def searchFlightsPage():
	return render_template("airlinestaff/search.html")
#Define route for Search Future Flights use case (Public Info)
airlinestaff_bp.add_url_rule("/searchFlights", view_func = SearchFlightsView.as_view("searchFlights", "airlinestaff/search.html"), methods = ['GET', 'POST'])


#Define route for View Flight Status use case (Public Info)
@airlinestaff_bp.route('/findFlightStatusPage')
def findFlightStatusPage():
	return render_template("airlinestaff/status.html")
#Define route for View Flight Status use case Requests (Public Info)
airlinestaff_bp.add_url_rule("/flightStatus", view_func = FlightStatusView.as_view("flightStatus", "airlinestaff/status.html"), methods = ['GET', 'POST'])


#Define route for View Future Flights use case (AirlineStaff 1)
# Shows default - flight the staff works for for the next 30 days
@airlinestaff_bp.route('/viewFlights')
def viewFlights():
	username = session['user']

	# check if logged in
	if not username:
		error = "Not logged in"
		return render_template("airlinestaff/viewFlights.html", error = error)

	'''
	# single query
	query = "SELECT *"\
			" FROM Flight"\
			" WHERE airline_name = ("\
				" SELECT airline_name FROM AirlineStaff WHERE username = %s"\
			") AND departure_timestamp BETWEEN CURRENT_TIMESTAMP() AND (CURRENT_TIMESTAMP() + INTERVAL 30 DAY)"
	data = fetchall(query, (username))
	'''

	# get airline name (separately, so it can be displayed)
	query = "SELECT airline_name FROM AirlineStaff WHERE username = %s"
	staff_airline_name = fetchone(query, (username))

	# get flights
	query = "SELECT *"\
			" FROM Flight"\
			" WHERE airline_name = %s"\
				" AND departure_timestamp BETWEEN CURRENT_TIMESTAMP() AND (CURRENT_TIMESTAMP() + INTERVAL 30 DAY)"
	data = fetchall(query, (staff_airline_name['airline_name']))

	# render template
	return render_template("airlinestaff/viewFlights.html", header = "In the Next 30 Days (Default)", airline = staff_airline_name['airline_name'], flights = data)

#Define route for View Future Flights Search use case (AirlineStaff 1)
@airlinestaff_bp.route('/viewFlightsSearch', methods=['GET', 'POST'])
def viewFlightsSearch():
	username = session['user']

	# check if logged in
	if not username:
		error = "Not logged in"
		return render_template("airlinestaff/viewFlights.html", error = error)

	# check dates
	start_date = request.form['start_date']
	end_date = request.form['end_date']


	'''
	# single query 
	query = "SELECT *"\
			" FROM Flight AS F, Airport AS D, Airport AS A"\
			" WHERE F.departure_airport = D.name AND F.arrival_airport = A.name"\
			" AND airline_name = ("\
				" SELECT airline_name FROM AirlineStaff WHERE username = %s"\
			")"
	parameters = (username,) #, required so Python will recognize () as tuple, or else (username) is str
	'''

	# get airline name (separately, so it can be displayed)
	query = "SELECT airline_name FROM AirlineStaff WHERE username = %s"
	staff_airline_name = fetchone(query, (username))

	# get flights
	query = "SELECT *"\
			" FROM Flight AS F, Airport AS D, Airport AS A"\
			" WHERE F.departure_airport = D.name AND F.arrival_airport = A.name"\
			" AND airline_name = %s"
	parameters = ((staff_airline_name['airline_name']),)


	# start date + end date (departure)
	header = ""
	if ((start_date or end_date) and not(start_date and end_date)):
		error = "Start date and end date both must be filled out if date is entered for either"
		return render_template("airlinestaff/viewFlights.html", airline = staff_airline_name['airline_name'], error = error)

	if (start_date and end_date):
		if (datetime.strptime(start_date, "%Y-%m-%d") > datetime.strptime(end_date, "%Y-%m-%d")):
			error = "Start date cannot be after end date"
			return render_template("airlinestaff/viewFlights.html", airline = staff_airline_name['airline_name'], error = error)

		query += " AND DATE(departure_timestamp) BETWEEN %s AND %s"
		header += "Between " + start_date + " and " + end_date + " "
		parameters = parameters + (start_date, end_date)
	

	# departure airport/city
	departure_info = request.form['departure_info']
	if (departure_info):
		formatted_departure_info = '%' + departure_info +'%'

		query += " AND (UPPER(F.departure_airport) LIKE UPPER(%s) OR UPPER(D.city) LIKE UPPER(%s))"
		header += "Flying From Airport/City Containing " + departure_info + " "
		parameters = parameters + (formatted_departure_info, formatted_departure_info)

	# arrival airport/city
	arrival_info = request.form['arrival_info']
	if (arrival_info):
		formatted_arrival_info = '%' + arrival_info + '%'

		query += " AND (UPPER(F.arrival_airport) LIKE UPPER(%s) OR UPPER(A.city) LIKE UPPER(%s))"
		header += "Flying To Airport/City Containing " + arrival_info + " "
		parameters = parameters + (formatted_arrival_info, formatted_arrival_info)


	# execute query
	data = fetchall(query, (parameters))

	#render template
	return render_template("airlinestaff/viewFlights.html", airline = staff_airline_name['airline_name'], header = header, flights = data)

#Define route to view all customers for a particular flight
@airlinestaff_bp.route('/viewFlightCustomers', methods=['GET', 'POST'])
def viewFlightCustomers():
	# get arguments
	airline_name = request.args['airline_name']
	flight_num = request.args['flight_num']
	departure_timestamp = request.args['departure_timestamp']

	# execute query
	query = "SELECT email, name, building_number, street, city, state, phone_number, date_of_birth, ticket_id, sold_price"\
			" FROM Customer JOIN Ticket ON (Customer.email = Ticket.customer_email)"\
			" WHERE airline_name = %s AND flight_num = %s AND departure_timestamp = %s"
	data = fetchall(query, (airline_name, flight_num, departure_timestamp))
	
	# render template
	return render_template("airlinestaff/viewFlightCustomers.html", 
		airline_name = airline_name, flight_num = flight_num, departure_timestamp = departure_timestamp, 
		customers = data)


#Define route for the Create New Flights Page (Airline Staff 2)
@airlinestaff_bp.route('/createFlightPage')
def createFlightPage():
	error = request.args.get('error', None) # gets (optional) error message

	# get airports to be set for form
	query = "SELECT name FROM Airport"
	airports = fetchall(query, ())

	# get airline name to be set for page
	query = "SELECT airline_name FROM AirlineStaff WHERE username = %s"
	airline_name = fetchone(query, (session['user']))

	# get airplane ids to be set for form
	query = "SELECT DISTINCT id FROM Airplane WHERE name = %s"
	airplanes = fetchall(query, (airline_name['airline_name']))

	# get flights
	query = "SELECT *"\
			" FROM Flight"\
			" WHERE airline_name = %s"\
				" AND departure_timestamp BETWEEN CURRENT_TIMESTAMP() AND (CURRENT_TIMESTAMP() + INTERVAL 30 DAY)"
	data = fetchall(query, (airline_name['airline_name']))

	return render_template("airlinestaff/createFlight.html", 
		airports = airports, airline = airline_name['airline_name'], airplanes = airplanes, flights = data, error = error)

#Define route for Create New Flights Requests (Airline Staff 2)
@airlinestaff_bp.route('/createFlight', methods=['GET', 'POST'])
def createFlight():
	username = session['user']
	error = None

	#check authorization
	query = "SELECT *"\
			" FROM AirlineStaff"\
			" WHERE username = %s"
	data = fetchone(query, (username))
		
	if not data:
		error = "Not authorized to create a flight"
		return redirect(url_for('.createFlightPage', error = error))

	#grabs information from the form
	flight_num = request.form['flight_num']
	departure_timestamp = request.form['departure_timestamp']
	arrival_timestamp = request.form['arrival_timestamp']
	base_price = request.form['base_price']
	status = request.form['status']
	departure_airport = request.form['departure_airport']
	arrival_airport = request.form['arrival_airport']

	airplane_id = request.form['airplane_id']

	#grabs airline_name information from session and query data
	query = "SELECT airline_name FROM AirlineStaff WHERE username = %s"
	airline_name = fetchone(query, (session['user']))


	#check that departure airport and arrival airport exists
	query = "SELECT * FROM Airport WHERE name = %s"
	if (not fetchone(query, (departure_airport))):
		error = "Departure airport does not exist in database"
		return redirect(url_for('.createFlightPage', error = error))

	if (not fetchone(query, (arrival_airport))):
		error = "Arrival airport does not exist in database"
		return redirect(url_for('.createFlightPage', error = error))

	#check that airplane id exists
	query = "SELECT * FROM Airplane WHERE id = %s"
	if (not fetchone(query, (airplane_id))):
		error = "Airplane ID does not exist in database"
		return redirect(url_for('.createFlightPage', error = error))


	#check that it is a future flight
	if (datetime.strptime(departure_timestamp, "%Y-%m-%dT%H:%M") <= datetime.now()):
		error = "Departure time cannot be before current time"
		return redirect(url_for('.createFlightPage', error = error))

	#check that departure time is before arrival time
	if (datetime.strptime(departure_timestamp, "%Y-%m-%dT%H:%M") >= datetime.strptime(arrival_timestamp, "%Y-%m-%dT%H:%M")):
		error = "Start date cannot be after end date"
		return redirect(url_for('.createFlightPage', error = error))


	# convert timestamps into uniform SQL format
	departure_timestamp = datetime.strptime(departure_timestamp, "%Y-%m-%dT%H:%M").strftime("%Y-%m-%d %H:%M:%S")
	arrival_timestamp = datetime.strptime(arrival_timestamp, "%Y-%m-%dT%H:%M").strftime("%Y-%m-%d %H:%M:%S")


	# check that flight is unique
	query = "SELECT * FROM Flight WHERE airline_name = %s AND flight_num = %s AND departure_timestamp = %s"
	if (fetchone(query, (airline_name['airline_name'], flight_num, departure_timestamp))):
		error = "Flight already exists"
		return redirect(url_for('.createFlightPage', error = error))


	query = "INSERT INTO Flight VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
	modify(query, (airline_name['airline_name'], flight_num, departure_timestamp, arrival_timestamp, base_price, status, departure_airport, arrival_airport, airplane_id))

	# return redirect
	return redirect(url_for('.createFlightPage'))

#XXX need to discuss how to get flight info
#TODO define route to page
#Define route for Change Flight Status use case (Airline Staff 3)
@airlinestaff_bp.route('/changeFlightReq', methods=['GET', 'POST'])
def changeFlightReq(airline_name, flight_num, departure_timestamp):
	username = session['user']
	error = None
	
	#check authorization
	query = "SELECT *"\
			" FROM AirlineStaff"\
			" WHERE username = %s"
	data = fetchone(query, (username))
		
	if not data:
		error = "Not authorized to create a flight"
		return render_template("airlinestaff/change_flight.html", error = error)

	#grabs information from the form
	status = request.form['status']

	query = "UPDATE Flight"\
			" SET status = %s"\
			" WHERE airline_name = %s AND flight_num = %s AND departure_timestamp = %s"
	modify(query, (airline_name, flight_num, departure_timestamp))

	#TODO return or redirect

#Define route for Add Airplane use case (Airline Staff 4) 
#TODO
@airlinestaff_bp.route('/addAirplane', methods=['GET', 'POST'])
def addAirplane():
	username = session['user']
	error = None
	
	#check authorization
	query = "SELECT *"\
			" FROM AirlineStaff"\
			" WHERE username = %s"
	data = fetchone(query, (username))
		
	if not data:
		error = "Not authorized to create a flight"
		return render_template("airlinestaff/change_flight.html", error = error)

	id = request.form['id']
	num_seats = request.form['num_seats']
	manufacturer = request.form['manufacturer']
	age = request.form['age']

	query = "SELECT airline_name FROM AirlineStaff WHERE username = %s"
	airline_name = fetchone(query, (session['user']))

	query = "INSERT INTO Airplane VALUES (%s, %s, %d, %s, %d)"
	modify(query, (id, airline_name, num_seats, manufactuerer, age))
	#TODO return
	pass


#Define route for Add Airport
@airlinestaff_bp.route('/addAirport')
def addAirport():
	return render_template('airlinestaff/add_airport.html')

#TODO
@airlinestaff_bp.route('/addAirportReq', methods=['GET', 'POST'])
def addAirportReq():
	username = session['user']
	error = None
	
	#check authorization
	query = "SELECT *"\
			" FROM AirlineStaff"\
			" WHERE username = %s"
	data = fetchone(query, (username))
		
	if not data:
		error = "Not authorized to create a flight"
		return render_template("airlinestaff/add_airport.html", error = error)

	#grabs information from the form
	name = request.form['name']
	city = request.form['city']
	country = request.form['country']
	airport_type = request.form['airport_type']

	query = "INSERT INTO Airport VALUES (%s, %s, %s, %s)"
	modify(query, (name, city, country, airport_type))

	#TODO return
	pass


#Define route for View Flight Ratings
#XXX may need another route that directs to view flight page depending on how web pages are structured
#TODO
#XXX need to get flight_num, departure_timestamp somehow -- either by GET parameters or form request
@airlinestaff_bp.route('/viewFlightRatingReq', methods=['GET', 'POST'])
def viewFlightRatingReq(flight_num, departure_timestamp):
	# check if logged in
	if not (session['user']):
		return render_template("airlinestaff/.html", error = "Not logged in") #TODO change name
		
	#grabs airline_name information from session and query data
	query = "SELECT airline_name FROM AirlineStaff WHERE username = %s"
	airline_name = fetchone(query, (session['user']))

	# Get average rating
	query = "SELECT AVG(rating)"\
			" FROM Rate"\
			" WHERE airline_name = %s AND flight_num = %s AND departure_timestamp = %s"
	avg_rating = fetchone(query, (session['user'], flight_num, departure_timestamp))

	# Get all ratings and comments
	query = "SELECT *"\
			" FROM Rate"\
			" WHERE airline_name = %s AND flight_num = %s AND departure_timestamp = %s"
	ratings = fetchall(query, (session['user'], flight_num, departure_timestamp))

	'''
	# check if there are ratings
	if not query:
		error = "No ratings or comments available for this flight"
		return render_template('airlinestaff/view_flight_ratings.html', error = error)
	'''

	#TODO return
	return render_template('airlinestaff/view_flight_ratings.html', avg_rating = avg_rating, ratings = ratings)


#Define route for View Frequent Customers
#TODO
@airlinestaff_bp.route('/viewFreqCustomers')
def viewFreqCustomer():
	# check if logged in
	if not (session['user']):
		return render_template("airlinestaff/.html", error = "Not logged in") #TODO change name

	#grabs airline_name information from session and query data
	query = "SELECT airline_name FROM AirlineStaff WHERE username = %s"
	airline_name = fetchone(query, (session['user']))

	# Get most frequent customer within the last year
	query = "WITH customer_ticket_count(email, ticket_count) AS ("\
				" SELECT customer_email, COUNT(ticket_id)"\
				" FROM Ticket"\
				" WHERE airline_name = %s"\
				" GROUP BY customer_email"\
			")"\
			" SELECT email"\
			" FROM customer_ticket_count"\
			" WHERE ticket_count = ("\
				" SELECT MAX(ticket_count)"\
				" FROM customer_ticket_count"\
			")"
	most_freq_customer = fetchone(query, (airline_name))

	#TODO also list all customers that has taken a flight at staff's airline or provide a form that allows staff to enter a customer email
	# if using the former option, need query as written below
	query = "SELECT DISTINCT customer_email"\
			" FROM Ticket"\
			" WHERE airline_name = %s"

	#TODO return

#Define route for View Particular Customer (part 2 of view frequent customer use case)
@airlinestaff_bp.route('/viewCustomerReq', methods = ['GET', 'POST'])
def viewCustomerReq(customer_email):
	# XXX if list all customer in previous route, then put customer_email as parameter in this route instead of using request.form.
		# else, dont use customer_email as parameter
	# Get customer email
	# customer_email = request.form['email']

	#grabs airline_name information from session and query data
	query = "SELECT airline_name FROM AirlineStaff WHERE username = %s"
	airline_name = fetchone(query, (session['user']))

	# See a list of all flights a particular Customer has taken only on that particular airline
	#XXX: maybe allow staff to enter or select a customer (in this case, would need a new route)
	query = "SELECT *"\
			" FROM Flight"\
			" WHERE airline_name = %s AND (airline_name, flight_num, departure_timestamp) IN ("\
				"SELECT airline_name, flight_num, departure_timestamp"\
				" FROM Ticket"\
				" WHERE customer_email = %s"\
			")"
	# if we want to display ticket information along with the information in the flight table, have to use new query (see below)
	query = "SELECT *"\
			" FROM Flight NATURAL JOIN Ticket"\
			" WHERE airline_name = %s AND customer_email = %s"

	#TODO return
	pass


#Define route for total amounts of ticket sold
@airlinestaff_bp.route('/viewReports')
def viewReports():
	return render_template("airlinestaff/view_reports.html")

@airlinestaff_bp.route('/viewReportLastYear')
def viewReportLastYear():
	# check if logged in
	if not (session['user']):
		return render_template("airlinestaff/view_reports.html", error = "Not logged in")

	#grabs airline_name information from session and query data
	query = "SELECT airline_name FROM AirlineStaff WHERE username = %s"
	airline_name = fetchone(query, (session['user']))

	#query for total tickets sold in last year
	query = "SELECT COUNT(ticket_id) AS total_tickets"\
			" FROM Ticket"\
			" WHERE airline_name = %s AND purchase_timestamp >= DATEADD(year, -1, CURRENT_TIMESTAMP())"
	total_tickets = fetchone(query, (airline_name))
	#NOTE if last year does not mean last 365 days, solely Last Year, have to compare YEAR(purchase_timestamp) >= YEAR(DATEADD(year, -1, CURRENT_TIMESTAMP()))

	#query for total tickets sold in each month in the last year
	query = "SELECT MONTH(purchase_timestamp) AS month, COUNT(ticket_id) AS total_tickets"\
			" FROM Ticket"\
			" WHERE airline_name = %s AND purchase_timestamp >= DATEADD(year, -1, CURRENT_TIMESTAMP())"\
			" GROUP BY MONTH(purchase_timestamp)"
	chart_data = fetchall(query, (airline_name))

	return render_template("airlinestaff/view_reports.html", total_tickets = total_tickets, chart_data = chart_data) #NOTE change name if needed

@airlinestaff_bp.route('/viewReportLastMonth')
def viewReportLastMonth():
	# check if logged in
	if not (session['user']):
		return render_template("airlinestaff/view_reports.html", error = "Not logged in")

	#grabs airline_name information from session and query data
	query = "SELECT airline_name FROM AirlineStaff WHERE username = %s"
	airline_name = fetchone(query, (session['user']))

	#query for total tickets sold in last month
	query = "SELECT COUNT(ticket_id) AS total_tickets"\
			" FROM Ticket"\
			" WHERE airline_name = %s AND purchase_timestamp >= DATEADD(month, -1, CURRENT_TIMESTAMP())"
	total_tickets = fetchone(query, (airline_name))

	#query for total tickets sold in each month in the last month
	query = "SELECT MONTH(purchase_timestamp) AS month, COUNT(ticket_id) AS total_tickets"\
			" FROM Ticket"\
			" WHERE airline_name = %s AND purchase_timestamp >= DATEADD(month, -1, CURRENT_TIMESTAMP())"\
			" GROUP BY MONTH(purchase_timestamp)"
	chart_data = fetchall(query, (airline_name))

	return render_template("airlinestaff/view_reports.html", total_tickets = total_tickets, chart_data = chart_data) #NOTE change name if needed
	
@airlinestaff_bp.route('/viewReportReq', methods=['GET', 'POST'])
def viewReportReq():
	# check if logged in
	if not (session['user']):
		return render_template("airlinestaff/view_reports.html", error = "Not logged in")

	#grabs airline_name information from session and query data
	query = "SELECT airline_name FROM AirlineStaff WHERE username = %s"
	airline_name = fetchone(query, (session['user']))
	
	#grabs information from the form
	start_date = request.form['start_date']
	end_date = request.form['end_date']

	#query for total tickets sold in between the time range given
	query = "SELECT COUNT(ticket_id) AS total_tickets"\
			" FROM Ticket"\
			" WHERE customer_email = %s AND"\
			" DATE(purchase_timestamp) BETWEEN %s AND %s"
	total_tickets = fetchone(query, (airline_name, start_date, end_date))

	#query for tickets sold in each month in time range given
	query = "SELECT MONTH(purchase_timestamp) AS month, COUNT(ticket_id) AS total_tickets"\
			" FROM Ticket"\
			" WHERE customer_email = %s AND"\
			" DATE(purchase_timestamp) BETWEEN %s AND %s"\
			" GROUP BY MONTH(purchase_timestamp)"
	chart_data = fetchall(query, (airline_name, start_date, end_date))

	return render_template("airlinestaff/view_reports.html", total_tickets = total_tickets, chart_data = chart_data) #NOTE change name if needed



#Define route for view revenue
@airlinestaff_bp.route('/viewRevenue')
def viewRevenue():
	# check if logged in
	if not (session['user']):
		return render_template("airlinestaff/view_reports.html", error = "Not logged in")

	#grabs airline_name information from session and query data
	query = "SELECT airline_name FROM AirlineStaff WHERE username = %s"
	airline_name = fetchone(query, (session['user']))

	#query for total tickets sold in last year
	query = "SELECT SUM(sold_price)"\
			" FROM Ticket"\
			" WHERE airline_name = %s AND purchase_timestamp >= DATEADD(year, -1, CURRENT_TIMESTAMP())"
	total_tickets = fetchone(query, (airline_name))

	#query for total tickets sold in last month
	query = "SELECT SUM(sold_price)"\
			" FROM Ticket"\
			" WHERE airline_name = %s AND purchase_timestamp >= DATEADD(month, -1, CURRENT_TIMESTAMP())"
	total_tickets = fetchone(query, (airline_name))

	return render_template("airlinestaff/view_revenue.html", last_month_revenue = last_month_revenue, last_year_revenue = last_year_revenue)


#Define route for logout
@airlinestaff_bp.route('/logout')
def logout():
	session.pop('user')
	return redirect(url_for('general_bp.staffLogin'))