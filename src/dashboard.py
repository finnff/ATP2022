import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import redis
from collections import deque
import random


# Initialize Redis client
r = redis.Redis(host='localhost', port=6379, db=0)
UPDATE_RATE = 500

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])



def random_color():
    return "#{:02x}{:02x}{:02x}".format(
        random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
    )




def random_color():
    return "#{:02x}{:02x}{:02x}".format(
        random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
    )

class GraphGenerator:
    def __init__(self, hash_name, redis_client, max_points=25):
        self.hash_name = hash_name
        self.data = {}
        self.colors = {}
        self.max_points = max_points
        self.redis_client = redis_client

    def update_graph(self):
        for key, value in self.redis_client.hgetall(self.hash_name).items():
            key_str = key.decode('utf-8')
            try:
                value_float = float(value.decode('utf-8'))

                if key_str not in self.data:
                    self.data[key_str] = deque([None] * self.max_points, maxlen=self.max_points)
                    self.colors[key_str] = random_color()

                self.data[key_str].append(value_float)
            except ValueError:
                pass

        traces = []
        for key, values in self.data.items():
            traces.append(
                go.Scatter(
                    x=list(range(self.max_points)),
                    y=list(values),
                    mode='lines+markers',
                    name=f"{self.hash_name}_{key}",
                    line=dict(color=self.colors[key])
                )
            )

        layout = go.Layout(
            title=f'{self.hash_name} Over Time',
            xaxis=dict(title='Time', range=[0, self.max_points - 1]),
            yaxis=dict(title='Value')
        )

        return {'data': traces, 'layout': layout}

# Generate graphs
#
graph1 = GraphGenerator('RealitySimReplay',r, max_points=25)
graph2 = GraphGenerator('Sensor_Actuator',r, max_points=25)
graph3 = GraphGenerator('sim_stat', r,max_points=25)

# Dash Layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(dcc.Graph(id='graph-A'), width=4),
        dbc.Col(dcc.Graph(id='graph-B'), width=4),
        dbc.Col(dcc.Graph(id='graph-C'), width=4),
    ]),
    dbc.Row([
        dbc.Col([
            html.Div(id='current-values-D'),
            dcc.Input(id='input-D1', type='number', value=0),
            dcc.Input(id='input-D2', type='number', value=0),
            dcc.Input(id='input-D3', type='number', value=0),
            dcc.Input(id='input-D4', type='number', value=0),
        ], width=4),
        dbc.Col([
            html.Div(id='current-values-E'),
            dcc.Input(id='input-E1', type='number', value=0),
            dcc.Input(id='input-E2', type='number', value=0),
            dcc.Input(id='input-E3', type='number', value=0),
            dcc.Input(id='input-E4', type='number', value=0),
        ], width=4),
        dbc.Col([
            html.Div(id='current-values-F'),
            dcc.Slider(id='input-F1', min=0.1, max=10, step=0.1, value=1),
            dcc.Input(id='input-F2', type='number', value=0),
            dcc.Input(id='input-F3', type='number', value=0),
            dcc.Input(id='input-F4', type='number', value=0),
        ], width=4),
    ]),
    dcc.Interval(id='interval-update', interval=1*UPDATE_RATE, n_intervals=0)
])

# Update the graphs

@app.callback(
    [Output('graph-A', 'figure'),
     Output('graph-B', 'figure'),
     Output('graph-C', 'figure')],
    Input('interval-update', 'n_intervals')
)
def update_all_graphs(n):
    return graph1.update_graph(), graph2.update_graph(), graph3.update_graph()


# Update current hash values
@app.callback(
    [Output('current-values-D', 'children'),
     Output('current-values-E', 'children'),
     Output('current-values-F', 'children')],
    Input('interval-update', 'n_intervals')
)
def update_current_values(n):
    def get_current_values(hash_name):
        values = []
        for key, value in r.hgetall(hash_name).items():
            try:
                values.append(f"{key.decode('utf-8')}: {float(value.decode('utf-8'))},\n")
            except ValueError:
                pass
        return html.Div(values)

    current_values_D = get_current_values('Sensor_Actuator')
    current_values_E = get_current_values('sim_stat')
    current_values_F = get_current_values('RealitySimReplay')
    
    return current_values_D, current_values_E, current_values_F

if __name__ == '__main__':
    app.run_server(debug=True)
