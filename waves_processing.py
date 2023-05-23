"""
В данном модуле находятся отдельно функции для объединения низкоуровневых движений в большие волны: боковики и импульсы
"""
from tqdm import tqdm

from service_processing import init_data_set, split_into_movements, add_extr_different


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
