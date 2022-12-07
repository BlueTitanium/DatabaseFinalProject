-- Evie Cundy, Taneim Miah, Anna Zheng

-- a. One Airline named "Jet Blue". 
INSERT INTO Airline(name) VALUE ('Jet Blue');

-- b. At least two airports named "JFK" in NYC and "PVG" in Shanghai.
INSERT INTO Airport(name, city, country, type) VALUE ('JFK','NYC','United States', 'Both');
INSERT INTO Airport(name, city, country, type) VALUE ('PVG','Shanghai','China', 'Both');

-- c. Insert at least three customers with appropriate names and other attributes.
INSERT INTO Customer(email, name, password, building_number, street, city, state, phone_number, passport_number, passport_expiration, passport_country, date_of_birth) VALUE ('dingus@gmail.com', 'Dingus Dingusson', 'password123', '370', 'Jay St.', 'Brooklyn', 'New York', '555-555-1022', 'A23456789', '2025-09-12', 'United States',  '2001-09-01');
INSERT INTO Customer(email, name, password, building_number, street, city, state, phone_number, passport_number, passport_expiration, passport_country, date_of_birth) VALUE ('az2306@nyu.edu', 'Anna Zheng', 'annaspassword',  '370', 'Jay St.', 'Brooklyn', 'New York', '555-525-1077', 'A21476329',  '2025-07-13', 'United States', '2002-07-28');
INSERT INTO Customer(email, name, password, building_number, street, city, state, phone_number, passport_number, passport_expiration, passport_country, date_of_birth) VALUE ('tsm6910@nyu.edu', 'Taneim Miah', 'taneimspassword', '370', 'Jay St.', 'Brooklyn', 'New York', '555-827-9292', 'A36476999',  '2025-10-02', 'United States', '2002-06-28');

-- d. Insert at least three airplanes. 
INSERT INTO Airplane(name, id, num_seats, manufacturer, age) VALUE ('Jet Blue', '1234', 416, 'Boeing', 2);
INSERT INTO Airplane(name, id, num_seats, manufacturer, age) VALUE ('Jet Blue', '5678', 416, 'Boeing', 3);
INSERT INTO Airplane(name, id, num_seats, manufacturer, age) VALUE ('Jet Blue', '9abc', 524, 'Boeing', 5);

-- e. Insert At least One airline Staff working for Jet Blue.
INSERT INTO AirlineStaff(username, password, firstname, lastname, date_of_birth, airline_name) VALUE ('XxAirlineWorkerxX', 'bestPassword!223', 'Robert', 'Robertson', '1994-04-28', 'Jet Blue');

-- f. Insert several flights with on-time, and delayed statuses. 
INSERT INTO Flight(airline_name, flight_num, departure_timestamp, arrival_timestamp, base_price, status, departure_airport, arrival_airport, airplane_id) VALUE ('Jet Blue', 'B60001', '2004-09-20 23:34:00', '2004-09-21 23:34:00', 323.45, 'delayed', 'JFK', 'PVG', '1234');
INSERT INTO Flight(airline_name, flight_num, departure_timestamp, arrival_timestamp, base_price, status, departure_airport, arrival_airport, airplane_id) VALUE ('Jet Blue', 'B60002', '2022-12-21 13:30:00', '2022-12-22 12:30:00', 323.45, 'on-time', 'JFK', 'PVG', '5678');
INSERT INTO Flight(airline_name, flight_num, departure_timestamp, arrival_timestamp, base_price, status, departure_airport, arrival_airport, airplane_id) VALUE ('Jet Blue', 'B60003', '2022-12-22 13:30:00', '2022-12-23 12:30:00', 323.45, 'delayed', 'JFK', 'PVG', '9abc');

-- g. Insert some tickets for corresponding flights and insert some purchase records (customers bought some tickets).
INSERT INTO Ticket(sold_price, card_type, name_on_card, card_number, expiration_date, purchase_timestamp, customer_email, airline_name, flight_num, departure_timestamp) VALUE (323.45, 'Credit', 'Dingus Dingusson', '1234456745674567', '2023-04-23', '2022-12-10 13:31:25', 'dingus@gmail.com', 'Jet Blue', 'B60003', '2022-12-22 13:30:00'); 
INSERT INTO Ticket(sold_price, card_type, name_on_card, card_number, expiration_date, purchase_timestamp, customer_email, airline_name, flight_num, departure_timestamp) VALUE (654.17, 'Debit', 'Anna Zheng', '1234456745675678', '2025-6-18', '2022-11-7 21:15:02', 'az2306@nyu.edu', 'Jet Blue', 'B60002', '2022-12-21 13:30:00');
INSERT INTO Ticket(sold_price, card_type, name_on_card, card_number, expiration_date, purchase_timestamp, customer_email, airline_name, flight_num, departure_timestamp) VALUE (435.78, 'Credit', 'Taneim Miah', '456789076543', '2026-05-26', '2022-04-13 08:24:48','tsm6910@nyu.edu', 'Jet Blue', 'B60001', '2004-09-20 23:34:00');