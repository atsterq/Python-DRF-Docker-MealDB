## Описание:
«MealDB» — это сайт, на котором можно публиковать собственные рецепты, добавлять чужие рецепты в избранное, подписываться на других авторов и создавать список покупок для выбранных блюд.  

## Что было сделано в ходе работы над проектом:  
- настроено взаимодействие Python-приложения с внешними API-сервисами;  

- создан собственный API-сервис на базе проекта Django;  

- подключено SPA к бэкенду на Django через API;  

- созданы образы и запущены контейнеры Docker;  

- созданы, развёрнуты и запущены на сервере мультиконтейнерные приложения;  

- закреплены на практике основы DevOps, включая CI&CD.

## Технологии:
- Python 3.10
- Django 3.2
- Django REST framework 3.12
- PostgreSQL
- Nginx
- Docker

## Как запустить проект:
Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/atsterq/MealDB
```

```
cd MealDB
```

Cоздать и активировать виртуальное окружение:

```
python -m venv venv
```

```
source venv/Scripts/activate
```

Установить зависимости из файла requirements.txt:

```
python -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python manage.py migrate
```

Запустить проект:

```
python manage.py runserver
```


Connect to your server:
ssh <server user>@<server IP>
Install Docker on your server
sudo apt install docker.io
Install Docker Compose (for Linux)
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
Get permissions for docker-compose
sudo chmod +x /usr/local/bin/docker-compose
Create project directory (preferably in your home directory)
mkdir foodgram && cd foodgram/
Create env-file:
touch .env
Fill in the env-file like it:
DEBUG=False
SECRET_KEY=<Your_some_long_string>
ALLOWED_HOSTS=<Your_host>
CSRF_TRUSTED_ORIGINS=https://<Your_host>
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=<Your_password>
DB_HOST=foodgram-db
DB_PORT=5432
Copy files from 'infra/' (on your local machine) to your server:
scp -r infra/* <server user>@<server IP>:/home/<server user>/foodgram/
Run docker-compose
sudo docker-compose up -d
