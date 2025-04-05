import pandas as pd
import numpy as np

# Function to calculate financial metrics
def calculate_financial_metrics(prices_df : pd.DataFrame):
    # Calculate daily returns
    prices_df['daily_return'] = prices_df['price'].pct_change()
    
    # Calculate CAGR
    start_price = prices_df['price'].iloc[0]
    end_price = prices_df['price'].iloc[-1]
    days = (prices_df['snapped_at'].iloc[-1] - prices_df['snapped_at'].iloc[0]).days
    years = days / 365.25
    cagr = ((end_price / start_price) ** (1/years) - 1) * 100
    
    metrics = {
        'CAGR (%)': cagr,
        'Average Daily Return (%)': prices_df['daily_return'].mean() * 100,
        'Daily Volatility (%)': prices_df['daily_return'].std() * 100,
        'Sharpe Ratio': (prices_df['daily_return'].mean() / prices_df['daily_return'].std()) * np.sqrt(252),  # Annualized
        'Max Drawdown (%)': calculate_max_drawdown(prices_df['price'])
    }
    
    return metrics




