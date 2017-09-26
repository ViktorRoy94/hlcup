# -*- coding: utf-8 -*-

import json
import sqlite3
import os

from datetime import datetime
from dateutil.relativedelta import relativedelta
import calendar

from flask import Flask
from flask import abort
from flask import request

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

@app.route('/locations/<int:id>', methods = ['GET'])
def get_location(id):
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

@app.route('/users/<int:id>', methods = ['GET'])
def get_user(id):
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

@app.route('/visits/<int:id>', methods = ['GET'])
def get_visit(id):
	conn = sqlite3.connect('db.sqlite')
	cursor = conn.cursor()
	cursor.execute('SELECT * FROM visits WHERE id=?', (id,))
	names = list(map(lambda x: x[0], cursor.description))
	response = cursor.fetchone()
	if response is None:
		abort(404)
	response = list(response)
	response = dict(zip(names, response))
	response = json.dumps(response, ensure_ascii=False)
	conn.close()
	return response


@app.route('/users/<int:id>/visits', methods = ['GET'])
def get_user_visits(id):
	args = {'fromDate':0, 'toDate':2000000000, 'country':None, 'toDistance':500}
	keys = set(args.keys()).intersection(set(request.args.keys()))
	for key in keys:
		args[key] = request.args.get(key)
	for int_key in ['fromDate', 'toDate', 'toDistance']:
		try:
			args[int_key] = int(args[int_key])
		except ValueError:
			abort(400)
	
	if args['country']is not None:
		country = "".join(args['country'].split())
		if not country.isalpha()
			abort(400)

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
			WHERE user=? and visited_at > ? and visited_at < ? and distance < ?
			ORDER BY visited_at''', 
			(id, args['fromDate'], args['toDate'], args['toDistance']))
	else:
		cursor.execute('''
			SELECT mark,visited_at,place 
			FROM visits JOIN locations ON locations.id=visits.location 
			WHERE user=? and visited_at > ? and visited_at < ? and distance < ?
						 and country=?
			ORDER BY visited_at''', 
			(id, args['fromDate'], args['toDate'], args['toDistance'], args['country']))

	names = list(map(lambda x: x[0], cursor.description))
	response = dict({"visits":[]})
	for row in cursor.fetchall():
		response["visits"].append(dict(zip(names, row)))
	response = json.dumps(response, ensure_ascii=False)
	conn.close()
	return response

@app.route('/locations/<int:id>/avg', methods = ['GET'])
def get_location_avg(id):
	args = {'fromDate':0, 'toDate':2000000000, 
			'fromAge':-1000, 'toAge':1000, 'gender':None}
	keys = set(args.keys()).intersection(set(request.args.keys()))
	for key in keys:
		args[key] = request.args.get(key)
	for int_key in ['fromDate', 'toDate', 'fromAge', 'toAge']:
		try:
			args[int_key] = int(args[int_key])
		except ValueError:
			abort(400)

	now = datetime.now() - relativedelta(years = args['fromAge'])
	args['fromAge'] = calendar.timegm(now.timetuple())
	now = datetime.now() - relativedelta(years = args['toAge'])
	args['toAge'] = calendar.timegm(now.timetuple())

	if args['gender'] is not None and not (args['gender'] == 'f' or args['gender'] == 'm'):
		abort(400)

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
	if cur[0] is not None:
		response['avg'] = round(float(cur[0]),5)
	response = json.dumps(response, ensure_ascii=False)
	conn.close()
	return response

@app.route('/locations/<int:id>', methods = ['POST'])
def set_location(id):
	data = request.get_json()
	keys = set(data.keys()).intersection(set(['place', 'country', 'city', 'distance']))
	post_data = {}
	for key in keys:
		if key == 'distance':
			try:
				post_data['distance'] = int(data['distance'])
			except ValueError:
				abort(400)
		else:
			post_data[key] = data[key]
			if not post_data[key].isalpha():
				abort(400)

	conn = sqlite3.connect('db.sqlite')
	cursor = conn.cursor()
	cursor.execute(''' SELECT *	FROM locations WHERE id=?''', (id,))
	if cursor.fetchone()[0] is None:
		abort(404)
	sql_request = ''' UPDATE locations SET '''
	for key in post_data.keys():
		sql_request += str(key) + ' = \'' + str(post_data[key]) + '\' '
	sql_request += 'WHERE id = ' + str(id)
	cursor.execute(sql_request)
	conn.commit()
	conn.close()
	return json.dumps("{}")


@app.route('/users/<int:id>', methods = ['POST'])
def set_user(id):
	data = request.get_json()
	keys = set(data.keys()).intersection(set(['email', 'first_name', 'last_name', 'gender', 'birth_date']))
	post_data = {}
	for key in keys:
		if key == 'gender' and not (data[key] == 'm' or data[key] == 'f'):
			abort(400)
		if key == 'birth_date':
			try:
				post_data['birth_date'] = int(data['birth_date'])
			except ValueError:
				abort(400)
		else:
			post_data[key] = data[key]
			if not post_data[key].isalpha():
				abort(400)

	conn = sqlite3.connect('db.sqlite')
	cursor = conn.cursor()
	cursor.execute(''' SELECT *	FROM users WHERE id=?''', (id,))
	if cursor.fetchone()[0] is None:
		abort(404)
	sql_request = ''' UPDATE users SET '''
	for key in post_data.keys():
		sql_request += str(key) + ' = \'' + str(post_data[key]) + '\' '
	sql_request += 'WHERE id = ' + str(id)
	cursor.execute(sql_request)
	conn.commit()
	conn.close()
	return json.dumps("{}")


@app.route('/visits/<int:id>', methods = ['POST'])
def set_visit(id):
	data = request.get_json()
	keys = set(data.keys()).intersection(set(['location', 'user', 'visited_at', 'mark']))
	post_data = {}
	for key in keys:
		try:
			post_data[key] = int(data[key])
		except ValueError:
			abort(400)

	conn = sqlite3.connect('db.sqlite')
	cursor = conn.cursor()
	cursor.execute(''' SELECT *	FROM visits WHERE id=?''', (id,))
	if cursor.fetchone()[0] is None:
		abort(404)
	sql_request = ''' UPDATE visits SET '''
	for key in post_data.keys():
		sql_request += str(key) + ' = \'' + str(post_data[key]) + '\' '
	sql_request += 'WHERE id = ' + str(id)
	cursor.execute(sql_request)
	conn.commit()
	conn.close()
	return json.dumps("{}")

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=80, debug=False)