import numpy as np
import pandas as pd

def run_monte_carlo(initial_value, cagr, volatility, years=10, simulations=500):
    """
    Run Monte Carlo simulation using geometric Brownian motion to model future portfolio wealth.
    
    Parameters:
    - initial_value: Starting portfolio value
    - cagr: Compound Annual Growth Rate (annualized return)
    - volatility: Annualized volatility
    - years: Number of years to simulate
    - simulations: Number of simulation paths to run
    
    Returns:
    - DataFrame with 10th, 50th, and 90th percentile projections indexed by year
    """
    # Trading days per year
    days = years * 252
    
    # Calculate daily parameters
    daily_drift = cagr / 252
    daily_vol = volatility / np.sqrt(252)
    
    # Generate random shocks for all simulations
    shock_matrix = np.random.normal(daily_drift, daily_vol, (days, simulations))
    
    # Calculate cumulative returns using geometric Brownian motion
    price_paths = initial_value * np.exp(np.cumsum(shock_matrix, axis=0))
    
    # Extract percentiles for each day
    percentile_10 = np.percentile(price_paths, 10, axis=1)
    percentile_50 = np.percentile(price_paths, 50, axis=1)
    percentile_90 = np.percentile(price_paths, 90, axis=1)
    
    # Create year index (fractional years)
    year_index = np.linspace(0, years, days)
    
    # Build DataFrame
    df = pd.DataFrame({
        '10th Percentile (Bear Market)': percentile_10,
        '50th Percentile (Expected)': percentile_50,
        '90th Percentile (Bull Market)': percentile_90
    }, index=year_index)
    
    df.index.name = 'Year'
    
    return df
