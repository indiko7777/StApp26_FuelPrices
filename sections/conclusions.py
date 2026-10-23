import streamlit as st


def show():
    st.header("Conclusion")

    st.markdown(
        """
**What I found**
- Prices went down after 2022, but **not back to 2019**. In 2025 diesel is still about 13% more expensive than in 2019.
- 2022 was not normal. Diesel even cost more than E10 for months.
- **Where you live matters a bit.** Brittany is the cheapest region almost every year. Paris and Corsica are the most expensive.
- **Which station you pick matters more.** Inside one region, stations differ more than regions differ from each other (Corsica aside).
- **Motorway stations are the most expensive** (about +16 cts/L vs their department). Small stations with a repair garage and stations that rarely change their price are also pricier.

**What it means for drivers**
- Do not expect 1.45 €/L again soon.
- Fill up before getting on the motorway.
- Compare stations near you before filling up: [prix-carburants.gouv.fr](https://www.prix-carburants.gouv.fr).
  On a 50 L tank, the right station saves more than living in a cheaper region.

**What it means for public decision makers**
- Help like the 2022 discount works fast (prices dropped the same month), but it is expensive and temporary.
- Making price comparison easier (like the official website) helps drivers every day, at no cost.

**Next steps**
- Add 2026 when the full year is out.
- Weight the averages by litres sold (not in this data).
- Compare with oil prices (Brent) to see how fast pump prices follow.
"""
    )
