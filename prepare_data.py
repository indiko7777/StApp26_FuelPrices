# Downloads the yearly fuel price files and turns them into small CSVs for the app.
# Run once before the app:  python prepare_data.py
# Takes around 10 min (each raw file is ~300 MB of XML).

import os
import zipfile
import xml.etree.ElementTree as ET
from collections import defaultdict

import pandas as pd
import requests

from utils.prep import FUELS, MIN_PRICE, MAX_PRICE, DEPT_TO_REGION, cp_to_dept, fix_price

YEARS = range(2019, 2026)
RAW_URL = "https://donnees.roulez-eco.fr/opendata/annee/{}"
GEO_URL = "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements-version-simplifiee.geojson"

RAW_DIR = "data/raw"
OUT_DIR = "data"


def download(url, path):
    if os.path.exists(path):
        return
    print("downloading", url)
    r = requests.get(url, timeout=300)
    r.raise_for_status()
    with open(path, "wb") as f:
        f.write(r.content)


def parse_year(year):
    zip_path = f"{RAW_DIR}/{year}.zip"
    download(RAW_URL.format(year), zip_path)

    # (station, fuel, month) -> [sum of prices, number of prices]
    sums = defaultdict(lambda: [0.0, 0])
    stations = {}
    q = {"year": year, "stations_in_file": 0, "stations_dropped": 0, "price_rows": 0,
         "duplicates": 0, "missing_price": 0, "out_of_range": 0, "wrong_year": 0,
         "missing_coords": 0}

    with zipfile.ZipFile(zip_path) as z:
        xml_name = z.namelist()[0]
        with z.open(xml_name) as f:
            for _, elem in ET.iterparse(f, events=("end",)):
                if elem.tag != "pdv":
                    continue
                q["stations_in_file"] += 1
                dept = cp_to_dept(elem.get("cp"))
                if dept is None:
                    # overseas, fake postcodes like 99999, etc.
                    q["stations_dropped"] += 1
                    elem.clear()
                    continue

                sid = elem.get("id")
                lat, lon = elem.get("latitude"), elem.get("longitude")
                try:
                    lat, lon = float(lat) / 100000, float(lon) / 100000
                except (TypeError, ValueError):
                    lat, lon = None, None
                if not lat or not lon:
                    q["missing_coords"] += 1
                ville = (elem.findtext("ville") or "").strip().title()
                # stations with a repair garage are mostly small independent ones
                services = [s.text or "" for s in elem.findall("services/service")]
                garage = any("réparation" in s for s in services)
                stations[sid] = (dept, elem.get("pop"), ville, lat, lon, garage)

                seen = set()
                for p in elem.findall("prix"):
                    fuel = p.get("nom")
                    if fuel not in FUELS:
                        continue
                    q["price_rows"] += 1
                    maj = p.get("maj") or ""
                    if (fuel, maj) in seen:
                        q["duplicates"] += 1
                        continue
                    seen.add((fuel, maj))
                    price = fix_price(p.get("valeur"))
                    if price is None:
                        q["missing_price"] += 1
                        continue
                    if price < MIN_PRICE or price > MAX_PRICE:
                        q["out_of_range"] += 1
                        continue
                    if not maj.startswith(str(year)):
                        q["wrong_year"] += 1
                        continue
                    month = maj[:7]
                    s = sums[(sid, FUELS[fuel], month)]
                    s[0] += price
                    s[1] += 1
                elem.clear()

    rows = [(sid, fuel, month, s / n, n) for (sid, fuel, month), (s, n) in sums.items()]
    df = pd.DataFrame(rows, columns=["station_id", "fuel", "month", "price", "n_changes"])
    info = pd.DataFrame.from_dict(stations, orient="index",
                                  columns=["dept", "road", "city", "lat", "lon", "garage"])
    df = df.merge(info, left_on="station_id", right_index=True)
    q["stations_kept"] = df["station_id"].nunique()
    q["price_rows_kept"] = sum(n for _, n in sums.values())
    return df, q


def main():
    os.makedirs(RAW_DIR, exist_ok=True)
    download(GEO_URL, f"{OUT_DIR}/departements.geojson")

    monthly, quality = [], []
    for year in YEARS:
        df, q = parse_year(year)
        print(year, q)
        quality.append(q)

        # one average per department / month / fuel / road type
        g = df.groupby(["month", "dept", "fuel", "road"], as_index=False).agg(
            avg_price=("price", "mean"), n_stations=("station_id", "nunique"))
        monthly.append(g)

        if year == max(YEARS):
            # one row per station and fuel: average price + how often it changed its price
            st = df.groupby(["station_id", "fuel", "dept", "road", "city", "lat", "lon", "garage"],
                            as_index=False, dropna=False).agg(price=("price", "mean"),
                                                              n_changes=("n_changes", "sum"),
                                                              n_months=("month", "nunique"))
            st["changes_per_month"] = (st["n_changes"] / st["n_months"]).round(1)
            st.to_csv(f"{OUT_DIR}/stations_{year}.csv", index=False)

    monthly = pd.concat(monthly)
    monthly["region"] = monthly["dept"].map(DEPT_TO_REGION)
    monthly["avg_price"] = monthly["avg_price"].round(4)
    monthly.to_csv(f"{OUT_DIR}/monthly_prices.csv", index=False)
    pd.DataFrame(quality).to_csv(f"{OUT_DIR}/quality_report.csv", index=False)
    print("done:", len(monthly), "rows")


if __name__ == "__main__":
    main()
