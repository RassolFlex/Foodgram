# Foodgram - рецепты для всех!

## Описание проекта
Проект, где можно делиться рецептами, добавлять их в избранное, подписываться на авторов, а также добавлять рецепты в список покупок, чтобы скачать его для удобства похода в магазин.

### Технологии
- Python
- Django
- Django REST framework
- nginx
- Gunicorn

полный список -> [requirements.txt](https://github.com/RassolFlex/foodgram-project-react/blob/master/backend/foodgram/requirements.txt)

## Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```bash
git clone https://github.com/RassolFlex/foodgram-project-react.git 
```

Перейти в корневую директорию:

```bash
cd foodgram
```

Создать файл .evn для хранения необходимых данных:

```python
SECRET_KEY='указать секретный ключ из файла /backend/settings.py'
ALLOWED_HOSTS='указать имя или IP хоста'
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram_password
DB_NAME=foodgram
DB_HOST=db
DB_PORT=5432
DEBUG=False
DB_SQLITE=False
```

Запустить сеть докер-контейнеров:

```bash
docker compose -f docker-compose.production.yml up
```

Выполнить миграции, сбор статики:

```bash
docker compose -f docker-compose.production.yml exec backend python manage.py migrate
docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /static/static/
```

Обязательно добавить заготовленные теги и ингредиенты командами:

```bash
docker compose -f docker-compose.production.yml exec backend python manage.py add_tags
docker compose -f docker-compose.production.yml exec backend python manage.py csv_import
```

Создать суперпользователя, ввести почту, логин и пароль после выполнения команды:

```bash
docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser
```

### Автор
Александр Огольцов [@RassolFlex](https://github.com/RassolFlex)

***

*Enjoy! Вы великолепны!*