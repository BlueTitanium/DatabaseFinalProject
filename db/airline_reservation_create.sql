-- Evie Cundy, Taneim Miah, Anna Zheng

CREATE TABLE Airport (
	name varchar(5),
	city varchar(20) NOT NULL,
	country varchar(20) NOT NULL,
	type varchar(13) CHECK (type IN ('Domestic', 'International', 'Both')),
	PRIMARY KEY (name)
);

CREATE TABLE Airline (
	name varchar(20),
	PRIMARY KEY(name)
);

CREATE TABLE Airplane (
	id varchar(10),
	name varchar(20),
	num_seats int CHECK (num_seats >= 0),
	manufacturer varchar(20),
	age int CHECK (age >= 0),
	PRIMARY KEY (id, name),
	FOREIGN KEY (name) REFERENCES Airline(name)
		ON DELETE CASCADE
);

CREATE TABLE AirlineStaff (
	username varchar(20),
   	password varchar(40) NOT NULL,
	firstname varchar(20) NOT NULL,
	lastname varchar(20) NOT NULL,
	date_of_birth date NOT NULL,
	airline_name varchar(20),
	PRIMARY KEY (username),
	FOREIGN KEY (airline_name) REFERENCES Airline(name)
		ON DELETE CASCADE
);

CREATE TABLE AirlineStaffPhoneNumbers (
	username varchar(20),
	phone_number varchar(15),
	PRIMARY KEY (username, phone_number),
	FOREIGN KEY (username) REFERENCES AirlineStaff(username)
		ON DELETE CASCADE
);

CREATE TABLE AirlineStaffEmails (
	username varchar(20),
   	email varchar(20),
	PRIMARY KEY (username, email),
	FOREIGN KEY (username) REFERENCES AirlineStaff(username)
		ON DELETE CASCADE
);

CREATE TABLE Customer (
	email varchar(20),
	name varchar(20) NOT NULL,
	password varchar(40) NOT NULL,
   	building_number varchar(20) NOT NULL,
	street varchar(20) NOT NULL,
	city varchar(20) NOT NULL,
	state varchar(20) NOT NULL,
	phone_number varchar(15),
	passport_number char(9) NOT NULL,
	passport_expiration date NOT NULL,
   	passport_country varchar(20) NOT NULL,
	date_of_birth date NOT NULL,
	PRIMARY KEY (email)
);

CREATE TABLE Flight (
	airline_name varchar(20),
	flight_num varchar(6),
	departure_timestamp timestamp,
	arrival_timestamp timestamp NULL,
	base_price numeric(6, 2) CHECK (base_price >= 0),
	status varchar(8) CHECK (status IN ('delayed', 'canceled', 'on-time')),
	departure_airport varchar(5),
	arrival_airport varchar(5),
	airplane_id varchar(10),
	PRIMARY KEY (airline_name, flight_num, departure_timestamp),
	FOREIGN KEY (airline_name) REFERENCES Airline(name)
		ON DELETE CASCADE,
	FOREIGN KEY (departure_airport) REFERENCES Airport(name)
		ON DELETE SET NULL,
	FOREIGN KEY (arrival_airport) REFERENCES Airport(name)
		ON DELETE SET NULL,
	FOREIGN KEY (airplane_id) REFERENCES Airplane(id)
		ON DELETE SET NULL
);

CREATE TABLE Ticket (
	ticket_id varchar(10),
	sold_price numeric(6, 2) CHECK (sold_price >= 0),
	card_type varchar(6) CHECK (card_type IN ('Debit', 'Credit')),
	name_on_card varchar(20),
	card_number varchar(16),
	expiration_date date,
	purchase_timestamp timestamp,
	customer_email varchar(20),
	airline_name varchar(20),
	flight_num varchar(6) NOT NULL,
	departure_timestamp timestamp NULL,
	PRIMARY KEY (ticket_id),
	FOREIGN KEY (customer_email) REFERENCES Customer(email)
		ON DELETE CASCADE,
	FOREIGN KEY (airline_name, flight_num, departure_timestamp) REFERENCES Flight(airline_name, flight_num, departure_timestamp)
);

CREATE TABLE Rate (
	email varchar(20),
	airline_name varchar(20),
	flight_num varchar(6),
	departure_timestamp timestamp,
	rating int CHECK (rating IN (1, 2, 3, 4, 5)),
	comment varchar(255),
	PRIMARY KEY (email, airline_name, flight_num, departure_timestamp),
	FOREIGN KEY (email) REFERENCES Customer(email)
		ON DELETE CASCADE,
	FOREIGN KEY (airline_name, flight_num, departure_timestamp) REFERENCES Flight(airline_name, flight_num, departure_timestamp)
		ON DELETE CASCADE
);