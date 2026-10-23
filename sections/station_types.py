import pandas as pd
import streamlit as st

from utils.prep import DEPT_TO_REGION
from utils.viz import station_type_bars


def show(stations, fuel, regions):
    st.header("3. What makes a station cheap or expensive?")
    st.write("Section 2 showed that the station matters more than the region. So which stations are cheap?")

    s = stations[stations["fuel"] == fuel].copy()
    s["region"] = s["dept"].map(DEPT_TO_REGION)
    s = s[s["region"].isin(regions)]
    if len(s) < 100:
        st.info("Not enough stations for these filters. Pick more regions.")
        return

    # compare each station to the average of its own department, so the region does not count
    s["gap"] = (s["price"] - s.groupby("dept")["price"].transform("mean")) * 100

    road = s[s["road"] == "R"]
    rare = road["changes_per_month"].quantile(0.25)
    groups = {
        "Motorway station": s[s["road"] == "A"],
        "Has a repair garage": road[road["garage"]],
        "Rarely changes its price": road[road["changes_per_month"] <= rare],
        "Typical normal-road station": road,
    }
    res = pd.DataFrame([(name, g["gap"].median(), len(g)) for name, g in groups.items() if len(g) >= 20],
                       columns=["group", "gap", "n"])

    worst = res.loc[res["gap"].idxmax()]
    typical = res.set_index("group")["gap"]["Typical normal-road station"]
    st.subheader(f"Most expensive: {worst['group'].lower()}, {worst['gap']:+.0f} cts/L compared to its department.")
    diff = worst["gap"] - typical
    st.write(f"A typical normal-road station is at {typical:+.0f} cts/L. "
             f"The difference is {diff:.0f} cts/L, so about {diff / 2:.0f} € on a 50 L tank.")

    st.plotly_chart(station_type_bars(res), width="stretch")
    st.caption(f"2025, {fuel}. Each bar = the median gap between a type of station and the average of its own "
               "department. Red = more expensive, blue = cheaper.")

    st.markdown(
        """
- **Motorways** are by far the most expensive. There is no other station nearby to compete with.
- **Stations with a repair garage** are often small independent stations. They sell less fuel, so they keep a bigger margin.
- **Stations that rarely change their price** (about once a week or less) are a few cents more expensive.
  They don't follow the market as closely as the others.
- I also tested the number of stations in the same town, 24/7 automatic pumps and the number of services. They made no real difference.
- These are links, not causes. The data does not say who owns the station.
"""
    )

    with st.expander("How it's calculated"):
        st.markdown(
            f"""
- For each station: its average 2025 price **minus the average of all stations in its department**.
  This removes the effect of the region (a station in Paris is not compared to one in Brittany).
- I use the **median** of each group, not the mean, so a few extreme stations don't change the result.
- **Rarely changes its price** = the 25% of normal-road stations with the fewest price changes per month
  (≤ {rare:.0f} changes per month for {fuel}).
- **Repair garage** = the station lists "Services réparation / entretien" in its services.
"""
        )
