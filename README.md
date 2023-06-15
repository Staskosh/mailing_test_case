# Сервис по созданию рассылок по почте.
Возможности сервиса:
1. Отправка рассылок с использованием html макета и списка подписчиков.
2. Для создания рассылки использовать ajax запрос. Форма для создания рассылки запоняется в модальном окне. Использовать библиотеки: jquery, bootstrap.
3. Отправка отложенных рассылок.
4. Использование переменных в макете рассылки. (Пример: имя, фамилия, день рождения из списка подписчиков)
5. Отслеживание открытий писем.
6. Отложенные отправки реализовать при помощи Celery.

## Дисклеймер:
- html макет вставляется в админке и сам пользователь вводит переменные. Упрощение, которое не влияет на функционал.
Риски: пользователь введет не существующие переменные.

- Открытие писем проверяется при помощи tracking pixel, что не является надежным способом, 
так как в почтовом клиенте могут быть отключены изображения или ссылки блокируются сервисом.
Надежный способ это встроить ссылку подтверждение и через контент побудить пользователя потвердить.
Проверено на gmail.com трекинг срабатывает.

- Для tracking pixel нужно создавать надежный токен. (было опущено для простоты)
Риски: могут воспользоваться этой уязвимостью.


# Инструкция по установке

1. Клонируйте репозиторий и перейдите в созданную директорию
```sh
git clone https://github.com/Staskosh/mailing_test_case
```

2. Создайте файл `.env` и заполните его по образцу
```
SECRET_KEY=<secret key>
ALLOWED_HOSTS=<allowed hosts>
DEBUG=<set up debug mode>
EMAIL_HOST=<email host>
EMAIL_HOST_USER=<email host user>
EMAIL_HOST_PASSWORD=<email host password>
EMAIL_PORT=<email port>
CELERY_BROKER_URL=<broker url>
CELERY_RESULT_BACKEND=<celery backend>
DB_PATH=<path to sqlite db>
POSTGRES_USER=<postger user>
POSTGRES_PASSWORD=<postgres password>
POSTGRES_DB=<postgres db name>
```

3. Соберите и поднимите проект с помощью `docker compose`
```sh
docker compose -f docker-compose.dev.yaml up -d --build
```

4. Запустите команду для создания суперпользователя
```sh
docker compose -f docker-compose.dev.yaml exec django ./mailing/manage.py createsuperuser
```

5. Запустите сервер и откройте сайт в браузере по адресу [http://localhost:8000/](http://localhost:8000/)

6. Для тестирования запустите.
```sh
docker compose -f docker-compose.dev.yaml exec django ./mailing/manage.py test
```