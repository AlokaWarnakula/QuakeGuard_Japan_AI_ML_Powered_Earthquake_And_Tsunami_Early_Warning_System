#Include custom range for better info
# [24, 46]
# Latitude
# [128, 146]
# Longitude

import pandas as pd
import os
import numpy as np
from glob import glob
from sklearn.impute import SimpleImputer
from datetime import datetime, timedelta

# Configuration
input_dir = "/"  # Directory with CSV files
raw_output_file = "../raw_japan_earthquakes_1990-2023.csv"
cleaned_output_file = "cleaned_japan_earthquakes_1990-2023.csv"
ncei_file = "../../tsunami/FinalTsunamiDataSet/tsunamisCorrect.csv"  # Path to NCEI tsunami CSV
chunk_size = 50000  # Reduced for 8GB RAM


# Significance calculation (round to 2 decimal places)
def calculate_significance(magnitude, depth):
    try:
        return round((magnitude * 100) + max(0, (600 - depth) / 2), 2)
    except (TypeError, ValueError):
        return None


# Haversine distance function
def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    lat1 = np.radians(lat1)
    lon1 = np.radians(lon1)
    lat2 = np.radians(lat2)
    lon2 = np.radians(lon2)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    c = 2 * np.arcsin(np.sqrt(a))
    return R * c


# Tsunami matching function (match all tsunamis in the lat/lon range)
def match_tsunami(row, ncei_df, time_tolerance="10min", dist_tolerance=100.0, decimal_precision=3):
    try:
        eq_time = pd.to_datetime(row['time'], utc=True)
        eq_lat = row['latitude']
        eq_lon = row['longitude']

        # Use pre-filtered ncei_df (by range, year, cause code)

        # Time match
        time_diff = abs(ncei_df['EVENT_TIME'] - eq_time)
        time_mask = time_diff <= pd.Timedelta(time_tolerance)

        # Exact coordinate match (rounded to decimal_precision)
        eq_lat_rounded = round(eq_lat, decimal_precision)
        eq_lon_rounded = round(eq_lon, decimal_precision)
        tsu_lat_rounded = ncei_df['Latitude'].round(decimal_precision)
        tsu_lon_rounded = ncei_df['Longitude'].round(decimal_precision)
        exact_coord_mask = (tsu_lat_rounded == eq_lat_rounded) & (tsu_lon_rounded == eq_lon_rounded)

        # Distance-based match
        dist = haversine_distance(eq_lat, eq_lon, ncei_df['Latitude'], ncei_df['Longitude'])
        dist_mask = dist <= dist_tolerance

        # Combined match
        match_mask = (exact_coord_mask | dist_mask) & time_mask

        # Return 1 if any match, else 0
        return 1 if match_mask.any() else 0
    except:
        return 0


# Find CSV files
csv_files = [
    os.path.join(input_dir, "1990_2000.csv"),
    os.path.join(input_dir, "2000_2010.csv"),
    os.path.join(input_dir, "2010_2020.csv"),
    os.path.join(input_dir, "2020_2023.csv")
]
csv_files = [f for f in csv_files if os.path.exists(f)]
if not csv_files:
    print(f"No CSV files found in {input_dir}")
    exit(1)

print(f"Found {len(csv_files)} CSV files: {csv_files}")

# Check row counts and coordinates per file
for file in csv_files:
    df_temp = pd.read_csv(file, low_memory=False)
    print(f"{file}: {len(df_temp)} rows, "
          f"Lat {df_temp['latitude'].min():.2f}–{df_temp['latitude'].max():.2f}, "
          f"Lon {df_temp['longitude'].min():.2f}–{df_temp['longitude'].max():.2f}")

# Load NCEI tsunami data
try:
    ncei_df = pd.read_csv(ncei_file)
    print("NCEI Events Loaded:", len(ncei_df))
except FileNotFoundError:
    print("NCEI tsunami file not found. Setting tsunami=0 for all rows.")
    ncei_df = None

# Filter NCEI to earthquake-caused tsunamis in the range [1990-2023, Cause Code=1, Lat 20-50, Lon 120-150]
if ncei_df is not None:
    ncei_df = ncei_df[(ncei_df['Year'] >= 1990) & (ncei_df['Year'] <= 2023) &
                      (ncei_df['Tsunami Cause Code'] == 1.0) &
                      (ncei_df['Latitude'] >= 24) & (ncei_df['Latitude'] <= 46) &
                      (ncei_df['Longitude'] >= 128) & (ncei_df['Longitude'] <= 146)]
    # Create EVENT_TIME once
    ncei_df['EVENT_TIME'] = pd.to_datetime(
        ncei_df[['Year', 'Mo', 'Dy', 'Hr', 'Mn', 'Sec']].rename(
            columns={'Year': 'year', 'Mo': 'month', 'Dy': 'day',
                     'Hr': 'hour', 'Mn': 'minute', 'Sec': 'second'}
        ),
        errors='coerce'
    ).dt.tz_localize('UTC')
    # Drop rows with invalid time
    ncei_df = ncei_df.dropna(subset=['EVENT_TIME'])
    print("Filtered NCEI Events (in range):", len(ncei_df))

# Initialize lists for DataFrames
raw_dfs = []
clean_dfs = []

# Imputers
imputer_num = SimpleImputer(strategy='mean')
imputer_cat = SimpleImputer(strategy='most_frequent')

# Process each CSV
for i, file in enumerate(csv_files):
    print(f"Processing {file} ({i + 1}/{len(csv_files)})")
    try:
        for chunk in pd.read_csv(file, chunksize=chunk_size, low_memory=False, encoding='utf-8'):
            # Keep raw chunk
            raw_dfs.append(chunk.copy())

            # Process for cleaned dataset
            chunk_clean = chunk.copy()

            # Filter mag >= 2.5
            chunk_clean = chunk_clean[chunk_clean['mag'] >= 2.5]

            # Drop rows with missing time
            chunk_clean = chunk_clean.dropna(subset=['time'])

            # Extract temporal features
            chunk_clean['time'] = pd.to_datetime(chunk_clean['time'], utc=True, errors='coerce')
            chunk_clean['month'] = chunk_clean['time'].dt.month
            chunk_clean['day'] = chunk_clean['time'].dt.day
            chunk_clean['hour'] = chunk_clean['time'].dt.hour

            # Calculate significance and mag_category
            chunk_clean['significance'] = chunk_clean.apply(
                lambda row: calculate_significance(row['mag'], row['depth']), axis=1)
            chunk_clean['mag_category'] = chunk_clean['mag'].apply(
                lambda x: 'High' if x >= 6.0 else 'Low')

            # Add tsunami column
            if ncei_df is not None:
                chunk_clean['tsunami'] = chunk_clean.apply(
                    lambda row: match_tsunami(row, ncei_df), axis=1)
            else:
                chunk_clean['tsunami'] = 0

            # Impute missing values
            num_cols = ['depthError', 'rms']
            cat_cols = ['magType']
            if all(col in chunk_clean.columns for col in num_cols):
                chunk_clean[num_cols] = imputer_num.fit_transform(chunk_clean[num_cols])
                # Round imputed numerical columns to 2 decimal places
                chunk_clean[num_cols] = chunk_clean[num_cols].round(2)
            if all(col in chunk_clean.columns for col in cat_cols):
                chunk_clean[cat_cols] = imputer_cat.fit_transform(chunk_clean[cat_cols])

            clean_dfs.append(chunk_clean)
    except Exception as e:
        print(f"Error reading {file}: {e}")
        continue

# Combine raw dataset
print("Combining raw DataFrames...")
raw_combined_df = pd.concat(raw_dfs, ignore_index=True, sort=False)
raw_combined_df = raw_combined_df.drop_duplicates(subset=['id'], keep='first')

# Check magSource distribution
print("Raw magSource Counts:\n", raw_combined_df['magSource'].value_counts())

# Save raw dataset
raw_combined_df.to_csv(raw_output_file, index=False, encoding='utf-8')
print(f"Raw dataset saved to {raw_output_file}")
print("Raw Shape:", raw_combined_df.shape)
print("Raw Columns:", raw_combined_df.columns.tolist())
print("Raw Missing Values (%):\n", raw_combined_df.isnull().mean() * 100)

# Combine cleaned dataset
print("\nCombining cleaned DataFrames...")
cleaned_combined_df = pd.concat(clean_dfs, ignore_index=True, sort=False)
cleaned_combined_df = cleaned_combined_df.drop_duplicates(subset=['id'], keep='first')

# Drop high-missing and irrelevant columns
drop_cols = ['nst', 'gap', 'dmin', 'horizontalError', 'magError', 'magNst',
             'id', 'updated', 'place', 'net', 'type', 'status', 'locationSource', 'magSource']
cleaned_combined_df = cleaned_combined_df.drop(
    columns=[col for col in drop_cols if col in cleaned_combined_df.columns], errors='ignore')

# Verify cleaned dataset
print("\nCleaned Shape:", cleaned_combined_df.shape)
print("Cleaned Columns:", cleaned_combined_df.columns.tolist())
print("Cleaned Missing Values (%):\n", cleaned_combined_df.isnull().mean() * 100)
print("Cleaned Sample Data:\n",
      cleaned_combined_df[['time', 'latitude', 'longitude', 'depth', 'mag', 'significance', 'tsunami']].head())
print("Cleaned Tsunami Counts:\n", cleaned_combined_df['tsunami'].value_counts())
print("Cleaned Magnitude Range:\nMin:", cleaned_combined_df['mag'].min(),
      "\nMax:", cleaned_combined_df['mag'].max())

# Save cleaned dataset
cleaned_combined_df.to_csv(cleaned_output_file, index=False, encoding='utf-8')
print(f"Cleaned dataset saved to {cleaned_output_file}")