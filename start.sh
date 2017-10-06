#!/usr/bin/env sh
# /usr/lib/postgresql/9.4/bin/postgres -D /home/root/code/server/ &
/etc/init.d/postgresql start
python3 ./createDB.py 
gunicorn -c gunicorn.conf main:app