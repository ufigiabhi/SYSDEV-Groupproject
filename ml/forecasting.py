import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX

'''
def load_and_prepare_series(csv_path, product_column):
    """
    loads a csv file and returns a cleaned pandas series
    indexed by date for the selected product
    """

    # will handle coffee vs croissant csv formats
    peek = pd.read_csv(csv_path, nrows=1)

    if any("Unnamed" in str(col) for col in peek.columns):
        df = pd.read_csv(csv_path, header=[0, 1])
        df.columns = [c[1] if "Unnamed" not in c[1] else c[0] for c in df.columns]
    else:
        df = pd.read_csv(csv_path)

    df.columns = df.columns.str.strip()

    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True)
    df.set_index("Date", inplace=True)

    series = pd.to_numeric(df[product_column], errors="coerce").dropna()
    return series 
'''
def sarima_forecast(series, steps=7):
    """
    trains a SARIMA model and returns a forecast series
    """

    model = SARIMAX(
        series,
        order=(1, 1, 1),
        seasonal_order=(1, 1, 1, 7),
        enforce_stationarity=False,
        enforce_invertibility=False
    )

    result = model.fit(disp=False)
    forecast = result.forecast(steps=steps)

    return forecast
