import requests
import numpy as np
import time
import os
import pickle
from telegram import Bot, InputMediaPhoto
from telegram.ext import Updater, CommandHandler
from telegram.utils.request import Request
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import pandas as pd
import json
import mplfinance as mpf
import matplotlib.dates as mdates
from telegram import Update, ParseMode

TOKEN = ''
CHAT_ID = ''

STATE_FILE = 'state.pickle'


def current_price_func(symbol):
    futures_ticker_url = f"https://fapi.binance.com/fapi/v1/ticker/price?symbol={symbol}"
    futures_ticker_response = requests.get(futures_ticker_url)
    futures_ticker_data = json.loads(futures_ticker_response.text)
    futures_price = float(futures_ticker_data['price'])
    return futures_price


def get_daily_volume(ticker: str) -> float:
    base_url = "https://fapi.binance.com"
    endpoint = "/fapi/v1/ticker/24hr"
    symbol = ticker

    response = requests.get(base_url + endpoint, params={"symbol": symbol})

    if response.status_code != 200:
        raise ValueError(f"Error {response.status_code}: Unable to fetch data for {ticker}")

    data = response.json()
    daily_volume_coins = float(data['volume'])
    weighted_avg_price = float(data['weightedAvgPrice'])

    daily_volume_dollars = round(daily_volume_coins * weighted_avg_price / 1000000, 0)

    return daily_volume_dollars


# Функция для получения исторических данных с Binance
def get_klines(symbol, interval, start_time):
    url = f'https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval={interval}&startTime={start_time}'
    response = requests.get(url)
    response.raise_for_status()
    klines = response.json()
    return klines


# Функция для создания DataFrame с данными
def create_dataframe(klines):
    data = {
        'Timestamp': [int(k[0]) for k in klines],
        'Open': [float(k[1]) for k in klines],
        'High': [float(k[2]) for k in klines],
        'Low': [float(k[3]) for k in klines],
        'Close': [float(k[4]) for k in klines],
        'Volume': [float(k[5]) for k in klines]
    }
    df = pd.DataFrame(data)
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')
    return df


def get_correlation(coin_symbol, base_symbol='BTC', interval='1h', since_last_week=None):
    if not since_last_week:
        since_last_week = int(time.time() * 1000) - (7 * 24 * 60 * 60 * 1000)

    # Получение исторических данных для монеты и базового актива
    coin_klines = get_klines(f'{coin_symbol}', interval, since_last_week)
    base_klines = get_klines(f'{base_symbol}USDT', interval, since_last_week)

    # Создание DataFrame для каждой монеты
    coin_df = create_dataframe(coin_klines)
    base_df = create_dataframe(base_klines)

    # Рассчет корреляции между ценами закрытия
    correlation = coin_df['Close'].corr(base_df['Close'])
    return correlation


def find_filtered_levels(symbol):
    interval = '1h'
    since_last_week = int(time.time() * 1000) - (7 * 24 * 60 * 60 * 1000)
    url = f'https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval={interval}&startTime={since_last_week}'
    futures_ticker_url = f"https://fapi.binance.com/fapi/v1/ticker/price?symbol={symbol}"
    futures_ticker_response = requests.get(futures_ticker_url)
    futures_ticker_data = json.loads(futures_ticker_response.text)
    futures_price = float(futures_ticker_data['price'])

    response = requests.get(url)
    response.raise_for_status()  # Это вызовет исключение, если статус ответа не равен 200
    klines = response.json()

    # Переворачиваем массив
    klines.reverse()

    current_price = float(klines[0][4])

    # Функции для нахождения уровней поддержки и сопротивления
    def find_support_levels(klines):
        support_levels = []
        for i in range(5, len(klines) - 8):
            low = float(klines[i][3])
            previous_lows = [float(k[3]) for k in klines[i - 5:i]]
            next_lows = [float(k[3]) for k in klines[i + 1:i + 9]]

            # Условие для проверки, был ли уровень пересечен
            is_crossed = any(float(k[2]) < low for k in klines[i + 1:i + 9])

            if all(low < pl for pl in previous_lows) and all(low < nl for nl in next_lows) and not is_crossed:
                if futures_price > low:
                    support_levels.append([symbol, low, klines[i][0]])
        return support_levels

    def find_resistance_levels(klines):
        resistance_levels = []
        for i in range(5, len(klines) - 8):
            high = float(klines[i][2])
            previous_highs = [float(k[2]) for k in klines[i - 5:i]]
            next_highs = [float(k[2]) for k in klines[i + 1:i + 9]]

            # Условие для проверки, был ли уровень пересечен
            is_crossed = any(float(k[3]) > high for k in klines[i + 1:i + 9])

            if all(high > ph for ph in previous_highs) and all(high > nh for nh in next_highs) and not is_crossed:
                if high > futures_price:
                    resistance_levels.append([symbol, high, klines[i][0]])
        return resistance_levels

    support_levels = find_support_levels(klines)
    resistance_levels = find_resistance_levels(klines)

    i = 0
    while i < len(support_levels) - 1:
        if support_levels[i + 1][1] < support_levels[i][1]:
            i += 1
        else:
            support_levels.pop(i + 1)

    # Оставляем только уровни сопротивления ниже текущей цены и выше следующего уровня
    i = 0
    while i < len(resistance_levels) - 1:
        if resistance_levels[i + 1][1] > resistance_levels[i][1]:
            i += 1
        else:
            resistance_levels.pop(i + 1)

    data = {
        'Timestamp': [int(k[0]) for k in klines],
        'Open': [float(k[1]) for k in klines],
        'High': [float(k[2]) for k in klines],
        'Low': [float(k[3]) for k in klines],
        'Close': [float(k[4]) for k in klines],
        'Volume': [float(k[5]) for k in klines]
    }

    df = pd.DataFrame(data)
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')

    # Фильтруем уровни поддержки и сопротивления по расстоянию между соседними уровнями
    filtered_support_levels = []
    for i in range(len(support_levels) - 1):
        if abs((support_levels[i][1] - support_levels[i + 1][1]) / support_levels[i][1]) < 0.008:
            filtered_support_levels.append(support_levels[i])
            filtered_support_levels.append(support_levels[i + 1])
    i = 0
    filtered_resistance_levels = []
    for i in range(len(resistance_levels) - 1):
        if abs((resistance_levels[i][1] - resistance_levels[i + 1][1]) / resistance_levels[i][1]) < 0.008:
            filtered_resistance_levels.append(resistance_levels[i])
            filtered_resistance_levels.append(resistance_levels[i + 1])

    # Инвертирование датафрейма
    df = df.iloc[::-1].reset_index(drop=True)

    # Подготовка данных для mplfinance
    df_mpf = df.copy()
    df_mpf.index = pd.to_datetime(df_mpf['Timestamp'], unit='ms')
    df_mpf = df_mpf[['Open', 'High', 'Low', 'Close']]

    # Изменение цвета свечей
    mc = mpf.make_marketcolors(up='g', down='r', inherit=True)
    s = mpf.make_mpf_style(marketcolors=mc, base_mpf_style='yahoo')

    # Создание фигуры и осей
    fig, ax = plt.subplots(figsize=(12, 6))

    # Создание свечного графика без объема
    mpf.plot(df_mpf, type='candle', ax=ax, style=s)

    # Добавление уровней поддержки и сопротивления от свечей
    for level in filtered_resistance_levels:
        index_value = df_mpf.index.get_loc(pd.to_datetime(level[2], unit='ms'))
        ax.axhline(level[1], color='red', linewidth=1, linestyle='-', label=f'{level[1]}',
                   xmin=index_value / len(df_mpf) - 0.03, xmax=1)

    for level in filtered_support_levels:
        index_value = df_mpf.index.get_loc(pd.to_datetime(level[2], unit='ms'))
        ax.axhline(level[1], color='green', linewidth=1, linestyle='-', label=f'{level[1]}',
                   xmin=index_value / len(df_mpf) - 0.04, xmax=1)

    # Удаление дублирования времени и скрытие меток оси X
    ax.get_xaxis().set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
    ax.get_xaxis().set_visible(False)

    # Настройка легенды и общего вида графика
    ax.legend(loc='best')
    ax.set_title(symbol)
    ax.set_ylabel('Цена')
    ax.grid(True, which='both', axis='both', linestyle='-', color='grey', alpha=0.2)

    # Сохранение графика в файл
    plt.savefig(f"{symbol}.png", dpi=300)
    return filtered_support_levels, filtered_resistance_levels


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'rb') as f:
            return pickle.load(f)
    return {}


def save_state(state):
    with open(STATE_FILE, 'wb') as f:
        pickle.dump(state, f)


def send_message_to_channel(bot, message, image_path):
    with open(image_path, 'rb') as image_file:
        bot.send_photo(chat_id=CHAT_ID, photo=image_file, caption=message, parse_mode=ParseMode.HTML)


def check_and_notify_levels(bot, symbol, filtered_support_levels, filtered_resistance_levels, current_price,
                            daily_volume, correlation):
    state = load_state()

    for level in filtered_support_levels:
        level_price = level[1]
        if abs(((current_price - level_price) / current_price)) < 0.01:
            key = f"{symbol}_level_{level_price}"
            if key not in state:
                image_path = f"{symbol.replace('/', '-')}.png"
                message = f"💥 Подход к уровню поддержки {level_price:.5f}({abs((current_price - level_price) / current_price) * 100:.1f}%) на #{symbol}\nДневной объем монеты: {daily_volume}m\nКорреляция с BTC: {correlation:.2f}"
                send_message_to_channel(bot, message, image_path)
                state[key] = True

    for level in filtered_resistance_levels:
        level_price = level[1]
        if abs(((current_price - level_price) / current_price)) < 0.01:
            key = f"{symbol}_level_{level_price}"
            if key not in state:
                image_path = f"{symbol.replace('/', '-')}.png"
                message = f"💥 Подход к уровню сопротивления {level_price:.5f}({abs((current_price - level_price) / current_price) * 100:.1f}%) на #{symbol}\nДневной объем монеты: {daily_volume}m\nКорреляция с BTC: {correlation:.2f}"
                send_message_to_channel(bot, message, image_path)
                state[key] = True

    save_state(state)


def main():
    request = Request(con_pool_size=8)
    bot = Bot(token=TOKEN, request=request)
    with open('C:/STTGS/FUT.txt') as f:
        content = list(filter(None, f.read().split('\n')))
    while True:
        for symbol in content:
            print(symbol)
            daily_volume = get_daily_volume(symbol)
            correlation = get_correlation(symbol)
            if daily_volume > 100 and correlation < 0.95:
                print(symbol)
                print(daily_volume)
                print(correlation)

                klines = get_klines(symbol, "1h", int(time.time() * 1000) - (7 * 24 * 60 * 60 * 1000))
                current_price = current_price_func(symbol)
                print(current_price)

                filtered_support_levels, filtered_resistance_levels = find_filtered_levels(symbol)
                check_and_notify_levels(bot, symbol, filtered_support_levels, filtered_resistance_levels, current_price,
                                        daily_volume, correlation)
        time.sleep(300)


if __name__ == '__main__':
    main()