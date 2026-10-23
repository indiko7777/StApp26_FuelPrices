import streamlit as st

from utils.io import SOURCE, SOURCE_URL, LICENSE


def show():
    st.title("Fuel prices in France: are we back to normal?")
    st.caption(f"Source: [{SOURCE}]({SOURCE_URL}) | {LICENSE} | 2019 to 2025")

    st.markdown(
        """
In June 2022, a litre of diesel cost more than **2 €** on average.
Prices went down since then. But are they really back to how they were before?
And does it matter where you live?

**For:** everyday drivers in France.

**Questions:**
1. Did prices go back down after the 2022 crisis?
2. Where is fuel the cheapest, and where is it the most expensive?
3. What makes a station cheap or expensive?
"""
    )
    with st.expander("About the data"):
        st.markdown(
            """
- Every fuel station in France has to send its prices to the government.
- The yearly files have **every price change** of every station (about 3.5 million per year).
- I kept 3 fuels: Diesel (Gazole), E10 and SP98.
- I made one average per station per month, then one average per department per month.
- Prices are what you pay at the pump, taxes included, in € per litre.
- Only mainland France and Corsica are in the data.
"""
        )
