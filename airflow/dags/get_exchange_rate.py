from datetime import datetime, timedelta, date
import requests
import psycopg2
from airflow import DAG
from airflow.models import Variable
from airflow.operators.empty import EmptyOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python import PythonOperator
from airflow.utils.task_group import TaskGroup
from airflow.hooks.postgres_hook import PostgresHook



URL_API = Variable.get('url')
ACCESS_KEY = Variable.get('access_key')
SOURCE = Variable.get('source')
CURRENCIES = Variable.get('currencies')

def get_exchange_rate(**kwargs):
    response = requests.get(URL_API, params={'access_key': ACCESS_KEY,
                                             'source': SOURCE,
                                             'currencies': CURRENCIES})
    data = response.json()
    datetime_rate = data['timestamp']
    value_rate = data['quotes'][SOURCE + CURRENCIES]
     # Сохраняем курс и время в XCom
    ti = kwargs['ti']
    ti.xcom_push(key='value_rate', value=value_rate)
    ti.xcom_push(key='datetime_rate', value=datetime_rate)
    print(f'##### Обменный курс {SOURCE} к  {CURRENCIES} получен ####')
    print('######### datetime_rate: ', datetime_rate)
    print('########## value_rate: ', value_rate)


def insert_exchange_rate_to_db(**kwargs):
    # соединяемся с БД
    hook = PostgresHook(postgres_conn_id='conn_exchange_rate')
    conn = hook.get_conn()
    cur = conn.cursor()
    
    # Получаем курс и время из XCom
    ti = kwargs['ti']
    datetime_rate = ti.xcom_pull(key='datetime_rate')
    value_rate = ti.xcom_pull(key='value_rate')
    
    # Вставляем курс и время в базу данных
    cur.execute(f"""INSERT INTO history_rate_btc_rub (date_rate, currencie_form, currencie_to, value_rate)
                 VALUES (to_timestamp({datetime_rate}), '{SOURCE}', '{CURRENCIES}', {value_rate})""")

    conn.commit()
    cur.close()
    conn.close()
    print("############# Данные успешно вставлены в базу данных ############")



# аргументы дага по умолчанию
default_args = {
    'owner': 'andrey',
    'retries': 5,
    'retry_delay': 5,
    'start_date': datetime(2023, 10, 21),
}

with DAG(dag_id='exchange_rate_to_postgres', 
         default_args=default_args, 
         schedule_interval='*/10 * * * *', 
         description= 'Получение кураса валют с сайта и запись курса в БД Postgresql', 
         catchup=False) as dag:

    start = EmptyOperator(task_id='start') 
    end = EmptyOperator(task_id='end')

    # запрашиваем api обменный курс
    get_rate_from_api = PythonOperator(task_id='get_rate_from_api',
                                       python_callable=get_exchange_rate,
                                       provide_context=True)
    # загружаем в postgresql данные
    insert_rate_in_bd_postgres = PythonOperator(task_id='insert_exchange_rate_in_bd',
                                                python_callable=insert_exchange_rate_to_db,
                                                provide_context=True)

    start >> get_rate_from_api >> insert_rate_in_bd_postgres >> end
