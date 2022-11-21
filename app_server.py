#Import Flask Library
from flask import Flask

#Import Blueprints
from general.routes import general_bp
from customer.routes import customer_bp

#Initialize the app from Flask
app = Flask(__name__)

#Register Blueprints
app.register_blueprint(general_bp)
app.register_blueprint(customer_bp, url_prefix='/customer')

app.secret_key = 'some key that you will never guess'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
	app.run('127.0.0.1', 5000, debug = True)