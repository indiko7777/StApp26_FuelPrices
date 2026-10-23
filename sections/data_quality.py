import streamlit as st


def show(monthly, quality):
    st.header("Data quality")
    st.write("What I checked and what I removed before making the charts.")

    st.markdown(
        """
**Cleaning steps**
1. Old files (2019 to 2021) write prices like `1328` instead of `1.328`. I divided them by 1000.
2. I removed prices below 0.50 €/L or above 3.50 €/L. These are typing mistakes.
3. I removed duplicates (same station, same fuel, same time).
4. I removed stations with a fake postcode (like `99999`).
5. I found the department from the postcode. Corsica (20xxx) is split in 2A and 2B.
"""
    )

    q = quality.rename(columns={
        "year": "Year", "stations_in_file": "Stations in file", "stations_kept": "Stations kept",
        "stations_dropped": "Bad postcode", "price_rows": "Price rows", "duplicates": "Duplicates",
        "out_of_range": "Out of range", "missing_price": "Missing price",
        "missing_coords": "Missing GPS", "price_rows_kept": "Rows kept",
    })
    q = q[["Year", "Stations in file", "Stations kept", "Bad postcode", "Missing GPS",
           "Price rows", "Duplicates", "Out of range", "Missing price", "Rows kept"]]
    st.dataframe(q, hide_index=True, width="stretch")
    st.caption("'Stations in file' is higher than 'Stations kept' because closed stations stay in the file "
               "with no price for the year.")

    # checks on the final table used by the app
    st.write("**Checks on the final table**")
    per_month = monthly.groupby("month")["dept"].nunique()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rows", f"{len(monthly):,}")
    c2.metric("Missing values", int(monthly.isna().sum().sum()))
    c3.metric("Duplicate rows", int(monthly.duplicated(["month", "dept", "fuel", "road"]).sum()))
    c4.metric("Departments per month (96 expected)", f"{per_month.min()} to {per_month.max()}")

    with st.expander("Limits of this data"):
        st.markdown(
            """
- The average is per **station**, not per litre sold. A big station counts the same as a small one.
- In a month, I average every price change. A price that lasted 1 hour counts like one that lasted 2 weeks.
- About 5% of stations are on motorways. They cost about 17 cts/L more and are included in the averages.
- Prices are not adjusted for inflation.
- This data shows **what** happened, not **why**. The reasons I give (war, COVID, discount) come from the news.
- The station data (section 3) is for 2025 only. "Repair garage" comes from the services the station declares itself.
"""
        )

    with st.expander("Ethics and license"):
        st.markdown(
            """
- **No personal data.** The data is about fuel stations (businesses), not people.
- **Data license:** Licence Ouverte / Open Licence (Etalab). Free to reuse if the source is cited, which I do at the top of the page.
- **Map shapes:** from the open project france-geojson (based on official IGN / INSEE data).
- I don't claim causes. When I give a reason (war, island, no competition), I say it is not proven by the data.
"""
        )
