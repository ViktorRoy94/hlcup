# Наследуемся от Python 
FROM python:3

# Выбираем рабочую папку
WORKDIR /home/root/code/server

# Устанавливаем Flask, Nginx, gunicorn
RUN pip3 install flask python-dateutil gunicorn && \
    apt-get update && apt-get install -y nginx && mkdir /tmp/data/
    
RUN rm /etc/nginx/sites-enabled/default && /etc/init.d/nginx start 

ADD flask_project /etc/nginx/sites-enabled/

# Копируем наш исходный main.py внутрь контейнера, в папку /home/root/code/server/
ADD main.py createDB.py /home/root/code/server/

#ADD data.zip /tmp/data

# Открываем 80-й порт наружу
EXPOSE 80

RUN /etc/init.d/nginx restart 

CMD python ./createDB.py && gunicorn main:app -b 0.0.0.0:80 -t 300