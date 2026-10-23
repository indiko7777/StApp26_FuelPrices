# cleaning helpers + region list
import pandas as pd

FUELS = {"Gazole": "Diesel", "E10": "E10", "SP98": "SP98"}

# 13 regions of metropolitan France -> department codes
REGIONS = {
    "Auvergne-Rhône-Alpes": ["01", "03", "07", "15", "26", "38", "42", "43", "63", "69", "73", "74"],
    "Bourgogne-Franche-Comté": ["21", "25", "39", "58", "70", "71", "89", "90"],
    "Bretagne": ["22", "29", "35", "56"],
    "Centre-Val de Loire": ["18", "28", "36", "37", "41", "45"],
    "Corse": ["2A", "2B"],
    "Grand Est": ["08", "10", "51", "52", "54", "55", "57", "67", "68", "88"],
    "Hauts-de-France": ["02", "59", "60", "62", "80"],
    "Île-de-France": ["75", "77", "78", "91", "92", "93", "94", "95"],
    "Normandie": ["14", "27", "50", "61", "76"],
    "Nouvelle-Aquitaine": ["16", "17", "19", "23", "24", "33", "40", "47", "64", "79", "86", "87"],
    "Occitanie": ["09", "11", "12", "30", "31", "32", "34", "46", "48", "65", "66", "81", "82"],
    "Pays de la Loire": ["44", "49", "53", "72", "85"],
    "Provence-Alpes-Côte d'Azur": ["04", "05", "06", "13", "83", "84"],
}

DEPT_TO_REGION = {d: r for r, depts in REGIONS.items() for d in depts}

# prices outside this range (€/L) are treated as typing errors
MIN_PRICE = 0.5
MAX_PRICE = 3.5


def cp_to_dept(cp):
    """postcode -> department code, None if not metropolitan France"""
    cp = str(cp).strip().zfill(5)
    if not cp.isdigit():
        return None
    dept = cp[:2]
    if dept == "20":
        # Corsica: 200xx-201xx is 2A, 202xx+ is 2B
        dept = "2A" if int(cp) < 20200 else "2B"
    if dept not in DEPT_TO_REGION:
        return None
    return dept


def fix_price(value):
    """old files store 1328 for 1.328 €/L, new ones store 1.328"""
    if value is None or value == "":
        return None
    p = float(value)
    if p > 10:
        p = p / 1000
    return p


def weighted_avg(df, by):
    """average price weighted by number of stations (rows are already averages)"""
    df = df.assign(_w=df["avg_price"] * df["n_stations"])
    out = df.groupby(by, as_index=False).agg(_w=("_w", "sum"), n_stations=("n_stations", "sum"))
    out["avg_price"] = out["_w"] / out["n_stations"]
    return out.drop(columns="_w")


def add_time_cols(df):
    df["month"] = pd.to_datetime(df["month"])
    df["year"] = df["month"].dt.year
    return df
