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
    html.Div(id='charts-container', children=[
        dcc.Graph(
            id='console-publisher-sunburst',
            figure=px.sunburst(agg_df, path=['console', 'publisher'], values='total_sales')
        ),
        html.Div(id='detail-chart-container')
    ])
])

# Define the callback function for interactivity
@app.callback(
    Output('detail-chart-container', 'children'),
    Input('console-publisher-sunburst', 'clickData')
)
def update_detail_chart(clickData):
    if clickData:
        path = clickData['points'][0]['id']
        logging.info(f"Clicked path: {path}")

        # Split the path into components
        path_parts = path.split('/')
        
        # Create a filtering condition based on the path parts
        condition = True
        for i, part in enumerate(path_parts):
            if part:
                column = ['console', 'publisher', 'developer', 'title'][i]
                condition = condition & (df[column] == part)
        
        filtered_df = df[condition]
        
        # Determine the path based on the depth of the click
        if len(path_parts) == 1:
            sunburst_path = ['publisher', 'developer', 'title']
        elif len(path_parts) == 2:
            sunburst_path = ['publisher', 'developer', 'title']
        elif len(path_parts) == 3:
            sunburst_path = ['developer', 'title']
        elif len(path_parts) == 4:
            sunburst_path = ['title']
        else:
            sunburst_path = ['console', 'publisher', 'developer', 'title']
        
        figure = px.sunburst(filtered_df, path=sunburst_path, values='total_sales')
        
        return dcc.Graph(id='detail-sunburst', figure=figure)

    # Return None if no clickData
    return None

# Run the app
if __name__ == '__main__':
    logging.info('Starting Dash server...')
    app.run_server(debug=True)
