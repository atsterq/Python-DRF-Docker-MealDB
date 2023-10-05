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

## Как запустить проект в докер контейнерах на вашем сервере:

1. Подключитесь к вашему серверу с помощью SSH:
```
ssh <server user>@<server IP>
```

2. Установите Docker на вашем сервере:
```
sudo apt install docker.io
```

3. Установите Docker Compose (для Linux):
```
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
```

4. Получите разрешения для docker-compose:
```
sudo chmod +x /usr/local/bin/docker-compose
```

5. Создайте директорию проекта (желательно в вашей домашней директории):
```
mkdir MealDB && cd MealDB/
```

6. Скопируйте файлы из 'infra/' (на вашем локальном компьютере) на ваш сервер:
```
scp -r infra/* <server user>@<server IP>:/home/<server user>/foodgram/
```

7. Переименуйте .env.example в .env

```
mv .env.example .env
```

8. Запустите docker-compose:
```
sudo docker-compose up -d
```
