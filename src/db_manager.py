import psycopg2


class DBManager:
    """Класс для работы с базой данных"""

    def __init__(self, params, db_name):
        self.__params = params
        self.__db_name = db_name
        self.conn = psycopg2.connect(database=self.db_name, **self.params)
        self.cur = self.conn.cursor()

    @property
    def params(self):
        return self.__params

    @property
    def db_name(self):
        return self.__db_name

    def get_companies_and_vacancies_count(self):
        """
        Получает список всех компаний и количество открытых вакансий у каждой компании
        """
        self.cur.execute("SELECT employees.name, COUNT(*) FROM vacancies "
                         "JOIN employees ON vacancies.employer_id = employees.id "
                         "GROUP BY employees.name")
        result = self.cur.fetchall()
        for row in result:
            print(f"{row[0]}\nКоличество открытых вакансий:  {row[1]}\n")
        print(f"___________________\nВсего компаний: {len(result)}")
        self.cur.close()
        self.conn.close()

    def get_all_vacancies(self):
        """
        Получает список всех вакансий с указанием названия вакансии, названия компании, зарплаты и ссылки на вакансию
        """
        self.cur.execute("SELECT vacancies.name, employees.name, salary_from, salary_to, currency, vacancies.url "
                         "FROM vacancies JOIN employees ON vacancies.employer_id = employees.id")
        result = self.cur.fetchall()
        for row in result:
            print(f"{row[0]}\nКомпания: {row[1]}\nЗарплата: {row[2]} - {row[3]} {row[4]}\nURL: {row[5]}\n")
        print(f"___________________\nВсего вакансий: {len(result)}")
        self.cur.close()
        self.conn.close()

    def get_avg_salary(self):
        """
        Получает среднюю зарплату по вакансиям. Берется только зарплата в рублях
        """
        self.cur.execute("SELECT AVG(salary_from) FROM vacancies "
                         "WHERE currency = 'RUR'")
        result = self.cur.fetchall()
        for row in result:
            print(f"___________________\nСредняя зарплата в рублях по всем вакансиям: {round(row[0])} руб.")
        self.cur.close()
        self.conn.close()

    def get_vacancies_with_higher_salary(self):
        """
        Получает список всех вакансий, у которых зарплата выше средней по всем вакансиям.
        Берутся только вакансии с зарплатой в рублях
        """
        self.cur.execute("SELECT * FROM vacancies "
                         "WHERE salary_from > (SELECT AVG(salary_from) FROM vacancies WHERE currency = 'RUR') "
                         "AND currency = 'RUR'")
        result = self.cur.fetchall()
        for row in result:
            print(f"{row[1]}\nГород {row[2]}\nЗарплата от {row[4]} руб.\nОпубликовано {row[7]}\n")
        print(f"___________________\nВсего вакансий: {len(result)}")
        self.cur.close()
        self.conn.close()

    def get_vacancies_with_keyword(self, keyword):
        """
        Получает список всех вакансий, в названии которых содержится переданное в метод слово
        :param keyword: ключевое слово, переданное в метод
        """
        self.cur.execute(f"SELECT * FROM vacancies WHERE name LIKE '%{keyword}%'")
        result = self.cur.fetchall()
        for row in result:
            print(f"{row[1]}\nГород {row[2]}\nОпубликовано {row[7]}\n")
        print(f"___________________\nВсего вакансий: {len(result)}")
        self.cur.close()
        self.conn.close()
