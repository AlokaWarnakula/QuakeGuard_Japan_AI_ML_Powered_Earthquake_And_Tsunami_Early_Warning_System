import requests
import time

# Define parameters
base_url = "https://earthquake.usgs.gov/fdsnws/event/1/query.csv"
params = {
    "minlatitude": -10,
    "maxlatitude": 82,
    "minlongitude": 25,
    "maxlongitude": 180,
    "orderby": "time"
}

years = range(1990, 2024)  # 1990 to 2023 inclusive

for year in years:
    params["starttime"] = f"{year}-01-01"
    params["endtime"] = f"{year}-12-31"

    print(f"📥 Downloading data for {year}...")

    try:
        response = requests.get(base_url, params=params, timeout=60)

        if response.status_code == 200:
            filename = f"asia_earthquakes_{year}.csv"
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