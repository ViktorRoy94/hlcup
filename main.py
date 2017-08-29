# -*- coding: utf-8 -*-
import zipfile
import json
import sqlite3
import os


def uzip_data():
    # unzip data.zip to the folder
    zip_ref = zipfile.ZipFile("data.zip", 'r')
    zip_ref.extractall("")
    zip_ref.close()
    print("complete uzip")


def read_data():
    os.remove("data/db.sqlite")
    conn = sqlite3.connect('data/db.sqlite')
    cursor = conn.cursor()
    cursor.execute(
        '''CREATE TABLE locations (id INTEGER PRIMARY KEY, place text, country text, city text, distance INTEGER)''')
    cursor.execute(
        '''CREATE TABLE users (id INTEGER PRIMARY KEY, email text, first_name text, last_name text, gender text, birth_date INTEGER)''')
    cursor.execute(
        '''CREATE TABLE visits (id INTEGER PRIMARY KEY, location INTEGER, user INTEGER, visited_at INTEGER, mark INTEGER)''')
    conn.commit()

    with open('data/locations_1.json') as loc:
        loc_data = json.load(loc)
        for location in loc_data['locations']:
            cursor.execute(
                "INSERT INTO locations VALUES (:id,:place,:country,:city,:distance)", location)
            conn.commit()

    with open('data/users_1.json') as user_file:
        user_data = json.load(user_file)
        for user in user_data['users']:
            cursor.execute(
                "INSERT INTO users VALUES (:id,:email,:first_name,:last_name,:gender,:birth_date)", user)
            conn.commit()

    with open('data/visits_1.json') as visit_file:
        visit_data = json.load(visit_file)
        for visit in visit_data['visits']:
            cursor.execute(
                "INSERT INTO visits VALUES (:id,:location,:user,:visited_at,:mark)", visit)
            conn.commit()
    conn.close()


def main():
    uzip_data()
    read_data_to_db()

if __name__ == "__main__":
    main()
