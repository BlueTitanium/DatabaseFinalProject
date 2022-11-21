import pymysql
import hashlib

#Configure MySQL
conn = pymysql.connect(host='localhost',
					   user='root',
					   password='',
					   db='airline_reservation',
					   charset='utf8mb4',
					   cursorclass=pymysql.cursors.DictCursor)

#For hashing passwords
def md5(string_to_hash):
	# encode string, hash with md5, return hexadecimal equivalent
	return hashlib.md5(string_to_hash.encode()).hexdigest()


def fetchone(query, params):
	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	cursor.execute(query, params)
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	#close cursor
	cursor.close()

	return data

def fetchall(query, params):
	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	cursor.execute(query, params)
	#stores the results in a variable
	data = cursor.fetchall()
	#close cursor
	cursor.close()
	
	return data

def modify(query, params):
	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	cursor.execute(query, params)
	conn.commit()
	#close cursor
	cursor.close()