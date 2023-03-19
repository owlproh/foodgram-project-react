# FOODGRAM. Продуктовый помощник с применением CI/CD

![badge](https://github.com/owlproh/foodgram-project-react/actions/workflows/main.yml/badge.svg)

---

- <b>Адрес: </b>
- http://62.84.125.214/

- <b> АДМИН: </b>
email: admin@mail.ru
password: admin

---

### Навигация по описанию проекта:
- [Описание проекта](#описание)
- [Функционал](#доступный-функционал)
- [Технологии](#технологии)
- [Запуск проекта локально](#запуск-проекта-локально)
- [Запуск проекта на сервере](#запуск-проекта-на-сервере)
- [Описание '.env'](#описание-конфигурации-файла-содержащего-переменные-виртуального-окружения-env)
- [Примеры-некоторых-запросов-api](#примеры-некоторых-запросов-api)
- [Примеры-запросов-json-формате](#примеры-запросов-json-формате)
- [Авторы](#авторы)

## Описание

Приложение «FOODGRAM» - сайт, на котором пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Сервис «Список покупок» позволяет пользователям создавать список продуктов, которые нужно купить для приготовления выбранных блюд.А перед походом в магазин можно скачать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.
  
#### Доступный функционал

Проект предоставляет возможность взаимодействовать с базой данных по следующим направлениям:

- регистрироваться
- авторизироваться с использованием djoser
- у неаутентифицированных пользователей доступ к API только на уровне чтения.
- создание объектов разрешено только аутентифицированным пользователям.
- создавать свои рецепты и управлять ими (корректировать\удалять)
- просматривать рецепты других пользователей
- подписываться на публикации других пользователей
- добавлять в избранное рецепты, которые понравятся
- добавлять рецепты в корзину и скачивать список продуктов в .txt формате

#### Документация

После запуска проекта (*см. ниже) по адресу [http://62.84.125.214/api/docs/](http://62.84.125.214/api/docs/) доступна документация к проекту.

#### Технологии 

- [Python 3.7+](https://www.python.org/)
- [Django](https://www.djangoproject.com)
- [Django Rest Framework 3.12.4](https://www.django-rest-framework.org)
- [Simple JWT](https://django-rest-framework-simplejwt.readthedocs.io/en/latest/)
- [PostgreSQL](https://www.postgresql.org/)
- [Nginx](https://nginx.org/ru/)
- [gunicorn](https://gunicorn.org/)
- [Docker/Docker-Compose](https://www.docker.com/)
- [DockerHub](https://www.docker.com/products/docker-hub)
- [GitHub_Actions](https://github.com/features/actions)
- [Yandex.Cloud](https://cloud.yandex.ru/)

#### Запуск проекта локально

- Склонируйте репозиторий:
``` git clone <ссылка на репозиторий> ```
- Создайте файл содержащий переменные виртуального окружения [(.env)](#описание-конфигурации-файла-содержащего-переменные-виртуального-окружения-env):
``` cd foodgram-project-react/infra/```
``` touch .env ```
- Соберите образ контейнера:
``` cd foodgram-project-react/backend/ ```
``` docker build -t <логин на DockerHub>/<название для образа>:<флаг, например версия приложения> .```
- Разверните контейнеры и выполните миграции:
``` cd foodgram-project-react/infra/ ```
``` docker-compose up -d или docker-compose up -d --build ```
``` docker-compose exec backend python3 manage.py migrate ```
- Создайте суперюзера:
``` docker-compose exec backend python3 manage.py createsuperuser ```
- Соберите статику:
``` docker-compose exec backend python3 manage.py collectstatic --no-input ```
- Для загрузки фикстур в БД выполните команду:
```docker-compose exec backend python3 manage.py load_tags ```
```docker-compose exec backend python3 manage.py load_ingredients ```
- * Для дальнейшего создания фикстур из Вашей БД, используйте команду:
``` docker-compose exec backend python3 manage.py dumpdata > fixtures.json ```

#### Запуск проекта на сервере

- Подключитесь к серверу:
``` ssh <username>@<публичный ip сервера> ```
- Установите Docker и Docker-Compose:
``` apt install docker.io ```
``` apt -y install curl ```
``` curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose ```
``` chmod +x /usr/local/bin/docker-compose ```
- * Чтобы проверить, что Docker-Compose запускается корректно - можно использовать команду:
``` docker-compose ```
- Создайте папку 'nginx':
``` mkdir nginx ```

- При успешном деплое проекта на сервер:

- Выполните миграции:
``` docker-compose exec backend python3 manage.py migrate ```
- Создайте суперюзера:
``` docker-compose exec backend python3 manage.py createsuperuser ```
- Соберите статику:
``` docker-compose exec backend python3 manage.py collectstatic --no-input ```
- Для загрузки фикстур в БД выполните команду:
```docker-compose exec backend python3 manage.py load_tags ```
```docker-compose exec backend python3 manage.py load_ingredients ```
- * Для дальнейшего создания фикстур из Вашей БД, используйте команду:
``` docker-compose exec backend python3 manage.py dumpdata > fixtures.json ```

#### Описание конфигурации файла содержащего переменные виртуального окружения (.env)
(Файл виртуального окружения .env необходимо разместить в папке infra)

- Основа для Вашей БД:
``` DB_ENGINE=django.db.backends.postgresql ```
- Имя для Вашей БД:
``` DB_NAME= ```
- Логин для БД:
``` POSTGRES_USER= ```
- Пароль для этого логина:
``` POSTGRES_PASSWORD= ```
- Название сервиса (контейнера):
``` DB_HOST= ```
- Порт для подключения к БД:
``` DB_PORT= ```

#### Примеры некоторых запросов API
Регистрация пользователя:  
``` POST /api/users/ ```  
Получение токена для авторизации пользователя:  
``` POST /api/auth/token/login/ ```  
Получение списка пользователей:  
``` GET /api/users/ ```  

``` Полный список доступных эндпоинтов по типу запроса: ```

POST
```
- /api/users/
- /api/users/set_password/
- /api/auth/token/login/
- /api/auth/token/logout/
- /api/users/{id}/subscribe/
- /api/recipes/
- /api/recipes/{id}/favorite/
- /api/recipes/{id}/shopping_cart/
```

GET
```
- /api/users/me/
- /api/users/{id}/
- /api/users/
- /api/users/subscriptions/
- /api/tags/
- /api/tags/{id}/
- /api/ingredients/
- /api/ingredients/{id}/
- /api/recipes/
- /api/recipes/?author=1/
- /api/recipes/?tags=breakfast/
- /api/recipes/{id}/
- /api/recipes/download_shopping_cart/
```

DELETE
```
- /api/users/{id}/subscribe/
- /api/recipes/{id}/
- /api/recipes/{id}/favorite/
- /api/recipes/{id}/shopping_cart/
```

PATCH
```
- /api/recipes/{id}/ 
```

#### Примеры запросов JSON-формате:

POST `api/users/`:
```
{
    "email": "e3@mail.ru",
    "first_name": "f3",
    "last_name": "l3",
	"username": "m3",
	"password": "Bom8cuz3"
}
```
GET `api/users/`:
```
Response:
{
    "count":5,
    "next":null,
    "previous":null,
    "results":[
    
        {
            "id":1,
            "username":"admin",
            "first_name":"admin",
            "last_name":"admin",
            "email":"admin@mail.ru",
            "is_follower":false
        },
        {
            "id":3,
            "username":"Евгенич",
            "first_name":"Владислав",
            "last_name":"Чупин",
            "email":"210nk@mail.ru",
            "is_follower":false
        },
        {
            "id":4,
            "username":"m2",
            "first_name":"f2",
            "last_name":"l2",
            "email":"e2@mail.ru",
            "is_follower":false
        },
        {
            "id":2,
            "username":"m1",
            "first_name":"f1",
            "last_name":"l1",
            "email":"e1@mail.ru",
            "is_follower":false
        },
        {
            "id":5,
            "username":"m3",
            "first_name":"f3",
            "last_name":"l3",
            "email":"e3@mail.ru",
            "is_follower":false
        }
    ]
}
```

POST `api/auth/token/login/`:
```
{
    "email": "e3@mail.ru",
	"password": "Bom8cuz3"
}
```
```
Response:

{
    "auth_token":"8a1b347a2a5c8889887c83eed77ea098d726bee7"
}
```

GET `api/tags/`:
```
Response:
[
    {
        "id":1,
        "name":"Завтрак",
        "color":"#E26C2D",
        "slug":"breakfast"
    },
    {
        "id":2,
        "name":"Обед",
        "color":"#49B64E",
        "slug":"dinner"
    },
    {
        "id":5,
        "name":"Острое",
        "color":"#cc0000",
        "slug":"sharp"
    },
    {
        "id":4,
        "name":"Сладенькое",
        "color":"#c9a2bf",
        "slug":"sweet"
    },
    {
        "id":3,
        "name":"Ужин",
        "color":"#8775D2",
        "slug":"supper"
    }
]
```

#### Автор:

[Святослав](https://github.com/owlproh)