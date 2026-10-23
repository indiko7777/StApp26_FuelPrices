# Fuel prices in France: are we back to normal?

Streamlit dashboard, EFREI Data Visualization project 2026.
By Indiko JABUA (Data Engineering, M1). Project proposed by Prof. Mano Mathew.

Live app: https://fuel-prices-france-jabua.streamlit.app  
Code: https://github.com/indiko7777/StApp26_FuelPrices  
Demo video: `StApp26_20221030_JABUA_DE1_demo.mp4` (in the zip)

## The story

In June 2022, diesel cost more than 2 € a litre. This dashboard is for drivers and answers 3 questions:

1. Did prices go back down after 2022?
2. Where is fuel the cheapest and the most expensive?
3. What makes a station cheap or expensive?

| Part of the page | What it says |
|---|---|
| Intro | Why it matters, where the data comes from |
| 1. Did prices go back down? | No. All fuels are still 10 to 13% above 2019 |
| 2. Where is fuel the cheapest? | Brittany every year. Paris and Corsica are the most expensive. But stations in the same region differ more than regions do |
| 3. What makes a station cheap? | Motorway stations cost about 16 cts more. Small garage stations and stations that rarely change their price also cost more |
| Data quality | What I removed and checked, limits |
| Conclusion | What drivers and the government can do |

## Main results

- Diesel: 1.46 € in 2019, 2.10 € in June 2022, 1.64 € in 2025 (+13% vs 2019).
- Diesel cost more than E10 from March 2022 to January 2023.
- Cheapest department: Finistère. Most expensive: Paris. Gap: 0.20 € per litre, about 10 € per tank.
- In one region, a cheap and an expensive station are about 0.15 € apart. Between regions, only about 0.09 €.

## Data

- Dataset: [Prix des carburants en France](https://www.data.gouv.fr/datasets/prix-des-carburants-en-france-flux-quotidien-1) on data.gouv.fr (Ministry of Economy).
- License: Licence Ouverte (free to reuse if you cite the source).
- I used the yearly files from 2019 to 2025. Links are in `dataset_link.txt`.
- Map shapes: [france-geojson](https://github.com/gregoiredavid/france-geojson) (made from IGN and INSEE data).
- No personal data. The data is about fuel stations.

## How to run

```
pip install -r requirements.txt
streamlit run app.py
```

Then open http://localhost:8501. The cleaned data is already in `data/`.

To download and clean the raw data again (about 200 MB, 10 minutes):

```
python prepare_data.py
```

## What I did with the data

1. Downloaded the 7 yearly files (XML, about 300 MB each, every price change of every station).
2. Kept 3 fuels: Diesel, E10, SP98.
3. Fixed old prices written `1328` instead of `1.328`.
4. Removed prices under 0.50 € or over 3.50 €, duplicates and fake postcodes.
5. Found the department from the postcode.
6. Made one average per station per month, then per department per month.
7. For 2025, added for each station: motorway or not, repair garage or not, how often it changes its price.

## Files

```
app.py              the page: sidebar + sections in order
prepare_data.py     downloads and cleans the raw data
sections/           one file per part of the page
utils/              loading data, cleaning functions, charts
data/               the cleaned data used by the app
assets/             EFREI logo
.streamlit/         light theme
requirements.txt    Python packages
dataset_link.txt    links to the data
```

## Limits

- Every station counts the same. The data has no litres sold.
- A price that lasted 1 hour counts like one that lasted 2 weeks.
- No overseas departments in the data.
- Prices are not adjusted for inflation.
- The data shows what happened, not why.
