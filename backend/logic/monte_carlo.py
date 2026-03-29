import numpy as np
import pandas as pd

def run_monte_carlo(initial_value, cagr, volatility, years=10, simulations=500, annual_withdrawal=0):
    """
    Run Monte Carlo simulation using path-dependent geometric Brownian motion with withdrawals.
    
    Parameters:
    - initial_value: Starting portfolio value
    - cagr: Compound Annual Growth Rate (annualized return)
    - volatility: Annualized volatility
    - years: Number of years to simulate
    - simulations: Number of simulation paths to run
    - annual_withdrawal: Fixed dollar amount withdrawn every year
    
    Returns:
    - DataFrame with 10th, 50th, and 90th percentile projections indexed by year
    """
    # Calculate fundamental daily variables
    days = int(years * 252)
    daily_withdrawal = annual_withdrawal / 252
    drift = (cagr - 0.5 * volatility**2) / 252
    shock = volatility / np.sqrt(252)
    
    # Generate the entire matrix of random daily returns for all simulations at once
    Z = np.random.normal(0, 1, (days, simulations))
    daily_returns = np.exp(drift + shock * Z)
    
    # Initialize a portfolio values matrix with zeros
    portfolio_values = np.zeros((days, simulations))
    
    # Set the starting value
    portfolio_values[0] = initial_value
    
    # The Path-Dependent Loop: Create a for loop from i = 1 to days
    for i in range(1, days):
        # Apply the return and subtract the withdrawal
        new_value = portfolio_values[i-1] * daily_returns[i] - daily_withdrawal
        
        # CRITICAL: Floor the value at zero (a portfolio cannot have a negative balance)
        portfolio_values[i] = np.maximum(0, new_value)
    
    # Extract the 10th, 50th, and 90th percentile arrays from portfolio_values across axis 1
    percentile_10 = np.percentile(portfolio_values, 10, axis=1)
    percentile_50 = np.percentile(portfolio_values, 50, axis=1)
    percentile_90 = np.percentile(portfolio_values, 90, axis=1)
    
    # Return the Pandas DataFrame with 'Year' as the index (fractional years) and the three percentile columns
    year_index = np.linspace(0, years, days)
    
    df = pd.DataFrame({
        '10th Percentile (Bear Market)': percentile_10,
        '50th Percentile (Expected)': percentile_50,
        '90th Percentile (Bull Market)': percentile_90
    }, index=year_index)
    
    df.index.name = 'Year'
    
    return df
