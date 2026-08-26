import pandas as pd
import numpy as np
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from datetime import timedelta

class ForecastingEngine:
    def __init__(self, df: pd.DataFrame):
        """
        Expects a daily aggregated dataframe with 'date' and 'amount' columns.
        """
        self.df = df.copy()
        if not self.df.empty:
            self.df = self.df.sort_values('date').reset_index(drop=True)
            # Ensure no missing dates by filling with 0
            self.df.set_index('date', inplace=True)
            # Find min and max date
            idx = pd.date_range(self.df.index.min(), self.df.index.max())
            self.df = self.df.reindex(idx, fill_value=0)
            self.df = self.df.reset_index().rename(columns={'index': 'date'})
        
    def forecast_category(self, category: str, horizon_days: int = 30):
        if self.df.empty:
            return self._empty_forecast(category, horizon_days)
            
        history_days = len(self.df)
        
        if history_days < 45:
            # Fallback to simple average
            return self._fallback_forecast(category, horizon_days)
            
        return self._predict(category, horizon_days)
        
    def _predict(self, category: str, horizon_days: int):
        series = self.df['amount'].values
        
        # Exponential Smoothing / Holt-Winters
        # Use additive trend and seasonality. 7-day seasonal period captures weekly spending habits.
        try:
            model = ExponentialSmoothing(
                series,
                trend='add',
                seasonal='add',
                seasonal_periods=7,
                initialization_method="estimated"
            )
            fit_model = model.fit()
            forecast = fit_model.forecast(horizon_days)
            
            # Ensure no negative values
            forecast = np.maximum(forecast, 0)
            
            # Determine trend direction
            trend = self._trend_direction(series)
            
            # Generate future dates
            last_date = self.df['date'].iloc[-1]
            future_dates = [(last_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(1, horizon_days + 1)]
            
            return {
                "category": category,
                "horizon_days": horizon_days,
                "forecast_dates": future_dates,
                "forecast_values": forecast.tolist(),
                "trend": trend,
                "method": "holt-winters"
            }
        except Exception as e:
            print(f"Forecasting error for {category}: {e}")
            return self._fallback_forecast(category, horizon_days)
            
    def _fallback_forecast(self, category: str, horizon_days: int):
        if self.df.empty:
            return self._empty_forecast(category, horizon_days)
            
        avg_amount = self.df['amount'].mean()
        forecast = [max(avg_amount, 0)] * horizon_days
        
        trend = self._trend_direction(self.df['amount'].values)
        
        last_date = self.df['date'].iloc[-1]
        future_dates = [(last_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(1, horizon_days + 1)]
        
        return {
            "category": category,
            "horizon_days": horizon_days,
            "forecast_dates": future_dates,
            "forecast_values": forecast,
            "trend": trend,
            "method": "average-fallback"
        }
        
    def _empty_forecast(self, category: str, horizon_days: int):
        return {
            "category": category,
            "horizon_days": horizon_days,
            "forecast_dates": [],
            "forecast_values": [],
            "trend": "stable",
            "method": "none"
        }
        
    def _trend_direction(self, series: np.ndarray) -> str:
        if len(series) < 2:
            return "stable"
            
        # Fit a simple linear regression to find the slope over the recent past (e.g., last 30-45 days if possible)
        recent_series = series[-45:] if len(series) >= 45 else series
        x = np.arange(len(recent_series))
        
        # Avoid perfectly flat cases throwing errors by checking variance
        if np.var(recent_series) == 0:
            return "stable"
            
        slope, _ = np.polyfit(x, recent_series, 1)
        
        # Define threshold for stable (slope close to 0)
        mean_val = np.mean(recent_series)
        # Normalize slope relatively to mean to determine threshold
        if mean_val == 0:
            threshold = 0.5
        else:
            threshold = (mean_val * 0.01) # 1% of mean per day change
            
        if slope > threshold:
            return "increasing"
        elif slope < -threshold:
            return "decreasing"
        else:
            return "stable"
