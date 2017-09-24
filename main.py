# -*- coding: utf-8 -*-
import zipfile
import json
import sqlite3
import os
import re

from datetime import datetime
from dateutil.relativedelta import relativedelta
import calendar

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
		abort(404)
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
		abort(404)
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
		abort(404)
	response = list(response)
	response = dict(zip(names, response))
	response = json.dumps(response, ensure_ascii=False)
	conn.close()
	return response


@app.route('/users/<int:id>/visits')
def show_user_visits(id):
	print(set(request.args.keys()))
	args = {'fromDate':0, 'toDate':2000000000, 'country':None, 'toDistance':500}
	print(set(args.keys()))
	keys = set(args.keys()).intersection(set(request.args.keys()))
	print(keys)
	for key in keys:
		args[key] = request.args.get(key)
	for int_key in ['fromDate', 'toDate', 'toDistance']:
		try:
			args[int_key] = int(args[int_key])
		except ValueError:
			abort(400)

	if args['country']is not None and not args['country'].isalpha():
		abort(400)

	print(args)
	
	conn = sqlite3.connect('db.sqlite')
	cursor = conn.cursor()

	# check user id exists
	cursor.execute(''' SELECT *	FROM users WHERE id=?''', (id,))
	if not cursor.fetchall():
		abort(404)

	if args['country'] is None:
		cursor.execute('''
			SELECT mark,visited_at,place 
			FROM visits JOIN locations ON locations.id=visits.location 
			WHERE user=? and visited_at > ? and visited_at < ? and distance < ? ''', 
			(id, args['fromDate'], args['toDate'], args['toDistance']))
	else:
		cursor.execute('''
			SELECT mark,visited_at,place 
			FROM visits JOIN locations ON locations.id=visits.location 
			WHERE user=? and visited_at > ? and visited_at < ? and distance < ?
						 and country=?''', 
			(id, args['fromDate'], args['toDate'], args['toDistance'], args['country']))

	names = list(map(lambda x: x[0], cursor.description))
	response = dict({"visits":[]})
	for row in cursor.fetchall():
		response["visits"].append(dict(zip(names, row)))
	response["visits"].sort(key=lambda x:x["visited_at"])
	response = json.dumps(response, ensure_ascii=False)
	conn.close()
	return response

@app.route('/locations/<int:id>/avg')
def show_location_avg(id):
	print(set(request.args.keys()))
	args = {'fromDate':0, 'toDate':2000000000, 
			'fromAge':-1000, 'toAge':1000, 'gender':None}
	print(set(args.keys()))
	keys = set(args.keys()).intersection(set(request.args.keys()))
	print(keys)
	for key in keys:
		args[key] = request.args.get(key)
	for int_key in ['fromDate', 'toDate', 'fromAge', 'toAge']:
		try:
			args[int_key] = int(args[int_key])
		except ValueError:
			print("ValueError")
			abort(400)

	now = datetime.now() - relativedelta(years = args['fromAge'])
	args['fromAge'] = calendar.timegm(now.timetuple())
	now = datetime.now() - relativedelta(years = args['toAge'])
	args['toAge'] = calendar.timegm(now.timetuple())

	print(args['gender'])
	if args['gender'] is not None and not (args['gender'] == 'f' or args['gender'] == 'm'):
		abort(400)

	print(args)

	conn = sqlite3.connect('db.sqlite')
	cursor = conn.cursor()

	# check user id exists
	cursor.execute(''' SELECT *	FROM locations WHERE id=?''', (id,))
	if not cursor.fetchall():
		abort(404)

	if args['gender'] is None:
		cursor.execute('''
			SELECT avg(mark)
			FROM visits JOIN users ON users.id = visits.user
			WHERE location = ? and visited_at > ? and visited_at < ?
							   and birth_date < ? and birth_date > ?''', 
			(id, args['fromDate'], args['toDate'], args['fromAge'], args['toAge']))
	else:
		cursor.execute('''
			SELECT avg(mark)
			FROM visits JOIN users ON users.id = visits.user
			WHERE location = ? and visited_at > ? and visited_at < ?
							   and birth_date < ? and birth_date > ?
							   and gender = ?''', 
			(id, args['fromDate'], args['toDate'], args['fromAge'], args['toAge'], args['gender']))

	response = dict({"avg":0})
	cur = cursor.fetchone()
	print(cur)
	if cur[0] is not None:
		response['avg'] = round(float(cur[0]),5)
	response = json.dumps(response, ensure_ascii=False)
	conn.close()
	return response

def main():

    uzip_data()
    read_data_to_db()

    app.run(host='0.0.0.0', port=80, debug=False, threaded=True)

if __name__ == "__main__":
    main()
