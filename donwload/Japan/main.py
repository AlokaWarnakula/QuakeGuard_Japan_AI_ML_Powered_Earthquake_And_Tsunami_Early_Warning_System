import requests
import time

# Define parameters for JAPAN region (JMA approximate bounds)
base_url = "https://earthquake.usgs.gov/fdsnws/event/1/query.csv"
params = {
    "minlatitude": 24.0,      # Southern tip of Okinawa
    "maxlatitude": 45.5,      # Northern Hokkaido
    "minlongitude": 122.0,    # West of Kyushu (includes some Sea of Japan)
    "maxlongitude": 154.0,    # East of Pacific coast (includes offshore quakes)
    "orderby": "time",
    "eventtype": "earthquake",  # Only real earthquakes
    "format": "csv"
}

years = range(1990, 2024)  # 1990 to 2023 inclusive

for year in years:
    params["starttime"] = f"{year}-01-01"
    params["endtime"] = f"{year}-12-31"

    print(f"📥 Downloading JMA-region data for {year}...")

    try:
        response = requests.get(base_url, params=params, timeout=60)

        if response.status_code == 200:
            filename = f"japan_earthquakes_{year}.csv"
            with open(filename, "wb") as f:
                f.write(response.content)
            print(f"✅ Saved {filename}")
        else:
            print(f"❌ Failed for {year}: HTTP {response.status_code}")
            print(response.text)

        # Be kind to the server — add delay
        time.sleep(1)

    except Exception as e:
        print(f"⚠️ Error for {year}: {e}")