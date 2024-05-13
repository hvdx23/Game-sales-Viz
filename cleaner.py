import pandas as pd

# Load the data into a pandas DataFrame
df = pd.read_csv('vgchartz-2024.csv')

# Drop the 'img' column
df = df.drop('img', axis=1)

# Write the DataFrame back to a CSV file
df.to_csv('1234.csv', index=False)