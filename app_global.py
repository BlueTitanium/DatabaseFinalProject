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

