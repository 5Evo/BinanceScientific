"""
Модуль используется для загрузки данных о фьючерсах с Бинанса
Стоит задержка в получении данных, чтобы избежать бана за частые запросы.
С помощью этого модуля получен рабочий датасет
получаем фьючерсные данные KLINE
"""

import requests
import pandas as pd
import datetime
import time
import os
from settings import BASE_DIR, FILENAME
from service_bot import check_file, write_to_file, convert_timestamp


def get_binance_klines(trade_symbol, time_interval, start_date, end_date):
    """
    Функция для получения и сохранения котировок по торговой паре на бирже Binance
    trade_symbol - торговая пара
    time_interval - интервал запроса ('1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M')
    start_date - дата начала получения данных в формате (год, месяц, день)
    end_date - дата окончания получения данных в формате (год, месяц, день)
    """
    print('начинаем загрузку данных...')
    start_date = datetime.datetime(*start_date)
    start_timestamp = int(start_date.timestamp() * 1000)

    end_date = datetime.datetime(*end_date, 23, 59, 59)
    end_timestamp = int(end_date.timestamp() * 1000)

    klines = []
    limit = 1000  # максимальное количество строк за один запрос

    while True:
        # Запросить данные по торгам
        response = requests.get(
            f'https://binance.com/fapi/v1/klines?symbol={trade_symbol}&interval={time_interval}&startTime={start_timestamp}&endTime={end_timestamp}&limit={limit}')

        if response.status_code == 200:
            # Данные получены успешно
            print(f'200 - данные получены - {convert_timestamp(start_timestamp)}')
            data = response.json()
            if not data:  # Если данные закончились, выходим из цикла
                break
            klines += data
            start_timestamp = int(data[-1][0]) + 1  # Новая начальная дата - на 1 больше, чем предыдущая конечная дата
        else:
            print(f'Ошибка при получении данных. Код ошибки: {response.status_code}')
            return None
        time.sleep(3)  # Добавляем задержку между запросами

    # Преобразуем данные в датафрейм
    df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time',
                                       'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume',
                                       'taker_buy_quote_asset_volume', 'ignore'])

    # Преобразуем timestamp в дату
    df['date'] = pd.to_datetime(df['timestamp'] / 1000, unit='s')

    # Удаляем ненужные столбцы
    # df.drop(columns=['timestamp', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume',
    #                 'taker_buy_quote_asset_volume', 'ignore'], inplace=True)

    return df


if __name__ == "__main__":


    #sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    symbol = 'BTCUSDT'
    interval = '1m'
    start_date = (2020, 1, 1)
    end_date = (2023, 4, 2)
    print(f'{symbol =}')

    df = get_binance_klines(symbol, interval, start_date, end_date)

    # определим название файла и полный путь
    start_date_str = f'{str(start_date[2])}_{str(start_date[1])}_{str(start_date[0])}'
    end_date_str = f'{str(end_date[2])}_{str(end_date[1])}_{str(end_date[0])}'
    filename = f'{start_date_str} - {end_date_str} - {interval}.txt'
    path = os.path.join(BASE_DIR, filename)
    os.makedirs(BASE_DIR, exist_ok=True)  # создаем папку (если она не существует)

    if df is not None:
        # Сохраняем датафрейм в файл
        with open(path, 'w') as f:
            df.to_csv(f, index=False)

        # Выводим информацию о том, что данные сохранены
        print(f'Данные с {start_date} по {end_date} успешно сохранены в файл fdata.csv')

        # Вычисляем, сколько должно было быть строк в данных с учетом интервала
        days = (datetime.date(end_date[0], end_date[1], end_date[2]) - datetime.date(start_date[0], start_date[1],
                                                                                     start_date[2])).days + 1
        interval_dict = {'1m': 1440, '5m': 288, '15m': 96, '30m': 48, '1h': 24, '2h': 12, '4h': 6, '6h': 4, '12h': 2,
                         '1d': 1}
        expected_rows = days * interval_dict[interval]

        # Сравниваем ожидаемое количество строк с фактическим
        if len(df) == expected_rows:
            print('Количество строк в датафрейме соответствует ожидаемому количеству строк.')
        else:
            print(
                f'Количество строк в датафрейме не соответствует ожидаемому количеству строк. Ожидаемое количество строк: {expected_rows}, фактическое количество строк: {len(df)}')
    else:
        print('Ошибка при получении данных')