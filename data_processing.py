# from tqdm.notebook import tqdm  # импортируем красивый progressbar для Jupiter
from tqdm import tqdm
from service_processing import init_data_set,  mx_corr, mn_corr, compile_extr
import traceback


def update_last_extremum(extremum_list, correct_extr):
    # обновим последний экстремум в списке
    try:
        extremum_list[-1] = correct_extr
    except Exception as e:
        print(f'__update_last_extremum__: не смогли обновить экстремум в списке. {traceback.format_tb(e.__traceback__)}')


def add_new_extr(extremum_list, new_extr):
    # добавим новый экстремум в списке
    try:
        extremum_list.append(new_extr)
    except Exception as e:
        print(f'__update_last_extremum__: не смогли обновить экстремум в списке. {traceback.format_tb(e.__traceback__)}')


def search_after_mx(extremum_list, index):
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

    if current_price > prev_mx:   # цена закрытия снова выросла
        new_extr = compile_extr(df, index, last_extr_type)
        update_last_extremum(extremum_list, new_extr)

    elif current_price == prev_mx:    # повторили старый экстремум
        upd_ext = compile_extr(df, index, last_extr_type)
        update_last_extremum(extremum_list, upd_ext)        # обновим (передвинем) последний экстремум

    elif prev_mx > current_price > limit_corr:              # идет откат в пределах допустимого
        return                                              # выходим из функциии, ничего не делаем
 
    elif limit_corr >= current_price:       # откатились сверх нормы. фиксируем новый экстремум:
        new_extr = compile_extr(df, index, new_extr_type)
        add_new_extr(extremum_list, new_extr)

    else:
        raise Exception('Ошибка в алгоритме: не смогли сравнить current_close')


def search_after_mn(extremum_list, index):
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

    elif current_price == prev_mn:  # повторили старый экстремум
        upd_ext = compile_extr(df, index, last_extr_type)
        update_last_extremum(extremum_list, upd_ext)  # обновим (передвинем) последний экстремум

    elif prev_mn < current_price < limit_corr:  # идет откат в пределах допустимого
        return  # выходим из функциии, ничего не делаем

    elif current_price >= limit_corr:  # откатились сверх нормы. фиксируем новый экстремум:
        new_extr = compile_extr(df, index, new_extr_type)
        add_new_extr(extremum_list, new_extr)

    else:
        raise Exception('Ошибка в алгоритме: не смогли сравнить current_close')


def split_into_movements(df):
    """
    функция разбивки датасета на отдельные движения с размером более заданного.
    Этот размер задается в переменной correction
    """
    from settings import correction

    col_trend = 'trend-' + str(correction)
    df[col_trend] = None  # добавим столбец для тренда, критерий размера (correction) - в названии столбца

    extremum_list = []
    #print(f'1. __split_into_movements__: Начало {extremum_list = }')

    # Поставим точку первого экстремума:
    price = []
    index = 0
    price.append(df.loc[index, 'close'])
    while price[0] == price[index]:
        index += 1
        price.append(df.loc[index, 'close'])
    #print(f'2. __split_into_movements__: {price[0] =}, {price[index] =}, {index =}')
    extr_type = 'mn' if price[0] < price[index] else 'mx'
    extr0 = compile_extr(df, 0, extr_type)
    #print(f'3. __split_into_movements__: {extr0 = }')
    # -----------------------------

    extremum_list.append(extr0)
    #print(f'4. __split_into_movements__: {extremum_list =}')
    #print(f'5. __split_into_movements__: {extremum_list[-1][3] =}')

    for index, row in tqdm(df.iterrows(), total=df.shape[0]):  # оборачиваем 'df.iterrows()' в прогрессбар
        # пропустим первый элемент df
        if index == 0:
            continue

        # проверим последний найденый экстремум и действуемт в зависимости от этого:
        last_extr_type = extremum_list[-1][3]
        if last_extr_type == 'mx':
            search_after_mx(extremum_list, index)
            # print('re-re')
            pass
        elif last_extr_type == 'mn':
            search_after_mn(extremum_list, index)
            # print('ку-ку')

        else:
            raise Exception("не смогли определить тип экстремума -  (__split_into_movements__)")

    print(f'__split_into_movements__ FINAL: {len(extremum_list) = }')


    # print(df.head(5))


if __name__ == "__main__":
    df = init_data_set('test')
    split_into_movements(df)
