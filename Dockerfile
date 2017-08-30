# Наследуемся от Python 
FROM python:3

# Выбираем рабочую папку
WORKDIR /usr/src/app

# Устанавливаем Flaskпапку проекта
RUN sudo apt-get install flask \
    mkdir code && mkdir code/server

# Копируем наш исходный main.py внутрь контейнера, в папку code/server
ADD main.py code/server

# Открываем 80-й порт наружу
EXPOSE 80

CMD [ "python", "./main.py" ]