import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

# Load and preprocess the data
df = pd.read_csv('1234.csv')
df['developer'] = df['developer'].fillna('Unknown')

# Aggregate data by console and publisher for the initial sunburst chart
agg_df = df.groupby(['console', 'publisher']).sum().reset_index()

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div([
    html.H1("Video Game Sales"),
    dcc.Graph(
        id='console-publisher-sunburst',
        figure=px.sunburst(agg_df, path=['console', 'publisher'], values='total_sales')
    ),
    dcc.Graph(id='detail-sunburst')
])

# Define the callback function for interactivity
@app.callback(
    Output('detail-sunburst', 'figure'),
    Input('console-publisher-sunburst', 'clickData')
)
def update_detail_sunburst(clickData):
    if clickData:
        label = clickData['points'][0]['label']
        parent = clickData['points'][0].get('parent', None)
        root = clickData['points'][0].get('root', None)

        logging.info(f"Clicked label: {label}, Parent: {parent}, Root: {root}")
        
        if root:
            # If root exists, it's the console
            filtered_df = df[(df['console'] == root) & (df['publisher'] == parent) & (df['developer'] == label)]
            figure = px.sunburst(filtered_df, path=['publisher', 'developer', 'title'], values='total_sales')
        elif parent:
            # If parent exists but not root, it's the publisher
            filtered_df = df[(df['console'] == parent) & (df['publisher'] == label)]
            figure = px.sunburst(filtered_df, path=['publisher', 'developer', 'title'], values='total_sales')
        else:
            # Otherwise, it's the console
            filtered_df = df[df['console'] == label]
            figure = px.sunburst(filtered_df, path=['console', 'publisher', 'developer', 'title'], values='total_sales')

        return figure

    return dash.no_update

# Run the app
if __name__ == '__main__':
    logging.info('Starting Dash server...')
    app.run_server(debug=True)
