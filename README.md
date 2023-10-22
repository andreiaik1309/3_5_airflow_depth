# Структура репозитория
## Папка airflow:
dags:

get_exchange_rate.py (скрипт создает даг)

## папка ddl:
create_table.sql (создает таблицу для сохранения курсов валют)

## docker-compose.yml (запуск контейнера: создается 8 контейнеров)

## параметры соединения с базой данных
{
  "conn_exchange_rate": {
    "conn_type": "postgres",
    "description": "",
    "login": "postgres",
    "password": "postgres",
    "host": "db",
    "port": 5432,
    "schema": "test",
    "extra": ""
  }
}

## переменные
{
    "access_key": "b56fa97aaac1908f5b8f9943cd9a02e5",
    "currencies": "RUB",
    "source": "BTC",
    "url": "http://api.exchangerate.host/live"
}


# Алгоритм работы

скачайте репозиторий на локальный ПК;

в терминале перейдите в директорию, где сохранили данный проект;

в командной строке запустите команду docker-compose up -d;

подключите базу данных к клиенту управления базами данных и изучите:
    Таблица: history_rate_btc_rub (данные в таблицу добавляются каждые 10 минут)

войдите http://localhost:8080, чтобы отследить работу Airflow
