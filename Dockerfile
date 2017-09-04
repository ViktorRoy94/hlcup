# Наследуемся от Python 
FROM python:3

# Выбираем рабочую папку
WORKDIR /home/root/code/server

# Устанавливаем Flaskпапку проекта
RUN pip3 install flask && mkdir /tmp/data/

# Копируем наш исходный main.py внутрь контейнера, в папку /home/root/code/server/
ADD main.py /home/root/code/server/

ADD data.zip /tmp/data

# Открываем 80-й порт наружу
EXPOSE 80

RUN ["/bin/bash", "-c", "pwd"]
RUN ["/bin/bash", "-c", "ls", "-a"]
RUN ["/bin/bash", "-c", "pwd"]
CMD [ "python", "./main.py" ]
