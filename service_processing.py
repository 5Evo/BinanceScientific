"""
Набор сервисных функция для обработки датасета
"""
import traceback

import pandas as pd
from tqdm import tqdm
# from tqdm.notebook import tqdm  # импортируем красивый progressbar для Jupiter
from settings import file_full, file_test, path


def tf_correction(df):
    '''
    Определяем относительное изменение цены, меньше которого движение цены включаем в более крупное движение.
    Считаем его как 5 медианных значение размеров свечей в датафрейме
    :param df:
    :return:
    '''
    return df.eval('(high - low) / close').median() * 5


def cursor(df, index):
    return [index, df.loc[index, 'date'], df.loc[index, 'close']]


def init_data_set(data_type='full'):
    file_name = file_full if data_type == 'full' else file_test
    df = pd.read_csv(path + file_name)
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')       # преобразовали данные к типу DatetimeIndex для дальнейшего агрегирования (изменения таймфрейма)
    mess = 'Прочитали ПОЛНЫЕ данные' if data_type == 'full' else 'Прочитали тестовые данные'
    mess = f'{mess}: {df.shape}'
    print(mess)
    print(f'{df.index.name = }')
    # Проверим значение Ignore
    start_shape = df.shape[0]
    ignore_len = len(df[df['ignore'] == 1])

    # удалим строки с Ignore = 1
    df = df[df['ignore'] != 1]
    finish_shape = df.shape[0]
    print(f'Удалили строки Ignore: {start_shape - finish_shape}, {ignore_len = }')

    # Удалим ненужные столбцы:
    df = df.drop(['ignore', 'close_time'], axis=1)
    print(df.head(5))

    return df, mess


def mx_corr(price, correction):
    """
    Цена максимального допустимого отката от максимума
    :param correction:
    :param price:
    :return:
    """
    #print(f'price: {type(price)}, correction: {type(correction)}')
    return price*(1-correction)


def mn_corr(price, correction):
    """
    Цена максимального допустимого отката от минимума
    :param correction:
    :param price:
    :return:
    """
    return price*(1+correction)


def compile_extr(df, index, extr_type):
    """
    соберем запись об экстремуме. формать должен быть:
    [index, date, close_price, 'mx'/'mn', correction_price]
    :param extr_type:
    :param df:
    :param index:
    :param type:
    :return:
    """
    extr = cursor(df, index)
    extr.append(extr_type)
    correction = tf_correction(df)
    if extr_type == 'mn':
        corr_price = mn_corr(cursor(df, 0)[2], correction)
    elif extr_type == 'mx':
        corr_price = mx_corr(cursor(df, 0)[2], correction)
    else:
        raise Exception('Ошибка в функции compile_extr: не смогли определить тип экстремума')
    extr.append(corr_price)
    return extr


def update_last_extremum(extremum_list, correct_extr):
    # обновим последний экстремум в списке
    try:
        extremum_list[-1] = correct_extr
    except Exception as e:
        print(
            f'__update_last_extremum__: не смогли обновить экстремум в списке. {traceback.format_tb(e.__traceback__)}')


def add_new_extr(extremum_list, new_extr):
    # добавим новый экстремум в списке
    try:
        extremum_list.append(new_extr)
    except Exception as e:
        print(
            f'__update_last_extremum__: не смогли обновить экстремум в списке. {traceback.format_tb(e.__traceback__)}')


def col_name_trend():
    return 'trend' # + str(correction)


def add_trend_into_df(df, index, trend_type):
    df.loc[index, col_name_trend()] = trend_type


def search_after_mx(df, extremum_list, index, correction):
    """
    последний найденый экстремум был mx (максимум).
    Дальше может быть как рост, так и падение
    :param correction:
    :param df:
    :param extremum_list: список всех найденных экстремумов
    :param index: текущий индекс свечей
    :return: список всех экстремумов
    """
    # Проверим что не проскочили окончание df:
    if index > df.shape[0]:
        raise Exception(f'__search_after_mx__: Дошли до конца df. {index = }')
    # ------------------------------------------

    # блок определения перменных для функции:
    prev_mx = extremum_list[-1][2]
    last_extr_type = 'mx'
    new_extr_type = 'mn'
    limit_corr = mx_corr(prev_mx, correction)
    current_price = df.loc[index, 'close']
    # ______________________________________

    if current_price > prev_mx:  # цена закрытия снова выросла
        new_extr = compile_extr(df, index, last_extr_type)
        update_last_extremum(extremum_list, new_extr)
        add_trend_into_df(df, index, 'up')

    elif current_price == prev_mx:  # повторили старый экстремум
        upd_ext = compile_extr(df, index, last_extr_type)
        update_last_extremum(extremum_list, upd_ext)  # обновим (передвинем) последний экстремум
        add_trend_into_df(df, index, 'up')

    elif prev_mx > current_price > limit_corr:  # идет откат в пределах допустимого
        add_trend_into_df(df, index, 'up')
        return  # выходим из функциии, ничего не делаем

    elif limit_corr >= current_price:  # откатились сверх нормы. фиксируем новый экстремум:
        new_extr = compile_extr(df, index, new_extr_type)
        add_new_extr(extremum_list, new_extr)
        add_trend_into_df(df, index, 'down')

    else:
        raise Exception('Ошибка в алгоритме: не смогли сравнить current_close')


def search_after_mn(df, extremum_list, index, correction):
    """
    последний найденый экстремум был mn (минимум).
    Дальше может быть как рост, так и падение
    :param correction:
    :param df:
    :param extremum_list: список всех найденных экстремумов
    :param index: текущий индекс свечей
    :return: список всех экстремумов
    """
    # Проверим что не проскочили окончание df:
    if index > df.shape[0]:
        raise Exception(f'__search_after_mx__: Дошли до конца df. {index = }')
    # ------------------------------------------

    # блок определения перменных для функции:
    prev_mn = extremum_list[-1][2]
    last_extr_type = 'mn'
    new_extr_type = 'mx'
    limit_corr = mn_corr(prev_mn, correction)
    current_price = df.loc[index, 'close']
    # ______________________________________

    if current_price < prev_mn:  # цена закрытия снова упала
        new_extr = compile_extr(df, index, last_extr_type)
        update_last_extremum(extremum_list, new_extr)
        add_trend_into_df(df, index, 'down')

    elif current_price == prev_mn:  # повторили старый экстремум
        upd_ext = compile_extr(df, index, last_extr_type)
        update_last_extremum(extremum_list, upd_ext)  # обновим (передвинем) последний экстремум
        add_trend_into_df(df, index, 'down')

    elif prev_mn < current_price < limit_corr:  # идет откат в пределах допустимого
        add_trend_into_df(df, index, 'down')
        return  # выходим из функциии, ничего не делаем

    elif current_price >= limit_corr:  # откатились сверх нормы. фиксируем новый экстремум:
        new_extr = compile_extr(df, index, new_extr_type)
        add_new_extr(extremum_list, new_extr)
        add_trend_into_df(df, index, 'up')

    else:
        raise Exception('Ошибка в алгоритме: не смогли сравнить current_close')


def split_into_movements(df):
    """
    функция разбивки датасета на отдельные движения с размером более заданного.
    Этот размер определяется исходя из медианного значения размера свечей таймфрейма
    """
    # print(df.head(5))
    extremum_list = []
    #print(f'1. __split_into_movements__: Начало {extremum_list = }')

    # Поставим точку первого экстремума и направление тренда:-----------------------------------
    price = []
    index = 0
    price.append(df.loc[index, 'close'])
    correction = tf_correction(df)
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
            search_after_mx(df, extremum_list, index, correction)

        elif last_extr_type == 'mn':
            search_after_mn(df, extremum_list, index, correction)

        else:
            raise Exception("не смогли определить тип экстремума -  (__split_into_movements__)")

    #print(f'__split_into_movements__ FINAL: {len(extremum_list) = }')

    copy_extr_df(df, extremum_list)
    print(df[df['extr'].notnull()].head(20))
    count = df['extr'].count()
    action_message = f'Перенесли экстремумы. Всего: {count = }'
    print(action_message)
    return df, action_message


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
    df.to_csv(path + file_calculated)
