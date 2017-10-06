#!/usr/bin/env sh
/usr/lib/postgresql/9.4/bin/postgres start -D /home/root/code/server/ &
/etc/init.d/postgresql start
python ./createDB.py 
gunicorn main:app -b -c gunicorn.conf&