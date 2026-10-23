# loading the processed files (made by prepare_data.py)
import json
import os

import pandas as pd
import streamlit as st

from utils.prep import add_time_cols

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

SOURCE = "Prix des carburants en France (Ministère de l'Économie), via data.gouv.fr"
SOURCE_URL = "https://www.data.gouv.fr/datasets/prix-des-carburants-en-france-flux-quotidien-1"
LICENSE = "Licence Ouverte / Open Licence (Etalab)"


@st.cache_data(show_spinner=False)
def load_monthly():
    df = pd.read_csv(os.path.join(DATA_DIR, "monthly_prices.csv"), dtype={"dept": str})
    return add_time_cols(df)


@st.cache_data(show_spinner=False)
def load_stations():
    return pd.read_csv(os.path.join(DATA_DIR, "stations_2025.csv"), dtype={"dept": str, "station_id": str})


@st.cache_data(show_spinner=False)
def load_quality():
    return pd.read_csv(os.path.join(DATA_DIR, "quality_report.csv"))


@st.cache_data(show_spinner=False)
def load_geojson():
    with open(os.path.join(DATA_DIR, "departements.geojson"), encoding="utf-8") as f:
        geo = json.load(f)
    names = {feat["properties"]["code"]: feat["properties"]["nom"] for feat in geo["features"]}
    return geo, names
