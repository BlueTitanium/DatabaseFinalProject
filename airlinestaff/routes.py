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
	parameters = (staff_airline_name['airline_name'],)


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

#Define route to view all customers for a particular flight (Airline Staff 1)
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



#Define route for Change Flight Status Page (Airline Staff 3)
@airlinestaff_bp.route('/changeFlightStatusPage')
def changeFlightStatusPage():
	message = request.args.get('message', None)
	print(message)
	return render_template("airlinestaff/changeFlightStatus.html", message = message)

#Define route for Change Flight Status Requests use case (Airline Staff 3)
@airlinestaff_bp.route('/changeFlightStatus', methods=['GET', 'POST'])
def changeFlightStatus():
	username = session['user']
	
	#check authorization
	query = "SELECT airline_name"\
			" FROM AirlineStaff"\
			" WHERE username = %s"
	data = fetchone(query, (username))
		
	if not data:
		error = "ERROR: Not authorized to change a flight status"
		return redirect(url_for('.changeFlightStatusPage', message = error))


	#grabs information from the form
	airline_name = data['airline_name']
	flight_num = request.form['flight_num']
	departure_timestamp = request.form['departure_timestamp']
	status = request.form['status']

	# convert timestamps into uniform SQL format
	departure_timestamp = datetime.strptime(departure_timestamp, "%Y-%m-%dT%H:%M").strftime("%Y-%m-%d %H:%M:%S")


	# check flight exists
	query = "SELECT *"\
			" FROM Flight"\
			" WHERE airline_name = %s AND flight_num = %s AND departure_timestamp = %s"
	data = fetchone(query, (airline_name, flight_num, departure_timestamp))
	if not data:
		error = "ERROR: Flight does not exist"
		return redirect(url_for('.changeFlightStatusPage', message = error))

	# check flight has not departed
	if (datetime.strptime(departure_timestamp, "%Y-%m-%d %H:%M:%S") <= datetime.now()):
		error = "ERROR: Flight as already departed"
		return redirect(url_for('.changeFlightStatusPage', message = error))

	# check flight is not canceled
	if (data['status'] == 'canceled'):
		error = "ERROR: Cannot change status of a canceled flight"
		return redirect(url_for('.changeFlightStatusPage', message = error))


	# update status
	query = "UPDATE Flight"\
			" SET status = %s"\
			" WHERE airline_name = %s AND flight_num = %s AND departure_timestamp = %s"
	modify(query, (status, airline_name, flight_num, departure_timestamp))

	#return redirect
	return redirect(url_for('.changeFlightStatusPage', message = "Flight status successfully changed"))



#Define route for Add Airplane Page (Airline Staff 4) 
@airlinestaff_bp.route('/addAirplanePage')
def addAirplanePage():
	error = request.args.get('error', None)

	return render_template("airlinestaff/addAirplane.html", error = error)

#Define route for Add Airplane Page use case (Airline Staff 4) 
@airlinestaff_bp.route('/addAirplane', methods=['GET', 'POST'])
def addAirplane():
	query = "SELECT airline_name FROM AirlineStaff WHERE username = %s"
	airline_name = fetchone(query, (session['user']))

	#check authorization
	if not airline_name:
		error = "Not authorized to add an airplane"
		return redirect(url_for('.addAirplanePage', error = error))

	#grabs information from the form
	id = request.form['airplane_id']
	num_seats = request.form['num_seats']
	manufacturer = request.form['manufacturer']
	age = request.form['age']

	# check if airplane already exists
	query = "SELECT * FROM Airplane WHERE name = %s AND id = %s"
	if (fetchone(query, (airline_name['airline_name'], id))):
		error = "This airplane already exists"
		return redirect(url_for('.addAirplanePage', error = error))

	query = "INSERT INTO Airplane VALUES (%s, %s, %s, %s, %s)"
	modify(query, (id, airline_name['airline_name'], num_seats, manufacturer, age))
	
	# go to confirmation page (show all airplanes owned by staff company)
	return redirect(url_for('.addAirplaneConfirmation'))

#Define route for Add Airplane Confirmation Page use case (Airline Staff 4)
@airlinestaff_bp.route('/addAirplaneConfirmation')
def addAirplaneConfirmation():
	query = "SELECT airline_name FROM AirlineStaff WHERE username = %s"
	airline_name = fetchone(query, (session['user']))

	#check authorization
	if not airline_name:
		error = "Not logged in"
		return render_template("airlinestaff/addAirplaneConfirmation.html", error = error)

	query = "SELECT * FROM Airplane WHERE name = %s"
	airplanes = fetchall(query, (airline_name['airline_name']))

	return render_template("airlinestaff/addAirplaneConfirmation.html", airline = airline_name['airline_name'], airplanes = airplanes)



#Define route for Add Airport Page (Airline Staff 5)
@airlinestaff_bp.route('/addAirportPage')
def addAirportPage():
	message = request.args.get('message', None)
	return render_template('airlinestaff/addNewAirport.html', message = message)

#Define route for Add Airport use case (Airline Staff 5)
@airlinestaff_bp.route('/addAirport', methods=['GET', 'POST'])
def addAirport():
	#check authorization
	query = "SELECT *"\
			" FROM AirlineStaff"\
			" WHERE username = %s"
	data = fetchone(query, (session['user']))
		
	if not data:
		error = "ERROR: Not authorized to create a flight"
		return redirect(url_for('.addAirportPage', message = error))

	#grabs information from the form
	name = request.form['name']
	city = request.form['city']
	country = request.form['country']
	airport_type = request.form['airport_type']

	# check airport is unique
	query = "SELECT * FROM Airport WHERE name = %s"
	if (fetchone(query, (name))):
		error = "ERROR: Airport already exists"
		return redirect(url_for('.addAirportPage', message = error))

	# execute query
	query = "INSERT INTO Airport VALUES (%s, %s, %s, %s)"
	modify(query, (name, city, country, airport_type))

	#return redirect
	return redirect(url_for('.addAirportPage', message = "Airport added successfully"))



#Define route for View Flight Average Ratings (Airline Staff 6)
@airlinestaff_bp.route('/viewFlightRatingsPage')
def viewFlightRatingsPage():	
	#grabs airline_name information from session and query data
	query = "SELECT airline_name FROM AirlineStaff WHERE username = %s"
	airline_name = fetchone(query, (session['user']))

	# Get average rating
	query = "SELECT flight_num, departure_timestamp, AVG(rating) AS avg_rating"\
			" FROM Flight NATURAL LEFT OUTER JOIN Rate"\
			" WHERE airline_name = %s"\
			" GROUP BY flight_num, departure_timestamp"
	flights_avg_rating = fetchall(query, (airline_name["airline_name"]))

	return render_template("airlinestaff/viewFlightRatings.html", 
		airline = airline_name['airline_name'], flights_avg_rating = flights_avg_rating)

#Define route for View Flight Ratings (Specific Flight) (Airline Staff 6)
@airlinestaff_bp.route('/viewFlightRating')
def viewFlightRating():
	flight_num = request.args['flight_num']
	departure_timestamp = request.args['departure_timestamp']

	#grabs airline_name information from session and query data
	query = "SELECT airline_name FROM AirlineStaff WHERE username = %s"
	airline_name = fetchone(query, (session['user']))

	# Get all ratings and comments
	query = "SELECT *"\
			" FROM Rate"\
			" WHERE airline_name = %s AND flight_num = %s AND departure_timestamp = %s"
	ratings = fetchall(query, (airline_name['airline_name'], flight_num, departure_timestamp))

	# return render template
	return render_template('airlinestaff/viewSpecificFlightRating.html', 
		airline = airline_name['airline_name'], flight_num = flight_num, departure_timestamp = departure_timestamp,
		ratings = ratings)



#Define route for View Frequent Customers (Airline Staff 7)
@airlinestaff_bp.route('/viewFreqCustomers')
def viewFreqCustomer():
	#grabs airline_name information from session and query data
	query = "SELECT airline_name FROM AirlineStaff WHERE username = %s"
	airline_name = fetchone(query, (session['user']))

	# Get most frequent customer within the last year
	query = "WITH customer_ticket_count(email, ticket_count) AS ("\
				" SELECT customer_email, COUNT(ticket_id)"\
				" FROM Ticket"\
				" WHERE airline_name = %s AND DATE(purchase_timestamp) >= DATE((CURRENT_TIMESTAMP() - INTERVAL 1 YEAR))"\
				" GROUP BY customer_email"\
			")"\
			" SELECT email"\
			" FROM customer_ticket_count"\
			" WHERE ticket_count = ("\
				" SELECT MAX(ticket_count)"\
				" FROM customer_ticket_count"\
			")"
	most_freq_customer = fetchone(query, (airline_name['airline_name']))

	#return
	return render_template("airlinestaff/viewFrequentCustomers.html", most_freq_customer = most_freq_customer['email'])

#Define route for View Particular Customer (part 2 of view frequent customer use case - Airline Staff 7)
@airlinestaff_bp.route('/viewCustomerFlights', methods = ['GET', 'POST'])
def viewCustomerFlights():
	# Get customer email
	customer_email = request.form['email']

	#grabs airline_name information from session and query data
	query = "SELECT airline_name FROM AirlineStaff WHERE username = %s"
	airline_name = fetchone(query, (session['user']))

	# see a list of all flights a particular Customer has taken only on that particular airline
	query = "SELECT Flight.*, ticket_id, sold_price"\
			" FROM Flight NATURAL JOIN Ticket"\
			" WHERE airline_name = %s AND customer_email = %s AND departure_timestamp < CURRENT_TIMESTAMP()"
	data = fetchall(query, (airline_name['airline_name'], customer_email))

	#return render template
	return render_template("airlinestaff/viewCustomerFlights.html", 
		airline = airline_name['airline_name'], customer_email = customer_email, flights = data)



#Define route for total amounts of ticket sold (Airline Staff 8)
@airlinestaff_bp.route('/viewReportLastYear')
def viewReportLastYear():
	#grabs airline_name information from session and query data
	query = "SELECT airline_name FROM AirlineStaff WHERE username = %s"
	airline_name = fetchone(query, (session['user']))

	#query for total tickets sold in last year
	query = "SELECT COUNT(ticket_id) AS total_tickets"\
			" FROM Ticket"\
			" WHERE airline_name = %s AND DATE(purchase_timestamp) >= DATE((CURRENT_TIMESTAMP() - INTERVAL 1 YEAR))"
	total_tickets = fetchone(query, (airline_name['airline_name']))

	#query for total tickets sold in each month in the last year
	query = "SELECT YEAR(purchase_timestamp) AS year, MONTH(purchase_timestamp) AS month, COUNT(ticket_id) AS total_tickets"\
			" FROM Ticket"\
			" WHERE airline_name = %s AND DATE(purchase_timestamp) >= DATE((CURRENT_TIMESTAMP() - INTERVAL 1 YEAR))"\
			" GROUP BY year, month"
	chart_data = fetchall(query, (airline_name['airline_name']))

	return render_template("airlinestaff/viewReports.html", 
		total_tickets_header = "in the last year (Default)", total_tickets = total_tickets['total_tickets'], 
		chart_data_header = "In the Last Year (Default)", chart_data = chart_data)

@airlinestaff_bp.route('/viewReportLastMonth')
def viewReportLastMonth():
	#grabs airline_name information from session and query data
	query = "SELECT airline_name FROM AirlineStaff WHERE username = %s"
	airline_name = fetchone(query, (session['user']))

	#query for total tickets sold in last month
	query = "SELECT COUNT(ticket_id) AS total_tickets"\
			" FROM Ticket"\
			" WHERE airline_name = %s AND DATE(purchase_timestamp) >= DATE((CURRENT_TIMESTAMP() - INTERVAL 1 MONTH))"
	total_tickets = fetchone(query, (airline_name['airline_name']))

	#query for total tickets sold in each month in the last month
	query = "SELECT YEAR(purchase_timestamp) AS year, MONTH(purchase_timestamp) AS month, COUNT(ticket_id) AS total_tickets"\
			" FROM Ticket"\
			" WHERE airline_name = %s AND DATE(purchase_timestamp) >= DATE((CURRENT_TIMESTAMP() - INTERVAL 1 MONTH))"\
			" GROUP BY year, month"
	chart_data = fetchall(query, (airline_name['airline_name']))

	return render_template("airlinestaff/viewReports.html", 
		total_tickets_header = "in the last month", total_tickets = total_tickets['total_tickets'], 
		chart_data_header = "In the Last Month", chart_data = chart_data)
	
@airlinestaff_bp.route('/viewReportReq', methods=['GET', 'POST'])
def viewReportReq():
	#grabs airline_name information from session and query data
	query = "SELECT airline_name FROM AirlineStaff WHERE username = %s"
	airline_name = fetchone(query, (session['user']))
	
	#grabs information from the form
	start_date = request.form['start_date']
	end_date = request.form['end_date']

	#check start date and end date is valid
	if (datetime.strptime(start_date, "%Y-%m-%d") > datetime.strptime(end_date, "%Y-%m-%d")):
		error = "Start date cannot be after end date"
		return render_template("airlinestaff/viewReports.html", total_tickets = None, error = error)

	#query for total tickets sold in between the time range given
	query = "SELECT COUNT(ticket_id) AS total_tickets"\
			" FROM Ticket"\
			" WHERE airline_name = %s AND"\
				" DATE(purchase_timestamp) BETWEEN %s AND %s"
	total_tickets = fetchone(query, (airline_name['airline_name'], start_date, end_date))

	#query for tickets sold in each month in time range given
	query = "SELECT YEAR(purchase_timestamp) AS year, MONTH(purchase_timestamp) AS month, COUNT(ticket_id) AS total_tickets"\
			" FROM Ticket"\
			" WHERE airline_name = %s AND"\
				" DATE(purchase_timestamp) BETWEEN %s AND %s"\
			" GROUP BY year, month"
	chart_data = fetchall(query, (airline_name['airline_name'], start_date, end_date))

	# set headers
	total_tickets_header = "from " + start_date + " to " + end_date 
	chart_data_header = "From " + start_date + " To " + end_date 

	return render_template("airlinestaff/viewReports.html", 
		total_tickets_header = total_tickets_header, total_tickets = total_tickets['total_tickets'], 
		chart_data_header = chart_data_header, chart_data = chart_data)



#Define route for view revenue (Airline Staff 9)
@airlinestaff_bp.route('/viewRevenue')
def viewRevenue():
	#grabs airline_name information from session and query data
	query = "SELECT airline_name FROM AirlineStaff WHERE username = %s"
	airline_name = fetchone(query, (session['user']))

	#query for total tickets sold in last year
	query = "SELECT SUM(sold_price) AS last_year_revenue"\
			" FROM Ticket"\
			" WHERE airline_name = %s AND DATE(purchase_timestamp) >= DATE(CURRENT_TIMESTAMP() - INTERVAL 1 YEAR)"
	last_year_revenue = fetchone(query, (airline_name['airline_name']))

	#query for total tickets sold in last month
	query = "SELECT SUM(sold_price) AS last_month_revenue"\
			" FROM Ticket"\
			" WHERE airline_name = %s AND DATE(purchase_timestamp) >= DATE(CURRENT_TIMESTAMP() - INTERVAL 1 MONTH)"
	last_month_revenue = fetchone(query, (airline_name['airline_name']))

	return render_template("airlinestaff/viewEarnedRevenue.html", airline = airline_name['airline_name'],
		last_month_revenue = last_month_revenue['last_month_revenue'], last_year_revenue = last_year_revenue['last_year_revenue'])


#Define route for logout
@airlinestaff_bp.route('/logout')
def logout():
	session.pop('user')
	return redirect(url_for('general_bp.staffLogin'))