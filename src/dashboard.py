from os import walk
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import redis
from collections import deque
import random
import threading
import time
from dash.exceptions import PreventUpdate


UPDATE_RATE = 200  # voor dashboard (in ms)
REDIS_INTERVAL = UPDATE_RATE / 1000  # Convert naar sec voor redis cacher


## data cacher so we dont ahve to IO operation every interval tick for each graph
class RedisDataCache:
    def __init__(self, redis_client, hash_names, interval=1, max_points=25):
        self.redis_client = redis_client
        self.hash_names = hash_names
        self.interval = interval
        self.max_points = max_points
        self.data = {hash_name: {} for hash_name in hash_names}
        self.update_lock = threading.Lock()

        # Initialize data fetcher thread
        self.data_fetcher_thread = threading.Thread(target=self.update_data)
        self.data_fetcher_thread.daemon = True
        self.data_fetcher_thread.start()

    def update_data(self):
        while True:
            with self.update_lock:
                for hash_name in self.hash_names:
                    for key, value in self.redis_client.hgetall(hash_name).items():
                        key_str = key.decode("utf-8")
                        try:
                            value_float = float(value.decode("utf-8"))
                            if key_str not in self.data[hash_name]:
                                self.data[hash_name][key_str] = deque(
                                    [None] * self.max_points, maxlen=self.max_points
                                )
                            self.data[hash_name][key_str].append(value_float)
                        except ValueError:
                            pass
            time.sleep(self.interval)

    def get_data(self, hash_name):
        with self.update_lock:
            return self.data.get(hash_name, {}).copy()


# Initialize Redis client
r = redis.Redis(host="localhost", port=6379, db=0)
hash_names = [
    "Sensor_Actuator",
    "sim_state",
    "RealitySimReplay",
    "TestResults",
    "FRPloggedInfo",
]

data_cache = RedisDataCache(r, hash_names, interval=REDIS_INTERVAL, max_points=100)

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])


def random_color():
    # BEter dan niks
    return "#{:02x}{:02x}{:02x}".format(
        random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
    )


class GraphGenerator:
    def __init__(self, hash_name, data_cache, max_points=25):
        self.hash_name = hash_name
        self.data = {}
        self.colors = {}
        self.max_points = max_points
        self.data_cache = data_cache

    def update_graph(self):
        cached_data = self.data_cache.get_data(self.hash_name)
        for (
            key_str,
            value_deque,
        ) in cached_data.items():  # Note that `value` is a deque here
            if key_str not in self.data:
                # self.data[key_str].append(value_deque)
                self.data[key_str] = value_deque  # Update the deque for the given key
                if None in self.data[key_str]:
                    self.data[key_str].remove(None)
                self.colors[key_str] = random_color()

        traces = []
        for key, values in self.data.items():
            traces.append(
                go.Scatter(
                    x=list(range(self.max_points)),
                    y=list(values),
                    mode="lines",
                    name=f"{key}",
                    line=dict(color=self.colors[key]),
                )
            )

        layout = go.Layout(
            title=f"{self.hash_name} x Time",
            xaxis=dict(title="Time", range=[0, self.max_points - 1]),
            yaxis=dict(title="Value"),
        )

        return {"data": traces, "layout": layout}


class SpecialGraph:
    def __init__(self, data_cache, max_points=25):
        self.data = deque([None] * max_points, maxlen=max_points)
        self.data_cache = data_cache  # pass data_cache into this class
        self.max_points = max_points

    def update_graph(self):
        cached_data = self.data_cache.get_data(
            "Sensor_Actuator"
        )  # fetch data using data_cache
        # value = cached_data.get("GasRemPedalPosPercentage", 0)  # Default to 0 if key is not found

        value_deque = cached_data.get(
            "GasRemPedalPosPercentage", deque([0])
        )  # Default to deque([0]) if key is not found
        if value_deque:
            value = value_deque[-1]
        else:
            value = 0

        self.data.append(value)
        # Create bar graph traces
        if value >= 0:
            bar_trace = go.Bar(
                x=["Positive"],
                y=[value],
                marker=dict(color="green"),
                width=[0.4],
            )
            negative_bar_trace = go.Bar(
                x=["Negative"],
                y=[0],
                marker=dict(color="red"),
                width=[0.4],
            )
        else:
            bar_trace = go.Bar(
                x=["Positive"],
                y=[0],
                marker=dict(color="green"),
                width=[0.4],
            )
            negative_bar_trace = go.Bar(
                x=["Negative"],
                y=[-value],  # Take absolute value
                marker=dict(color="red"),
                width=[0.4],
            )

        # Create sparkline
        sparkline_trace = go.Scatter(
            x=list(range(self.max_points)),
            y=list(self.data),
            mode="lines+markers",
        )

        # Create layout
        layout = go.Layout(
            title="Special Graph",
            xaxis=dict(title="Category"),
            yaxis=dict(title="Value"),
        )

        # Create Figure and add Subplots
        fig = go.Figure()
        fig.add_trace(bar_trace)
        fig.add_trace(negative_bar_trace)
        fig.add_trace(sparkline_trace)

        fig.update_layout(layout)

        return fig


# Generate graphs
#
graph4 = GraphGenerator("Sensor_Actuator", data_cache, max_points=100)
graph3 = GraphGenerator("sim_state", data_cache, max_points=100)
graph1 = GraphGenerator("RealitySimReplay", data_cache, max_points=100)
graph2 = GraphGenerator("TestResults", data_cache, max_points=100)
# graph9 = SpecialGraph(data_cache, max_points=100)

# Dash Layout
app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id="graph-C"), width=6),
                dbc.Col(dcc.Graph(id="graph-D"), width=6),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id="graph-A"), width=6),
                dbc.Col(dcc.Graph(id="graph-B"), width=6),
            ]
        ),
        dcc.Interval(id="interval-update", interval=1 * UPDATE_RATE, n_intervals=0),
    ]
)

# Update the graphs


@app.callback(
    [
        Output("graph-A", "figure"),
        Output("graph-B", "figure"),
        Output("graph-D", "figure"),
        Output("graph-C", "figure"),
    ],
    Input("interval-update", "n_intervals"),
)
def update_all_graphs(n):
    if n is None:
        raise PreventUpdate
    return (
        graph1.update_graph(),
        graph2.update_graph(),
        graph3.update_graph(),
        graph4.update_graph(),
    )


#
# @app.callback(
#     [Output('current-values-D', 'children'),
#      Output('current-values-E', 'children'),
#      Output('current-values-F', 'children')],
#     [Input('some-input', 'value')]
# )
# def my_callback(input_value):
#     return 'value_for_D', 'value_for_E', 'value_for_F'

#
#
#
# @app.callback(
#     [Output('current-values-D.children', 'children'),
#      Output('current-values-E.children', 'children'),
#      Output('current-values-F.children', 'children')],
#     [Input('some-input', 'value')]
# )
# def my_callback(input_value):
#     return 'value_for_D', 'value_for_E', 'value_for_F'


# Update current hash values
# @app.callback(
#     [Output('current-values-D', 'children'),
#      Output('current-values-E', 'children'),
#      Output('current-values-F', 'children')],
#     Input('interval-update', 'n_intervals')
# )
# def get_current_values(hash_name):
#         return data_cache.get_data(hash_name)
#


def update_current_values(n):
    current_values_D = str(get_current_values("Sensor_Actuator"))
    current_values_E = str(get_current_values("sim_state"))
    current_values_F = str(get_current_values("RealitySimReplay"))
    return current_values_D, current_values_E, current_values_F


if __name__ == "__main__":
    app.run_server(debug=True)
