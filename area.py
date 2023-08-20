import requests


def get_country_id() -> str:
    """
    Получете по API id страны, соответствующий введенному пользователем названию страны
    :return: id страны
    """
    while True:
        country_name = input("Введите название страны если не важно, нажмите ENTER:  ").lower()
        countries = requests.get('https://api.hh.ru/areas/countries').json()
        countries_names = []
        for con in countries:
            countries_names.append(con['name'].lower())
        if country_name == '':
            break
        else:
            if country_name not in countries_names:
                print("Такой страны нет в списке!")
                continue
            else:
                for con in countries:
                    if con['name'].lower() == country_name:
                        return con['id']
            break


def get_region_id(country_id: str) -> str:
    """
    Получете по API id региона, соответствующий введенному пользователем названию региона
    :param country_id: id страны
    :return: id региона
    """
    while True:
        region_name = input("Введите название региона если не важно, нажмите ENTER:  ").lower()
        regions = requests.get(f'https://api.hh.ru/areas/{country_id}').json()['areas']
        regions_names = []
        for reg in regions:
            regions_names.append(reg['name'].lower())
        if region_name == '':
            break
        else:
            if region_name not in regions_names:
                print("Такого региона нет в списке!")
                continue
            else:
                for reg in regions:
                    if reg['name'].lower() == region_name:
                        return reg['id']
            break


def get_city_id(region_id: str) -> str:
    """
    Получете по API id города, соответствующий введенному пользователем названию города
    :param region_id: id региона
    :return: id города
    """
    while True:
        city_name = input("Введите название города если не важно, нажмите ENTER:  ").lower()
        cities = requests.get(f'https://api.hh.ru/areas/{region_id}').json()['areas']
        cities_names = []
        for cty in cities:
            cities_names.append(cty['name'].lower())
        if city_name == '':
            break
        else:
            if city_name not in cities_names:
                print("Такого города нет в списке!")
                continue
            else:
                for cty in cities:
                    if cty['name'].lower() == city_name:
                        return cty['id']
            break

