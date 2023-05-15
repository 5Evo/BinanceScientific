"""
Хранение переменных проекта
"""
# хранение данных:
BASE_DIR = '/home/alex/binance_data'   # полный путь к папкам для хранения данных
FILENAME = 'data.txt'

# настройки модуля data_processing
is_test = True  # в зависимости от того для теста или для работы - берем короткий датасет или большой
path = '/home/alex/binance_data/'
file_test = '20_3_2023 - 2_4_2023 - 1m.txt'
file_full = '1_1_2020 - 2_4_2023 - 1m.txt'
file_calculated = 'data_calculated.csv'



# Настройки сокетов:
KLINE_INTERVAL = '1s'   # интревал получения данных свечей для сокета 'ks = bm.kline_socket'

# Настройки графического модуля
SCREEN_WIDTH = 1900
SCREEN_HEIGHT = 1000
