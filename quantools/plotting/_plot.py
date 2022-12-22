import numpy as np

from bokeh.layouts import column, layout, row
from bokeh.models import ColumnDataSource, RangeTool, HoverTool
from bokeh.plotting import figure, show
import pandas as pd
from bokeh.models.widgets import DataTable, TableColumn

import quantools as qt


def plot(
    self: qt.TableSeries,
    to_plot: list = ["normality", "cumsum", "drawdown", "autocorrelation", "indicators"],
    return_type: str = "percentage",
):
    """
    Plot the table with bokeh
    """

    self_df = self.as_df()
    source_base = ColumnDataSource(data = {'date': self_df.index, 'value': self_df, 'cumsum': self_df.cumsum()})

    col1, col2 = [], []
    col1_width, col2_width = 800, 400

    assert return_type in [
        "percentage",
        "monetary",
        "log",
    ], "return_type must be one of ['percentage', 'monetary', 'log']"
    # to complete

    p = figure(
        width=col1_width,
        height=400,
        x_axis_type="datetime",
        title="Table",
        x_range=(self_df.index[0], self_df.index[-1]),
    )

    if "cumsum" in to_plot:

        p.line(x="date", y="cumsum", source=source_base, color="red", legend_label="cumsum")

    range_tool = RangeTool(x_range=p.x_range)
    range_tool.overlay.fill_color = "navy"
    range_tool.overlay.fill_alpha = 0.2

    select = figure(
        title="Drag the middle and edges of the selection box to change the range above",
        height=130,
        width=col1_width,
        y_range=p.y_range,
        x_axis_type="datetime",
        y_axis_type=None,
        tools="",
        toolbar_location=None,
        background_fill_color="#efefef",
    )

    select.line(x="date", y="cumsum", source=source_base, color="red")
    select.ygrid.grid_line_color = None
    select.add_tools(range_tool)
    select.toolbar.active_multi = range_tool

    print(self_df)

    ht = HoverTool(
    tooltips=[
        ( 'date',   '@date{%F}'            ),
        ( 'close',  '$@{cumsum}{%0.2f}' ), # use @{ } for field names with spaces
    ],

    formatters={
        '@date'        : 'datetime', # use 'datetime' formatter for '@date' field
        '@{cumsum}' : 'printf',   # use 'printf' formatter for '@{adj close}' field
                                     # use default 'numeral' formatter for other fields
    },

    # display a tooltip whenever the cursor is vertically in line with a glyph
    mode='vline'
)
    p.add_tools(ht)

    col1 += [p, select]

    if "indicators" in to_plot:

        indicators_df = self.indicators()

        if not indicators_df.empty:
            indicators_df = indicators_df.rename(
                columns={indicators_df.columns[0]: "Indicator"}
            )
            indicators_df = indicators_df.reset_index()
            indicators_df["index"] = indicators_df["index"].astype(str)
            source = ColumnDataSource(indicators_df)
            columns = [
                TableColumn(field="index", title="Indicator"),
                TableColumn(field="Indicator", title="Value"),
            ]
            data_table = DataTable(source=source, columns=columns, width=col2_width, height=len(indicators_df) * 30)

            col2.append(data_table)


    p_n = figure(width=col2_width, height=400, title="Normality")
    if "normality" in to_plot:
        #restric df to p.x_range
        hist, edges = np.histogram(self_df, bins=50, density=True)
        mean, var = self_df.mean(), self_df.std() ** 2
        print(mean)
        x = np.linspace(self_df.min(), self_df.max(), len(self_df))
        pdf = 1 / np.sqrt(2 * np.pi * var) * np.exp(-((x - mean) ** 2) / (2 * var))


        p_n.quad(
            top=hist, bottom=0, left=edges[:-1], right=edges[1:], fill_color="#036564"
        )
        p_n.line(x=x, y=pdf, color="red", legend_label="PDF")

        col2.append(p_n)

    p_d = figure(width=800, height=200, x_axis_type="datetime", x_range=p.x_range, title="Drawdown")
    if "drawdown" in to_plot:
        drawdown = self_df.where(self_df < 0, 0)
        p_d.line(x=self_df.index, y=drawdown, color="red")
        # dont plot axis
        p_d.xaxis.visible = False
        # dont plot title
        # mix with upper plot
        p_d.toolbar_location = None

        col1.append(p_d)



    if "returns" in to_plot:
        p_r = figure(
            width=col1_width,
            height=200,
            x_axis_type="datetime",
            x_range=p.x_range,
            title="Returns",
        )
        p_r.line(x=self_df.index, y=self_df, color="red")
        p_r.xaxis.visible = False
        p_r.toolbar_location = None

        col1.append(p_r)

    if "autocorrelation" in to_plot:
        p_a = figure(
            width=col2_width,
            height=200,
            title=f"Autocorrelation, unit:{self_df.index.freqstr}",
        )
        df_with_lags = pd.concat([self_df.shift(i) for i in range(0,100)], axis=1)
        autocorr = df_with_lags.corr().iloc[0, 1:]
        lag = np.arange(1, 100)

        source_autocorr = ColumnDataSource(data = {'lag': lag, 'autocorr': autocorr})

        #p_a.line(top="autocorr", bottom=0, left="lag", right="lag", source=source_autocorr, fill_color="#036564")
        p_a.vbar(x="lag", top="autocorr", source=source_autocorr, color="red")

        tootltips = [
            ("lag", "@lag"),
            ("autocorr", "@autocorr"),
        ]
        p_a.add_tools(HoverTool(tooltips=tootltips, mode="vline"))

        col2.append(p_a)

    # plots[0].append()
    return (layout(row(column(col1), column(col2))))
