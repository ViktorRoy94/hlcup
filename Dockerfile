# Наследуемся от Python 
FROM python:3

# Выбираем рабочую папку
WORKDIR /home/root/code/server

# Устанавливаем Flask, Nginx, gunicorn, postgresql
RUN pip3 install flask python-dateutil gunicorn Psycopg2 && \
    apt-get update && apt-get install -y nginx postgresql postgresql-contrib \
    && mkdir /tmp/data/
    
RUN rm /etc/nginx/sites-enabled/default 

# копируем конфиг nginx
ADD nginx.conf /etc/nginx/sites-enabled/

RUN /etc/init.d/nginx start

# переключаем юзера на postgres
USER postgres

# создаем пользователя docker с паролем docker и бд hlcup
RUN /etc/init.d/postgresql start &&\
    psql --command "CREATE USER docker WITH SUPERUSER PASSWORD 'docker';" &&\
    psql --command "CREATE DATABASE hlcup;" &&\
    psql --command "GRANT ALL ON DATABASE hlcup TO docker;" 

#USER root

# Adjust PostgreSQL configuration so that remote connections to the
# database are possible.
#RUN echo "host all  all    0.0.0.0/0  md5" >> /etc/postgresql/9.4/main/pg_hba.conf
 
#RUN /etc/init.d/postgresql stop
#RUN /usr/lib/postgresql/9.4/bin/postgres -D /etc/postgresql/9.4/main/ -h localhost &

#RUN /etc/init.d/postgresql stop

# Копируем наш исходный main.py внутрь контейнера, в папку /home/root/code/server/
ADD main.py createDB.py gunicorn.conf postgres.conf start.sh /home/root/code/server/

# Открываем 80-й порт наружу
EXPOSE 80

CMD ./start.sh
