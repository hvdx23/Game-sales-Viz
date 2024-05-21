import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd

df = pd.read_csv('1234.csv')
df = df.groupby(['console', 'publisher']).sum().reset_index()

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Video Game Sales"),
    dcc.Graph(
        id='console',
        figure=px.sunburst(df, path=['console', 'publisher'], values='total_sales'))
])

if __name__ == '__main__':
    app.run_server(debug=True)