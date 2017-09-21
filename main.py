# -*- coding: utf-8 -*-
import zipfile
import json
import sqlite3
import os
import re

from webargs import fields, validate
from webargs.flaskparser import use_args

from flask import Flask
from flask import abort
from flask import request
app = Flask(__name__)


def uzip_data():
    # unzip data.zip to the folder
    zip_ref = zipfile.ZipFile("/tmp/data/data.zip", 'r')
    zip_ref.extractall("data")
    zip_ref.close()
    print("complete uzip")


def read_data_to_db():
	# os.remove("db.sqlite")
	conn = sqlite3.connect('db.sqlite')
	cursor = conn.cursor()
	cursor.execute(
	    '''CREATE TABLE IF NOT EXISTS locations (id INTEGER PRIMARY KEY, place text, country text, city text, distance INTEGER)''')
	cursor.execute(
	    '''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, email text, first_name text, last_name text, gender text, birth_date INTEGER)''')
	cursor.execute(
	    '''CREATE TABLE IF NOT EXISTS visits (id INTEGER PRIMARY KEY, location INTEGER, user INTEGER, visited_at INTEGER, mark INTEGER)''')
	conn.commit()
	print(os.listdir("data"))
	location_files = [x for x in os.listdir("data") if re.match("locations_", x)]
	users_files = [x for x in os.listdir("data") if re.match("users_", x)]
	visits_files = [x for x in os.listdir("data") if re.match("visits_", x)]
	print(location_files)
	print(users_files)
	print(visits_files)

	for file in location_files:
		with open("data/" + file) as loc:
		    loc_data = json.load(loc)
		    for location in loc_data['locations']:
		        cursor.execute(
		            "INSERT INTO locations VALUES (:id,:place,:country,:city,:distance)", location)
	print("locations complete")
	for file in users_files:
		with open("data/" + file) as user_file:
		    user_data = json.load(user_file)
		    for user in user_data['users']:
		        cursor.execute(
		            "INSERT INTO users VALUES (:id,:email,:first_name,:last_name,:gender,:birth_date)", user)
	print("users complete")
	for file in visits_files:
		with open("data/" + file) as visit_file:
		    visit_data = json.load(visit_file)
		    for visit in visit_data['visits']:
		        cursor.execute(
		            "INSERT INTO visits VALUES (:id,:location,:user,:visited_at,:mark)", visit)
	print("visits complete")
	conn.commit()
	conn.close()


@app.route("/")
def hello():
    return "Hello World!"

@app.route('/locations/<int:id>')
def show_location(id):
	conn = sqlite3.connect('db.sqlite')
	cursor = conn.cursor()
	cursor.execute('SELECT * FROM locations WHERE id=?', (id,))
	names = list(map(lambda x: x[0], cursor.description))
	response = cursor.fetchone()
	if response is None:
		return "HTTP Status Code: 404", 404
	response = list(response)
	response = dict(zip(names, response))
	response = json.dumps(response, ensure_ascii=False)
	conn.close()
	return response

@app.route('/users/<int:id>')
def show_user(id):
	conn = sqlite3.connect('db.sqlite')
	cursor = conn.cursor()
	cursor.execute('SELECT * FROM users WHERE id=?', (id,))
	names = list(map(lambda x: x[0], cursor.description))
	response = cursor.fetchone()
	if response is None:
		return "HTTP Status Code: 404", 404
	response = list(response)
	response = dict(zip(names, response))
	response = json.dumps(response, ensure_ascii=False)
	conn.close()
	return response

@app.route('/visits/<int:id>')
def show_visit(id):
	conn = sqlite3.connect('db.sqlite')
	cursor = conn.cursor()
	cursor.execute('SELECT * FROM visits WHERE id=?', (id,))
	names = list(map(lambda x: x[0], cursor.description))
	response = cursor.fetchone()
	print("response = ",response)
	if response is None:
		return "HTTP Status Code: 404", 404
	response = list(response)
	response = dict(zip(names, response))
	response = json.dumps(response, ensure_ascii=False)
	conn.close()
	return response


visits_args = {
	'fromDate' : fields.Int(),
	'toDate' : fields.Int(),
	'country' : fields.Str(),
	'toDistanse' : fields.Int()
}

@app.route('/users/<int:id>/visits')
@use_args(visits_args)
def show_user_visits(args, id):
	# print(args)
	# from_date = args['fromDate']
	# to_date = args['toDate']
	# country = args['country']
	# to_distanse = args['toDistanse']

	# print(from_date)
	# print(to_date)
	# print(country)
	# print(to_distanse)
	conn = sqlite3.connect('db.sqlite')
	cursor = conn.cursor()
	cursor.execute('''
		SELECT mark,visited_at,place 
		FROM visits JOIN locations ON locations.id=visits.location 
		WHERE user=? ''', (id,))
	names = list(map(lambda x: x[0], cursor.description))
	response = dict({"visits":[]})
	for row in cursor.fetchall():
		response["visits"].append(dict(zip(names, row)))
	# # if response is None:
	# # 	return "HTTP Status Code: 404", 404
	response["visits"].sort(key=lambda x:x["visited_at"])
	response = json.dumps(response, ensure_ascii=False)
	conn.close()
	return response

# @app.route('/locations/<int:id>/avg')
# def show_location_avg(id):
# 	conn = sqlite3.connect('db.sqlite')
# 	cursor = conn.cursor()
# 	cursor.execute('SELECT mark,visited_at,place FROM visits JOIN locations ON locations.id=visits.location WHERE user=?', (id,))
# 	names = list(map(lambda x: x[0], cursor.description))
# 	response = dict({"visits":[]})
# 	for row in cursor.fetchall():
# 		response["visits"].append(dict(zip(names, row)))
# 	# # if response is None:
# 	# # 	return "HTTP Status Code: 404", 404
# 	response["visits"].sort(key=lambda x:x["visited_at"])
# 	response = json.dumps(response, ensure_ascii=False)
# 	conn.close()
# 	return response

# @app.errorhandler(404)
# def page_not_found(error):
#     return "HTTP Status Code: 404", 404

def main():

    uzip_data()
    read_data_to_db()

    app.run(host='0.0.0.0', port=80, debug=False, threaded=True)

if __name__ == "__main__":
    main()
