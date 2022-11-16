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

#Define route for View Future Flights Search use case (AirlineStaff 1)
@airlinestaff_bp.route('/viewFlightsSearch', methods=['GET', 'POST'])
def viewFlightsSearch():
    start_date = request.form['start_date']
    end_date = request.form['end_date']

    query = "SELECT *"\
            " FROM Flight"\
            " WHERE airline_name = ("\
                " SELECT airline_name FROM AirlineStaff WHERE username = %s"\
            ")"
    
    if ((start_date or end_date) and not(start_date and end_date)):
        error = "Start date and end date both must be filled out if date is entered for either"
        render_template(".html", error = error)

    if (start_date and end_date):
        query += " AND DATE(departure_timestamp) BETWEEN %s AND %s"

    # departure airport/city

    # arrival airport/city

    pass


#Define route for Create New Flights (use case 2)
@airlinestaff_bp.route('/createFlight', methods=['GET', 'POST'])
def createFlight():
    #TODO check authorization

    #grabs information from the form
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
    if (not departure_airport):
        # check value is written -- this should be checked in HTML but also checked here just in case
        error = "Departure airport cannot be empty"
        return render_template(".html",) #TODO change html name

    #check that airplane id exists

    query = "INSERT INTO Flight VALUES()"


#XXX need to discuss how to get flight info
#Define route for Change Flight Status use case (Airline Staff 3)
@airlinestaff_bp.route('/changeFlight', methods=['GET', 'POST'])
def changeFlight():
    #TODO check authorization

    #grabs information from the form
    status = request.form['status']

    query = "UPDATE Flight"\
            " SET status = %s"\
            " WHERE airline_name = %s AND flight_num = %s AND departure_timestamp = %s"

    #TODO return


#Define route for Add Airplane use case (Airline Staff 4) 
#TODO
@airlinestaff_bp.route('/addAirplane', methods=['GET', 'POST'])
def addAirplane():
    #TODO check authorization

    id = request.form['id']
    num_seats = request.form['num_seats']
    manufacturer = request.form['manufacturer']
    age = request.form['age']

    query = "SELECT airline_name FROM AirlineStaff WHERE username = %s"
    airline_name = fetchone(query, (session['user']))
    #TODO return
    pass


#Define route for Add Airport
#TODO
@airlinestaff_bp.route('/addAirport', methods=['GET', 'POST'])
def addAirport():
    #TODO check authorization

    #grabs information from the form
    name = request.form['name']
    city = request.form['city']
    country = request.form['country']
    airport_type = request.form['airport_type']

    query = "INSERT INTO Airport VALUES (%s, %s, %s, %s)"
    #TODO execute query

    #TODO return
    pass


#Define route for View Flight Ratings
#TODO
#XXX need to get airline_name, flight_num, departure_timestamp somehow -- either by GET parameters or form request
@airlinestaff_bp.route('/viewFlightRatings', methods=['GET', 'POST'])
def viewFlightRatings():
    # check if logged in
    if not (session['user']):
        return render_template(".html", error = "Not logged in") #TODO change name
        
    #grabs airline_name information from session and query data
    query = "SELECT airline_name FROM AirlineStaff WHERE username = %s"
    airline_name = fetchone(query, (session['user']))

    # Get average rating
    query = "SELECT AVG(rating)"\
            " FROM Rate"\
            " WHERE airline_name = %s AND flight_num = %s AND departure_timestamp = %s"

    # Get all ratings and comments
    query = "SELECT *"\
            " FROM Rate"\
            " WHERE airline_name = %s AND flight_num = %s AND departure_timestamp = %s"

    #TODO return
    pass


#Define route for View Frequent Customers
#TODO
@airlinestaff_bp.route('/viewFreqCustomers')
def viewFreqCustomer():
    # check if logged in
    if not (session['user']):
        return render_template(".html", error = "Not logged in") #TODO change name

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


    # See a list of all flights a particular Customer has taken only on that particular airline
    #XXX: maybe allow staff to enter or select a customer (in this case, would need a new route)
    query = "SELECT *"\
            " FROM Flight"\
            " WHERE (airline_name, flight_num, departure_timestamp) IN ("\
                "SELECT airline_name, flight_num, departure_timestamp"\
                " FROM Ticket"\
                " WHERE customer_email = %s"\
            ")"
    # if we want to display ticket information along with the information in the flight table, have to use new query (see below)
    query = "SELECT *"\
            " FROM Flight NATURAL JOIN Ticket"\
            " WHERE customer_email = %s"

    #TODO return
    pass


#Define route for total amounts of ticket sold
@airlinestaff_bp.route('/viewReports')
def viewReports():
    return render_template("view_reports.html")

@airlinestaff_bp.route('/viewReportLastYear')
def viewReportLastYear():
    # check if logged in
    if not (session['user']):
        return render_template("view_reports.html", error = "Not logged in")

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

	return render_template("view_reports.html", total_tickets = total_tickets, chart_data = chart_data) #NOTE change name if needed

@airlinestaff_bp.route('/viewReportLastMonth')
def viewReportLastMonth():
    # check if logged in
    if not (session['user']):
        return render_template("view_reports.html", error = "Not logged in")

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

	return render_template("view_reports.html", total_tickets = total_tickets, chart_data = chart_data) #NOTE change name if needed
    
@airlinestaff_bp.route('/viewReportReq', methods=['GET', 'POST'])
def viewReportReq():
    # check if logged in
    if not (session['user']):
        return render_template("view_reports.html", error = "Not logged in")

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
	total_tickets = fetchone(query, (airline_name))

	#query for tickets sold in each month in time range given
	query = "SELECT MONTH(purchase_timestamp) AS month, COUNT(ticket_id) AS total_tickets"\
			" FROM Ticket"\
			" WHERE customer_email = %s AND"\
			" DATE(purchase_timestamp) BETWEEN %s AND %s"\
			" GROUP BY MONTH(purchase_timestamp)"
	chart_data = fetchall(query, (airline_name))

	return render_template("view_reports.html", total_tickets = total_tickets, chart_data = chart_data) #NOTE change name if needed



#Define route for view revenue
@airlinestaff_bp.route('/viewRevenue')
def viewRevenue():
    # check if logged in
    if not (session['user']):
        return render_template("view_reports.html", error = "Not logged in")

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

    return render_template("view_revenue.html", last_month_revenue = last_month_revenue, last_year_revenue = last_year_revenue)


#Define route for logout
@airlinestaff_bp.route('/logout')
def logout():
	session.pop('user')
	return redirect('/')