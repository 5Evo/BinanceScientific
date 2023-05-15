"""
запуск меню для работы с ботом

!!! ВНИМАНИЕ!!!

в начале функции menu(), перед выводом пунктов меню, стоит настройка на конкретные размеры датасетов разработчика.
тестовый - 20160 записей
полный - 1710720 записей
все остальное - будут называться "Конвертированный df"

Для корректоного отображения и вашего понимания - измените под себя эти проверки

"""

import sys
import pandas as pd
from service_processing import init_data_set, tf_correction, split_into_movements, save_df_to_file
from timeframe_processing import convert_timeframe


def menu(df):
    while True:
        if df.shape[0] == 0:
            print("\n__________________\nDF не инициирован:\n__________________")
        elif df.shape[0] == 20160:
            print(f"\n__________________\nТЕСТОВЫЙ df {df.shape[0]}:\n__________________")
        elif df.shape[0] == 1710720:
            print(f"\n__________________\nПОЛНЫЙ df {df.shape[0]}:\n__________________")
        elif df.shape[0]:
            print(f"\n__________________\nКонверитрованный df {df.shape[0]}:\n__________________")
        else:
            raise Exception("Не смогли определить тип df  (__menu()__)")

        print("1. Инициировать тестовый датасет")
        print("2. Инициировать ПОЛНЫЙ датасет")
        print("3. Разбить датасет на движения (с сохранением в файл)")
        print("4. Сохранить в файл")
        print("5. посчитать коррекцию TimeFrame")
        print("6. Изменить TimeFrame (15 минут)")
        print("q. Выход")

        choice = input("Выберите действие: ")

        if choice == "1":
            df = init_data_set('test')
            print(df.columns.tolist())
        elif choice == "2":
            df = init_data_set('full')
        elif choice == "3":
            df = split_into_movements(df)
            save_df_to_file(df)
        elif choice == "4":
            save_df_to_file(df)
        elif choice == "5":
            print(f'{tf_correction(df)}')
        elif choice == "6":
            df = convert_timeframe(df)
        elif choice == "q":
            sys.exit()
        else:
            print("Неверный выбор")


if __name__ == "__main__":
    df = pd.DataFrame() # подготовим пустой df для нашего датасета
    menu(df)
