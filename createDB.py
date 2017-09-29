import zipfile
import re
import json
import psycopg2
import os
import shutil

def uzip_data():
    # unzip data.zip to the folder
    zip_ref = zipfile.ZipFile("/tmp/data/data.zip", 'r')
    zip_ref.extractall("data")
    zip_ref.close()
    print("complete uzip")

def create_db():
	conn = psycopg2.connect(dbname='postgres', user='postgres', host='localhost', password='everything')
	cursor = con.cursor()
	cursor.execute('CREATE DATABASE hlcup')
	cursor.execute('CREATE USER hlcup_user WITH PASSWORD 8658')
	cursor.execute('GRANT ALL PRIVILEGES ON DATABASE hlcup to hlcup_user')
	cursor.close()

def read_data_to_db():
	# os.remove("db.sqlite")
	conn = psycopg2.connect(dbname = hlcup, user = posgres)
	cursor = conn.cursor()
	cursor.execute(
	    '''CREATE TABLE IF NOT EXISTS locations (id INTEGER PRIMARY KEY, place text, country text, city text, distance INTEGER)''')
	cursor.execute(
	    '''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, email text, first_name text, last_name text, gender text, birth_date INTEGER)''')
	cursor.execute(
	    '''CREATE TABLE IF NOT EXISTS visits (id INTEGER PRIMARY KEY, location INTEGER, user INTEGER, visited_at INTEGER, mark INTEGER)''')
	conn.commit()
	location_files = [x for x in os.listdir("data") if re.match("locations_", x)]
	users_files = [x for x in os.listdir("data") if re.match("users_", x)]
	visits_files = [x for x in os.listdir("data") if re.match("visits_", x)]

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
	shutil.rmtree("data")


def main():

    # uzip_data()
    create_db()
    read_data_to_db()

if __name__ == "__main__":
    main()