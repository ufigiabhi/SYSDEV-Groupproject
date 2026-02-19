import pandas as pd
import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error
import warnings
warnings.filterwarnings('ignore')

class AdvancedForecaster:
    def __init__(self):
        self.models = {}
        self.metrics = {}
        
    def prepare_series(self, df, product_column):
        """Prepare time series data with advanced features"""
        data = df.copy()
        
        # Ensure Date column is datetime
        data['Date'] = pd.to_datetime(data['Date'], dayfirst=True, errors='coerce')
        data = data.dropna(subset=['Date', product_column])
        
        if data.empty:
            return None
        
        # Set date as index
        data.set_index('Date', inplace=True)
        series = pd.to_numeric(data[product_column], errors='coerce').dropna()
        
        if len(series) == 0:
            return None
        
        # Add time-based features
        series_df = pd.DataFrame({'sales': series})
        series_df['day_of_week'] = series_df.index.dayofweek
        series_df['month'] = series_df.index.month
        series_df['week_of_year'] = series_df.index.isocalendar().week
        series_df['is_weekend'] = series_df['day_of_week'].isin([5, 6]).astype(int)
        
        return series_df
    
    def sarima_forecast(self, series_df, steps=7, product_name=""):
        """Advanced SARIMA forecasting with auto-parameter tuning"""
        try:
            if series_df is None or len(series_df) == 0:
                return self._simple_forecast_array(steps), {}
            
            sales_series = series_df['sales']
            
            if len(sales_series) < 14:  # Need at least 2 weeks
                return self._simple_forecast_series(sales_series, steps), {}
            
            # Try different SARIMA parameters
            best_model = None
            best_aic = np.inf
            best_forecast = None
            
            # Simplified grid search for performance
            param_combinations = [
                ((1, 1, 1), (1, 1, 1, 7)),
                ((0, 1, 1), (1, 1, 0, 7)),
                ((1, 1, 0), (0, 1, 1, 7)),
                ((0, 1, 0), (1, 1, 1, 7)),
                ((1, 0, 1), (1, 0, 1, 7)),
            ]
            
            for order, seasonal_order in param_combinations:
                try:
                    model = SARIMAX(
                        sales_series,
                        order=order,
                        seasonal_order=seasonal_order,
                        enforce_stationarity=False,
                        enforce_invertibility=False
                    )
                    result = model.fit(disp=False, maxiter=50)
                    
                    if result.aic < best_aic:
                        best_aic = result.aic
                        best_model = result
                        best_forecast = result.forecast(steps=steps)
                except:
                    continue
            
            if best_forecast is None:
                return self._simple_forecast_series(sales_series, steps), {}
            
            # Calculate metrics on last 20% of data
            train_size = int(len(sales_series) * 0.8)
            if train_size < 7:
                train_size = max(7, len(sales_series) - 7)
            
            train = sales_series[:train_size]
            test = sales_series[train_size:]
            
            mae = 0
            mape = 0
            
            if len(test) > 0 and len(train) >= 14:
                try:
                    # Fit model on train data
                    model = SARIMAX(
                        train,
                        order=(1, 1, 1),
                        seasonal_order=(1, 1, 1, 7)
                    )
                    result = model.fit(disp=False, maxiter=50)
                    test_forecast = result.forecast(steps=len(test))
                    
                    mae = mean_absolute_error(test, test_forecast)
                    mape = mean_absolute_percentage_error(test, test_forecast) * 100
                except:
                    pass
            
            self.metrics[product_name] = {
                'MAE': round(mae, 2),
                'MAPE': round(mape, 2),
                'Best_AIC': round(best_aic, 2),
                'Data_Points': len(sales_series),
                'Last_Value': float(sales_series.iloc[-1]),
                'Forecast_Mean': float(best_forecast.mean()),
                'Forecast_Std': float(best_forecast.std())
            }
            
            return best_forecast.clip(lower=0), self.metrics.get(product_name, {})
            
        except Exception as e:
            print(f"Advanced forecast failed: {e}")
            if series_df is not None and 'sales' in series_df:
                return self._simple_forecast_series(series_df['sales'], steps), {}
            return self._simple_forecast_array(steps), {}
    
    def _simple_forecast_series(self, series, steps):
        """Fallback forecasting method for pandas Series"""
        if len(series) == 0:
            return pd.Series([0] * steps)
        
        # Simple moving average forecast
        last_week_avg = series[-7:].mean() if len(series) >= 7 else series.mean()
        return pd.Series([last_week_avg] * steps)
    
    def _simple_forecast_array(self, steps):
        """Fallback forecasting method returning array"""
        return pd.Series([0] * steps)
    
    def calculate_stats(self, df, product_column):
        """Calculate comprehensive statistics"""
        try:
            data = df.copy()
            data['Date'] = pd.to_datetime(data['Date'], dayfirst=True, errors='coerce')
            data = data.dropna(subset=['Date', product_column])
            
            if data.empty:
                return {}
            
            series = pd.to_numeric(data[product_column], errors='coerce').dropna()
            
            if len(series) < 2:
                return {}
            
            stats = {
                'total_sold': int(series.sum()),
                'avg_daily': round(series.mean(), 2),
                'std_daily': round(series.std(), 2),
                'min_daily': int(series.min()),
                'max_daily': int(series.max()),
                'total_days': len(series),
                'current_trend': self._calculate_trend(series),
                'weekly_pattern': self._analyze_weekly_pattern(data, product_column),
                'best_day': self._find_best_day(data, product_column),
                'waste_estimate': self._estimate_waste(series)
            }
            
            return stats
        except Exception as e:
            print(f"Stats calculation error: {e}")
            return {}
    
    def _calculate_trend(self, series):
        """Calculate trend direction"""
        if len(series) < 14:
            return "Insufficient data"
        
        recent = series[-14:].mean()
        previous = series[-28:-14].mean() if len(series) >= 28 else series[:-14].mean()
        
        if recent > previous * 1.1:
            return "📈 Increasing"
        elif recent < previous * 0.9:
            return "📉 Decreasing"
        else:
            return "➡️ Stable"
    
    def _analyze_weekly_pattern(self, df, product_column):
        """Analyze weekly sales patterns"""
        try:
            df_copy = df.copy()
            df_copy['day_name'] = pd.to_datetime(df_copy['Date']).dt.day_name()
            daily_avg = df_copy.groupby('day_name')[product_column].mean()
            
            if len(daily_avg) > 0:
                best_day = daily_avg.idxmax()
                worst_day = daily_avg.idxmin()
                return f"Best: {best_day}, Worst: {worst_day}"
            return "No pattern"
        except:
            return "No pattern"
    
    def _find_best_day(self, df, product_column):
        """Find the best selling day"""
        try:
            df_copy = df.copy()
            df_copy['day_name'] = pd.to_datetime(df_copy['Date']).dt.day_name()
            daily_totals = df_copy.groupby('day_name')[product_column].sum()
            
            if len(daily_totals) > 0:
                return daily_totals.idxmax()
            return "Unknown"
        except:
            return "Unknown"
    
    def _estimate_waste(self, series):
        """Estimate potential waste based on variability"""
        if len(series) < 7:
            return "N/A"
        
        std_dev = series.std()
        avg_sales = series.mean()
        
        if avg_sales > 0:
            waste_percentage = (std_dev / avg_sales) * 100
            return f"{min(100, round(waste_percentage, 1))}%"
        return "0%"


# Simple functions for backward compatibility
def load_and_prepare_series(df, product_column):
    forecaster = AdvancedForecaster()
    series_df = forecaster.prepare_series(df, product_column)
    if series_df is not None:
        return series_df['sales']
    return pd.Series()


def sarima_forecast(series, steps=7):
    forecaster = AdvancedForecaster()
    forecast, _ = forecaster.sarima_forecast(
        pd.DataFrame({'sales': series}), 
        steps=steps
    )
    return forecast