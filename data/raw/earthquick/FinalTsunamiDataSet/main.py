# # convert_tsv_to_csv.py
# import pandas as pd
#
# # Input and output file paths
# tsv_file = 'tsunamis.tsv'
# csv_file = 'tsunamisCorrect.csv'
#
# # Read TSV with proper handling for quotes and bad lines
# df = pd.read_csv(
#     tsv_file,
#     sep='\t',
#     quotechar='"',        # Handle fields enclosed in quotes
#     escapechar='\\',      # Handle escaped quotes (though TSV uses "" inside "")
#     on_bad_lines='skip',  # Skip any malformed rows
#     dtype=str,            # Read everything as string to avoid type inference issues
#     encoding='utf-8'
# )
#
# # Optional: Remove any rows that are completely empty
# df.dropna(how='all', inplace=True)
#
# # Save as clean CSV
# df.to_csv(csv_file, index=False, quoting=1, quotechar='"', escapechar='\\')
#
# print(f"✅ Converted '{tsv_file}' to '{csv_file}'")
# print(f"📊 Data shape: {df.shape[0]} rows, {df.shape[1]} columns")


# convert_tsv_to_csv.py
import pandas as pd

# File paths
tsv_file = 'tsunamis.tsv'
csv_file = 'tsunamisCorrect123.csv'

# Read TSV with proper handling for quotes and tabs
df = pd.read_csv(
    tsv_file,
    sep='\t',
    quotechar='"',
    escapechar='\\',
    on_bad_lines='skip',
    dtype=str,  # Keep everything as string to avoid type issues
    skiprows=1  # ⚠️ Skip the first data row (it's metadata, not real data)
)

# Remove rows that are completely empty
df.dropna(how='all', inplace=True)

# Optionally: Remove the first column if it's all empty or useless
# In your case, the first column is "Search Parameters" — not needed
df.drop(columns=[df.columns[0]], inplace=True)  # Remove first column

# Rename the first actual column to "Id" (since we removed "Search Parameters")
df.rename(columns={df.columns[0]: "Id"}, inplace=True)

# Save as clean CSV without unnecessary quoting
df.to_csv(csv_file, index=False, quoting=1, quotechar='"', escapechar='\\')

print(f"✅ Converted '{tsv_file}' to '{csv_file}'")
print(f"📊 Data shape: {df.shape[0]} rows, {df.shape[1]} columns")
print(f"📋 Columns: {list(df.columns)}")