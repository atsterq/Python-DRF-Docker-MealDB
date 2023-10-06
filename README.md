## Описание:
«MealDB» — это сайт с базой данных рецептов и ингридиентов, на котором можно публиковать собственные рецепты, добавлять чужие рецепты в избранное, подписываться на других авторов и создавать список покупок для выбранных блюд.  
Приложение упаковано в докер контейнеры и готово к развертыванию по инструкции ниже.

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

## Как запустить проект в докер контейнерах на вашем сервере:

- Скопируйте репозиторий на свой локальный компьютер:

```
git clone https://github.com/atsterq/MealDB
```

- Локально отредактируйте файл infra/nginx.conf и в строке server_name впишите свой IP

- Подключитесь к вашему серверу с помощью SSH:
```
ssh <server user>@<server IP>
```

- Установите Docker на вашем сервере:
```
sudo apt install docker.io
```

- Установите Docker Compose (для Linux):
```
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
```

- Получите разрешения для docker-compose:
```
sudo chmod +x /usr/local/bin/docker-compose
```

- Создайте директорию проекта (желательно в вашей домашней директории):
```
mkdir MealDB && cd MealDB/
```

- Скопируйте файлы из 'infra/' (на вашем локальном компьютере) на ваш сервер:
```
scp -r infra/* <server user>@<server IP>:/home/<server user>/MealDB/
```

- Cоздайте .env файл:
```
mv .env.example .env
```

- И впишите в него:
```
POSTGRES_DB=<имя базы данных postgres>
POSTGRES_USER=<пользователь бд>
POSTGRES_PASSWORD=<пароль>
DB_HOST=db
DB_PORT=5432
SECRET_KEY=секретный ключ проекта django>
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,158.160.70.1,0.0.0.0,<IP или название вашего сервера>
```

- Запустите docker-compose:
```
sudo docker-compose.production up -d
```

- После успешной сборки на сервере выполните команды (только после первого деплоя):
- Соберите статические файлы:

```
sudo docker-compose exec backend python manage.py collectstatic --noinput
```
Примените миграции:
```
sudo docker-compose exec backend python manage.py migrate --noinput
```
Загрузите ингридиенты в базу данных c помощью менеджмент комманды:
```
sudo docker-compose exec backend python manage.py csv_to_db
```
Создайте суперпользователя Django:
```
sudo docker-compose exec backend python manage.py createsuperuser
```
Готово, проект будет доступен по вашему IP!

## Backend:
https://github.com/atsterq/
