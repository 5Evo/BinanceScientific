import pandas as pd
from flask import Flask, render_template
from flask_socketio import socketio
from tqdm import tqdm

from service_processing import split_into_movements, save_df_to_file, init_data_set, tf_correction

app = Flask(__name__)
df = None

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
    df, message = split_into_movements(df)
    save_df_to_file(df)
    html_table = pd.concat([df.head(5), pd.DataFrame(index=['...'] * 2), df.tail(5)]).to_html(index=True)
    return render_template('1.html', result=html_table, action_message=message)

@app.route('/save_to_file/')
def view_save_to_file():
    global df
    save_df_to_file(df)
    message = 'Сохранили в файл'
    html_table = pd.concat([df.head(5), pd.DataFrame(index=['...'] * 2), df.tail(5)]).to_html(index=True)
    return render_template('1.html', result=html_table, action_message=message)

@app.route('/calculate_correction/')
def view_correction():
    global df
    message = f'Размер коррекции для данного таймфрейма: {round(tf_correction(df)*100,2)}%'
    html_table = pd.concat([df.head(5), pd.DataFrame(index=['...'] * 2), df.tail(5)]).to_html(index=True)
    return render_template('1.html', result=html_table, action_message=message)


if __name__ == '__main__':
    app.run(debug=True)