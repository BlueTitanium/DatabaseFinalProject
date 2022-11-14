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
	query = 'SELECT * FROM customer WHERE email = %s and password = %s'
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
	query = 'SELECT email FROM customer WHERE email = %s'
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
		ins = 'INSERT INTO customer VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
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
	query = 'SELECT * FROM airlinestaff WHERE username = %s and password = %s'
	cursor.execute(query, (username, password))
	#stores the results in a variable
	data = cursor.fetchone() #use fetchall() if you are expecting more than 1 data row

	cursor.close()

	error = None
	if(data):
		#creates a session for the the user
		#session is a built in
		session['user'] = username
		return redirect(url_for('airlinestaff.home'))
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
	query = 'SELECT username FROM airlinestaff WHERE username = %s'
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
		ins = 'INSERT INTO airlinestaff VALUES(%s, %s, %s, %s, %s, %s)'
		cursor.execute(ins, ins_data)
		conn.commit()
		cursor.close()

		return render_template('index.html')