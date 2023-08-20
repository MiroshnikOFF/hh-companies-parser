import requests
import psycopg2
from psycopg2 import errors

from area import get_country_id, get_region_id, get_city_id


def create_params() -> dict:
    """
    Создает параметры для запроса списка работодателей по критериям пользователя
    :return: словарь с параметрами
    """
    # user_text = input("Введите ключевое слово для поиска работодателя, если не важно, нажмите ENTER:  ")
    # if user_text == '':
    #     user_text = None
    area_id = None
    country_id = get_country_id()
    if country_id:
        area_id = country_id
        region_id = get_region_id(area_id)
        if region_id:
            area_id = region_id
            city_id = get_city_id(area_id)
            if city_id:
                area_id = city_id
    params = {
        'page': 19,  # Количество страниц для выборки
        'per_page': 100,  # Количество работодателей на странице
        'only_with_vacancies': True,  # Только с активными вакансиями
        'text': "it",  # Ключевое слово для поиска - it
        'area': area_id
    }
    return params


def get_employers_id(params: dict) -> list:
    """
    Получает список id работодателей по API
    :param params: параметры для запроса
    :return: список id работодателей
    """
    employers_id = []
    while params['page'] > 0:
        response_emp = requests.get('https://api.hh.ru/employers', params=params).json()['items']
        for emp in response_emp:
            employers_id.append(emp['id'])
        params['page'] -= 1
    return employers_id


def get_employees_info(employers_id: list) -> list:
    """
    Получает данные о работодателях по API используя id работодателя
    :param employers_id: список id работодателей
    :return: список словарей с данными о работодателях
    """
    employees_info = []
    for emp_id in employers_id:
        response = requests.get(f"https://api.hh.ru/employers/{emp_id}").json()
        employees_info.append(response)
    return employees_info


def get_vacancies_by_employees(employees_id: list) -> list:
    """
    Получает список вакансий по id работодателей
    :param employees_id: список id работодателей
    :return: список вакансий
    """
    vacancies = []
    for emp_id in employees_id:
        response_vac = requests.get(f"https://api.hh.ru/vacancies?employer_id={emp_id}").json()['items']
        vacancies.extend(response_vac)
    return vacancies


def create_database(db_name: str, params: dict) -> None:
    """
    Создает базу данных с полученным именем
    :param db_name: имя базы данных
    :param params: словарь с параметрами для подключения к базе данных
    """
    conn = psycopg2.connect(database='postgres', **params)
    conn.autocommit = True
    cur = conn.cursor()
    try:
        cur.execute(f"DROP DATABASE {db_name}")                                   # Удалить базу
    except psycopg2.errors.InvalidCatalogName:                                    # Такой базы нет
        cur.execute(f"CREATE DATABASE {db_name}")                                 # Создать базу
    except psycopg2.errors.ObjectInUse:                                           # Есть открытые сессии
        cur.execute(f"SELECT pg_terminate_backend(pid) "
                    f"FROM pg_stat_activity "                                     # Сбросить все подключения к БД
                    f"WHERE pid <> pg_backend_pid() AND datname = '{db_name}'")
        cur.execute(f"DROP DATABASE {db_name}")                                   # Удалить базу
        cur.execute(f"CREATE DATABASE {db_name}")                                 # Создать базу
    else:
        cur.execute(f"CREATE DATABASE {db_name}")                                 # Создать базу

    finally:
        cur.close()
        conn.close()


def create_tables(db_name: str, params: dict) -> None:
    """
    Создает две таблицы employees и vacancies в базе данных с полученным именем
    :param db_name: имя базы данных, в которой создает таблицы
    :param params: словарь с параметрами для подключения к базе данных
    """
    with psycopg2.connect(database=db_name, **params) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE employees (
                    id INT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    url VARCHAR(200),
                    area VARCHAR(100),
                    open_vacancies INT
                )
            """)
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE vacancies (
                    id INT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    area VARCHAR(100),
                    employer_id INT REFERENCES employees(id), 
                    salary_from INT,
                    salary_to INT,
                    currency VARCHAR(10),
                    published DATE,
                    url VARCHAR(200)
                )
            """)

    conn.close()


def save_employees_to_database(employees: list, params: dict) -> None:
    """
    Сохраняет данные работодателей в таблицу employees
    :param employees: список словарей с данными работодателей
    :param params: словарь с параметрами для подключения к базе данных
    """
    conn = psycopg2.connect(database='hh', **params)
    for employer in employees:
        emp_id = int(employer['id'])
        name = employer['name']
        url = employer['site_url']
        area = employer['area']['name']
        open_vacancies = employer['open_vacancies']
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO employees (id, name, url, area, open_vacancies)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (emp_id, name, url, area, open_vacancies)
                )

    conn.commit()
    conn.close()


def save_vacancies_to_database(vacancies: list, params: dict) -> None:
    """
    Сохраняет данные вакансий в таблицу vacancies
    :param vacancies: список словарей с данными вакансий
    :param params: словарь с параметрами для подключения к базе данных
    """
    conn = psycopg2.connect(database='hh', **params)
    for vacancy in vacancies:
        vac_id = int(vacancy['id'])
        name = vacancy['name']
        area = vacancy['area']['name']
        employer_id = vacancy['employer']['id']
        if vacancy['salary']:
            salary_from = vacancy['salary']['from']
            salary_to = vacancy['salary']['to']
            currency = vacancy['salary']['currency']
        else:
            salary_from = None
            salary_to = None
            currency = None
        published = vacancy['published_at']
        url = vacancy['apply_alternate_url']
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO vacancies (id, name, area, employer_id, salary_from, salary_to, currency, published, url)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (vac_id, name, area, employer_id, salary_from, salary_to, currency, published, url)
                 )

    conn.commit()
    conn.close()

