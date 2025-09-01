import pandas as pd

# Read only the first line (header) of the CSV
df = pd.read_csv('cleaned_japan_earthquakes_1990-2023.csv', nrows=0)
print("CSV Column Titles:")
print(df.columns.tolist())