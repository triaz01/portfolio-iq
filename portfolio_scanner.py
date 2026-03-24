import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from datetime import datetime, timedelta
import numpy as np

class PortfolioScanner:
    def __init__(self):
        self.portfolio = {}
        self.data = {}
    
    def add_stock(self, symbol, shares):
        """Add a stock to the portfolio"""
        symbol = symbol.upper()
        self.portfolio[symbol] = shares
        st.success(f"Added {shares} shares of {symbol} to portfolio")
    
    def remove_stock(self, symbol):
        """Remove a stock from the portfolio"""
        symbol = symbol.upper()
        if symbol in self.portfolio:
            del self.portfolio[symbol]
            st.success(f"Removed {symbol} from portfolio")
        else:
            st.error(f"{symbol} not found in portfolio")
    
    def fetch_stock_data(self, symbol, period="1mo"):
        """Fetch stock data using yfinance"""
        try:
            stock = yf.Ticker(symbol)
            data = stock.history(period=period)
            return data, stock.info
        except Exception as e:
            st.error(f"Error fetching data for {symbol}: {str(e)}")
            return None, None
    
    def calculate_portfolio_value(self):
        """Calculate current portfolio value"""
        total_value = 0
        stock_values = {}
        
        for symbol, shares in self.portfolio.items():
            data, info = self.fetch_stock_data(symbol, "5d")
            if data is not None and not data.empty:
                current_price = data['Close'].iloc[-1]
                stock_value = current_price * shares
                stock_values[symbol] = {
                    'shares': shares,
                    'current_price': current_price,
                    'total_value': stock_value,
                    'change': data['Close'].iloc[-1] - data['Close'].iloc[0]
                }
                total_value += stock_value
        
        return total_value, stock_values
    
    def create_portfolio_chart(self):
        """Create a pie chart showing portfolio distribution"""
        total_value, stock_values = self.calculate_portfolio_value()
        
        if not stock_values:
            return None
        
        labels = list(stock_values.keys())
        values = [stock_values[sym]['total_value'] for sym in labels]
        
        fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.3)])
        fig.update_layout(title="Portfolio Distribution")
        return fig
    
    def create_performance_chart(self, symbol):
        """Create a performance chart for a specific stock"""
        data, info = self.fetch_stock_data(symbol, "3mo")
        
        if data is None or data.empty:
            return None
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data.index, y=data['Close'], 
                                mode='lines', name='Close Price'))
        fig.update_layout(title=f"{symbol} Stock Performance",
                         xaxis_title="Date",
                         yaxis_title="Price ($)")
        return fig

def main():
    st.set_page_config(page_title="Portfolio Scanner", layout="wide")
    st.title("📊 Portfolio Scanner")
    
    # Initialize portfolio scanner in session state
    if 'scanner' not in st.session_state:
        st.session_state.scanner = PortfolioScanner()
    
    scanner = st.session_state.scanner
    
    # Sidebar for portfolio management
    st.sidebar.header("Portfolio Management")
    
    # Add stock form
    with st.sidebar.expander("Add Stock"):
        symbol = st.text_input("Stock Symbol", key="add_symbol")
        shares = st.number_input("Number of Shares", min_value=0, step=1, key="add_shares")
        if st.button("Add to Portfolio"):
            if symbol and shares > 0:
                scanner.add_stock(symbol, shares)
            else:
                st.error("Please enter valid symbol and shares")
    
    # Remove stock form
    with st.sidebar.expander("Remove Stock"):
        symbol_to_remove = st.selectbox("Select Stock", list(scanner.portfolio.keys()), key="remove_symbol")
        if st.button("Remove from Portfolio"):
            scanner.remove_stock(symbol_to_remove)
    
    # Display current portfolio
    st.sidebar.header("Current Portfolio")
    if scanner.portfolio:
        for symbol, shares in scanner.portfolio.items():
            st.sidebar.write(f"**{symbol}**: {shares} shares")
    else:
        st.sidebar.write("No stocks in portfolio")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("Portfolio Overview")
        
        if scanner.portfolio:
            # Calculate and display portfolio value
            total_value, stock_values = scanner.calculate_portfolio_value()
            st.metric("Total Portfolio Value", f"${total_value:,.2f}")
            
            # Display portfolio distribution chart
            chart_fig = scanner.create_portfolio_chart()
            if chart_fig:
                st.plotly_chart(chart_fig, use_container_width=True)
            
            # Display individual stock performance
            st.subheader("Stock Performance")
            for symbol in scanner.portfolio.keys():
                with st.expander(f"{symbol} Details"):
                    perf_fig = scanner.create_performance_chart(symbol)
                    if perf_fig:
                        st.plotly_chart(perf_fig, use_container_width=True)
                    
                    # Display stock metrics
                    if symbol in stock_values:
                        metrics = stock_values[symbol]
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            st.metric("Current Price", f"${metrics['current_price']:.2f}")
                        with col_b:
                            st.metric("Total Value", f"${metrics['total_value']:,.2f}")
                        with col_c:
                            change_color = "normal" if metrics['change'] >= 0 else "inverse"
                            st.metric("Change", f"${metrics['change']:.2f}", delta_color=change_color)
        else:
            st.info("Add stocks to your portfolio to see analysis")
    
    with col2:
        st.header("Market Data")
        
        # Stock lookup
        lookup_symbol = st.text_input("Lookup Stock", key="lookup_symbol")
        if lookup_symbol:
            data, info = scanner.fetch_stock_data(lookup_symbol, "5d")
            if data is not None and not data.empty:
                st.subheader(f"{lookup_symbol.upper()}")
                current_price = data['Close'].iloc[-1]
                change = data['Close'].iloc[-1] - data['Close'].iloc[0]
                change_pct = (change / data['Close'].iloc[0]) * 100
                
                st.metric("Price", f"${current_price:.2f}", 
                         f"{change_pct:.2f}%" if change_pct != 0 else "0%")
                
                if 'companyName' in info:
                    st.write(f"**Company**: {info['companyName']}")
                if 'sector' in info:
                    st.write(f"**Sector**: {info['sector']}")
            else:
                st.error(f"Could not fetch data for {lookup_symbol}")

if __name__ == "__main__":
    main()
