from fpdf import FPDF
import tempfile
import os
from datetime import datetime

def generate_pdf_report(metrics, ips_profile, ips_alignment_text, growth_chart_fig, projection_df, ips_targets=None, monte_carlo_fig=None):
    """
    Generate a professionally formatted PDF tear sheet of the portfolio analysis.
    
    Parameters:
    - metrics: Dictionary containing portfolio metrics
    - ips_profile: String describing the investor's risk profile
    - ips_alignment_text: List of bullet points describing IPS alignment
    - growth_chart_fig: Plotly figure object for the growth trajectory chart
    - projection_df: DataFrame with analyst projections
    - ips_targets: Dictionary with IPS target ranges (optional)
    - monte_carlo_fig: Plotly figure object for Monte Carlo simulation (optional)
    
    Returns:
    - PDF as byte string
    """
    # Initialize PDF with Unicode support
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Header
    pdf.set_font('Helvetica', 'B', 16)
    pdf.cell(0, 10, 'Investment Policy & Portfolio Tear Sheet', ln=True, align='C')
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(0, 6, f'Generated: {datetime.now().strftime("%B %d, %Y")}', ln=True, align='C')
    
    # Pastel blue line for styling
    pdf.set_draw_color(132, 132, 216)  # Pastel blue
    pdf.set_line_width(0.5)
    pdf.line(10, pdf.get_y() + 2, 200, pdf.get_y() + 2)
    pdf.ln(8)
    
    # Section 1: IPS & Risk Profile
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 8, f'Risk Profile: {ips_profile}', ln=True)
    pdf.set_font('Helvetica', '', 11)
    pdf.ln(2)
    
    # Write alignment text (use dash instead of bullet)
    for bullet in ips_alignment_text:
        if bullet and bullet.strip():  # Only write non-empty bullets
            try:
                # Ensure text fits within margins
                clean_text = bullet.strip()[:500]  # Limit length
                pdf.multi_cell(0, 5, f'  - {clean_text}')
            except Exception as e:
                # Skip problematic bullets
                continue
    pdf.ln(4)
    
    # Section 2: Core Metrics
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 8, 'Core Portfolio Metrics', ln=True)
    pdf.ln(2)
    
    # Create metrics table
    pdf.set_font('Helvetica', 'B', 10)
    pdf.cell(95, 7, 'Metric', border=1)
    pdf.cell(95, 7, 'Value', border=1, ln=True)
    
    pdf.set_font('Helvetica', '', 10)
    metrics_data = [
        ('Annualized Return', f"{metrics['annualized_return'] * 100:.2f}%"),
        ('Annualized Volatility', f"{metrics['annual_volatility'] * 100:.2f}%"),
        ('Portfolio Beta', f"{metrics['portfolio_beta']:.2f}"),
        ('Dividend Yield', f"{metrics['weighted_dividend_yield']:.2f}%"),
        ('Max Drawdown', f"{metrics['max_drawdown'] * 100:.2f}%"),
        ('Total Portfolio Value', f"${metrics['total_value']:,.2f}")
    ]
    
    for metric_name, metric_value in metrics_data:
        pdf.cell(95, 6, metric_name, border=1)
        pdf.cell(95, 6, metric_value, border=1, ln=True)
    
    pdf.ln(6)
    
    # Section 3: Growth Trajectory Chart
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 8, '3-Year Growth Trajectory', ln=True)
    pdf.ln(2)
    
    # Save chart as temporary image
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            temp_path = tmp.name
        
        # Export Plotly chart to image
        growth_chart_fig.write_image(temp_path, width=800, height=400, scale=2)
        
        # Insert image into PDF
        pdf.image(temp_path, x=10, w=190)
        pdf.ln(4)
    
    finally:
        # Clean up temporary file
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)
    
    # Section 4: Holdings & Projections
    pdf.add_page()  # New page for projections
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 8, 'Analyst Price Targets & Projections', ln=True)
    pdf.ln(2)
    
    # Create projections table (total width: 180mm to be safe)
    pdf.set_font('Helvetica', 'B', 7)
    pdf.cell(25, 6, 'Ticker', border=1, align='C')
    pdf.cell(20, 6, 'Shares', border=1, align='C')
    pdf.cell(45, 6, 'Current', border=1, align='C')
    pdf.cell(45, 6, 'Target', border=1, align='C')
    pdf.cell(45, 6, 'Projected', border=1, align='C', ln=True)
    
    pdf.set_font('Helvetica', '', 8)
    
    # Smart formatting for large numbers (define once outside loop)
    def format_currency(val):
        try:
            if val >= 1000000:
                return f"${val/1000000:.2f}M"
            elif val >= 1000:
                return f"${val/1000:.1f}K"
            else:
                return f"${val:.2f}"
        except:
            return "$0.00"
    
    # Loop through projection DataFrame
    for _, row in projection_df.iterrows():
        try:
            # Truncate and format data to fit columns
            ticker = str(row['Ticker'])[:6]  # Max 6 chars
            shares_val = int(row['Shares'])
            shares = f"{shares_val:,}" if shares_val < 10000 else f"{shares_val/1000:.0f}K"
            shares = shares[:7]  # Limit to 7 chars
            
            # Format currency values with smart truncation
            current_str = format_currency(row['Current Value'])[:10]
            target_str = format_currency(row['Target Price'])[:10]
            projected_str = format_currency(row['Projected Value'])[:10]
            
            pdf.cell(25, 6, ticker, border=1)
            pdf.cell(20, 6, shares, border=1, align='R')
            pdf.cell(45, 6, current_str, border=1, align='R')
            pdf.cell(45, 6, target_str, border=1, align='R')
            pdf.cell(45, 6, projected_str, border=1, align='R', ln=True)
        except Exception as e:
            # Skip problematic rows
            continue
    
    # Add totals row
    pdf.set_font('Helvetica', 'B', 7)
    
    # Format totals with smart truncation
    def format_total(val):
        if val >= 1000000:
            return f"${val/1000000:.2f}M"
        elif val >= 1000:
            return f"${val/1000:.1f}K"
        else:
            return f"${val:,.2f}"
    
    total_current = format_total(metrics['total_value'])[:10]
    total_projected = format_total(metrics['total_projected_value'])[:10]
    
    pdf.cell(45, 6, 'TOTAL', border=1)
    pdf.cell(45, 6, total_current, border=1, align='R')
    pdf.cell(45, 6, '', border=1)
    pdf.cell(45, 6, total_projected, border=1, align='R', ln=True)
    
    # Calculate upside
    upside_pct = ((metrics['total_projected_value'] - metrics['total_value']) / metrics['total_value']) * 100
    pdf.ln(2)
    pdf.set_font('Helvetica', 'I', 10)
    pdf.cell(0, 6, f'Total Projected Upside: {upside_pct:.2f}%', ln=True)
    
    # Section 5: IPS Alignment Check (if targets provided)
    if ips_targets and False:  # Temporarily disabled to isolate error
        pdf.add_page()
        pdf.set_font('Helvetica', 'B', 14)
        pdf.cell(0, 8, 'IPS Alignment Check', ln=True)
        pdf.ln(2)
        
        # Create alignment table (total width: 185mm to be safe)
        pdf.set_font('Helvetica', 'B', 8)
        pdf.cell(55, 6, 'Metric', border=1, align='C')
        pdf.cell(40, 6, 'Your Portfolio', border=1, align='C')
        pdf.cell(50, 6, 'Target Range', border=1, align='C')
        pdf.cell(40, 6, 'Status', border=1, align='C', ln=True)
        
        pdf.set_font('Helvetica', '', 8)
        
        # Beta alignment
        beta_min, beta_max = ips_targets['beta_range']
        beta_val = metrics['portfolio_beta']
        beta_status = 'OK' if beta_min <= beta_val <= beta_max else 'Adjust'
        
        pdf.cell(55, 6, 'Portfolio Beta', border=1)
        pdf.cell(40, 6, f'{beta_val:.2f}', border=1, align='C')
        pdf.cell(50, 6, f'{beta_min:.2f} - {beta_max:.2f}', border=1, align='C')
        pdf.cell(40, 6, beta_status, border=1, align='C', ln=True)
        
        # Volatility alignment
        vol_min, vol_max = ips_targets['volatility_range']
        vol_min_pct = vol_min * 100  # Convert to percentage
        vol_max_pct = vol_max * 100  # Convert to percentage
        vol_val = metrics['annual_volatility'] * 100
        vol_status = 'OK' if vol_min <= (vol_val/100) <= vol_max else 'Adjust'
        
        pdf.cell(55, 6, 'Volatility', border=1)
        pdf.cell(40, 6, f'{vol_val:.1f}%', border=1, align='C')
        pdf.cell(50, 6, f'{vol_min_pct:.1f}% - {vol_max_pct:.1f}%', border=1, align='C')
        pdf.cell(40, 6, vol_status, border=1, align='C', ln=True)
        
        # Dividend yield alignment
        div_min = ips_targets.get('yield_min', 0) * 100  # Convert to percentage
        div_max = ips_targets.get('yield_max', 100) * 100  # Convert to percentage
        div_val = metrics['weighted_dividend_yield']
        div_status = 'OK' if div_min <= div_val <= div_max else 'Adjust'
        
        pdf.cell(55, 6, 'Dividend Yield', border=1)
        pdf.cell(40, 6, f'{div_val:.2f}%', border=1, align='C')
        pdf.cell(50, 6, f'{div_min:.1f}% - {div_max:.1f}%', border=1, align='C')
        pdf.cell(40, 6, div_status, border=1, align='C', ln=True)
        
        pdf.ln(4)
        
        # Alignment summary
        pdf.set_font('Helvetica', 'B', 11)
        in_range_count = sum([
            beta_min <= beta_val <= beta_max,
            vol_min <= vol_val <= vol_max,
            div_min <= div_val <= div_max
        ])
        pdf.cell(0, 6, f'Alignment Summary: {in_range_count}/3 metrics within target ranges', ln=True)
        pdf.ln(2)
        
        # Detailed recommendations
        pdf.set_font('Helvetica', '', 9)
        pdf.multi_cell(0, 5, 'Recommendations:')
        for bullet in ips_alignment_text:
            if bullet and bullet.strip():
                try:
                    clean_text = bullet.strip()[:500]
                    pdf.multi_cell(0, 5, f'  - {clean_text}')
                except:
                    continue
        
        pdf.ln(4)
    
    # Section 6: Monte Carlo Wealth Simulation (if provided)
    if monte_carlo_fig:
        # Force new page and reset cursor position
        pdf.add_page()
        pdf.set_xy(10, 10)  # Reset to top-left with margins
        pdf.set_left_margin(10)
        pdf.set_right_margin(10)
        
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
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                mc_temp_path = tmp.name
            
            # Export Plotly chart to image
            monte_carlo_fig.write_image(mc_temp_path, width=800, height=400, scale=2)
            
            # Insert image into PDF
            pdf.image(mc_temp_path, x=10, w=190)
            pdf.ln(4)
        
        finally:
            # Clean up temporary file
            if mc_temp_path and os.path.exists(mc_temp_path):
                os.unlink(mc_temp_path)
    
    # Footer
    pdf.ln(10)
    pdf.set_font('Helvetica', 'I', 8)
    pdf.set_text_color(128, 128, 128)
    pdf.multi_cell(0, 4, 'Disclaimer: This report is for informational purposes only and does not constitute investment advice. Past performance does not guarantee future results. Analyst price targets are consensus estimates and may not be achieved.')
    
    # Return PDF as bytes
    # Note: fpdf2 returns bytearray, convert to bytes for Streamlit compatibility
    pdf_output = pdf.output()
    if isinstance(pdf_output, bytearray):
        return bytes(pdf_output)
    return pdf_output
