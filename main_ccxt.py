"""
Модуль получения котировки с Binance

Используем библиотеку CCXT подключения в Криптобиржам:
https://github.com/ccxt/ccxt/wiki/Manual


"""

import ccxt
import matplotlib.pyplot as plt
import time

exchange = ccxt.binance()

symbol = 'BTC/USDT'

times = []
bids = []
asks = []
spreads = []

plt.ion()  # turn on interactive mode (включили интерактивный режим графика)

fig, ax = plt.subplots()
while True:
    try:
        orderbook = exchange.fetch_order_book(symbol)
        bid = orderbook['bids'][0][0] if len(orderbook['bids']) > 0 else None
        ask = orderbook['asks'][0][0] if len(orderbook['asks']) > 0 else None
        spread = (ask - bid) if (bid and ask) else None
        #print(f'Bid: {bid}, Ask: {ask}, Spread: {spread}')

        times.append(time.time())
        bids.append(bid)
        asks.append(ask)
        spreads.append(spread)

        # подгоним значение шкалы:
        ylim_min = min(bids)
        ylim_max = max(bids)
        ax.set_ylim([ylim_min, ylim_max])
        print(f'Bid: {bid}, Ask: {ask}, Spread: {spread}, Axe Y:{ylim_min} - {ylim_max}')

        # Clear the previous plot
        ax.clear()

        # Plot the updated data
        ax.plot(times, bids, label='Bid')
        ax.plot(times, asks, label='Ask')
        # ax.plot(times, spreads, label='Spread')

        # Add a legend to the plot
        ax.legend()

        # Update the plot
        fig.canvas.draw()

    except Exception as e:
        print(f'An error occurred: {e}')

    time.sleep(1)  # Sleep for 1 second

