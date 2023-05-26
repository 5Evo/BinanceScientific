"""
В данном модуле находятся отдельно функции для объединения низкоуровневых движений в большие волны: боковики и импульсы
"""
from tqdm import tqdm

from service_processing import init_data_set, split_into_movements


def add_extr_different(extremum_lst):
    """
    проверяем волновую структуру движений.
    для этого вычисляем разницу между текущим экстремумом и предыдущим (сравниваем между собой отдельно максимумы и отдельно минимумы)
    по разнице между соседними максимумами и соседними минимумами видно боковик или импульс
    В словари Extremum из списка extremum_list добавим начения "diff"
    """
    print(f'Начало процедуры _add_extr_different()_,  {extremum_lst[0].keys() =}')
    с = input(f'Продолжим? нажми любую клавишу')
    for index, extremum in tqdm(enumerate(extremum_lst), desc='Расчет разницы экстремумов в df'):
        if index in (0, 1):     # для первых 2-х экстремумов не можем вычислить разность, поэтому приравниваем их 0
            extremum_lst[index]['diff'] = 0
        else:                   # для остальных экстремумов считаем относительное изменение
            different = (extremum_lst[index]['close'] - extremum_lst[index-2]['close'])/extremum_lst[index]['close']
            extremum_lst[index]['diff'] = different
        # print(extremum)       # выводит огромный список всех экстремумов

    # добавим "impulse_up", "imnpule_down", "flat" в extremum_list (найдем импульсы)
    # импульсом считаем 4 и более экстремума с одинаковым знаком different
    for index, extremum in tqdm(enumerate(extremum_lst), desc='Разбиваем на импульсы и боковики:'):
        # проверим в списке экстремумов все точки окном в 4 экстремума
        start_window = max(0, index-3)
        stop_window = min(len(extremum_lst)-4, index)
        extremum_set = []       # подготовим список для 4 значений different
        print(f'точка {index}, {start_window =} {stop_window =}:')

        for j in range(start_window, stop_window+1):
            extremum_set.append(extremum_lst[j]['diff'])
            # print(f'     ({j}, {j + 3}), {index in range(j, j + 4)}')

        if all(diff > 0 for diff in extremum_set):
            impulse = True
            print(f'impulse_up: {extremum_set}')
            # TODO: поставить признак impulse_up
        elif all(diff < 0 for diff in extremum_set):
            impulse = True
            print(f'impulse_down: {extremum_set}')
            # TODO: поставить признак impulse_down
        else:
            impulse = False
            print(f'flat: {extremum_set}')
            # TODO: поставить признак flat (или оставить без изменений, если был выставлен ранее)

    return extremum_lst


def identify_the_waves(df, extremum_list):
    """
    после выделения низкоуровневых движений объединим их в волны: в боковики и импульсы
    :param df:
    :param extremum_list:
    :return:
    """
    pass


if __name__ == "__main__":

    # подготовим датасет для работы:
    df, message = init_data_set('test')
    df, extremum_list, message = split_into_movements(df)
    extremum_list = add_extr_different(extremum_list)
