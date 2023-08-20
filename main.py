from utils import (create_params, get_employers_id, get_employees_info, get_vacancies_by_employees, create_database,
                   create_tables, save_employees_to_database, save_vacancies_to_database)
from config import config
from db_manager import DBManager

if __name__ == '__main__':

    db_name = "hh"             # Название базы данных для проекта
    params = create_params()   # Параметры для запроса по API
    config_params = config()   # Параметры для подключения к БД

    # Формирование данных
    print("___________________\nИдет формирование данных о работодателях связанных с IT.")
    employees_ids = get_employers_id(params)
    employees_info = get_employees_info(employees_ids)
    print("___________________\nИдет формирование данных об открытых вакансиях выбранных работодателей")
    vacancies = get_vacancies_by_employees(employees_ids)

    create_database(db_name, config_params)   # Создание базы данных
    create_tables(db_name, config_params)     # Создание таблиц

    if len(vacancies) == 0:
        print("___________________\nВакансии не найдены")

    else:
        # Сохраниние данных в таблицы
        save_employees_to_database(employees_info, config_params)
        save_vacancies_to_database(vacancies, config_params)
        print(f"__________________\nДанные сформированы.\n"
              f"Найдено:\nРаботодателей - {len(employees_info)}\nВакансий - {len(vacancies)}")

        # Цикл взаимодействия с пользователем
        while True:
            action = input("___________________\nВыберите действие:\n"
                           "1 - Получить список всех компаний и количество открытых вакансий у каждой компании.\n"
                           "2 - Получить список всех вакансий с указанием названия вакансии, названия компании, "
                           "зарплаты и ссылки на вакансию.\n"
                           "3 - Получить среднюю зарплату по вакансиям.\n"
                           "4 - Получить список всех вакансий, у которых зарплата выше средней по всем вакансиям.\n"
                           "5 - Получить список всех вакансий по ключевому слову в названии вакансии.\n"
                           "0 - Выход.\n")
            if not action.isdigit():
                print("Не верный ввод! Должна быть цифра!\n")
            elif int(action) not in [0, 1, 2, 3, 4, 5]:
                print("Не верный ввод! Введите цифру от 0 до 5\n")
            elif int(action) == 0:
                print("___________________\nДо скорого!!!")
                break
            else:
                db_manager = DBManager(config_params, db_name)
                result = int(action)
                if result == 1:
                    db_manager.get_companies_and_vacancies_count()
                elif result == 2:
                    db_manager.get_all_vacancies()
                elif result == 3:
                    db_manager.get_avg_salary()
                elif result == 4:
                    db_manager.get_vacancies_with_higher_salary()
                elif result == 5:
                    keyword = input("Введите ключевое слово для поиска: ")
                    db_manager.get_vacancies_with_keyword(keyword)

