from flask import request, render_template
from flask.views import View
from app_global import *

class SearchFlightsView(View):
    def __init__(self, template):
        self.template = template

    def dispatch_request(self):
        #grabs information from the forms
        departure_info = request.form['departure_info']
        destination_info = request.form['destination_info']

        departure_date = request.form['departure_date']
        return_date = request.form['return_date']

        formatted_departure_info = '%' + departure_info +'%'
        formatted_destination_info = '%' + destination_info + '%'


        #executes query and stores the results in a variable
        query = "WITH FlightTicketCount AS ("\
                    " SELECT airline_name, flight_num, departure_timestamp, COUNT(ticket_id) AS ticket_count"\
                    " FROM Ticket"\
                    " GROUP BY airline_name, flight_num, departure_timestamp"\
                ")"\
                " SELECT *, CASE"\
                    " WHEN ticket_count >= 0.6*num_seats THEN ROUND(base_price * 1.25, 2)"\
                    " ELSE base_price"\
                " END AS sell_price"\
                " FROM Flight AS F NATURAL JOIN FlightTicketCount JOIN Airplane ON (F.airline_name = Airplane.name AND F.airplane_id = Airplane.id), Airport AS D, Airport AS A"\
                " WHERE F.departure_airport = D.name AND F.arrival_airport = A.name AND"\
                    " (UPPER(F.departure_airport) LIKE UPPER(%s) OR UPPER(D.city) LIKE UPPER(%s)) AND"\
                    " (UPPER(F.arrival_airport) LIKE UPPER(%s) OR UPPER(A.city) LIKE UPPER(%s)) AND"\
                    " DATE(F.departure_timestamp) = %s AND status <> 'canceled'"\
                    " AND ticket_count < num_seats"
        departure_flights_data = fetchall(query, (formatted_departure_info, formatted_departure_info, formatted_destination_info, formatted_destination_info, departure_date))
        arrival_flights_data = []

        # for round trips
        if (return_date):
            #executes query and stores the results in a variable
            arrival_flights_data = fetchall(query, (formatted_destination_info, formatted_destination_info, formatted_departure_info, formatted_departure_info, return_date))

        
        return render_template(self.template, departure_flights = departure_flights_data, arrival_flights = arrival_flights_data)


class FlightStatusView(View):
    def __init__(self, template):
        self.template = template

    def dispatch_request(self):
        #grabs information from the form
        airline_name = request.form['airline_name']
        flight_num = request.form['flight_num']
        departure_date = request.form['departure_date']

        #executes query and stores the results in a variable
        query = "SELECT status"\
                " FROM Flight"\
                " WHERE airline_name = %s AND flight_num = %s AND DATE(departure_timestamp) = %s"
        data = fetchone(query, (airline_name, flight_num, departure_date))


        return render_template(self.template, status_airline_name = airline_name, status_flight_num = flight_num, status_departure_date = departure_date, status_data = data)