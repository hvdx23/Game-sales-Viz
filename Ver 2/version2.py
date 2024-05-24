import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import logging
import numpy as np

# Set up logging
logging.basicConfig(level=logging.INFO)

# Load and preprocess the data
df = pd.read_csv('1234.csv')

# Aggregate data by console and publisher for the initial sunburst chart
agg_df = df.groupby(['console', 'publisher']).sum().reset_index()

# Create the initial scatter plot (with all data)
fig_scatter = px.scatter(
    df, x='critic_score', y='total_sales', color='genre', 
    title='Critic Score vs. Total Sales',
    labels={'critic_score': 'Critic Score', 'total_sales': 'Total Sales'}
)

# Initialize the Dash app
app = dash.Dash(__name__)

# Define a function to fill null values in a DataFrame
def fill_null_values(df):
    df['critic_score'] = df['critic_score'].fillna(pd.Series(np.random.uniform(1, 5, size=len(df))))  # Fill nulls with random values between 1 and 5
    df['total_sales'] = df['total_sales'].fillna(pd.Series(np.random.uniform(0.1, 2.5, size=len(df))))  # Fill nulls with random values between 0.1 and 2.5
    return df

# Define the layout of the app
app.layout = html.Div([
    html.H1("Video Game Sales"),
    html.Div(id='charts-container', children=[
        dcc.Graph(
            id='console-publisher-sunburst',
            figure=px.sunburst(agg_df, path=['console', 'publisher'], values='total_sales')
        ),
        html.Div(id='detail-chart-container')
    ]),
    html.Div([
        dcc.Graph(id='scatter-plot', figure=fig_scatter)
    ])
])

# Define the callback function for interactivity
@app.callback(
    [Output('detail-chart-container', 'children'),
     Output('scatter-plot', 'figure')],
    Input('console-publisher-sunburst', 'clickData')
)
def update_charts(clickData):
    if clickData:
        path = clickData['points'][0]['id']
        logging.info(f"Clicked path: {path}")

        # Split the path into components
        path_parts = path.split('/')
        logging.info(f"Length of path_parts: {len(path_parts)}")

        # Create a filtering condition based on the path parts
        condition = pd.Series([True] * len(df))
        for i, part in enumerate(path_parts):
            if part:
                column = ['console', 'publisher', 'developer', 'title'][i]
                condition = condition & (df[column] == part)
        
        filtered_df = df[condition]

        # Determine the path based on the depth of the click
        if len(path_parts) == 1:
            # Reset the detail chart and scatter plot when returning to the first level
            return None, fig_scatter
        elif len(path_parts) == 2:
            sunburst_path = ['developer', 'title']
        elif len(path_parts) == 3:
            sunburst_path = ['title']
        else:
            sunburst_path = ['console', 'publisher', 'developer', 'title']

        # Fill null values for the filtered DataFrame
        filtered_df = fill_null_values(filtered_df)

        detail_figure = px.sunburst(filtered_df, path=sunburst_path, values='total_sales')
        
        scatter_figure = px.scatter(
            filtered_df, x='critic_score', y='total_sales', color='genre', 
            title='Critic Score vs. Total Sales',
            labels={'critic_score': 'Critic Score', 'total_sales': 'Total Sales'}
        )

        return dcc.Graph(id='detail-sunburst', figure=detail_figure), scatter_figure

    # Clear the detail chart and reset the scatter plot if no clickData
    return None, fig_scatter

# Run the app
if __name__ == '__main__':
    logging.info('Starting Dash server...')
    app.run_server(debug=True)
