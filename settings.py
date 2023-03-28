"""
Хранение переменных проекта
"""
# хранение данных:
BASE_DIR = '/home/alex/binance_data'   # полный путь к папкам для хранения данных
FILENAME = 'data.txt'


# Настройки сокетов:
KLINE_INTERVAL = '1s'   # интревал получения данных свечей для сокета 'ks = bm.kline_socket'

if __name__ == "__main__":
    pass