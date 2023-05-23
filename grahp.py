from math import pi
import pandas as pd
from service_processing import init_data_set
from bokeh.client import pull_session
from bokeh.plotting import figure, show, output_file
from bokeh.models import RangeSlider, CustomJS, Range1d, LinearAxis, RangeTool, ColumnDataSource
from bokeh.layouts import column, layout

from settings import SCREEN_HEIGHT, SCREEN_WIDTH
from service_processing import col_name_trend, split_into_movements


def chart_range_slider(df):
    """
    инстурмент HoverTool выводит подсказки на график при наведении курсора мыши на данные
    :param df:
    :return:
    """
    df["date"] = pd.to_datetime(df["date"])

    inc = (df[col_name_trend()] == 'up')
    dec = (df[col_name_trend()] == 'down')

    tools: str = "pan,wheel_zoom,box_zoom,reset,save"
    p = figure(tools=tools, width=SCREEN_WIDTH, height=SCREEN_HEIGHT,
               title="My test chart", background_fill_color="#efefef")
    p.xaxis.major_label_orientation = 1  # radians
    p.x_range.range_padding = 0.05

    # map dataframe indices to date strings and use as label overrides
    p.xaxis.major_label_overrides = {
        i: date.strftime('%b %d') for i, date in zip(df.index, df["date"])
    }

    # one tick per week (5 weekdays)
    p.xaxis.ticker = list(range(df.index[0], df.index[-1], 20))

    p.segment(df.index, df.high, df.index, df.low, color="black")

    p.vbar(df.index[dec], 0.6, df.open[dec], df.close[dec], color="red")
    p.vbar(df.index[inc], 0.6, df.open[inc], df.close[inc], color='blue')

    volume = df['volume']  # массив данных для объема сделок
    volume_inc = volume.where(inc)  # массив данных для объема сделок при росте цены
    volume_dec = volume.where(dec)  # массив данных для объема сделок при падении цены
    p.vbar(df.index[dec], 0.6, volume_dec, color="red", width=1, y_range_name="volume")
    p.vbar(df.index[inc], 0.6, volume_inc, color='blue', width=1, y_range_name="volume")
    #
    # p.extra_y_ranges = {"volume": Range1d(start=0, end=volume.max() * 2)}
    # p.add_layout(LinearAxis(y_range_name="volume"), 'right')

    range_slider = RangeSlider(start=df.index[0], end=df.index[-1], value=(df.index[0], df.index[-1]), step=1)
    range_slider.js_on_change('value', CustomJS(args=dict(xr=p.x_range), code="""
        xr.start = cb_obj.value[0]
        xr.end = cb_obj.value[1]
    """))
    l = layout([[range_slider]], [p])
    show(l)

    # show(p)


def chart_range_tool(df):
    """
    инстурмент HoverTool выводит подсказки на график при наведении курсора мыши на данные
    :param df:
    :return:
    """
    df["date"] = pd.to_datetime(df["date"])

    inc = (df[col_name_trend()] == 'up')
    dec = (df[col_name_trend()] == 'down')

    tools: str = "pan,wheel_zoom,box_zoom,reset,save"
    p = figure(tools=tools, width=SCREEN_WIDTH, height=SCREEN_HEIGHT-130,
               title="My test p", background_fill_color="#efefef", x_range=(0, df.shape[0]))

    p.xaxis.major_label_orientation = 1.57  # наклон меток Х в радианах
    #p.x_range = Range1d(0, df.shape[0])

    # map dataframe indices to date strings and use as label overrides
    p.xaxis.major_label_overrides = {
        i: date.strftime('%d %b %H:%M') for i, date in zip(df.index, df["date"])
    }

    # определим шаг тиков:
    ticks = 100
    step = int(df.shape[0]/ticks)
    p.xaxis.ticker = list(range(df.index[0], df.index[-1], step))

    p.segment(df.index, df.high, df.index, df.low, color="black")

    p.vbar(df.index[dec], 0.6, df.open[dec], df.close[dec], color="red")
    p.vbar(df.index[inc], 0.6, df.open[inc], df.close[inc], color='blue')

    select = figure(title="Drag the middle and edges of the selection box to change the range above",
                    height=130, width=SCREEN_WIDTH, y_range=p.y_range,
                    x_axis_type="datetime", y_axis_type=None,
                    tools="", toolbar_location=None, background_fill_color="#efefef")

    range_tool = RangeTool(x_range=p.x_range)
    range_tool.x_range = p.x_range
    range_tool.overlay.fill_color = "navy"
    range_tool.overlay.fill_alpha = 0.2

    select.line('date', 'close', source=ColumnDataSource(df))
    select.ygrid.grid_line_color = None
    select.add_tools(range_tool)



    show(column(p, select))

def chart_onlain(df):
    # Создаём браузерную сессию (вкладку в браузере, где мы будем рисовать графики)
    session = pull_session()

    # Создаём т.н. документ, который будем показывать на сессии (фигуру с осями и графиками)
    tools = "pan,wheel_zoom,box_zoom,reset,save"
    p = figure(tools=tools, width=SCREEN_WIDTH, height=SCREEN_HEIGHT,
               title="My test chart", background_fill_color="#efefef")


if __name__ == "__main__":
    df, message = init_data_set('test')
    df, extremum_list, message = split_into_movements(df)
    #df = df[:5000]

    df["date"] = pd.to_datetime(df["date"])

    chart_range_slider(df)
    #chart_range_tool(df)