import pandas as pd
import plotly.express as px

# Read the CSV file into a DataFrame
df = pd.read_csv('1234_small.csv')

# Create a new DataFrame with a row for each console, title, and sales category
new_df = pd.DataFrame(columns=['id', 'parent', 'value'])

# Add a row for each console
for console in df['console'].unique():
    new_df = pd.concat([new_df, pd.DataFrame({'id': [console], 'parent': [''], 'value': [df[df['console'] == console]['total_sales'].sum()]})], ignore_index=True)

# Add a row for each title within each console
for _, row in df.iterrows():
    new_df = pd.concat([new_df, pd.DataFrame({'id': [row['title']], 'parent': [row['console']], 'value': [row['total_sales']]})], ignore_index=True)

# Add a row for each sales category within each title
sales_categories = ['na_sales', 'jp_sales', 'pal_sales', 'other_sales']
for _, row in df.iterrows():
    for category in sales_categories:
        new_df = pd.concat([new_df, pd.DataFrame({'id': [f"{row['title']}_{category}"], 'parent': [row['title']], 'value': [row[category]]})], ignore_index=True)

# Create the sunburst chart
fig = px.sunburst(
    new_df,
    names='id',
    parents='parent',
    values='value'
)

# Display the chart
fig.show()