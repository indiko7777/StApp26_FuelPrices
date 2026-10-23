import streamlit as st

from utils.prep import weighted_avg
from utils.viz import fuel_lines


def show(df, base, fuel):
    # df = filtered by years and regions, base = filtered by regions only (to get 2019)
    f = df[df["fuel"] == fuel]
    by_month = weighted_avg(f, ["month"])
    by_year = weighted_avg(f, ["year"]).set_index("year")["avg_price"]
    # use the years that really have data (some fuels are missing in Corsica)
    start, end = by_year.index[0], by_year.index[-1]
    by_dept = weighted_avg(f[f["year"] == end], ["dept"])

    st.header("1. Did prices go back down?")

    p_start, p_end = by_year[start], by_year[end]
    change = (p_end - p_start) / p_start * 100
    if start == end:
        st.subheader(f"In {end}, {fuel} cost {p_end:.2f} €/L on average.")
    else:
        word = "more" if change > 0 else "less"
        st.subheader(f"In {end}, {fuel} cost {p_end:.2f} €/L. That is {abs(change):.0f}% {word} than in {start}.")

    # KPIs
    top = by_month.loc[by_month["avg_price"].idxmax()]
    low = by_month.loc[by_month["avg_price"].idxmin()]
    gap = by_dept["avg_price"].max() - by_dept["avg_price"].min()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(f"Average price {end}", f"{p_end:.3f} €/L",
              None if start == end else f"{p_end - p_start:+.3f} vs {start}", delta_color="inverse")
    c2.metric("Highest month", f"{top['avg_price']:.3f} €/L", top["month"].strftime("%b %Y"),
              delta_color="off", delta_arrow="off")
    c3.metric("Lowest month", f"{low['avg_price']:.3f} €/L", low["month"].strftime("%b %Y"),
              delta_color="off", delta_arrow="off")
    c4.metric(f"Cheapest vs priciest dept. {end}", f"{gap:.3f} €/L",
              f"{gap * 50:.0f} € on a 50 L tank", delta_color="off", delta_arrow="off")

    # all fuels on one chart
    all_fuels = weighted_avg(df, ["month", "fuel"])
    st.markdown("#### All 3 fuels, month by month")
    st.plotly_chart(fuel_lines(all_fuels), width="stretch")
    st.caption("Average price at the pump in France. Red dashed lines = big events. Red band = state discount.")

    st.markdown(
        """
- **2020:** COVID. Nobody was driving, prices hit their lowest.
- **2022:** war in Ukraine. Prices passed 2 €/L in June.
- **Apr to Dec 2022:** the state discount (red band). Prices drop twice even though oil was still expensive.
- **2023 to 2025:** prices go down slowly.
"""
    )
    with st.expander("What is the state discount?"):
        st.markdown(
            """
In 2022 the French government paid part of the fuel price for every driver (the *remise carburant*).
The station took it off the price at the pump, and the state paid the station back.

| Period | Discount per litre |
|---|---|
| 1 April to 31 August 2022 | 18 cts |
| 1 September to 15 November 2022 | 30 cts |
| 16 November to 31 December 2022 | 10 cts |

The prices in this data are what drivers really paid, so the discount is included.
Without it, prices in 2022 would have been even higher.
"""
        )

    pivot = all_fuels.pivot(index="month", columns="fuel", values="avg_price")
    if {"Diesel", "E10"} <= set(pivot.columns):
        n = int((pivot["Diesel"] > pivot["E10"]).sum())
        if n > 0:
            st.info(f"Diesel is usually the cheapest fuel. But it cost more than E10 for {n} months, mostly in 2022.")

    # compared to 2019
    ref = weighted_avg(base[base["year"] == 2019], ["fuel"]).set_index("fuel")["avg_price"]
    idx = all_fuels.assign(pct=(all_fuels["avg_price"] / all_fuels["fuel"].map(ref) - 1) * 100).dropna()
    if idx.empty:
        return
    last = idx[idx["month"] == idx["month"].max()]
    st.markdown("#### Are we back to 2019 prices?")
    if (last["pct"] > 0).all():
        st.write(f"**No.** In {last['month'].iloc[0]:%B %Y}, all fuels are still "
                 f"{last['pct'].min():.0f}% to {last['pct'].max():.0f}% above their 2019 price.")
    st.plotly_chart(fuel_lines(idx, y="pct", ylabel="% vs 2019 average", fmt="+.1f", unit=" %",
                               ref=0, end_labels=False), width="stretch")
    st.caption("0 = the average price of 2019. Above 0 = more expensive than in 2019.")

    with st.expander("How it's calculated"):
        st.markdown(
            """
- **Monthly price:** for each station, the average of all its prices in the month. Then the average of all stations.
- **Combining departments:** weighted by the number of stations, so big departments count more than small ones.
- **% vs 2019:** (price of the month / average price of 2019 - 1) x 100.
"""
        )
