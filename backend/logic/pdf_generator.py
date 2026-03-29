from fpdf import FPDF
import tempfile
import os
from datetime import datetime
import pandas as pd

# Try to use Unicode-compatible font
try:
    import sys
    import os
    # Create a fonts directory if it doesn't exist
    FPDF_FONT_DIR = os.path.join(os.path.dirname(__file__), '..', 'fonts')
    if not os.path.exists(FPDF_FONT_DIR):
        os.makedirs(FPDF_FONT_DIR, exist_ok=True)
    
    # Try to add DejaVu font (Unicode compatible)
    try:
        # On Windows, try to find DejaVu fonts
        import platform
        if platform.system() == 'Windows':
            # Common Windows font locations
            font_paths = [
                'C:/Windows/Fonts/DejaVuSans.ttf',
                'C:/Windows/Fonts/arial.ttf',  # Fallback to Arial
                'C:/Windows/Fonts/calibri.ttf',  # Fallback to Calibri
            ]
            
            for font_path in font_paths:
                if os.path.exists(font_path):
                    # Add the font to FPDF
                    pdf = FPDF()
                    pdf.add_font('DejaVu', '', font_path, uni=True)
                    break
    except:
        pass
except:
    pass

def create_growth_chart(chart_data):
    """Create a Plotly growth chart from chart_data"""
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
        
        if not chart_data or not isinstance(chart_data, dict):
            return None
            
        # Convert chart_data to arrays
        dates = list(chart_data.keys())
        portfolio_values = []
        sp500_values = []
        tsx_values = []
        
        for date in dates:
            data_point = chart_data[date]
            if isinstance(data_point, dict):
                portfolio_values.append(data_point.get('Portfolio', 0))
                sp500_values.append(data_point.get('S&P 500', 0))
                tsx_values.append(data_point.get('TSX Composite', 0))
            else:
                portfolio_values.append(0)
                sp500_values.append(0)
                tsx_values.append(0)
        
        # Create figure
        fig = go.Figure()
        
        # Add Portfolio line
        fig.add_trace(go.Scatter(
            x=dates,
            y=portfolio_values,
            mode='lines',
            name='Portfolio',
            line=dict(color='#1a3d6e', width=2)
        ))
        
        # Add S&P 500 line
        fig.add_trace(go.Scatter(
            x=dates,
            y=sp500_values,
            mode='lines',
            name='S&P 500',
            line=dict(color='#64748b', width=1.5, dash='dash')
        ))
        
        # Add TSX Composite line
        fig.add_trace(go.Scatter(
            x=dates,
            y=tsx_values,
            mode='lines',
            name='TSX Composite',
            line=dict(color='#c9943a', width=1.5, dash='dash')
        ))
        
        # Update layout
        fig.update_layout(
            title='Portfolio Growth vs Benchmarks',
            xaxis_title='Date',
            yaxis_title='Normalized Value',
            template='plotly_white',
            height=400,
            font=dict(size=10),
            margin=dict(l=50, r=50, t=50, b=50)
        )
        
        return fig
        
    except Exception as e:
        print(f"Error creating growth chart: {e}")
        return None

def create_monte_carlo_chart(mc_data):
    """Create a Plotly Monte Carlo chart from Monte Carlo data"""
    try:
        import plotly.graph_objects as go
        import numpy as np
        import pandas as pd
        
        if mc_data is None:
            return None
            
        # Handle DataFrame or dict input
        if isinstance(mc_data, dict):
            # Convert dict to DataFrame
            df = pd.DataFrame.from_dict(mc_data, orient='index')
        elif hasattr(mc_data, 'to_dict'):
            # Already a DataFrame
            df = mc_data
        else:
            return None
        
        # Get the data columns
        if '10th Percentile (Bear Market)' in df.columns:
            p10_values = df['10th Percentile (Bear Market)']
            p50_values = df['50th Percentile (Expected)']
            p90_values = df['90th Percentile (Bull Market)']
            years = df.index.tolist()
        else:
            # Fallback for different column names
            cols = list(df.columns)
            if len(cols) >= 3:
                p10_values = df[cols[0]]
                p50_values = df[cols[1]]
                p90_values = df[cols[2]]
                years = df.index.tolist()
            else:
                return None
        
        # Create figure
        fig = go.Figure()
        
        # Add bear market (10th percentile)
        fig.add_trace(go.Scatter(
            x=years,
            y=p10_values,
            mode='lines',
            name='Bear Market (10th %)',
            line=dict(color='red', width=2),
            fill=None
        ))
        
        # Add expected case (50th percentile)
        fig.add_trace(go.Scatter(
            x=years,
            y=p50_values,
            mode='lines',
            name='Expected Case (50th %)',
            line=dict(color='blue', width=2),
            fill=None
        ))
        
        # Add bull market (90th percentile)
        fig.add_trace(go.Scatter(
            x=years,
            y=p90_values,
            mode='lines',
            name='Bull Market (90th %)',
            line=dict(color='green', width=2),
            fill=None
        ))
        
        # Update layout
        fig.update_layout(
            title='Monte Carlo Wealth Simulation',
            xaxis_title='Years',
            yaxis_title='Portfolio Value',
            template='plotly_white',
            height=400,
            font=dict(size=10),
            margin=dict(l=50, r=50, t=50, b=50)
        )
        
        return fig
        
    except Exception as e:
        print(f"Error creating Monte Carlo chart: {e}")
        return None

# Try to use a Unicode-compatible font
try:
    import sys
    import os
    # Add a font that supports Unicode
    FPDF_FONT_DIR = os.path.join(os.path.dirname(__file__), '..', 'fonts')
    if not os.path.exists(FPDF_FONT_DIR):
        os.makedirs(FPDF_FONT_DIR, exist_ok=True)
except:
    pass

def clean_text(text):
    """Aggressive character cleaning for PDF compatibility"""
    if text is None:
        return ""
    try:
        text = str(text)
        # Remove ALL control characters and non-ASCII characters
        cleaned = ''.join(char for char in text if 32 <= ord(char) <= 126)
        return cleaned
    except:
        return str(text)

def safe_pdf_text(text):
    """Ultra-safe text cleaning for PDF"""
    if not text:
        return ""
    # Only allow basic ASCII printable characters
    return ''.join(c for c in str(text) if 32 <= ord(c) <= 126)

def set_font(pdf, font_style='', size=12, use_unicode_font=False):
    """Helper function to set font with Unicode support"""
    if use_unicode_font:
        pdf.set_font('Arial', font_style, size)
    else:
        pdf.set_font('Helvetica', font_style, size)

def generate_pdf_report(metrics, ips_profile, ips_alignment_text, growth_chart_fig, projection_df, ips_targets=None, monte_carlo_fig=None, correlation_matrix=None, chart_data=None, signals=None, currency="CAD"):
    """
    Generate a comprehensive PDF tear sheet with all analysis sections.
    
    Parameters:
    - All existing parameters plus:
    - correlation_matrix: Dict of correlation matrix data
    - chart_data: Dict of growth chart data  
    - signals: List of trading signals
    - currency: Currency string
    
    Returns:
    - PDF as byte string
    """
    try:
        # Clean all inputs
        ips_profile = safe_pdf_text(ips_profile) if ips_profile else ""
        currency = safe_pdf_text(currency) if currency else "CAD"
        
        # Clean metrics
        if metrics and isinstance(metrics, dict):
            cleaned_metrics = {}
            for key, value in metrics.items():
                if isinstance(value, str):
                    cleaned_metrics[key] = safe_pdf_text(value)
                else:
                    cleaned_metrics[key] = value
            metrics = cleaned_metrics
        else:
            metrics = {}
        
        # Create charts from data if figures not provided
        if growth_chart_fig is None and chart_data:
            growth_chart_fig = create_growth_chart(chart_data)
        
        # Note: Monte Carlo chart would need to be created from Monte Carlo data
        # For now, we'll use the provided figure or skip if None
        
        # Initialize PDF with Unicode font support
        pdf = FPDF()
        use_unicode_font = False
        
        try:
            # Try to use Arial (most common on Windows) with Unicode support
            import platform
            if platform.system() == 'Windows':
                arial_path = 'C:/Windows/Fonts/arial.ttf'
                if os.path.exists(arial_path):
                    pdf.add_font('Arial', '', arial_path, uni=True)
                    use_unicode_font = True
        except Exception as font_error:
            print(f"Font loading error: {font_error}")
            pass
        
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # Header - Use Unicode font if available, otherwise fallback to Helvetica
        if use_unicode_font:
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, 'Portfolio Analysis & Investment Policy Report', ln=True, align='C')
            pdf.set_font('Arial', '', 10)
            pdf.cell(0, 6, f'Generated: {datetime.now().strftime("%B %d, %Y")} | Currency: {currency}', ln=True, align='C')
        else:
            pdf.set_font('Helvetica', 'B', 16)
            pdf.cell(0, 10, safe_pdf_text('Portfolio Analysis & Investment Policy Report'), ln=True, align='C')
            pdf.set_font('Helvetica', '', 10)
            pdf.cell(0, 6, safe_pdf_text(f'Generated: {datetime.now().strftime("%B %d, %Y")} | Currency: {currency}'), ln=True, align='C')
        
        # Navy line for styling
        pdf.set_draw_color(37, 86, 160)  # Navy blue
        pdf.set_line_width(0.5)
        pdf.line(10, pdf.get_y() + 2, 200, pdf.get_y() + 2)
        pdf.ln(8)
        
        # Section 1: IPS Profile & Target Ranges
        set_font(pdf, 'B', 14, use_unicode_font)
        pdf.cell(0, 8, 'Investment Policy Profile' if use_unicode_font else safe_pdf_text('Investment Policy Profile'), ln=True)
        set_font(pdf, '', 11, use_unicode_font)
        pdf.ln(2)
        
        # IPS Profile description
        if ips_profile:
            profile_text = f'Profile: {ips_profile}' if use_unicode_font else safe_pdf_text(f'Profile: {ips_profile}')
            pdf.multi_cell(0, 5, profile_text)
            pdf.ln(3)
        
        # Target ranges if available
        if ips_targets and isinstance(ips_targets, dict):
            set_font(pdf, 'B', 11, use_unicode_font)
            pdf.cell(0, 6, 'Target Ranges:' if use_unicode_font else safe_pdf_text('Target Ranges:'), ln=True)
            set_font(pdf, '', 10, use_unicode_font)
            
            if 'beta_range' in ips_targets:
                beta_min, beta_max = ips_targets['beta_range']
                beta_text = f'  • Beta: {beta_min:.2f} - {beta_max:.2f}' if use_unicode_font else safe_pdf_text(f'  • Beta: {beta_min:.2f} - {beta_max:.2f}')
                pdf.cell(0, 4, beta_text, ln=True)
            
            if 'volatility_range' in ips_targets:
                vol_min, vol_max = ips_targets['volatility_range']
                vol_text = f'  • Volatility: {vol_min*100:.1f}% - {vol_max*100:.1f}%' if use_unicode_font else safe_pdf_text(f'  • Volatility: {vol_min*100:.1f}% - {vol_max*100:.1f}%')
                pdf.cell(0, 4, vol_text, ln=True)
            
            if 'yield_min' in ips_targets and 'yield_max' in ips_targets:
                yield_text = f'  • Dividend Yield: {ips_targets["yield_min"]*100:.1f}% - {ips_targets["yield_max"]*100:.1f}%' if use_unicode_font else safe_pdf_text(f'  • Dividend Yield: {ips_targets["yield_min"]*100:.1f}% - {ips_targets["yield_max"]*100:.1f}%')
                pdf.cell(0, 4, yield_text, ln=True)
            
            pdf.ln(4)
        
        # Section 2: Core Portfolio Metrics
        pdf.set_font('Helvetica', 'B', 14)
        pdf.cell(0, 8, 'Portfolio Performance Metrics', ln=True)
        pdf.ln(2)
        
        # Create metrics table
        pdf.set_font('Helvetica', 'B', 10)
        pdf.cell(95, 7, 'Metric', border=1)
        pdf.cell(95, 7, 'Value', border=1, ln=True)
        
        pdf.set_font('Helvetica', '', 10)
        metrics_data = [
            ('Annualized Return', f"{metrics.get('annualized_return', 0) * 100:.2f}%"),
            ('Annual Volatility', f"{metrics.get('annual_volatility', 0) * 100:.2f}%"),
            ('Portfolio Beta', f"{metrics.get('portfolio_beta', 0):.2f}"),
            ('Dividend Yield', f"{metrics.get('weighted_dividend_yield', 0) * 100:.2f}%"),
            ('Max Drawdown', f"{metrics.get('max_drawdown', 0) * 100:.2f}%"),
            ('Total Portfolio Value', f"{currency} {metrics.get('total_value', 0):,.2f}"),
            ('Projected Value', f"{currency} {metrics.get('total_projected_value', 0):,.2f}"),
        ]
        
        for metric_name, metric_value in metrics_data:
            pdf.cell(95, 6, metric_name, border=1)
            pdf.cell(95, 6, metric_value, border=1, ln=True)
        
        pdf.ln(6)
        
        # Section 3: Growth Chart
        if growth_chart_fig is not None:
            pdf.add_page()
            pdf.set_font('Helvetica', 'B', 14)
            pdf.cell(0, 8, 'Portfolio Growth Trajectory', ln=True)
            pdf.ln(2)
            
            pdf.set_font('Helvetica', '', 10)
            pdf.cell(0, 5, '3-year portfolio growth projection based on historical performance:', ln=True)
            pdf.ln(3)
            
            # Save chart as temporary image
            temp_path = None
            try:
                import tempfile
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                    temp_path = tmp.name
                
                # Export Plotly chart to image
                growth_chart_fig.write_image(temp_path, width=800, height=400, scale=2)
                
                # Insert image into PDF
                pdf.image(temp_path, x=10, w=190)
                pdf.ln(4)
            
            except Exception as chart_error:
                pdf.set_font('Helvetica', 'I', 9)
                pdf.cell(0, 5, f'Chart generation error: {safe_pdf_text(str(chart_error))}', ln=True)
                pdf.ln(2)
            
            finally:
                # Clean up temporary file
                if temp_path and os.path.exists(temp_path):
                    try:
                        os.unlink(temp_path)
                    except:
                        pass
        
        # Section 4: Holdings & Projections
        pdf.add_page()
        pdf.set_font('Helvetica', 'B', 14)
        pdf.cell(0, 8, 'Holdings & Analyst Projections', ln=True)
        pdf.ln(2)
        
        # Create projections table
        pdf.set_font('Helvetica', 'B', 7)
        pdf.cell(25, 6, 'Ticker', border=1, align='C')
        pdf.cell(20, 6, 'Shares', border=1, align='C')
        pdf.cell(45, 6, 'Current', border=1, align='C')
        pdf.cell(45, 6, 'Target', border=1, align='C')
        pdf.cell(45, 6, 'Projected', border=1, align='C', ln=True)
        
        pdf.set_font('Helvetica', '', 8)
        
        def format_currency(val):
            try:
                val = float(val)
                if val >= 1000000:
                    return f"{currency} {val/1000000:.2f}M"
                elif val >= 1000:
                    return f"{currency} {val/1000:.1f}K"
                else:
                    return f"{currency} {val:.2f}"
            except:
                return f"{currency} 0.00"
        
        # Loop through projection DataFrame
        if projection_df is not None and len(projection_df) > 0:
            for _, row in projection_df.iterrows():
                try:
                    ticker = safe_pdf_text(str(row.get('Ticker', '')))[:6]
                    shares_val = int(row.get('Shares', 0))
                    shares = f"{shares_val:,}" if shares_val < 10000 else f"{shares_val/1000:.0f}K"
                    shares = shares[:7]
                    
                    current_str = format_currency(row.get('Current Value', 0))[:10]
                    target_str = format_currency(row.get('Target Price', 0))[:10]
                    projected_str = format_currency(row.get('Projected Value', 0))[:10]
                    
                    pdf.cell(25, 6, ticker, border=1)
                    pdf.cell(20, 6, shares, border=1, align='R')
                    pdf.cell(45, 6, current_str, border=1, align='R')
                    pdf.cell(45, 6, target_str, border=1, align='R')
                    pdf.cell(45, 6, projected_str, border=1, align='R', ln=True)
                except:
                    continue
        
        # Add totals row
        pdf.set_font('Helvetica', 'B', 7)
        total_current = format_currency(metrics.get('total_value', 0))[:10]
        total_projected = format_currency(metrics.get('total_projected_value', 0))[:10]
        
        pdf.cell(45, 6, 'TOTAL', border=1)
        pdf.cell(45, 6, total_current, border=1, align='R')
        pdf.cell(45, 6, '', border=1)
        pdf.cell(45, 6, total_projected, border=1, align='R', ln=True)
        
        # Calculate upside
        total_val = metrics.get('total_value', 0)
        total_proj = metrics.get('total_projected_value', 0)
        if total_val > 0:
            upside_pct = ((total_proj - total_val) / total_val) * 100
            pdf.ln(2)
            pdf.set_font('Helvetica', 'I', 10)
            pdf.cell(0, 6, f'Total Projected Upside: {upside_pct:.2f}%', ln=True)
        
        # Section 5: Monte Carlo Simulation
        if monte_carlo_fig is not None:
            pdf.add_page()
            pdf.set_font('Helvetica', 'B', 14)
            pdf.cell(0, 8, 'Monte Carlo Wealth Simulation', ln=True)
            pdf.ln(2)
            
            pdf.set_font('Helvetica', '', 9)
            pdf.cell(0, 5, '500 randomized scenarios based on portfolio risk/return profile:', ln=True)
            pdf.ln(2)
            pdf.set_font('Helvetica', '', 8)
            pdf.cell(0, 4, '  - Bear Market (10th percentile): Conservative outcome', ln=True)
            pdf.cell(0, 4, '  - Expected Case (50th percentile): Median outcome', ln=True)
            pdf.cell(0, 4, '  - Bull Market (90th percentile): Optimistic outcome', ln=True)
            pdf.ln(4)
            
            # Save Monte Carlo chart as temporary image
            mc_temp_path = None
            try:
                import tempfile
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                    mc_temp_path = tmp.name
                
                # Export Plotly chart to image
                monte_carlo_fig.write_image(mc_temp_path, width=800, height=400, scale=2)
                
                # Insert image into PDF
                pdf.image(mc_temp_path, x=10, w=190)
                pdf.ln(4)
            
            except Exception as mc_error:
                pdf.set_font('Helvetica', 'I', 9)
                pdf.cell(0, 5, f'Monte Carlo chart error: {safe_pdf_text(str(mc_error))}', ln=True)
                pdf.ln(2)
            
            finally:
                # Clean up temporary file
                if mc_temp_path and os.path.exists(mc_temp_path):
                    try:
                        os.unlink(mc_temp_path)
                    except:
                        pass
        
        # Section 6: Trading Signals
        if signals and isinstance(signals, list) and len(signals) > 0:
            pdf.add_page()
            pdf.set_font('Helvetica', 'B', 14)
            pdf.cell(0, 8, 'Trading Signals & Recommendations', ln=True)
            pdf.ln(2)
            
            # Create signals table with actual field names from the signals data
            pdf.set_font('Helvetica', 'B', 8)
            pdf.cell(25, 6, 'Ticker', border=1, align='C')
            pdf.cell(30, 6, 'Momentum', border=1, align='C')
            pdf.cell(30, 6, 'Trend', border=1, align='C')
            pdf.cell(35, 6, 'Rel Strength', border=1, align='C')
            pdf.cell(25, 6, 'Score', border=1, align='C')
            pdf.cell(45, 6, 'Recommendation', border=1, align='C', ln=True)
            
            pdf.set_font('Helvetica', '', 8)
            
            for signal in signals:
                try:
                    if isinstance(signal, dict):
                        ticker = safe_pdf_text(str(signal.get('Ticker', signal.get('ticker', ''))))[:6]
                        momentum = safe_pdf_text(str(signal.get('Momentum (%)', signal.get('momentum', 'N/A'))))[:8]
                        trend = safe_pdf_text(str(signal.get('Trend vs 200DMA (%)', signal.get('trend', 'N/A'))))[:8]
                        rel_strength = safe_pdf_text(str(signal.get('Rel Strength vs SPY (%)', signal.get('rel_strength', 'N/A'))))[:10]
                        score = safe_pdf_text(str(signal.get('Total Score', signal.get('score', 'N/A'))))[:6]
                        recommendation = safe_pdf_text(str(signal.get('Recommendation', signal.get('recommendation', 'N/A'))))[:15]
                        
                        pdf.cell(25, 5, ticker, border=1)
                        pdf.cell(30, 5, momentum, border=1, align='R')
                        pdf.cell(30, 5, trend, border=1, align='R')
                        pdf.cell(35, 5, rel_strength, border=1, align='R')
                        pdf.cell(25, 5, score, border=1, align='C')
                        pdf.cell(45, 5, recommendation, border=1, ln=True)
                except Exception as signal_error:
                    # Add a row for the error if we have at least a ticker
                    try:
                        if isinstance(signal, dict):
                            ticker = safe_pdf_text(str(signal.get('Ticker', signal.get('ticker', 'Unknown'))))[:6]
                            pdf.cell(25, 5, ticker, border=1)
                            pdf.cell(30, 5, 'Error', border=1)
                            pdf.cell(30, 5, 'Error', border=1)
                            pdf.cell(35, 5, 'Error', border=1)
                            pdf.cell(25, 5, '-', border=1, align='C')
                            pdf.cell(45, 5, 'Data Error', border=1, ln=True)
                    except:
                        continue
                    continue
        
        # Section 7: Correlation Matrix
        if correlation_matrix and isinstance(correlation_matrix, dict):
            pdf.add_page()
            pdf.set_font('Helvetica', 'B', 14)
            pdf.cell(0, 8, 'Portfolio Correlation Matrix', ln=True)
            pdf.ln(2)
            
            pdf.set_font('Helvetica', '', 8)
            pdf.cell(0, 4, 'Correlation coefficients between portfolio holdings:', ln=True)
            pdf.ln(3)
            
            # Create correlation table
            tickers = [safe_pdf_text(t) for t in correlation_matrix.keys()][:8]  # Limit to 8 tickers for space
            col_width = 180 / (len(tickers) + 1)
            
            # Header row
            pdf.set_font('Helvetica', 'B', 7)
            pdf.cell(col_width, 6, '', border=1)
            for ticker in tickers:
                pdf.cell(col_width, 6, ticker[:4], border=1, align='C')
            pdf.ln()
            
            # Data rows
            pdf.set_font('Helvetica', '', 7)
            for i, ticker in enumerate(tickers):
                pdf.cell(col_width, 6, ticker[:4], border=1, align='C')
                for j, other_ticker in enumerate(tickers):
                    if ticker in correlation_matrix and isinstance(correlation_matrix[ticker], dict) and other_ticker in correlation_matrix[ticker]:
                        corr_val = correlation_matrix[ticker][other_ticker]
                        pdf.cell(col_width, 6, f"{corr_val:.2f}", border=1, align='C')
                    else:
                        pdf.cell(col_width, 6, "0.00", border=1, align='C')
                pdf.ln()
        
        # Skip growth analysis text - frontend only shows the chart
        
        # Section 9: IPS Alignment Check
        if ips_targets and isinstance(ips_targets, dict):
            pdf.add_page()
            pdf.set_font('Helvetica', 'B', 14)
            pdf.cell(0, 8, 'IPS Alignment Analysis', ln=True)
            pdf.ln(2)
            
            # Create alignment table
            pdf.set_font('Helvetica', 'B', 8)
            pdf.cell(55, 6, 'Metric', border=1, align='C')
            pdf.cell(40, 6, 'Portfolio', border=1, align='C')
            pdf.cell(50, 6, 'Target Range', border=1, align='C')
            pdf.cell(40, 6, 'Status', border=1, align='C', ln=True)
            
            pdf.set_font('Helvetica', '', 8)
            
            # Beta alignment
            if 'beta_range' in ips_targets:
                beta_min, beta_max = ips_targets['beta_range']
                beta_val = metrics.get('portfolio_beta', 0)
                beta_status = 'OK In Range' if beta_min <= beta_val <= beta_max else 'Out of Range'
                
                pdf.cell(55, 6, 'Portfolio Beta', border=1)
                pdf.cell(40, 6, f'{beta_val:.2f}', border=1, align='C')
                pdf.cell(50, 6, f'{beta_min:.2f} - {beta_max:.2f}', border=1, align='C')
                pdf.cell(40, 6, beta_status, border=1, align='C', ln=True)
            
            # Volatility alignment
            if 'volatility_range' in ips_targets:
                vol_min, vol_max = ips_targets['volatility_range']
                vol_val = metrics.get('annual_volatility', 0)
                vol_status = 'OK In Range' if vol_min <= vol_val <= vol_max else 'Out of Range'
                
                pdf.cell(55, 6, 'Volatility', border=1)
                pdf.cell(40, 6, f'{vol_val*100:.1f}%', border=1, align='C')
                pdf.cell(50, 6, f'{vol_min*100:.1f}% - {vol_max*100:.1f}%', border=1, align='C')
                pdf.cell(40, 6, vol_status, border=1, align='C', ln=True)
            
            # Dividend yield alignment
            if 'yield_min' in ips_targets and 'yield_max' in ips_targets:
                div_min = ips_targets['yield_min']
                div_max = ips_targets['yield_max']
                div_val = metrics.get('weighted_dividend_yield', 0)
                div_status = 'OK In Range' if div_min <= div_val <= div_max else 'Out of Range'
                
                pdf.cell(55, 6, 'Dividend Yield', border=1)
                pdf.cell(40, 6, f'{div_val:.2f}%', border=1, align='C')
                pdf.cell(50, 6, f'{div_min*100:.1f}% - {div_max*100:.1f}%', border=1, align='C')
                pdf.cell(40, 6, div_status, border=1, align='C', ln=True)
            
            pdf.ln(4)
            
            # Alignment summary
            in_range_count = 0
            total_metrics = 0
            
            if 'beta_range' in ips_targets:
                beta_min, beta_max = ips_targets['beta_range']
                if beta_min <= metrics.get('portfolio_beta', 0) <= beta_max:
                    in_range_count += 1
                total_metrics += 1
            
            if 'volatility_range' in ips_targets:
                vol_min, vol_max = ips_targets['volatility_range']
                if vol_min <= metrics.get('annual_volatility', 0) <= vol_max:
                    in_range_count += 1
                total_metrics += 1
            
            if 'yield_min' in ips_targets and 'yield_max' in ips_targets:
                div_min = ips_targets['yield_min']
                div_max = ips_targets['yield_max']
                if div_min <= metrics.get('weighted_dividend_yield', 0) <= div_max:
                    in_range_count += 1
                total_metrics += 1
            
            pdf.set_font('Helvetica', 'B', 11)
            pdf.cell(0, 6, f'Alignment Summary: {in_range_count}/{total_metrics} metrics within target ranges', ln=True)
            pdf.ln(2)
            
            # IPS alignment recommendations
            if ips_alignment_text and isinstance(ips_alignment_text, list):
                pdf.set_font('Helvetica', '', 9)
                for bullet in ips_alignment_text:
                    if bullet and bullet.strip():
                        try:
                            clean_bullet = safe_pdf_text(bullet.strip())[:200]
                            pdf.multi_cell(0, 5, safe_pdf_text(f'  - {clean_bullet}'))
                        except:
                            continue
        
        # Footer
        pdf.ln(10)
        pdf.set_font('Helvetica', 'I', 8)
        pdf.set_text_color(128, 128, 128)
        pdf.multi_cell(0, 4, safe_pdf_text('Disclaimer: This report is for informational purposes only and does not constitute investment advice. Past performance does not guarantee future results. Analyst price targets are consensus estimates and may not be achieved.'))
        
        # Return PDF as bytes
        result = pdf.output(dest='S')
        if isinstance(result, str):
            return result.encode('latin1')
        elif isinstance(result, bytearray):
            return bytes(result)
        return result
        
    except Exception as e:
        # Fallback to simple PDF
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font('Helvetica', '', 12)
            pdf.cell(0, 10, safe_pdf_text('Portfolio Report'), ln=True, align='C')
            pdf.cell(0, 10, safe_pdf_text('Error generating full report'), ln=True, align='C')
            pdf.cell(0, 10, safe_pdf_text(f'Error: {safe_pdf_text(str(e))}'), ln=True, align='C')
            result = pdf.output(dest='S')
            if isinstance(result, str):
                return result.encode('latin1')
            elif isinstance(result, bytearray):
                return bytes(result)
            return result
        except:
            # Last resort - return empty PDF bytes
            return b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f\n0000000010 00000 n\n0000000079 00000 n\n0000000173 00000 n\ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n250\n%%EOF'
    
    # Header
    pdf.set_font('Helvetica', 'B', 16)
    pdf.cell(0, 10, 'Portfolio Analysis & Investment Policy Report', ln=True, align='C')
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(0, 6, f'Generated: {datetime.now().strftime("%B %d, %Y")} | Currency: {currency}', ln=True, align='C')
    
    # Navy line for styling
    pdf.set_draw_color(37, 86, 160)  # Navy blue
    pdf.set_line_width(0.5)
    pdf.line(10, pdf.get_y() + 2, 200, pdf.get_y() + 2)
    pdf.ln(8)
    
    # Section 1: IPS Profile & Target Ranges
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 8, 'Investment Policy Profile', ln=True)
    pdf.set_font('Helvetica', '', 11)
    pdf.ln(2)
    
    # IPS Profile description
    if ips_profile:
        pdf.multi_cell(0, 5, f'Profile: {clean_text(ips_profile)}')
        pdf.ln(3)
    
    # Target ranges if available
    if ips_targets:
        pdf.set_font('Helvetica', 'B', 11)
        pdf.cell(0, 6, 'Target Ranges:', ln=True)
        pdf.set_font('Helvetica', '', 10)
        
        if 'beta_range' in ips_targets:
            beta_min, beta_max = ips_targets['beta_range']
            pdf.cell(0, 4, safe_pdf_text(f'  • Beta: {beta_min:.2f} - {beta_max:.2f}'), ln=True)
        
        if 'volatility_range' in ips_targets:
            vol_min, vol_max = ips_targets['volatility_range']
            pdf.cell(0, 4, safe_pdf_text(f'  • Volatility: {vol_min*100:.1f}% - {vol_max*100:.1f}%'), ln=True)
        
        if 'yield_min' in ips_targets and 'yield_max' in ips_targets:
            pdf.cell(0, 4, safe_pdf_text(f'  • Dividend Yield: {ips_targets["yield_min"]*100:.1f}% - {ips_targets["yield_max"]*100:.1f}%'), ln=True)
        
        pdf.ln(4)
    
    # Section 2: Core Portfolio Metrics
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 8, 'Portfolio Performance Metrics', ln=True)
    pdf.ln(2)
    
    # Create metrics table
    pdf.set_font('Helvetica', 'B', 10)
    pdf.cell(95, 7, 'Metric', border=1)
    
    pdf.ln(6)
    
    # Section 3: Holdings & Projections
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 8, 'Holdings & Analyst Projections', ln=True)
    pdf.ln(2)
    
    # Create projections table
    pdf.set_font('Helvetica', 'B', 7)
    pdf.cell(25, 6, 'Ticker', border=1, align='C')
    pdf.cell(20, 6, 'Shares', border=1, align='C')
    pdf.cell(45, 6, 'Current', border=1, align='C')
    pdf.cell(45, 6, 'Target', border=1, align='C')
    pdf.cell(45, 6, 'Projected', border=1, align='C', ln=True)
    
    pdf.set_font('Helvetica', '', 8)
    
    def format_currency(val):
        try:
            val = float(val)
            if val >= 1000000:
                return f"{currency} {val/1000000:.2f}M"
            elif val >= 1000:
                return f"{currency} {val/1000:.1f}K"
            else:
                return f"{currency} {val:.2f}"
        except:
            return f"{currency} 0.00"
    
    # Loop through projection DataFrame
    for _, row in projection_df.iterrows():
        try:
            ticker = clean_text(str(row.get('Ticker', '')))[:6]
            shares_val = int(row.get('Shares', 0))
            shares = f"{shares_val:,}" if shares_val < 10000 else f"{shares_val/1000:.0f}K"
            shares = shares[:7]
            
            current_str = format_currency(row.get('Current Value', 0))[:10]
            target_str = format_currency(row.get('Target Price', 0))[:10]
            projected_str = format_currency(row.get('Projected Value', 0))[:10]
            
            pdf.cell(25, 6, ticker, border=1)
            pdf.cell(20, 6, shares, border=1, align='R')
            pdf.cell(45, 6, current_str, border=1, align='R')
            pdf.cell(45, 6, target_str, border=1, align='R')
            pdf.cell(45, 6, projected_str, border=1, align='R', ln=True)
        except:
            continue
    
    # Add totals row
    pdf.set_font('Helvetica', 'B', 7)
    total_current = format_currency(metrics.get('total_value', 0))[:10]
    total_projected = format_currency(metrics.get('total_projected_value', 0))[:10]
    
    pdf.cell(45, 6, 'TOTAL', border=1)
    pdf.cell(45, 6, total_current, border=1, align='R')
    pdf.cell(45, 6, '', border=1)
    pdf.cell(45, 6, total_projected, border=1, align='R', ln=True)
    
    # Calculate upside
    total_val = metrics.get('total_value', 0)
    total_proj = metrics.get('total_projected_value', 0)
    if total_val > 0:
        upside_pct = ((total_proj - total_val) / total_val) * 100
        pdf.ln(2)
        pdf.set_font('Helvetica', 'I', 10)
        pdf.cell(0, 6, f'Total Projected Upside: {upside_pct:.2f}%', ln=True)
    
    # Section 4: Trading Signals
    if signals:
        pdf.add_page()
        pdf.set_font('Helvetica', 'B', 14)
        pdf.cell(0, 8, 'Trading Signals & Recommendations', ln=True)
        pdf.ln(2)
        
        # Create signals table
        pdf.set_font('Helvetica', 'B', 8)
        pdf.cell(30, 6, 'Ticker', border=1, align='C')
        pdf.cell(50, 6, 'Signal', border=1, align='C')
        pdf.cell(50, 6, 'Recommendation', border=1, align='C')
        pdf.cell(60, 6, 'Rationale', border=1, align='C', ln=True)
        
        pdf.set_font('Helvetica', '', 8)
        
        for signal in signals:
            try:
                ticker = clean_text(signal.get('ticker', ''))[:8]
                signal_type = clean_text(signal.get('signal', ''))[:15]
                recommendation = clean_text(signal.get('recommendation', ''))[:15]
                rationale = clean_text(signal.get('rationale', ''))[:25]
                
                pdf.cell(30, 5, ticker, border=1)
                pdf.cell(50, 5, signal_type, border=1)
                pdf.cell(50, 5, recommendation, border=1)
                pdf.cell(60, 5, rationale, border=1, ln=True)
            except:
                continue
    
    # Section 5: Correlation Matrix
    if correlation_matrix:
        pdf.add_page()
        pdf.set_font('Helvetica', 'B', 14)
        pdf.cell(0, 8, 'Portfolio Correlation Matrix', ln=True)
        pdf.ln(2)
        
        pdf.set_font('Helvetica', '', 8)
        pdf.cell(0, 4, 'Correlation coefficients between portfolio holdings:', ln=True)
        pdf.ln(3)
        
        # Create correlation table
        tickers = [clean_text(t) for t in correlation_matrix.keys()][:8]  # Limit to 8 tickers for space
        col_width = 180 / (len(tickers) + 1)
        
        # Header row
        pdf.set_font('Helvetica', 'B', 7)
        pdf.cell(col_width, 6, '', border=1)
        for ticker in tickers:
            pdf.cell(col_width, 6, ticker[:4], border=1, align='C')
        pdf.ln()
        
        # Data rows
        pdf.set_font('Helvetica', '', 7)
        for i, ticker in enumerate(tickers):
            pdf.cell(col_width, 6, ticker[:4], border=1, align='C')
            for j, other_ticker in enumerate(tickers):
                if ticker in correlation_matrix and other_ticker in correlation_matrix.get(ticker, {}):
                    corr_val = correlation_matrix[ticker][other_ticker]
                    pdf.cell(col_width, 6, f"{corr_val:.2f}", border=1, align='C')
                else:
                    pdf.cell(col_width, 6, "0.00", border=1, align='C')
            pdf.ln()
    
    # Skip growth analysis text - frontend only shows the chart
    
    # Section 7: IPS Alignment Check
    if ips_targets:
        pdf.add_page()
        pdf.set_font('Helvetica', 'B', 14)
        pdf.cell(0, 8, 'IPS Alignment Analysis', ln=True)
        pdf.ln(2)
        
        # Create alignment table
        pdf.set_font('Helvetica', 'B', 8)
        pdf.cell(55, 6, 'Metric', border=1, align='C')
        pdf.cell(40, 6, 'Portfolio', border=1, align='C')
        pdf.cell(50, 6, 'Target Range', border=1, align='C')
        pdf.cell(40, 6, 'Status', border=1, align='C', ln=True)
        
        pdf.set_font('Helvetica', '', 8)
        
        # Beta alignment
        if 'beta_range' in ips_targets:
            beta_min, beta_max = ips_targets['beta_range']
            beta_val = metrics.get('portfolio_beta', 0)
            beta_status = '✓ In Range' if beta_min <= beta_val <= beta_max else '✗ Out of Range'
            
            pdf.cell(55, 6, 'Portfolio Beta', border=1)
            pdf.cell(40, 6, f'{beta_val:.2f}', border=1, align='C')
            pdf.cell(50, 6, f'{beta_min:.2f} - {beta_max:.2f}', border=1, align='C')
            pdf.cell(40, 6, beta_status, border=1, align='C', ln=True)
        
        # Volatility alignment
        if 'volatility_range' in ips_targets:
            vol_min, vol_max = ips_targets['volatility_range']
            vol_val = metrics.get('annual_volatility', 0)
            vol_status = '✓ In Range' if vol_min <= vol_val <= vol_max else '✗ Out of Range'
            
            pdf.cell(55, 6, 'Volatility', border=1)
            pdf.cell(40, 6, f'{vol_val*100:.1f}%', border=1, align='C')
            pdf.cell(50, 6, f'{vol_min*100:.1f}% - {vol_max*100:.1f}%', border=1, align='C')
            pdf.cell(40, 6, vol_status, border=1, align='C', ln=True)
        
        # Dividend yield alignment
        if 'yield_min' in ips_targets and 'yield_max' in ips_targets:
            div_min = ips_targets['yield_min']
            div_max = ips_targets['yield_max']
            div_val = metrics.get('weighted_dividend_yield', 0)
            div_status = '✓ In Range' if div_min <= div_val <= div_max else '✗ Out of Range'
            
            pdf.cell(55, 6, 'Dividend Yield', border=1)
            pdf.cell(40, 6, f'{div_val:.2f}%', border=1, align='C')
            pdf.cell(50, 6, f'{div_min*100:.1f}% - {div_max*100:.1f}%', border=1, align='C')
            pdf.cell(40, 6, div_status, border=1, align='C', ln=True)
        
        pdf.ln(4)
        
        # Alignment summary
        in_range_count = 0
        total_metrics = 0
        
        if 'beta_range' in ips_targets:
            beta_min, beta_max = ips_targets['beta_range']
            if beta_min <= metrics.get('portfolio_beta', 0) <= beta_max:
                in_range_count += 1
            total_metrics += 1
        
        if 'volatility_range' in ips_targets:
            vol_min, vol_max = ips_targets['volatility_range']
            if vol_min <= metrics.get('annual_volatility', 0) <= vol_max:
                in_range_count += 1
            total_metrics += 1
        
        if 'yield_min' in ips_targets and 'yield_max' in ips_targets:
            div_min = ips_targets['yield_min']
            div_max = ips_targets['yield_max']
            if div_min <= metrics.get('weighted_dividend_yield', 0) <= div_max:
                in_range_count += 1
            total_metrics += 1
        
        pdf.set_font('Helvetica', 'B', 11)
        pdf.cell(0, 6, f'Alignment Summary: {in_range_count}/{total_metrics} metrics within target ranges', ln=True)
        pdf.ln(2)
        
        # IPS alignment recommendations
        if ips_alignment_text:
            pdf.set_font('Helvetica', '', 9)
            for bullet in ips_alignment_text:
                if bullet and bullet.strip():
                    try:
                        clean_bullet = safe_pdf_text(bullet.strip())[:200]
                        pdf.multi_cell(0, 5, safe_pdf_text(f'  • {clean_bullet}'))
                    except:
                        continue
    
    # Footer
    pdf.ln(10)
    pdf.set_font('Helvetica', 'I', 8)
    pdf.set_text_color(128, 128, 128)
    pdf.multi_cell(0, 4, 'Disclaimer: This report is for informational purposes only and does not constitute investment advice. Past performance does not guarantee future results. Analyst price targets are consensus estimates and may not be achieved.')
    
    # Return PDF as bytes
    pdf_output = pdf.output()
    if isinstance(pdf_output, bytearray):
        return bytes(pdf_output)
    return pdf_output
