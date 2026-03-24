# Portfolio Scanner

A web-based portfolio tracking and analysis application built with Streamlit and yfinance.

## Features

- **Portfolio Management**: Add/remove stocks from your portfolio
- **Real-time Data**: Fetch current stock prices and historical data
- **Visual Analytics**: Interactive charts for portfolio distribution and stock performance
- **Market Lookup**: Quick stock information lookup
- **Performance Metrics**: Track portfolio value and individual stock changes

## Requirements

- Python 3.7+
- Virtual environment (recommended)

## Installation

### 1. Set up Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Application

```bash
streamlit run portfolio_scanner.py
```

The application will open in your web browser at `http://localhost:8501`

## Usage

1. **Add Stocks**: Use the sidebar to add stocks to your portfolio by entering the stock symbol and number of shares
2. **View Portfolio**: See your portfolio distribution and total value
3. **Track Performance**: View individual stock performance charts
4. **Market Lookup**: Look up any stock for current price and basic information

## Dependencies

- **streamlit**: Web application framework
- **yfinance**: Yahoo Finance API for stock data
- **pandas**: Data manipulation and analysis
- **plotly**: Interactive visualization library
- **numpy**: Numerical computing
- **requests**: HTTP library for API calls

## Project Structure

```
Portfolio-Scanner/
├── portfolio_scanner.py    # Main application file
├── requirements.txt        # Python dependencies
├── README.md              # Project documentation
├── .gitignore             # Git ignore file
└── venv/                  # Virtual environment (git ignored)
```

## Notes

- The virtual environment (`venv/`) is already set up with the required packages
- Stock data is fetched from Yahoo Finance API
- The application stores portfolio data only in memory (session state)
- No database is required for basic functionality

## Troubleshooting

- If you encounter import errors, make sure the virtual environment is activated
- For stock data issues, check your internet connection
- Some symbols may not be available or may have limited data
