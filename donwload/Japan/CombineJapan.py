import pandas as pd
import glob

# Load all Asia CSVs
asia_files = glob.glob("japan_earthquakes_*.csv")
print(f"📂 Found {len(asia_files)} files.")

# Combine into one DataFrame
dfs = [pd.read_csv(f) for f in asia_files]
df = pd.concat(dfs, ignore_index=True)
print(f"📊 Combined {len(df):,} rows before filtering.")

# 🧹 Apply ONLY your two filters:
# 1. Keep only earthquakes
df = df[df['type'] == 'earthquake'].copy()
# 2. Keep only magnitude >= 2.5 and not NaN
df = df[(df['mag'] >= 2.5) & (df['mag'].notna())].copy()

print(f"🧽 After filtering (earthquake + mag≥2.5): {len(df):,} rows")

# 💾 SAVE — Keep ALL columns
output_filename = 'japan_earthquakes_combined_filtered.csv'
df.to_csv(output_filename, index=False)
print(f"✅ Saved to: {output_filename}")