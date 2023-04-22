# from tqdm.notebook import tqdm  # импортируем красивый progressbar для Jupiter
import sys

import pandas as pd
from tqdm import tqdm
from service_processing import init_data_set, mx_corr, mn_corr, compile_extr, add_trend_into_df, search_after_mx, \
    search_after_mn, col_name_trend
import traceback
from settings import correction


def split_into_movements(df):
    """
    функция разбивки датасета на отдельные движения с размером более заданного.
    Этот размер задается в переменной correction
    """
    # print(df.head(5))
    extremum_list = []
    #print(f'1. __split_into_movements__: Начало {extremum_list = }')

    # Поставим точку первого экстремума и направление тренда:-----------------------------------
    price = []
    index = 0
    price.append(df.loc[index, 'close'])
    while price[0] == price[index]:
        index += 1
        price.append(df.loc[index, 'close'])
    #print(f'2. __split_into_movements__: {price[0] =}, {price[index] =}, {index =}')

    if price[0] < price[index]:
        extr_type = 'mn'
        add_trend_into_df(df, 0, 'down')
    else:
        extr_type = 'mx'
        add_trend_into_df(df, 0, 'up')

    extr0 = compile_extr(df, 0, extr_type)
    #print(f'3. __split_into_movements__: {extr0 = }')
    extremum_list.append(extr0)
    # ---------------------------------------------------------------------------------------


    #print(f'4. __split_into_movements__: {extremum_list =}')
    #print(f'5. __split_into_movements__: {extremum_list[-1][3] =}')

    for index, row in tqdm(df.iterrows(), total=df.shape[0], desc='Поиск экстремумов'):  # оборачиваем 'df.iterrows()' в прогрессбар
        # пропустим первый элемент df
        if index == 0:
            continue

        # проверим последний найденый экстремум и действуемт в зависимости от этого:
        last_extr_type = extremum_list[-1][3]
        if last_extr_type == 'mx':
            search_after_mx(df, extremum_list, index)

        elif last_extr_type == 'mn':
            search_after_mn(df, extremum_list, index)

        else:
            raise Exception("не смогли определить тип экстремума -  (__split_into_movements__)")

    #print(f'__split_into_movements__ FINAL: {len(extremum_list) = }')

    copy_extr_df(df, extremum_list)
    print(df[df['extr'].notnull()].head(20))
    count = df['extr'].count()
    print(f'Перенесли экстремумы. Всего: {count = }')
    return df


def copy_extr_df(df, extremum_list):
    df['extr'] = None
    for extremum in tqdm(extremum_list, desc='Переносим экстремумы в df'):
        #print(f'{extremum}')
        df.loc[extremum[0], 'extr'] = extremum[3]

    # добавим столбец для тренда, размер коррекции (correction) - в названии столбца
    df[col_name_trend()] = None
    # Инициируем первую волну, даже если экстремум стоит на в первой строке. Но берем не первое значение из Списка эестремумов, а второе, тк они чередуются
    last_extr = extremum_list[1][3]

    for index, row in tqdm(df.iterrows(), total=df.shape[0], desc='Разметка по экстремумам'):  # оборачиваем 'df.iterrows()' в прогрессбар
        trend = 'up' if last_extr == 'mn' else 'down'
        df.loc[index, col_name_trend()] = trend
        #print(f'{index}: {df[index, col_name_trend()] = }')

        if row.extr != None:
            last_extr = row.extr


def save_df_to_file(df):
    from settings import file_calculated, path
    df = df.to_csv(path + file_calculated)


def menu(df):
    while True:
        if df.shape[0] == 0:
            print("__________________\nDF не инициирован\n__________________\n")
        elif df.shape[0] == 20160:
            print(f"__________________\nТЕСТОВЫЙ df {df.shape[0]}\n__________________\n")
        elif df.shape[0] == 1710720:
            print(f"__________________\nПОЛНЫЙ df {df.shape[0]}\n__________________\n")
        else:
            raise Exception("Не смогли определить тип df  (__menu()__)")

        print("1. Инициировать тестовый датасет")
        print("2. Инициировать ПОЛНЫЙ датасет")
        print("3. Разбить датасет на движения")
        print("4. Сохранить в файл")
        print("5. Выход")

        choice = input("Выберите действие: ")

        if choice == "1":
            df = init_data_set('test')
        elif choice == "2":
            df = init_data_set('full')
        elif choice == "3":
            df = split_into_movements(df)
            save_df_to_file(df)
        elif choice == "4":
            save_df_to_file(df)
        elif choice == "5":
            sys.exit()
        else:
            print("Неверный выбор")


if __name__ == "__main__":
    df = pd.DataFrame() # подготовим пустой df для нашего датасета
    menu(df)
    # #df = init_data_set('test')
    # df = init_data_set('full')
    # df = split_into_movements(df)
    # save_df_to_file(df)
