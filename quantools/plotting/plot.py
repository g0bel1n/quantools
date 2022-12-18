import numpy as np

from bokeh.layouts import column, layout
from bokeh.models import ColumnDataSource, RangeTool
from bokeh.plotting import figure, show
import pandas as pd

from quantools.table.table import Table



def plot(self: Table, to_plot: list = ["cumsum", "cumprod"]):
    """
    Plot the table with bokeh
    """
    # if self.empty:
    #     raise ValueError("Table is empty")

    # if self.shape[1] > 1:
    #     raise ValueError("Table has more than one column")

    # if self.shape[0] > 1000:
    #     raise ValueError("Table has more than 1000 rows")

    # source = ColumnDataSource(self)
    # print(source)

    plots = []
    print(len(self.index))
    print(len(self.data.cumsum()))
    p = figure(width=800, height=400, x_axis_type="datetime", title="Table")
    if "cumsum" in to_plot:
        (p.line(x=self.index, y=self.data.cumsum(), color="red", legend_label="cumsum"))

    if "cumprod" in to_plot:
        (
            p.line(
                x="index",
                y=self.data.cumprod(),
                source=source,
                color="green",
                legend_label="cumprod",
            )
        )

    if "cummax" in to_plot:
        (
            p.line(
                x="index",
                y=self.cummax(),
                source=source,
                color="blue",
                legend_label="cummax",
            )
        )

    if "cummin" in to_plot:
        (
            p.line(
                x="index",
                y=self.cummin(),
                color="orange",
                legend_label="cummin",
            )
        )

    plots.append([p])

    p = figure(width=400, height=400, title="Normality")
    if "normality" in to_plot:
        hist, edges = np.histogram(self.data, bins=50, density=True)
        mean, var = self.data.mean(), self.data.std() ** 2
        print(mean)
        x = np.linspace(self.data.min(), self.data.max(), len(self.data))
        pdf = 1 / np.sqrt(2 * np.pi * var) * np.exp(-((x - mean) ** 2) / (2 * var))
        p.quad(
            top=hist, bottom=0, left=edges[:-1], right=edges[1:], fill_color="#036564"
        )
        p.line(x=x, y=pdf, color="red", legend_label="PDF")

        plots[0].append(p)

    p = figure(width=800, height=200, x_axis_type="datetime")
    if "drawdown" in to_plot:
        drawdown = self.data.where(self.data < 0, 0)
        p.line(x=self.index, y=drawdown, color="red")
        # dont plot axis
        p.xaxis.visible = False
        # dont plot title
        # mix with upper plot
        p.toolbar_location = None

        plots.append(p)

    print(self.sharpe())

    # plots[0].append()
    show(layout(plots))