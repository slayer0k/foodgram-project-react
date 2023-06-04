# Проект FoodGram
## Сервис для публикации рецептов.

### Стэк:
- Django REST Framework
- Gunicorn
- Nginx
### Установка:
> скопируйте репозиторий в нужную папку
> создайте и заполните файл .env в папке backend/ в соответствии с шаблоном
##### .env:
    - DB_ENGINE=django.db.backends.postgresql
    - DB_NAME=postgres
    - POSTGRES_USER=postgres
    - POSTGRES_PASSWORD=postgres
    - DB_HOST=db
    - DB_PORT=5432
    - ALLOWED_HOSTS=['*']
    - DEBUG=FALSE
    - SECRET=SECRET_KEY
> установите Docker в соответствии с вашей системой https://docs.docker.com/engine/install/
> перейдите в папку infra/ и выполните команду docker-compose docker-compose.yml -d --build
> доступ к сайту можно получить по адресу http://localhost:8000/

### Автор - Самойленко Дмитрий
