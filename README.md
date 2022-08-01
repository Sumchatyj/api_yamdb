# api_yamdb

## Описание

API для проектра YaMDb.

Проект YaMDb собирает отзывы пользователей на произведения.
Сами произведения в YaMDb не хранятся, здесь нельзя посмотреть фильм или послушать музыку.


## Как запустить проект

### Зависимости

* python 3.7
* django 4.0.4
* djangorestframework 3.13.1

### Установка

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/Sumchatyj/api_yamdb
```

```
cd api_final_yatube
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

```
source env/bin/activate
```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate
```
### Запуск

Запустить проект:

```
python3 manage.py runserver
```


## Примеры:

Регистрация новго пользователя.

POST /api/v1/auth/signup/

```
{
    "email": "string",
    "username": "string"
}
```

Получение JWT-токена.

POST /api/v1/auth/token/

```
{
    "username": "string",
    "confirmation_code": "string"
}
```

Получение информации о произведении.

GET /api/v1/titles/{titles_id}/


Частичное обновление отзыва по id. Обновить отзыв может только автор комментария, модератор или администратор. Анонимные запросы запрещены.

PATCH /api/v1/titles/{title_id}/reviews/{review_id}/

```
{
    "text": "string",
    "score": 1
}
```
