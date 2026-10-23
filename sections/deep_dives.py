import pandas as pd
import streamlit as st

from utils.prep import DEPT_TO_REGION, weighted_avg
from utils.viz import dept_map, ranking_bars, region_heatmap, station_range


def show(df, france_df, fuel, geo, names, stations, regions):
    # df = filtered data, france_df = all regions and all years (for the France average)
    f = df[df["fuel"] == fuel]
    end = f["year"].max()
    fr = france_df[france_df["fuel"] == fuel]
    france_by_year = weighted_avg(fr, ["year"]).set_index("year")["avg_price"]
    france = france_by_year[end]

    st.header("2. Where is fuel the cheapest?")

    by_dept = weighted_avg(f[f["year"] == end], ["dept"])
    by_dept["name"] = by_dept["dept"].map(names)
    by_dept["diff"] = (by_dept["avg_price"] - france) * 100
    by_dept = by_dept.sort_values("avg_price")
    cheap, exp = by_dept.iloc[0], by_dept.iloc[-1]
    gap = exp["avg_price"] - cheap["avg_price"]

    st.subheader(f"In {end}, {fuel} was cheapest in {cheap['name']} and most expensive in {exp['name']}.")
    st.write(f"The difference is {gap:.2f} €/L. For a 50 L tank, that is about {gap * 50:.0f} € more.")

    col1, col2 = st.columns([3, 2])
    with col1:
        st.markdown(f"#### Price vs France average, {end}")
        st.plotly_chart(dept_map(by_dept, geo), width="stretch")
        st.caption(f"Blue = cheaper than the France average ({france:.3f} €/L). Red = more expensive.")
    with col2:
        st.markdown(f"#### 5 cheapest and 5 most expensive, {end}")
        top = pd.concat([by_dept.head(5).assign(group="Cheapest"),
                         by_dept.tail(5).assign(group="Most expensive")]).drop_duplicates("dept")
        st.plotly_chart(ranking_bars(top), width="stretch")
        st.caption(f"Average {fuel} price per department.")

    st.markdown(
        """
- **Brittany and the west** are the cheapest.
- **Paris, the area around it and Corsica** are the most expensive.
- Possible reasons (not proven by this data): Corsica is an island so fuel comes by boat.
  Paris has few stations and high rents. The west has a lot of supermarket stations.
"""
    )

    # heatmap: is the ranking the same every year?
    reg = weighted_avg(f, ["year", "region"])
    reg["diff"] = (reg["avg_price"] - reg["year"].map(france_by_year)) * 100
    pivot = reg.pivot(index="region", columns="year", values="diff")
    pivot = pivot.loc[pivot.mean(axis=1).sort_values().index]

    cheapest = reg.loc[reg.groupby("year")["diff"].idxmin(), "region"].unique()
    if len(cheapest) == 1 and reg["year"].nunique() > 1:
        st.markdown(f"#### {cheapest[0]} is the cheapest region every year")
    else:
        st.markdown("#### Each region vs the France average, every year")
    st.plotly_chart(region_heatmap(pivot), width="stretch")
    st.caption("Each number = cents per litre above (red) or below (blue) the France average that year.")

    with st.expander("How it's calculated"):
        st.markdown(
            """
- **Map and grid:** (price of the area - France average) x 100, in cents per litre. White = same as France.
- **France average:** all stations of mainland France and Corsica, weighted by the number of stations.
- **Station chart below:** I sort all the stations of a region by price.
  Cheap station = 10% of stations are cheaper. Typical station = the one in the middle (median).
  Expensive station = 10% of stations are more expensive.
- **Between regions:** the gap between the region with the lowest typical price and the one with the highest (Corsica left out).
"""
        )

    # stations: how much prices vary inside a region
    s = stations[stations["fuel"] == fuel].copy()
    s["region"] = s["dept"].map(DEPT_TO_REGION)
    s = s[s["region"].isin(regions)]
    if s["region"].nunique() < 2:
        return

    p = s.groupby("region")["price"].quantile([0.1, 0.9]).unstack()
    within = (p[0.9] - p[0.1]).median()
    medians = s.groupby("region")["price"].median().drop("Corse", errors="ignore")
    between = medians.max() - medians.min()

    if within > between:
        st.markdown("#### Picking the right station matters more than the region")
    else:
        st.markdown("#### Prices also change a lot inside each region")
    st.write(f"From one region to another, the typical price changes by about {between:.2f} €/L. "
             f"Inside one region, a cheap station and an expensive one are about {within:.2f} €/L apart.")
    if "Corse" in s["region"].values:
        st.write("Corsica is left out of this comparison. It is an island and much more expensive.")

    st.plotly_chart(station_range(s, france_by_year[2025]), width="stretch")
    st.caption("2025 only. One line per region, from a cheap station (blue) to an expensive one (red). "
               "The long lines show that stations in the same region have very different prices.")
