import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

df = pd.read_csv('1234.csv')

# Fill missing values
df['developer'] = df['developer'].fillna('Unknown')

df = df.groupby(['console', 'publisher']).sum().reset_index()

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Video Game Sales"),
    dcc.Graph(
        id='console',
        figure=px.sunburst(df, path=['console', 'publisher'], values='total_sales'))
])

@app.callback(
    Output('console', 'figure'),
    Input('console', 'clickData')
)
def display_click_data(clickData):
    if clickData:
        logging.info(f"Clicked data: {clickData}")
    return dash.no_update

if __name__ == '__main__':
    logging.info('Starting Dash server...')
    app.run_server(debug=True)