import os

import streamlit as st

from utils.io import load_monthly, load_stations, load_quality, load_geojson
from utils.prep import REGIONS
from sections import intro, overview, deep_dives, station_types, data_quality, conclusions

st.set_page_config(page_title="Fuel prices in France", layout="wide")

monthly = load_monthly()
geo, dept_names = load_geojson()

LOGO = os.path.join(os.path.dirname(__file__), "assets", "efrei_logo.png")

with st.sidebar:
    st.image(LOGO, width="stretch")
    st.markdown(
        "**Indiko JABUA**  \n"
        "Data Engineering, M1 (2026-2027)  \n"
        "[indiko.jabua@efrei.net](mailto:indiko.jabua@efrei.net)  \n"
        "[LinkedIn](https://www.linkedin.com/in/indiko-jabua-5b5049252/) | "
        "[GitHub](https://github.com/indiko7777)"
    )
    st.markdown(
        "**Course:** Data Visualization  \n"
        "**Project proposed by:** Prof. Mano Mathew  \n"
        "[mano.mathew@efrei.fr](mailto:mano.mathew@efrei.fr)"
    )
    st.divider()

    st.header("Filters")
    fuel = st.selectbox("Fuel", ["Diesel", "E10", "SP98"])
    years = st.slider("Years", 2019, 2025, (2019, 2025))
    all_regions = sorted(REGIONS)
    regions = st.multiselect("Regions", all_regions, default=all_regions)

if not regions:
    st.warning("Pick at least one region in the sidebar.")
    st.stop()

base = monthly[monthly["region"].isin(regions)]
df = base[base["year"].between(*years)]

# ex: Corsica has almost no SP98
if df[df["fuel"] == fuel].empty:
    st.warning(f"No {fuel} data for these filters. Try another fuel or region.")
    st.stop()

intro.show()
overview.show(df, base, fuel)
stations = load_stations()
deep_dives.show(df, monthly, fuel, geo, dept_names, stations, regions)
station_types.show(stations, fuel, regions)
data_quality.show(monthly, load_quality())
conclusions.show()
