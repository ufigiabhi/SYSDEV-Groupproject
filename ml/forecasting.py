import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX


def load_and_prepare_series(series_df, product_column):
    """
    Takes a dataframe with Date and product column, returns a cleaned pandas series
    indexed by date for the selected product
    """
    # Make a copy to avoid modifying original
    df = series_df.copy()
    
    # Ensure Date column is datetime
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
    
    # Drop rows with invalid dates or NaN in product column
    df = df.dropna(subset=["Date", product_column])
    
    if df.empty:
        raise ValueError(f"No valid data for {product_column}")
    
    # Set index and return series
    df.set_index("Date", inplace=True)
    series = df[product_column]
    
    # Ensure it's numeric
    series = pd.to_numeric(series, errors="coerce").dropna()
    
    return series


def sarima_forecast(series, steps=7):
    """
    trains a SARIMA model and returns a forecast series
    """
    if len(series) < 14:
        raise ValueError(f"Need at least 14 data points, got {len(series)}")
    
    try:
        model = SARIMAX(
            series,
            order=(1, 1, 1),
            seasonal_order=(1, 1, 1, 7),
            enforce_stationarity=False,
            enforce_invertibility=False,
            initialization='approximate_diffuse'
        )
        
        result = model.fit(disp=False, maxiter=200)
        forecast = result.forecast(steps=steps)
        
        # Ensure forecast is positive (no negative sales)
        forecast = forecast.clip(lower=0)
        
        return forecast
        
    except Exception as e:
        raise Exception(f"SARIMA forecast failed: {str(e)}")