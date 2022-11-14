#Import Flask Library
from flask import Blueprint, render_template, session, request, url_for, redirect
from app_global import *

general_bp = Blueprint('general_bp', __name__, template_folder='templates')

#Define route for index
@general_bp.route('/')
def index():
	return render_template('index.html')

#Define route for login
@general_bp.route('/login')
def login():
	return render_template('login.html')

#Define route for register
@general_bp.route('/register')
def register():
	return render_template('register.html')


# --- CUSTOMER LOGIN AND REGISTER ---
#Define route for customer login
@general_bp.route('/customerLoginAuth', methods=['GET', 'POST'])
def customerLoginAuth():
	#grabs information from the forms
	email = request.form['email']
	password = md5(request.form['password'])

	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT * FROM Customer WHERE email = %s and password = %s'
	cursor.execute(query, (email, password))
	#stores the results in a variable
	data = cursor.fetchone() #use fetchall() if you are expecting more than 1 data row

	cursor.close()

	error = None
	if(data):
		#creates a session for the the user
		#session is a built in
		session['user'] = email
		return redirect(url_for('customer_bp.home'))
	else:
		#returns an error message to the html page
		error = 'Invalid login or email'
		return render_template('login.html', error=error)

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

	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT email FROM Customer WHERE email = %s'
	cursor.execute(query, (email))
	#stores the results in a variable
	data = cursor.fetchone() #use fetchall() if you are expecting more than 1 data row

	error = None
	if(data):
		#If the previous query returns data, then user exists
		error = "This user already exists"
		return render_template('register.html', error = error)
	else:
		ins_data = (email, name, password, building_number, street, city, state, phone_number, passport_number, passport_expiration, passport_country, date_of_birth)
		ins = 'INSERT INTO Customer VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
		cursor.execute(ins, ins_data)
		conn.commit()
		cursor.close()

		return render_template('index.html')


# --- AIRLINE STAFF LOGIN AND REGISTER ---
#Define route for airline staff login
@general_bp.route('/airlineStaffLoginAuth', methods=['GET', 'POST'])
def airlineStaffLoginAuth():
	#grabs information from the forms
	username = request.form['username']
	password = md5(request.form['password'])

	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT * FROM AirlineStaff WHERE username = %s and password = %s'
	cursor.execute(query, (username, password))
	#stores the results in a variable
	data = cursor.fetchone() #use fetchall() if you are expecting more than 1 data row

	cursor.close()

	error = None
	if(data):
		#creates a session for the the user
		#session is a built in
		session['user'] = username
		return redirect(url_for('airlinestaff_bp.home'))
	else:
		#returns an error message to the html page
		error = 'Invalid login or username'
		return render_template('login.html', error=error)

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

	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT username FROM AirlineStaff WHERE username = %s'
	cursor.execute(query, (username))
	#stores the results in a variable
	data = cursor.fetchone() #use fetchall() if you are expecting more than 1 data row

	error = None
	if(data):
		#If the previous query returns data, then user exists
		error = "This user already exists"
		return render_template('register.html', error = error)
	else:
		ins_data = (username, password, firstname, lastname, date_of_birth, airline_name)
		ins = 'INSERT INTO AirlineStaff VALUES(%s, %s, %s, %s, %s, %s)'
		cursor.execute(ins, ins_data)
		conn.commit()
		cursor.close()

		return render_template('index.html')


# --- SEARCH FUTURE FLIGHTS ---
@general_bp.route('/searchFlights', methods=['GET', 'POST'])
def searchFlights():
	#grabs information from the forms
	departure_info = request.form['departure_info']
	destination_info = request.form['destination_info']

	departure_date = request.form['departure_date']
	return_date = request.form['return_date']

	formatted_departure_info = '%' + departure_info +'%'
	formatted_destination_info = '%' + destination_info + '%'

	#cursor used to send queries
	cursor = conn.cursor()

	#executes query
	query = "SELECT *"\
			" FROM Flight AS F, Airport AS D, Airport AS A"\
			" WHERE F.departure_airport = D.name AND F.arrival_airport = A.name AND"\
				" (UPPER(F.departure_airport) LIKE UPPER(%s) OR UPPER(D.city) LIKE UPPER(%s)) AND"\
				" (UPPER(F.arrival_airport) LIKE UPPER(%s) OR UPPER(A.city) LIKE UPPER(%s)) AND"\
				" DATE(F.departure_timestamp) = %s"
	cursor.execute(query, (formatted_departure_info, formatted_departure_info, formatted_destination_info, formatted_destination_info, departure_date))
	#stores the results in a variable
	departure_flights_data = cursor.fetchall()
	arrival_flights_data = []

	# for round trips
	if (return_date):
		#executes query
		query = "SELECT *"\
				" FROM Flight AS F, Airport AS D, Airport AS A"\
				" WHERE F.departure_airport = D.name AND F.arrival_airport = A.name AND"\
					" (UPPER(F.departure_airport) LIKE UPPER(%s) OR UPPER(D.city) LIKE UPPER(%s)) AND"\
					" (UPPER(F.arrival_airport) LIKE UPPER(%s) OR UPPER(A.city) LIKE UPPER(%s)) AND"\
					" DATE(F.departure_timestamp) = %s"
		cursor.execute(query, (formatted_destination_info, formatted_destination_info, formatted_departure_airport, formatted_departure_airport, return_date))
		#stores the results in a variable
		arrival_flights_data = cursor.fetchall()

	cursor.close()
	
	return render_template("search_flights.html", departure_flights = departure_flights_data, arrival_flights = arrival_flights_data)