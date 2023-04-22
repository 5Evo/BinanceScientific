"""
Набор сервисных функция для обработки датасета
"""
import pandas as pd
from settings import correction


def cursor(df, index):
    return [index, df.loc[index, 'date'], df.loc[index, 'close']]


def init_data_set(data_type='full'):
    from settings import file_full, file_test, path
    file_name = file_full if data_type == 'full' else file_test
    df = pd.read_csv(path + file_name)

    mess = 'Прочитали ПОЛНЫЕ данные' if data_type == 'full' else 'Прочитали тестовые данные'
    print(f'{mess}: {df.shape}')

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

    return df


def mx_corr(price):
    """
    Цена максимального допустимого отката от максимума
    :param price:
    :return:
    """
    #print(f'price: {type(price)}, correction: {type(correction)}')
    return price*(1-correction)


def mn_corr(price):
    """
    Цена максимального допустимого отката от минимума
    :param price:
    :return:
    """
    return price*(1+correction)


def compile_extr(df, index, extr_type):
    """
    соберем запись об экстремуме. формать должен быть:
    [index, date, close_price, 'mx'/'mn', correction_price]
    :param df:
    :param index:
    :param type:
    :return:
    """
    extr = cursor(df, index)
    extr.append(extr_type)
    if extr_type == 'mn':
        corr_price = mn_corr(cursor(df, 0)[2])
    elif extr_type == 'mx':
        corr_price = mx_corr(cursor(df, 0)[2])
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
    return 'trend-' + str(correction)


def add_trend_into_df(df, index, trend_type):
    df.loc[index, col_name_trend()] = trend_type


def search_after_mx(df, extremum_list, index):
    """
    последний найденый экстремум был mx (максимум).
    Дальше может быть как рост, так и падение
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
    limit_corr = mx_corr(prev_mx)
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


def search_after_mn(df, extremum_list, index):
    """
    последний найденый экстремум был mn (минимум).
    Дальше может быть как рост, так и падение
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
    limit_corr = mn_corr(prev_mn)
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

