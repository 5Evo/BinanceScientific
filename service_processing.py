"""
Набор сервисных функция для обработки датасета
"""
import pandas as pd
from settings import correction


def cursor(df, index):
    return [index, df.loc[index, 'date'], df.loc[index, 'close']]


# def candel_trend(df, index):
#     """
#     функция возвращает 'up' или 'down' в зависиомсти от ...
#     """
#     move_candle = df.loc[index, 'close'] - df.loc[index, 'open']
#     if move_candle > 0:
#         trend = 'up'
#     elif move_candle < 0:
#         trend = 'down'
#     else:
#         trend = 'side'
#     return trend
#

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
