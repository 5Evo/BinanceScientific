"""
Данные, которые вы получаете в ответ на запрос торговых данных на Binance, представляют собой словарь Python.

Каждый ключ в словаре соответствует определенному атрибуту торговых данных. Вот что означают ключи в вашем словаре:

‘e’: ‘trade’ - тип события (в данном случае - торговля)
‘E’: 1679756947225 - время события (в миллисекундах)
‘s’: ‘BTCUSDT’ - символ валютной пары
‘t’: 3057021005 - идентификатор сделки
‘p’: ‘27522.38000000’ - цена сделки
‘q’: ‘0.00066000’ - количество базовой валюты (в данном случае - BTC)
‘b’: 20593613754 - идентификатор покупателя
‘a’: 20593613661 - идентификатор продавца
‘T’: 1679756947224 - время сделки (в миллисекундах)
‘m’: False - тип ордера (True для ордеров типа maker)
‘M’: True - флаг мейкера

Тип ордера (order type) - это тип ордера на покупку или продажу.
В вашем случае тип ордера - это ордер типа taker (False), который сразу исполняется по текущей цене.

Флаг мейкера (maker flag) - это флаг, который указывает, является ли ордер мейкером или тейкером.
Мейкер (maker) - это тот, кто размещает лимитный ордер на покупку или продажу.
Тейкер (taker) - это тот, кто исполняет лимитный ордер мейкера.
"""

import asyncio
import cProfile
from binance import AsyncClient, BinanceSocketManager
from service_bot import check_file, write_to_file
from settings import KLINE_INTERVAL, FILENAME

######## задел на будущее: получение ключей из окружения  ######
# from dotenv import load_dotenv
# load_dotenv()
# API_TOKEN = os.getenv('API_TOKEN')
# SECRET_TOKEN = os.getenv('SECRET_TOKEN')


#  определяем функцию для обработки сообщений из сокета сделок
@write_to_file
async def process_res(res):
    try:
        print(res)
        return res
    except Exception as e:
        print(f"An error occurred: {e}")


# определяем функцию для обработки сообщений из сокета стакана
@write_to_file
async def process_orderbook(orderbook):
    try:
        print(orderbook)
        return orderbook
    except Exception as e:
        print(f"An error occurred: {e}")

# определяем функцию для обработки сообщений из сокета стакана
@write_to_file
async def process_candle(candle):
    try:
        print(candle)
        return candle
    except Exception as e:
        print(f"An error occurred: {e}")


async def my_bot():
    client = await AsyncClient.create()     # создаем асинхронное подключение к Binance
    bm = BinanceSocketManager(client)       # создаем менеджер сокетов

    # start any sockets here, i.e a trade socket
    ts = bm.trade_socket('BTCUSDT')  # создаем сокет для торговли валютной парой BTCUSDT
    ds = bm.depth_socket('BTCUSDT')  # создаем сокет для получения данных стакана валютной пары BTCUSDT
    ks = bm.kline_socket('BTCUSDT', interval=KLINE_INTERVAL)

    # then start receiving messages
    async with \
            ds as dscm, \
            ts as tscm, \
            ks as ksm:  # начинаем получать сообщения из сокетов

        while True:
            res = await tscm.recv()     # получаем сообщение из сокета сделок
            #print(f'{res = }')        # выводим сообщение на экран
            await process_res(res)      # запускаем сохранение в файл и консольный вывод

            # orderbook = await dscm.recv()       # получаем сообщение из сокета стакана
            # #print(f'{orderbook = }')          # выводим сообщение на экран
            # await process_orderbook(orderbook)  # запускаем сохранение в файл и консольный вывод

            canlde_res = await ksm.recv()      # получаем сообщение из сокета свечей
            #print(f'{canlde_res = }')          # выводим сообщение на экран
            await process_candle(canlde_res)


if __name__ == "__main__":

    loop = asyncio.new_event_loop()
    #loop.run_until_complete(my_bot())
    loop.run_until_complete(cProfile.run('my_bot()'))