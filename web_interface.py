import sys
import pandas as pd
from flask import Flask, render_template
from flask_socketio import SocketIO
from tqdm import tqdm

from grahp import chart_range_tool
from service_processing import split_into_movements, save_df_to_file, init_data_set, tf_correction
from settings import file_calculated, path
from timeframe_processing import convert_timeframe

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret!'        # Настройка секретного ключа для приложения Flask
socketio = SocketIO(app)                    # Создание экземпляра SocketIO

df = None                                   # Инициируем пустой df

@app.route('/')
def index():
    return render_template('menu.html')


@app.route('/init_test/')
def view_init_test_data():
    global df
    df, message = init_data_set('test')
    html_table = pd.concat([df.head(5), pd.DataFrame(index=['...'] * 2), df.tail(5)]).to_html(index=True)
    return render_template('1.html', result=html_table, action_message=message)


@app.route('/init_full/')
def view_init_full_data():
    global df
    df, message = init_data_set('full')
    html_table = pd.concat([df.head(5), pd.DataFrame(index=['...'] * 2), df.tail(5)]).to_html(index=True)
    return render_template('1.html', result=html_table, action_message=message)


@app.route('/split/')
def view_split():
    global df
    df, extremum_list, message = split_into_movements(df)
    save_df_to_file(df)
    html_table = pd.concat([df.head(50), pd.DataFrame(index=['...'] * 2), df.tail(5)]).to_html(index=True)
    return render_template('1.html', result=html_table, action_message=message)


@app.route('/save_to_file/')
def view_save_to_file():
    global df
    save_df_to_file(df)
    message = f'Сохранили в файл {path+file_calculated}'
    html_table = pd.concat([df.head(5), pd.DataFrame(index=['...'] * 2), df.tail(5)]).to_html(index=True)
    return render_template('1.html', result=html_table, action_message=message)

@app.route('/calculate_correction/')
def view_correction():
    global df
    message = f'Размер коррекции для данного таймфрейма: {round(tf_correction(df)*100,2)}%'
    html_table = pd.concat([df.head(5), pd.DataFrame(index=['...'] * 2), df.tail(5)]).to_html(index=True)
    return render_template('1.html', result=html_table, action_message=message)


@app.route('/change_tf/')
def view_change_tf():
    global df
    df = convert_timeframe(df)
    message = f'Изменение таймфрейма'
    html_table = pd.concat([df.head(5), pd.DataFrame(index=['...'] * 2), df.tail(5)]).to_html(index=True)
    return render_template('1.html', result=html_table, action_message=message)

@app.route('/graph/')
def view_grahf():
    global df
    chart_range_tool(df)
    message = f'График постоен в соседнем окне'
    html_table = pd.concat([df.head(5), pd.DataFrame(index=['...'] * 2), df.tail(5)]).to_html(index=True)
    return render_template('1.html', result=html_table, action_message=message)


@app.route('/stop/')
def view_stop():
    message = 'Остановка программы'
    sys.exit()
    # return render_template('1.html', action_message=message)


if __name__ == '__main__':

    # Внимание! ТОЛЬКО для запуска в локальной среде!
    socketio.run(app, allow_unsafe_werkzeug=True)  # Запуск приложения Flask с использованием SocketIO
    # app.run(debug=True)