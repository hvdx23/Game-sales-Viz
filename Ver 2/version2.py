import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import logging
import numpy as np
import dash_bootstrap_components as dbc

# Set up logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load and preprocess the data
df = pd.read_csv('1234.csv')



# Aggregate data by console and publisher for the initial sunburst chart
agg_df = df.groupby(['console', 'publisher']).sum().reset_index()

# Create the initial scatter plot (with all data)
fig_scatter = px.scatter(
    df, x='critic_score', y='total_sales', color='genre', 
    title='Critic Score vs. Total Sales',
    labels={'critic_score': 'Critic Score', 'total_sales': 'Total Sales'},
    hover_data =['title', 'developer', 'publisher', 'total_sales', 'genre', 'console']
)

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Define a function to fill null values in a DataFrame with random values within specified ranges
# def fill_null_values(df):
#     null_count = df.isnull().sum().sum()  # Count total null values before filling
#     df.loc[df['critic_score'].isnull(), 'critic_score'] = np.round(np.random.uniform(1, 6, size=len(df[df['critic_score'].isnull()])), 2)
#     df.loc[df['total_sales'].isnull(), 'total_sales'] = np.round(np.random.uniform(0.1, 2.5, size=len(df[df['total_sales'].isnull()])), 2)
#     filled_null_count = df.isnull().sum().sum() - null_count  # Count total null values filled
#     logging.info(f"Filled {filled_null_count} null values.")
#     return df
def fill_null_values(df):
    null_count = df['critic_score'].isnull().sum() + df['total_sales'].isnull().sum()  # Count total null values before filling
    df.loc[df['critic_score'].isnull(), 'critic_score'] = np.round(np.random.uniform(1, 6, size=len(df[df['critic_score'].isnull()])), 2)
    df.loc[df['total_sales'].isnull(), 'total_sales'] = np.round(np.random.uniform(0.1, 2.5, size=len(df[df['total_sales'].isnull()])), 2)
    filled_null_count = null_count - df['critic_score'].isnull().sum() - df['total_sales'].isnull().sum()  # Count total null values filled
    logging.info(f"Filled {filled_null_count} null values.")
    return df

app.layout = html.Div(style={'backgroundColor': 'black'}, children=[
    html.H1("Video Game Sales Visualization Dashboard", style={'textAlign': 'center', 'font-family': ' Agency FB', 'font-style':'bold', 'color':'orange','font-size':'75px'}),
    html.Div(className='row',style={'backgroundColor': 'lightblack'}, children=[
        html.Div(className='col-md-6', children=[
            html.H2("Selection & filtering", style={'textAlign': 'center','font-family': ' Agency FB', 'color' :'orange'}),
            html.Div(id='charts-container', children=[
                dcc.Graph(
                    id='console-publisher-sunburst',
                    figure=px.sunburst(agg_df, path=['console', 'publisher'], values='total_sales')
                ),
                html.Div(id='detail-chart-container')
            ])
        ]),
        html.Div(className='col-md-6', children=[

            html.H2("Visualization of genres", style={'textAlign': 'center', 'font-family': ' Agency FB','color':'red'}),
            dcc.Graph(id='scatter-plot', figure=fig_scatter),
            html.H2("Total sales details", style={'textAlign': 'center', 'font-family': ' Agency FB','color':'blue'}),

            html.Div(id='bar-chart-container'),
            
        ])
    ])
])

@app.callback(
    [Output('detail-chart-container', 'children'),
     Output('scatter-plot', 'figure'),
     Output('bar-chart-container', 'children')],
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
            logging.info("Creating bar chart for total sales by title")
            sunburst_path = ['publisher', 'developer', 'title']
            bar_chart = px.bar(filtered_df, x='developer', y='total_sales', title='Total Sales by Title', hover_data=['title','total_sales'])

            # Fill null values for the filtered DataFrame
            filtered_df = fill_null_values(filtered_df)

            detail_figure = px.sunburst(filtered_df, path=sunburst_path, values='total_sales')
            
            scatter_figure = px.scatter(
                filtered_df, x='critic_score', y='total_sales', color='genre', 
                title='Critic Score vs. Total Sales',
                labels={'critic_score': 'Critic Score', 'total_sales': 'Total Sales'},
                hover_data =['title', 'developer', 'publisher', 'total_sales', 'genre']
            )

            return [dcc.Graph(id='detail-sunburst', figure=detail_figure), 
                scatter_figure, 
                dcc.Graph(id='detail-bar-chart', figure=bar_chart)]
    return None, fig_scatter, None, None

# Run the app
if __name__ == '__main__':
    app.run_server(debug=False)
