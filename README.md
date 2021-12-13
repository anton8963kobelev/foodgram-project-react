# Foodgram

## Описание проекта

Адрес сервера:
[http://51.250.30.99/](http://51.250.30.99/)

### Данные администратора:
- логин: admin
- пароль: 456789

Продуктовый помощник - это сервис, где пользователи смогут:
* публиковать рецепты;
* подписываться на публикации других пользователей;
* добавлять понравившиеся рецепты в список «Избранное»;
* перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления выбранных блюд.

## Запуск проекта

Клонируйте репозиторий: 
 
``` 
git clone https://github.com/anton8963kobelev/foodgram-project-react.git
``` 

Перейдите в папку *infra*:

``` 
cd foodgram-project-react/infra/
``` 
 
Запустите контейнеры: 
 
``` 
docker-compose up
``` 
 
Запустите миграции: 
 
``` 
docker-compose exec web python manage.py migrate --noinput
```
 
Соберите статику: 
 
``` 
docker-compose exec web python manage.py collectstatic --no-input  
``` 
 
Создайте суперпользователя, введя логин, почтовый адрес и пароль: 
 
``` 
docker-compose exec web python manage.py createsuperuser 
``` 
 
Заполните базу данных с ингредиентами: 
 
``` 
docker-compose exec web python manage.py loaddata ingredient.json
```

Полный список возможных запросов и соответствующих ответов можно найти в документации *Redoc*.
