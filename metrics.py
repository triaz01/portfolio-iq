import yfinance as yf
import pandas as pd
import numpy as np

def calculate_portfolio_metrics(portfolio, base_currency="CAD"):
    try:
        print("\n" + "="*50)
        print("📊 STARTING PORTFOLIO METRICS CALCULATION")
        print("="*50)
        
        if not portfolio or not isinstance(portfolio, dict):
            print("❌ Error: Invalid portfolio input")
            return None
        
        price_data = {}
        stock_info = {}
        fx_cache = {}
        ignored_tickers = []
        
        print(f"📈 Processing {len(portfolio)} tickers for {base_currency} base currency")
        
        for ticker, shares in portfolio.items():
            print(f"\n🔍 Processing {ticker} ({shares} shares)")
            
            stock = yf.Ticker(ticker)
            hist = stock.history(period="3y")
            
            # Enhanced Auto-Retry Logic: Handle TSX-Venture and Canadian REITs/Trusts
            if hist.empty or 'Close' not in hist.columns:
                # Create sanitized version for Yahoo's unit/preferred share formatting
                clean_ticker = ticker.replace('.UN', '-UN').replace('.PR', '-PR')
                
                # Create fallback candidates in specific order
                fallback_candidates = [
                    f"{clean_ticker}.TO",  # Mainboard stocks and corrected REITs like CAR-UN.TO
                    f"{clean_ticker}.V",   # TSX-Venture stocks like ASE.V
                    f"{clean_ticker}.VN",  # Alternative Venture tag
                    clean_ticker           # US stock that just needed formatting cleanup
                ]
                
                print(f"  🔄 Initial fetch failed, trying {len(fallback_candidates)} fallback candidates")
                found_match = False
                
                for candidate in fallback_candidates:
                    print(f"    🔍 Trying {candidate}...")
                    fallback_stock = yf.Ticker(candidate)
                    fallback_hist = fallback_stock.history(period="3y")
                    
                    if not fallback_hist.empty and 'Close' in fallback_hist.columns:
                        # Found a match! Use this candidate
                        ticker = candidate
                        stock = fallback_stock
                        hist = fallback_hist
                        print(f"  ✅ Success! Found data for {ticker}")
                        found_match = True
                        break
                    else:
                        print(f"    ❌ No data for {candidate}")
                
                if not found_match:
                    # All fallback candidates failed - add to ignored list
                    ignored_tickers.append({
                        'symbol': ticker,
                        'reason': 'Could not find valid price data on US or Canadian exchanges after trying all fallback candidates.'
                    })
                    print(f"  ❌ All fallback candidates failed. Ignoring {ticker}")
                    continue
            
            if not hist.empty and 'Close' in hist.columns:
                stock_prices = hist['Close'].copy()
                
                info = stock.info
                stock_currency = info.get('currency', 'USD')
                print(f"  💰 Stock currency: {stock_currency}")
                
                # Currency conversion logic
                if stock_currency != base_currency:
                    if stock_currency == 'USD' and base_currency == 'CAD':
                        fx_ticker = 'USDCAD=X'
                    elif stock_currency == 'CAD' and base_currency == 'USD':
                        fx_ticker = 'CADUSD=X'
                    else:
                        fx_ticker = f"{stock_currency}{base_currency}=X"
                    
                    print(f"  🔄 Converting {stock_currency} to {base_currency} using {fx_ticker}")
                    
                    if fx_ticker not in fx_cache:
                        fx_data = yf.Ticker(fx_ticker).history(period="3y")
                        if not fx_data.empty and 'Close' in fx_data.columns:
                            fx_cache[fx_ticker] = fx_data['Close'].copy()
                        else:
                            fx_cache[fx_ticker] = None
                    
                    if fx_cache[fx_ticker] is not None:
                        combined_df = pd.DataFrame({
                            'stock': stock_prices,
                            'fx': fx_cache[fx_ticker]
                        })
                        combined_df['fx'] = combined_df['fx'].ffill()
                        combined_df = combined_df.dropna()
                        
                        stock_prices = combined_df['stock'] * combined_df['fx']
                        print(f"  ✅ Successfully converted prices to {base_currency}")
                    else:
                        print(f"  ❌ Failed to fetch FX data for {fx_ticker}")
                
                price_data[ticker] = stock_prices
                
                # Safe extraction of dividend yield only (beta will be calculated from portfolio returns)
                # Critical: Try dividendYield first, then fallback to trailingAnnualDividendYield
                div_yield = info.get('dividendYield')
                if div_yield is None:
                    div_yield = info.get('trailingAnnualDividendYield', 0.0)
                if div_yield is None:
                    div_yield = 0.0
                
                # Keep as raw decimal (e.g., 0.05 for 5%)
                div_yield = float(div_yield)
                
                current_price = stock_prices.iloc[-1]
                current_value = shares * current_price
                
                print(f"  📊 Latest price: {current_price:.2f} {base_currency}")
                print(f"  📊 Current value: {current_value:.2f} {base_currency}")
                print(f"  📊 Dividend Yield (raw): {div_yield:.4f} ({div_yield*100:.2f}%)")
                
                # Extract analyst price target
                raw_target = info.get('targetMeanPrice') or info.get('targetMedianPrice')
                
                if raw_target is not None:
                    # Target price needs FX conversion if stock needed it
                    if stock_currency != base_currency and fx_cache.get(fx_ticker) is not None:
                        latest_fx = combined_df['fx'].iloc[-1]
                        target_price = raw_target * latest_fx
                        print(f"  🎯 Analyst target: {raw_target:.2f} {stock_currency} → {target_price:.2f} {base_currency}")
                    else:
                        target_price = raw_target
                        print(f"  🎯 Analyst target: {target_price:.2f} {base_currency}")
                else:
                    # Fallback to current price for ETFs and stocks without analyst coverage
                    target_price = current_price
                    print(f"  🎯 No analyst target available, using current price: {target_price:.2f} {base_currency}")
                
                projected_value = shares * target_price
                
                stock_info[ticker] = {
                    'dividend_yield': div_yield,
                    'latest_price': current_price,
                    'shares': shares,
                    'current_value': current_value,
                    'target_price': target_price,
                    'projected_value': projected_value
                }
            else:
                print(f"  ❌ No price data available for {ticker}")
        
        if not price_data:
            print("❌ No valid price data found")
            return None
        
        print(f"\n📈 Building price dataframe with {len(price_data)} tickers")
        price_df = pd.DataFrame(price_data)
        print(f"📈 Price data shape: {price_df.shape}")
        
        # Calculate total portfolio value and true capital weights
        total_portfolio_value = sum([info['current_value'] for info in stock_info.values()])
        weights = np.array([info['current_value'] / total_portfolio_value for info in stock_info.values()])
        
        print(f"\n💰 Total Portfolio Value: {total_portfolio_value:.2f} {base_currency}")
        print("💰 Portfolio Weights:")
        for i, (ticker, info) in enumerate(stock_info.items()):
            print(f"  {ticker}: {weights[i]:.4f} ({weights[i]*100:.2f}%)")
        
        # Calculate weighted dividend yield only (beta will be calculated from portfolio returns)
        dividend_yields = np.array([info['dividend_yield'] for info in stock_info.values()])
        weighted_dividend_yield = np.dot(dividend_yields, weights)
        
        print(f"\n📊 Weighted Dividend Yield: {weighted_dividend_yield:.4f} ({weighted_dividend_yield*100:.2f}%)")
        
        # CRITICAL FIX: Calculate daily returns first, then apply weights
        print(f"\n📈 Calculating daily returns...")
        daily_returns = price_df.pct_change().dropna()
        print(f"📈 Daily returns shape: {daily_returns.shape}")
        
        # Calculate portfolio daily returns as weighted average of individual returns
        portfolio_daily_returns = daily_returns.dot(weights)
        print(f"📈 Portfolio daily returns shape: {portfolio_daily_returns.shape}")
        
        # Calculate timeframe information
        trading_days = len(daily_returns)
        years_available = trading_days / 252
        print(f"📊 Trading days available: {trading_days}")
        print(f"📊 Years available: {years_available:.2f}")
        
        # Calculate Annualized Volatility over entire timeframe
        annual_volatility = portfolio_daily_returns.std() * np.sqrt(252)
        print(f"📊 Annualized Volatility: {annual_volatility:.4f} ({annual_volatility*100:.1f}%)")
        
        # Calculate 3-Year Portfolio Beta using covariance/variance method
        print(f"\n📈 Calculating 3-Year Portfolio Beta...")
        
        # Determine local benchmark based on base currency
        if base_currency == 'CAD':
            benchmark_ticker = '^GSPTSE'  # S&P/TSX Composite
            benchmark_name = 'S&P/TSX Composite'
        else:
            benchmark_ticker = '^GSPC'  # S&P 500
            benchmark_name = 'S&P 500'
        
        print(f"  🔍 Using local benchmark: {benchmark_name} ({benchmark_ticker})")
        
        # Download 3 years of benchmark data
        benchmark_stock = yf.Ticker(benchmark_ticker)
        benchmark_hist = benchmark_stock.history(period="3y")
        
        if not benchmark_hist.empty and 'Close' in benchmark_hist.columns:
            benchmark_prices = benchmark_hist['Close'].copy()
            benchmark_daily_returns = benchmark_prices.pct_change().dropna()
            
            print(f"  📊 Benchmark daily returns shape: {benchmark_daily_returns.shape}")
            
            # Combine portfolio and benchmark returns to align dates
            combined_returns = pd.DataFrame({
                'Portfolio': portfolio_daily_returns,
                'Benchmark': benchmark_daily_returns
            }).dropna()
            
            print(f"  📊 Aligned returns shape: {combined_returns.shape}")
            
            # Calculate portfolio beta using covariance/variance formula
            covariance_matrix = combined_returns.cov()
            covariance_portfolio_benchmark = covariance_matrix.loc['Portfolio', 'Benchmark']
            variance_benchmark = covariance_matrix.loc['Benchmark', 'Benchmark']
            
            portfolio_beta = covariance_portfolio_benchmark / variance_benchmark
            
            print(f"  📊 Covariance(Portfolio, Benchmark): {covariance_portfolio_benchmark:.6f}")
            print(f"  📊 Variance(Benchmark): {variance_benchmark:.6f}")
            print(f"  📊 3-Year Portfolio Beta: {portfolio_beta:.3f}")
        else:
            print(f"  ❌ No benchmark data available for {benchmark_ticker}")
            portfolio_beta = 1.0  # Default to market beta
        
        # Build cumulative returns series for return and drawdown calculations
        cumulative_returns = (1 + portfolio_daily_returns).cumprod()
        
        # Calculate Maximum Drawdown over entire timeframe
        running_max = cumulative_returns.cummax()
        drawdown = (cumulative_returns - running_max) / running_max
        max_drawdown = drawdown.min()
        
        # Calculate Annualized Return over entire available timeframe
        annualized_return = (cumulative_returns.iloc[-1]) ** (252 / trading_days) - 1
        print(f"📊 Annualized Return: {annualized_return:.4f} ({annualized_return*100:.2f}%)")
        
        # Calculate correlation matrix using full aligned timeframe
        correlation_matrix = daily_returns.corr()
        
        # Fetch benchmark data
        print(f"\n📈 Fetching benchmark data...")
        benchmarks = {
            'S&P 500': {'ticker': '^GSPC', 'currency': 'USD'},
            'TSX Composite': {'ticker': '^GSPTSE', 'currency': 'CAD'}
        }
        
        benchmark_data = {}
        
        for benchmark_name, benchmark_info in benchmarks.items():
            print(f"  🔍 Fetching {benchmark_name} ({benchmark_info['ticker']})")
            
            benchmark_stock = yf.Ticker(benchmark_info['ticker'])
            benchmark_hist = benchmark_stock.history(period="3y")
            
            if not benchmark_hist.empty and 'Close' in benchmark_hist.columns:
                benchmark_prices = benchmark_hist['Close'].copy()
                benchmark_currency = benchmark_info['currency']
                
                print(f"    💰 Benchmark currency: {benchmark_currency}")
                
                # Apply same FX conversion logic as stocks
                if benchmark_currency != base_currency:
                    if benchmark_currency == 'USD' and base_currency == 'CAD':
                        fx_ticker = 'USDCAD=X'
                    elif benchmark_currency == 'CAD' and base_currency == 'USD':
                        fx_ticker = 'CADUSD=X'
                    else:
                        fx_ticker = f"{benchmark_currency}{base_currency}=X"
                    
                    print(f"    � Converting {benchmark_currency} to {base_currency} using {fx_ticker}")
                    
                    if fx_ticker not in fx_cache:
                        fx_data = yf.Ticker(fx_ticker).history(period="3y")
                        if not fx_data.empty and 'Close' in fx_data.columns:
                            fx_cache[fx_ticker] = fx_data['Close'].copy()
                        else:
                            fx_cache[fx_ticker] = None
                    
                    if fx_cache[fx_ticker] is not None:
                        combined_df = pd.DataFrame({
                            'benchmark': benchmark_prices,
                            'fx': fx_cache[fx_ticker]
                        })
                        combined_df['fx'] = combined_df['fx'].ffill()
                        combined_df = combined_df.dropna()
                        
                        benchmark_prices = combined_df['benchmark'] * combined_df['fx']
                        print(f"    ✅ Successfully converted benchmark prices to {base_currency}")
                    else:
                        print(f"    ❌ Failed to fetch FX data for {fx_ticker}")
                
                benchmark_data[benchmark_name] = benchmark_prices
            else:
                print(f"    ❌ No price data available for {benchmark_name}")
        
        # Calculate cumulative returns and risk metrics for benchmarks
        benchmark_cumulative = {}
        benchmark_metrics = {}
        
        for benchmark_name, prices in benchmark_data.items():
            benchmark_daily_returns = prices.pct_change().dropna()
            benchmark_cum = (1 + benchmark_daily_returns).cumprod()
            benchmark_cumulative[benchmark_name] = benchmark_cum
            
            # Calculate benchmark risk metrics
            # 1-Year CAGR
            if len(benchmark_daily_returns) >= 252:
                one_year_returns = benchmark_daily_returns.iloc[-252:]
                one_year_cumulative = (1 + one_year_returns).cumprod()
                benchmark_cagr_1y = (one_year_cumulative.iloc[-1] / one_year_cumulative.iloc[0]) ** (252 / len(one_year_returns)) - 1
            else:
                benchmark_cagr_1y = 0.0
            
            # Max Drawdown
            benchmark_running_max = benchmark_cum.cummax()
            benchmark_drawdown = (benchmark_cum - benchmark_running_max) / benchmark_running_max
            benchmark_max_drawdown = benchmark_drawdown.min()
            
            benchmark_metrics[benchmark_name] = {
                'cagr_1y': benchmark_cagr_1y,
                'max_drawdown': benchmark_max_drawdown
            }
            
            print(f"  📊 {benchmark_name} - 1Y CAGR: {benchmark_cagr_1y:.4f} ({benchmark_cagr_1y*100:.2f}%), Max DD: {benchmark_max_drawdown:.4f} ({benchmark_max_drawdown*100:.2f}%)")
        
        # Create chart data - combine portfolio and benchmarks, normalized to start at 1.0
        chart_data = pd.DataFrame({
            'Portfolio': cumulative_returns
        })
        
        for benchmark_name, benchmark_cum in benchmark_cumulative.items():
            chart_data[benchmark_name] = benchmark_cum
        
        # Normalize all series to start at 1.0
        chart_data = chart_data / chart_data.iloc[0]
        
        print(f"📊 Chart data shape: {chart_data.shape}")
        print(f"📊 Chart data columns: {list(chart_data.columns)}")
        
        # Calculate total projected value and build projection DataFrame
        total_projected_value = sum([info['projected_value'] for info in stock_info.values()])
        
        projection_data = []
        for ticker, info in stock_info.items():
            projection_data.append({
                'Ticker': ticker,
                'Shares': info['shares'],
                'Current Price': info['latest_price'],
                'Target Price': info['target_price'],
                'Current Value': info['current_value'],
                'Projected Value': info['projected_value']
            })
        
        projection_df = pd.DataFrame(projection_data)
        
        print(f"\n📊 Final Metrics:")
        print(f"  Annualized Return: {annualized_return:.4f} ({annualized_return*100:.2f}%)")
        print(f"  Annualized Volatility: {annual_volatility:.4f} ({annual_volatility*100:.1f}%)")
        print(f"  Years Available: {years_available:.2f}")
        print(f"  Max Drawdown: {max_drawdown:.4f} ({max_drawdown*100:.2f}%)")
        print(f"  Correlation Matrix shape: {correlation_matrix.shape}")
        print(f"  Total Projected Value: {total_projected_value:.2f} {base_currency}")
        
        metrics = {
            'portfolio_beta': portfolio_beta,
            'weighted_dividend_yield': weighted_dividend_yield,
            'annualized_return': annualized_return,
            'max_drawdown': max_drawdown,
            'annual_volatility': annual_volatility,
            'years_available': years_available,
            'correlation_matrix': correlation_matrix,
            'total_value': total_portfolio_value,
            'total_projected_value': total_projected_value,
            'projection_df': projection_df,
            'weights': dict(zip(portfolio.keys(), weights)),
            'chart_data': chart_data,
            'benchmark_metrics': benchmark_metrics,
            'ignored_tickers': ignored_tickers
        }
        
        print("="*50 + "\n")
        return metrics
    
    except Exception as e:
        print(f"❌ FATAL ERROR IN METRICS CALCULATION: {e}")
        return None

def generate_investor_summary(metrics):
    try:
        beta = metrics['portfolio_beta']
        dividend_yield = metrics['weighted_dividend_yield']
        max_drawdown = metrics['max_drawdown']
        correlation_matrix = metrics['correlation_matrix']
        
        # Sentence 1: Volatility/Beta
        if beta > 1.15:
            volatility_sentence = f"Your portfolio has a beta of {beta:.2f}, indicating an aggressive, high-growth stance that will swing harder than the broader market during both upswings and downturns."
        elif beta < 0.85:
            volatility_sentence = f"Your portfolio has a beta of {beta:.2f}, suggesting a defensive, conservative approach that typically moves less dramatically than the overall market."
        else:
            volatility_sentence = f"Your portfolio has a beta of {beta:.2f}, meaning it generally moves in tandem with the broader market."
        
        # Sentence 2: Income/Yield
        if dividend_yield > 0.04:
            income_sentence = f"With a dividend yield of {dividend_yield:.2f}%, your portfolio generates strong passive income that could provide meaningful cash flow for your investment goals."
        elif dividend_yield < 0.015:
            income_sentence = f"At a dividend yield of {dividend_yield:.2f}%, your portfolio is heavily focused on capital appreciation rather than dividend income, prioritizing long-term growth over immediate cash flow."
        else:
            income_sentence = f"Your portfolio's dividend yield of {dividend_yield:.2f}% provides a moderate balance between income generation and capital appreciation."
        
        # Sentence 3: Stress/Drawdown
        drawdown_percent = abs(max_drawdown) * 100
        stress_sentence = f"Historically, this mix has experienced temporary drops of up to {drawdown_percent:.1f}%. Make sure you are mentally prepared to hold through that level of volatility without panic-selling during market downturns."
        
        # Sentence 4: Diversification/Correlation
        # Calculate average correlation excluding diagonal (1.0 values)
        correlation_values = []
        n = len(correlation_matrix)
        for i in range(n):
            for j in range(n):
                if i != j:  # Exclude diagonal
                    correlation_values.append(correlation_matrix.iloc[i, j])
        
        avg_correlation = np.mean(correlation_values) if correlation_values else 0
        
        if avg_correlation > 0.65:
            diversification_sentence = f"Your stocks have an average correlation of {avg_correlation:.2f}, meaning they tend to move highly in sync with each other. This suggests you may lack true diversification and could benefit from adding less correlated assets to your portfolio."
        elif avg_correlation < 0.3:
            diversification_sentence = f"Your stocks have an average correlation of {avg_correlation:.2f}, indicating strong structural diversification. Your holdings move independently of each other, which can help smooth out portfolio volatility over time."
        else:
            diversification_sentence = f"Your stocks have an average correlation of {avg_correlation:.2f}, showing moderate diversification. There's room for improvement, but your portfolio isn't overly concentrated in highly correlated assets."
        
        # Combine all sentences
        summary = f"{volatility_sentence} {income_sentence} {stress_sentence} {diversification_sentence}"
        
        return summary
    
    except Exception as e:
        print(f"Error generating investor summary: {e}")
        return "Unable to generate portfolio summary at this time."
