"""
Набор функций для работы с различными Таймфраймами
"""
import pandas as pd


def convert_timeframe(df, new_tf='15min'):
    '''
    Конвертор базового DataFrame к новому таймфрейму
    Cтобцы исходного DF:
    ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'date']

    :param df: исходный df c 1 минутным таймфреймом
    :param new_tf: новый таймфрейм, к которому приводим данные
        может принимать значения:
        ‘D’: ежедневно
        ‘W’: еженедельно
        ‘M’: ежемесячно
        ‘Q’: ежеквартально
        ‘Y’: ежегодно
        ‘H’: каждые часы
        ‘T’: каждые минуты
        можно комбинироавать таймфпеймы: freq="2h20min"
        https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Grouper.html#pandas-grouper
        https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases
    :return:
    '''
    print(f'Начальный инлекс: {df.index = }')
    df = df.set_index('timestamp')

    new_df = df.groupby(pd.Grouper(freq=new_tf)).agg({"open": "first",
                                                      "high": "max",
                                                      "low": "min",
                                                      "close": "min",
                                                      "volume": "sum",
                                                      'quote_asset_volume': 'sum',
                                                      'number_of_trades': 'sum',
                                                      'taker_buy_base_asset_volume': 'sum',
                                                      'taker_buy_quote_asset_volume': 'sum',
                                                      'date': "first"})

    new_df['new_index'] = range(len(new_df))  # добавляем новый столбец с последовательными значениями
    new_df.reset_index(inplace=True)
    new_df.rename(columns={'index': 'timestamp  '}, inplace=True)
    new_df.set_index('new_index', inplace=True)  # устанавливаем новый столбец в качестве индекса
    print(f'новый индекс: {new_df.index = }')
    return new_df


if __name__ == "__main__":
    pass