import os
import asyncio
from binance import AsyncClient, BinanceSocketManager


def decorator(f):
    def wrapped_f(*args):
        print('Декоратор:', args)
        return f(*args)
    return wrapped_f

@decorator
def func_with_args(arg1, arg2):
    print('основная функция', arg1, arg2)



func_with_args("hello", "world")