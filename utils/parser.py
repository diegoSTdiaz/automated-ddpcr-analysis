import pandas as pd

def parse_qxmanager_csv(df):
    df = df.copy()
    df["Well"] = df["Well"].astype(str).str.upper()
    df["Copies/µL"] = pd.to_numeric(df["Copies/µL"], errors="coerce").fillna(0)
    return df
