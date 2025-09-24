import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 📂 Load the dataset
file_path = 'asia_earthquakes_combined_filtered.csv'
df = pd.read_csv(file_path)

print(f"✅ Loaded {len(df):,} earthquakes.")

# 🔍 Basic Magnitude Stats
min_mag = df['mag'].min()
max_mag = df['mag'].max()
print(f"\n📊 Magnitude Range: {min_mag:.2f} to {max_mag:.2f}")

# 🧮 Define Magnitude Bins (Customize as needed)
mag_bins = [2.5, 4.0, 5.5, 6.5, 7.5, 10.0]
bin_labels = ['2.5 - 4.0', '4.0 - 5.5', '5.5 - 6.5', '6.5 - 7.5', '7.5+']

# 🗃️ Assign each earthquake to a bin
df['mag_bin'] = pd.cut(df['mag'], bins=mag_bins, labels=bin_labels, right=False)

# 📊 Count per bin
mag_distribution = df['mag_bin'].value_counts().sort_index()

# 📈 Calculate percentages
mag_percentage = (mag_distribution / len(df) * 100).round(2)

# 🖨️ Display Results
print("\n" + "="*60)
print("📈 EARTHQUAKE COUNT BY MAGNITUDE RANGE")
print("="*60)
for bin_name, count in mag_distribution.items():
    pct = mag_percentage[bin_name]
    print(f"{bin_name:<12} → {count:>8,} quakes ({pct:>6.2f}%)")

print(f"\n🧮 Total: {len(df):,} earthquakes")

# 🎨 Plot Bar Chart
plt.figure(figsize=(12, 7))
bars = plt.bar(mag_distribution.index, mag_distribution.values,
               color=['#FFB3BA', '#BAFFC9', '#BAE1FF', '#FFFFBA', '#E0BBE4'],
               edgecolor='black', linewidth=1.2)

# Add value labels on bars
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
             f'{int(height):,}', ha='center', va='bottom', fontweight='bold')

plt.title('Asia Earthquake Distribution by Magnitude (1990–2023)\nMagnitude ≥ 2.5 | Source: USGS',
          fontsize=16, fontweight='bold', pad=20)
plt.xlabel('Magnitude Range', fontsize=14)
plt.ylabel('Number of Earthquakes', fontsize=14)
plt.xticks(rotation=45, fontsize=12)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()

# 📊 Optional: Pie Chart for Percentage View
plt.figure(figsize=(10, 10))
plt.pie(mag_percentage, labels=mag_percentage.index, autopct='%1.1f%%',
        startangle=90, colors=['#FFB3BA', '#BAFFC9', '#BAE1FF', '#FFFFBA', '#E0BBE4'])
plt.title('Percentage of Earthquakes by Magnitude Range', fontsize=16, fontweight='bold', pad=20)
plt.show()