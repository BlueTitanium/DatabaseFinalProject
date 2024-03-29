#Import Flask Library
from flask import Blueprint, render_template, session, request, url_for, redirect
from app_global import *
from app_public_views import *

general_bp = Blueprint('general_bp', __name__, template_folder='templates')

#Define route for index
@general_bp.route('/')
def index():
	return render_template('general/index.html')

#Define route for login
@general_bp.route('/login')
def login():
	return render_template('general/login.html')

@general_bp.route('/customerLogin')
def customerLogin():
	try:
		#check if logged in
		if (session['customer']):
			return redirect(url_for('customer_bp.home'))
		
		#otherwise, display login page
		return render_template('general/customerLogin.html')

	except KeyError:
		#otherwise, display login page
		return render_template('general/customerLogin.html')

@general_bp.route('/staffLogin')
def staffLogin():
	try:
		#check if logged in
		if (session['user']):
			return redirect(url_for('airlinestaff_bp.home'))
	
		#otherwise, display login page
		return render_template('general/staffLogin.html')
	except KeyError:
		#otherwise, display login page
		return render_template('general/staffLogin.html')

#Define route for register
@general_bp.route('/register')
def register():
	return render_template('general/register.html')

@general_bp.route('/registerCustomer')
def registerCustomer():
	return render_template('general/registerCustomer.html')

@general_bp.route('/registerAirlineStaff')
def registerAirlineStaff():
	query = "SELECT name FROM Airline"
	data = fetchall(query, ())
	return render_template('general/registerAirlineStaff.html', airline_names = data)


# --- CUSTOMER LOGIN AND REGISTER ---
#Define route for customer login
@general_bp.route('/customerLoginAuth', methods=['GET', 'POST'])
def customerLoginAuth():
	#grabs information from the forms
	email = request.form['email']
	password = md5(request.form['password'])

	#executes query and stores result in a variable
	query = 'SELECT * FROM Customer WHERE email = %s and password = %s'
	data = fetchone(query, (email, password))

	error = None
	if(data):
		#creates a session for the customer
		#session is a built in
		session['customer'] = email
		return redirect(url_for('customer_bp.home'))
	else:
		#returns an error message to the html page
		error = 'Invalid login or email'
		return render_template('general/customerLogin.html', error=error)

#Authenticates the customer register
@general_bp.route('/customerRegisterAuth', methods=['GET', 'POST'])
def customerRegisterAuth():
	#grabs information from the forms
	email = request.form['email']
	password = md5(request.form['password'])

	name = request.form['name']
	building_number = request.form['building_number']
	street = request.form['street']
	city = request.form['city']
	state = request.form['state']
	phone_number = request.form['phone_number']

	passport_number = request.form['passport_number']
	passport_expiration = request.form['passport_expiration']
	passport_country = request.form['passport_country']

	date_of_birth = request.form['date_of_birth']

	#executes query and stores result in a variable
	query = 'SELECT email FROM Customer WHERE email = %s'
	data = fetchone(query, (email))

	error = None
	if(data):
		#If the previous query returns data, then user exists
		error = "This user already exists"
		return render_template('general/registerCustomer.html', error = error)
	else:
		ins_data = (email, name, password, building_number, street, city, state, phone_number, passport_number, passport_expiration, passport_country, date_of_birth)
		ins = 'INSERT INTO Customer VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
		modify(ins, ins_data)

		return redirect(url_for('.index'))


# --- AIRLINE STAFF LOGIN AND REGISTER ---
#Define route for airline staff login
@general_bp.route('/airlineStaffLoginAuth', methods=['GET', 'POST'])
def airlineStaffLoginAuth():
	#grabs information from the forms
	username = request.form['username']
	password = md5(request.form['password'])

	#executes query and stores the results in a variable
	query = 'SELECT * FROM AirlineStaff WHERE username = %s and password = %s'
	data = fetchone(query, (username, password))

	error = None
	if(data):
		#creates a session for the the user
		#session is a built in
		session['user'] = username
		return redirect(url_for('airlinestaff_bp.home'))
	else:
		#returns an error message to the html page
		error = 'Invalid login or username'
		return render_template('general/staffLogin.html', error=error)

#Authenticates the airline staff register
@general_bp.route('/airlineStaffRegisterAuth', methods=['GET', 'POST'])
def airlineStaffRegisterAuth():
	#grabs information from the forms
	username = request.form['username']
	password = md5(request.form['password'])

	firstname = request.form['firstname']
	lastname = request.form['lastname']

	date_of_birth = request.form['date_of_birth']

	airline_name = request.form['airline_name']

	email = request.form['email']
	phone_number = request.form['phone_number']

	#executes query and stores the results in a variable
	query = 'SELECT username FROM AirlineStaff WHERE username = %s'
	data = fetchone(query, (username))

	error = None
	if(data):
		#If the previous query returns data, then user exists
		error = "This user already exists"

		#And re-render all the airline names
		query = "SELECT name FROM Airline"
		data = fetchall(query, ())

		return render_template('general/registerAirlineStaff.html', airline_names = data, error = error)
	else:
		ins = 'INSERT INTO AirlineStaff VALUES(%s, %s, %s, %s, %s, %s)'
		ins_data = (username, password, firstname, lastname, date_of_birth, airline_name)
		modify(ins, ins_data)

		ins = 'INSERT INTO AirlineStaffEmails VALUES(%s, %s)'
		ins_data = (username, email)
		modify(ins, ins_data)

		ins = 'INSERT INTO AirlineStaffPhoneNumbers VALUES(%s, %s)'
		ins_data = (username, phone_number)
		modify(ins, ins_data)

		return redirect(url_for('.index'))


# USE CASES
#Define route for Search Future Flights use case (General 1a)
'''
@general_bp.route('/searchFlights', methods=['GET', 'POST'])
def searchFlights():
	# See dispatch_request(self) in app_public_views.SearchFlightView
	pass
'''
general_bp.add_url_rule("/searchFlights", view_func = SearchFlightsView.as_view("searchFlights", "general/index.html"), methods = ['GET', 'POST'])

#Define route for View Flight Status use case (General 1b)
'''
@general_bp.route('/flightStatus', methods=['GET', 'POST'])
def flightStatus():
	# See dispatch_request(self) in app_public_views.FlightStatusView
	pass
'''
general_bp.add_url_rule("/flightStatus", view_func = FlightStatusView.as_view("flightStatus", "general/index.html"), methods = ['GET', 'POST'])