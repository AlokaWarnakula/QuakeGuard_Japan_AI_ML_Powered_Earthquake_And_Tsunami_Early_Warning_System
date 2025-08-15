import pandas as pd

# Read only the first line (header) of the CSV
df = pd.read_csv('tsunamisCorrect.csv', nrows=0)
print("CSV Column Titles:")
print(df.columns.tolist())