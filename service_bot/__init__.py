"""
Функции пакета используются при получения данных фьючерсов в "take_fapi.py"
"""

import os
import datetime
from settings import BASE_DIR, FILENAME


def convert_timestamp(ts):
    '''
    функция переводит время в милисекундах (timestamp) от Binance в обычное время
    :param ts:время в милисекундах
    :return: обычное время
    '''
    dt = datetime.datetime.fromtimestamp(ts / 1000.0)
    return dt


def path_to_data(data):
    '''
    Функция конвертирует дату в имена папок, и создает все необходимые папки и файлы для записи данных.
    использыуется в декораторе write_to_file().
    :param data: дата данных
    :return: полный путь к файлу
    '''
    # now = datetime.datetime.now()  # создаем объект datetime, который представляет текущую дату и время

    year = str(data.year)  # извлекаем год из объекта datetime и преобразуем его в строку
    month = str(data.month).zfill(2)  # извлекаем месяц из объекта datetime и преобразуем его в строку с ведущим нулем, если месяц состоит из одной цифры
    day = str(data.day).zfill(2)  # извлекаем день из объекта datetime и преобразуем его в строку с ведущим нулем, если день состоит из одной цифры

    path = os.path.join(BASE_DIR, year, month, day)  # создаем путь к папке, которая будет содержать файл
    os.makedirs(path, exist_ok=True)  # создаем папку (если она не существует)

    filename = data.strftime("%Y-%m-%d.txt")  # создаем имя файла в формате YYYY-MM-DD_HH-MM-SS.txt ("%Y-%m-%d_%H-%M-%S.txt")
    filepath = os.path.join(path, filename)  # создаем полный путь к файлу
    return filepath


def check_file(filename):
    print('Check_file Старт - ОК')
    full_path = os.path.abspath(filename)
    print(full_path)

    if os.path.isfile(filename):
        print(f"Файл {full_path} уже существует")
    else:
        with open(filename, "w") as f:
            f.write("Пример текста")
        print(f"Файл {full_path} создан")


# определяем декоратор для записи в файл
def write_to_file(func):
    """
    Декоратор для записи данных в файл.
    :param func:
    :return:
    """
    async def wrapper(*args, **kwargs):
        # print(f'запуск Декоратора write_to_file -\n {type(args)}, {args[0] =} \n {args[0]["E"] =}')
        try:
            data = convert_timestamp(args[0]['E'])
            # print(f'Дата в ответе: {data}')
        except Exception as e:
            print(f'{e}: Не смогли извлечь дату, берем текущую ')
            data = datetime.datetime.now()

        # print(f'получаем дату в декораторе: {data}')

        try:
            res = await func(*args, **kwargs)
            with open(path_to_data(data), 'a') as f:  # параметр 'a' - открытие файла для добавления данных
                f.write(f'{res}\n')
        except Exception as e:
            print(f"An error occurred: {e}")
    return wrapper

