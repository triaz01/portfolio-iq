import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime
from extractor import parse_pasted_text, parse_csv_dataframe
from metrics import calculate_portfolio_metrics, generate_investor_summary
from ips_engine import calculate_ips, assess_alignment
from monte_carlo import run_monte_carlo
from pdf_generator import generate_pdf_report

st.set_page_config(page_title='Portfolio Analyzer', layout='wide', initial_sidebar_state='collapsed')

# Top Navigation Bar
nav1, nav2, spacer, nav3 = st.columns([1.5, 1.5, 4, 2])

with nav1:
    if st.button('🏠 Start Over', use_container_width=True):
        st.session_state.app_step = 'onboarding'
        st.session_state.ips_profile = None
        st.session_state.ips_targets = None
        st.rerun()

with nav2:
    if st.button('📊 Dashboard', use_container_width=True):
        if 'ips_targets' in st.session_state and st.session_state.ips_targets:
            st.session_state.app_step = 'analysis'
            st.rerun()
        else:
            st.toast('Please generate your IPS first!')

with nav3:
    base_currency = st.selectbox('Currency', ['CAD', 'USD'], index=0, label_visibility='collapsed')

st.divider()

# Pastel Design System CSS
st.markdown("""
<style>
    /* Global background */
    .stApp {
        background-color: #faf9f8;
    }
    
    /* Card containers */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.04);
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    /* Metric cards */
    [data-testid="stMetric"] {
        background-color: #f8fafc;
        border-radius: 12px;
        padding: 15px;
        border: none;
        transition: transform 0.2s ease;
    }
    
    [data-testid="stMetric"]:hover {
        transform: translateY(-2px);
    }
    
    /* Pastel buttons */
    .stButton>button {
        border-radius: 20px;
        font-weight: 500;
        padding: 0.5rem 1.5rem;
        background: #e2e8f0;
        color: #4a5568;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background: #cbd5e1;
        transform: translateY(-1px);
    }
    
    /* Container spacing */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    
    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .block-container {
            padding-left: 0.5rem;
            padding-right: 0.5rem;
        }
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'app_step' not in st.session_state:
    st.session_state.app_step = 'onboarding'
if 'ips_profile' not in st.session_state:
    st.session_state.ips_profile = None
if 'ips_targets' not in st.session_state:
    st.session_state.ips_targets = None
if 'pdf_data' not in st.session_state:
    st.session_state.pdf_data = None
if 'current_metrics' not in st.session_state:
    st.session_state.current_metrics = None
if 'current_portfolio' not in st.session_state:
    st.session_state.current_portfolio = None
if 'current_chart' not in st.session_state:
    st.session_state.current_chart = None

# Onboarding UI
if st.session_state.app_step == 'onboarding':
    with st.container(border=True):
        st.markdown("### Step 1 of 2: Risk Profile")
        st.progress(0.5)
        
        st.subheader('📝 Define Your Investment Policy')
        st.markdown("Answer a few questions to create your personalized Investment Policy Statement")
        
        st.markdown("---")
        
        # Time & Liquidity Section
        st.markdown("##### ⏰ Time Horizon & Liquidity")
        time_horizon = st.slider(
            'How long until you need to withdraw a significant portion of this money?',
            min_value=1,
            max_value=30,
            value=10,
            format='%d Years',
            help='Longer time horizons generally allow you to take on more risk because you have time to recover from market dips.'
        )
        
        liquidity = st.select_slider(
            'What portion of your portfolio might you need in cash within the next 12 months?',
            options=['None (0%)', 'Low (< 10%)', 'Moderate (10-25%)', 'High (> 25%)'],
            value='Low (< 10%)',
            help='Money you need in cash soon should not be exposed to the stock market. High liquidity needs require a more conservative approach.'
        )
        
        st.markdown("---")
        
        # Investment Goals Section
        st.markdown("##### 🎯 Investment Objectives")
        objective = st.radio(
            'What is your primary goal?',
            ['Capital Preservation', 'Steady Income', 'Balanced Growth', 'Maximum Capital Appreciation'],
            horizontal=True,
            help='Capital preservation protects what you have. Income generates cash flow. Growth aims to increase the total value of your assets over time.'
        )
        
        st.markdown("---")
        
        # Risk Tolerance Section
        st.markdown("##### 📉 Risk Tolerance")
        crash_reaction = st.radio(
            'If your portfolio dropped 20% in one month, what would you do?',
            ['Sell to avoid further losses', 'Do nothing and wait', 'Buy more at a discount'],
            horizontal=True,
            help='This measures your emotional tolerance for risk. Panic selling locks in losses, while buying the dip requires strong risk tolerance.'
        )
        
        knowledge = st.select_slider(
            'How would you rate your investment experience?',
            options=['Novice', 'Intermediate', 'Advanced', 'Expert'],
            value='Intermediate'
        )
        
        st.markdown("---")
        
        # Generate IPS Button
        if st.button('Generate My IPS', use_container_width=True):
            # Calculate IPS and store in session state
            profile, targets = calculate_ips(time_horizon, liquidity, objective, crash_reaction, knowledge)
            st.session_state.ips_profile = profile
            st.session_state.ips_targets = targets
            st.session_state.app_step = 'analysis'
            st.rerun()

# Analysis UI
elif st.session_state.app_step == 'analysis':
    st.markdown("### Step 2 of 2: Portfolio Analysis")
    st.progress(1.0)
    
    # Display IPS summary banner with reset button and PDF download
    if st.session_state.ips_profile and st.session_state.ips_targets:
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.success(f"🎯 **Your Active IPS**: {st.session_state.ips_profile}")
        with col2:
            # PDF Download button (only shows if analysis data is available)
            if 'pdf_data' in st.session_state and st.session_state.pdf_data:
                st.download_button(
                    label="📄 Download PDF",
                    data=st.session_state.pdf_data,
                    file_name="Portfolio_Tear_Sheet.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
        with col3:
            if st.button("🔄 Reset IPS", use_container_width=True):
                st.session_state.app_step = 'onboarding'
                st.session_state.ips_profile = None
                st.session_state.ips_targets = None
                st.session_state.pdf_data = None
                st.rerun()
    
    # Input Method Selection
    input_method = st.radio(
        "Input Method",
        options=["Paste Text", "Upload CSV"],
        horizontal=True
    )
    
    # Data Ingestion Card
    with st.container(border=True):
        st.subheader('📥 Update Portfolio Data')
        
        if input_method == "Paste Text":
            pasted_text = st.text_area(
                "Enter your portfolio data (e.g., 'AAPL 100, MSFT 50, GOOGL 25')",
                height=150,
                placeholder="AAPL 100\nMSFT 50\nGOOGL 25",
                help='Paste your holdings directly from your brokerage account (Format: Ticker followed by Shares, e.g., AAPL 100).'
            )
            
            if st.button("Analyze Portfolio"):
                try:
                    portfolio = parse_pasted_text(pasted_text)
                    
                    if not portfolio:
                        st.error("No valid tickers found. Please check your input format.")
                    else:
                        st.success(f"Found {len(portfolio)} ticker(s): {', '.join(portfolio.keys())}")
                        
                        with st.spinner("Fetching market data..."):
                            metrics = calculate_portfolio_metrics(portfolio, base_currency)
                        
                        if metrics is None:
                            st.error("Unable to fetch data for the provided tickers. Please verify ticker symbols.")
                        else:
                            # Store metrics in session state for PDF generation
                            st.session_state.current_metrics = metrics
                            st.session_state.current_portfolio = portfolio
                            
                            # Create and store chart for later use
                            pastel_colors = ['#8884d8', '#82ca9d', '#ffc658']
                            chart_fig = px.line(
                                metrics['chart_data'],
                                labels={
                                    "value": "Growth Multiplier",
                                    "index": "Date",
                                    "variable": "Series"
                                },
                                color_discrete_sequence=pastel_colors
                            )
                            chart_fig.update_traces(line=dict(width=3))
                            chart_fig.update_layout(
                                template='plotly_white',
                                paper_bgcolor='rgba(0,0,0,0)',
                                plot_bgcolor='rgba(0,0,0,0)',
                                yaxis_title="Growth Multiplier (Starting at 1.0)",
                                xaxis_title="",
                                showlegend=True,
                                legend=dict(
                                    orientation="h",
                                    yanchor="bottom",
                                    y=1.02,
                                    xanchor="right",
                                    x=1,
                                    font=dict(color='#4a5568')
                                ),
                                hovermode="x unified",
                                margin=dict(l=0, r=0, t=40, b=0),
                                font=dict(color='#4a5568')
                            )
                            chart_fig.update_xaxes(showgrid=False, tickfont=dict(color='#4a5568'))
                            chart_fig.update_yaxes(showgrid=False, tickformat=".1f", tickfont=dict(color='#4a5568'))
                            st.session_state.current_chart = chart_fig
                            
                            st.success("✅ Analysis complete! Your portfolio results are displayed below.")
                
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

    # Analysis Display Section - Shows cards based on session state
    if st.session_state.get('current_metrics'):
        metrics = st.session_state.current_metrics
        
        # Display ignored tickers warning if any
        if metrics.get('ignored_tickers') and len(metrics['ignored_tickers']) > 0:
            with st.expander("⚠️ Some tickers were excluded from analysis"):
                st.warning("The following tickers could not be found on US or Canadian exchanges:")
                for ignored in metrics['ignored_tickers']:
                    st.write(f"• **{ignored['symbol']}**: {ignored['reason']}")
        
        # Metrics Card
        with st.container(border=True):
            st.subheader('📈 Portfolio Performance')
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("Annualized Return", f"{metrics['annualized_return'] * 100:.2f}%", 
                        help='The average yearly growth of your portfolio over the analysis timeframe, assuming all dividends are reinvested.')
            
            with col2:
                st.metric("Annualized Volatility", f"{metrics['annual_volatility'] * 100:.2f}%", 
                        help='How wildly your portfolio swings up and down. A lower percentage means a smoother, steadier ride. A higher percentage means extreme ups and downs.')
            
            with col3:
                st.metric("Portfolio Beta", f"{metrics['portfolio_beta']:.2f}", 
                        help='Measures how much your portfolio moves compared to the broader market. A Beta of 1.0 moves exactly with the market. >1.0 is more aggressive, <1.0 is more defensive.')
            
            with col4:
                st.metric("Dividend Yield", f"{metrics['weighted_dividend_yield']:.2f}%", 
                        help='The percentage of your portfolio\'s total value that is paid out to you in cash dividends over the course of a year.')
            
            with col5:
                st.metric("Max Drawdown", f"{metrics['max_drawdown'] * 100:.2f}%", 
                        help='The ultimate "sleep at night" metric. This is the largest single percentage drop your portfolio experienced from a peak to a bottom during this timeframe.')
        
        # Visualization Card
        with st.container(border=True):
            st.subheader('📊 3-Year Growth Trajectory')
            
            # Generate chart if not in session state
            if 'current_chart' not in st.session_state:
                # Pastel color scheme
                pastel_colors = ['#8884d8', '#82ca9d', '#ffc658']
                chart_fig = px.line(
                    metrics['chart_data'],
                    labels={
                        "value": "Growth Multiplier",
                        "index": "Date",
                        "variable": "Series"
                    },
                    color_discrete_sequence=pastel_colors
                )
                
                chart_fig.update_traces(line=dict(width=3))
                
                chart_fig.update_layout(
                    template='plotly_white',
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    yaxis_title="Growth Multiplier (Starting at 1.0)",
                    xaxis_title="",
                    showlegend=True,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1,
                        font=dict(color='#4a5568')
                    ),
                    hovermode="x unified",
                    margin=dict(l=0, r=0, t=40, b=0),
                    font=dict(color='#4a5568')
                )
                
                chart_fig.update_xaxes(showgrid=False, tickfont=dict(color='#4a5568'))
                chart_fig.update_yaxes(showgrid=False, tickformat=".1f", tickfont=dict(color='#4a5568'))
                
                # Store chart in session state for PDF generation
                st.session_state.current_chart = chart_fig
                
                st.plotly_chart(chart_fig, use_container_width=True)
            else:
                # Validate that current_chart is a valid Plotly figure
                if st.session_state.current_chart and hasattr(st.session_state.current_chart, 'data'):
                    st.plotly_chart(st.session_state.current_chart, use_container_width=True)
                else:
                    st.error("Chart data is not available. Please try analyzing your portfolio again.")
                    # Clear invalid chart from session state
                    st.session_state.current_chart = None
        
        # IPS Alignment Card
        if st.session_state.ips_targets:
            with st.container(border=True):
                st.subheader('⚖️ IPS Alignment Check')
                
                # Create alignment table
                targets = st.session_state.ips_targets
                beta_min, beta_max = targets['beta_range']
                vol_min, vol_max = targets['volatility_range']
                yield_min = targets.get('yield_min', 0)
                yield_max = targets.get('yield_max', 1.0)
                
                alignment_table = pd.DataFrame({
                    'Metric': ['Portfolio Beta', 'Annualized Volatility', 'Dividend Yield'],
                    'Your Portfolio': [
                        f"{metrics['portfolio_beta']:.2f}",
                        f"{metrics['annual_volatility']:.1%}",
                        f"{metrics['weighted_dividend_yield']:.2f}%"
                    ],
                    'Target Range': [
                        f"{beta_min:.2f} - {beta_max:.2f}",
                        f"{vol_min:.1%} - {vol_max:.1%}",
                        f"{yield_min*100:.1f}% - {yield_max*100:.1f}%" if yield_max < 1.0 else f"> {yield_min*100:.1f}%"
                    ],
                    'Status': [
                        '✅ Aligned' if beta_min <= metrics['portfolio_beta'] <= beta_max else '⚠️ Misaligned',
                        '✅ Aligned' if vol_min <= metrics['annual_volatility'] <= vol_max else '⚠️ Misaligned',
                        '✅ Aligned' if yield_min <= metrics['weighted_dividend_yield']/100 <= yield_max else '⚠️ Misaligned'
                    ]
                })
                
                st.dataframe(alignment_table, use_container_width=True, hide_index=True)
                
                # Display detailed alignment feedback
                alignment_result = assess_alignment(metrics, st.session_state.ips_targets, st.session_state.ips_profile)
                
                if alignment_result['is_aligned']:
                    st.success("\n".join(alignment_result['bullets']))
                else:
                    st.warning("\n".join(alignment_result['bullets']))
        
        # Projections Card
        with st.container(border=True):
            st.subheader('🔮 12-Month Analyst Projections')
            
            # Calculate portfolio upside
            upside_pct = ((metrics['total_projected_value'] - metrics['total_value']) / metrics['total_value']) * 100
            
            # Display current vs projected values
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Current Portfolio Value", f"${metrics['total_value']:,.2f}")
            with col2:
                st.metric("Projected Portfolio Value", f"${metrics['total_projected_value']:,.2f}", delta=f"{upside_pct:.2f}% Upside",
                        help='Calculated using the 12-month aggregated consensus price targets from Wall Street analysts. If no target exists (like for ETFs), it assumes 0% growth for that asset.')
            
            # Format and display projection DataFrame with color coding
            def color_projections(row):
                current_price = row['Current Price']
                target_price = row['Target Price']
                
                if target_price > current_price:
                    return ['background-color: #d4edda'] * len(row)  # Pastel green
                elif target_price < current_price:
                    return ['background-color: #f8d7da'] * len(row)  # Pastel red
                else:
                    return ['background-color: #ffffff'] * len(row)  # White
            
            projection_styled = metrics['projection_df'].style.format({
                'Current Price': '${:,.2f}',
                'Target Price': '${:,.2f}',
                'Current Value': '${:,.2f}',
                'Projected Value': '${:,.2f}'
            }).apply(color_projections, axis=1)
            
            st.dataframe(projection_styled, use_container_width=True, hide_index=True)
        
        # Monte Carlo Simulation Card
        with st.container(border=True):
            st.subheader('🎲 Monte Carlo Wealth Simulation')
            
            # Interactive slider for simulation horizon
            sim_years = st.slider('Projection Horizon (Years)', min_value=5, max_value=30, value=10, step=1)
            
            # Run Monte Carlo simulation
            mc_results = run_monte_carlo(
                initial_value=metrics['total_value'],
                cagr=metrics['annualized_return'],
                volatility=metrics['annual_volatility'],
                years=sim_years,
                simulations=500
            )
            
            # Create Plotly chart
            mc_fig = px.line(
                mc_results,
                labels={
                    "value": "Portfolio Value",
                    "Year": "Years from Now",
                    "variable": "Scenario"
                },
                color_discrete_map={
                    '10th Percentile (Bear Market)': '#ff9999',  # Pastel red/coral
                    '50th Percentile (Expected)': '#9ca3af',      # Gray/slate
                    '90th Percentile (Bull Market)': '#82ca9d'    # Pastel green/teal
                }
            )
            
            mc_fig.update_traces(line=dict(width=2.5))
            
            mc_fig.update_layout(
                template='plotly_white',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                yaxis_title="Portfolio Value",
                xaxis_title="Years from Now",
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                    font=dict(color='#4a5568')
                ),
                hovermode="x unified",
                margin=dict(l=0, r=0, t=40, b=0),
                font=dict(color='#4a5568')
            )
            
            mc_fig.update_xaxes(showgrid=False, tickfont=dict(color='#4a5568'))
            mc_fig.update_yaxes(showgrid=False, tickformat="$,.0f", tickfont=dict(color='#4a5568'))
            
            # Store Monte Carlo figure in session state for PDF generation
            st.session_state.current_monte_carlo_fig = mc_fig
            
            st.plotly_chart(mc_fig, use_container_width=True)
            
            st.caption("📊 This simulation runs 500 randomized market scenarios based on your portfolio's historical risk/return profile. The three lines represent the range of probable outcomes: bear market (10th percentile), expected case (median), and bull market (90th percentile).")
        
        # PDF Generation Button
        st.divider()
        
        # Add anchor point for auto-scroll
        st.markdown('<div id="pdf-generation-section"></div>', unsafe_allow_html=True)
        
        if st.button("📄 Generate PDF Report", type="primary", use_container_width=True, key="pdf_generate"):
            # Auto-scroll to this section
            st.markdown(
                """
                <script>
                    window.parent.document.getElementById('pdf-generation-section').scrollIntoView({behavior: 'smooth', block: 'start'});
                </script>
                """,
                unsafe_allow_html=True
            )
            
            # Create progress container
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Use session state data
                if 'current_metrics' in st.session_state:
                    # Step 1: Prepare data
                    status_text.text("⏳ Preparing data... (20%)")
                    progress_bar.progress(20)
                    
                    # Get alignment text
                    alignment_result = assess_alignment(
                        st.session_state.current_metrics, 
                        st.session_state.ips_targets, 
                        st.session_state.ips_profile
                    )
                    
                    # Step 2: Clean text
                    status_text.text("⏳ Processing alignment data... (40%)")
                    progress_bar.progress(40)
                    
                    # Remove emojis from alignment text for PDF compatibility
                    clean_bullets = []
                    for bullet in alignment_result['bullets']:
                        # Remove emojis and special characters
                        clean_bullet = bullet
                        # Remove common emojis
                        for emoji in ['📊', '⚠️', '✅', '🎯', '📈', '📉', '💰', '🔮', '🎲', '📄', '📥', '🔄']:
                            clean_bullet = clean_bullet.replace(emoji, '')
                        # Remove any remaining non-ASCII characters
                        clean_bullet = ''.join(char for char in clean_bullet if ord(char) < 128)
                        clean_bullets.append(clean_bullet.strip())
                    
                    # Step 3: Prepare chart
                    status_text.text("⏳ Preparing chart... (60%)")
                    progress_bar.progress(60)
                    
                    # Generate PDF
                    chart_fig = st.session_state.get('current_chart')
                    if not chart_fig or not hasattr(chart_fig, 'data'):
                        # Generate chart if not available
                        pastel_colors = ['#8884d8', '#82ca9d', '#ffc658']
                        chart_fig = px.line(
                            st.session_state.current_metrics['chart_data'],
                            labels={
                                "value": "Growth Multiplier",
                                "index": "Date",
                                "variable": "Series"
                            },
                            color_discrete_sequence=pastel_colors
                        )
                        chart_fig.update_traces(line=dict(width=3))
                        chart_fig.update_layout(
                            template='plotly_white',
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            yaxis_title="Growth Multiplier (Starting at 1.0)",
                            xaxis_title="",
                            showlegend=True,
                            legend=dict(
                                orientation="h",
                                yanchor="bottom",
                                y=1.02,
                                xanchor="right",
                                x=1,
                                font=dict(color='#4a5568')
                            ),
                            hovermode="x unified",
                            margin=dict(l=0, r=0, t=40, b=0),
                            font=dict(color='#4a5568')
                        )
                        chart_fig.update_xaxes(showgrid=False, tickfont=dict(color='#4a5568'))
                        chart_fig.update_yaxes(showgrid=False, tickformat=".1f", tickfont=dict(color='#4a5568'))
                    
                    # Step 4: Generate PDF
                    status_text.text("⏳ Generating PDF document... (80%)")
                    progress_bar.progress(80)
                    
                    pdf_bytes = generate_pdf_report(
                        metrics=st.session_state.current_metrics,
                        ips_profile=st.session_state.ips_profile,
                        ips_alignment_text=clean_bullets,
                        growth_chart_fig=chart_fig,
                        projection_df=st.session_state.current_metrics['projection_df'],
                        ips_targets=st.session_state.ips_targets,
                        monte_carlo_fig=st.session_state.get('current_monte_carlo_fig')
                    )
                    
                    # Step 5: Complete
                    status_text.text("✅ Finalizing... (100%)")
                    progress_bar.progress(100)
                    
                    # Store in session state
                    st.session_state.pdf_data = pdf_bytes
                    
                    # Clear progress indicators
                    progress_bar.empty()
                    status_text.empty()
                    
                    # Trigger automatic download
                    st.success("✅ PDF Report generated successfully! Download starting...")
                    st.download_button(
                        label="📄 Download PDF Report",
                        data=pdf_bytes,
                        file_name=f"Portfolio_Tear_Sheet_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf",
                        type="primary",
                        use_container_width=True
                    )
                else:
                    progress_bar.empty()
                    status_text.empty()
                    st.error("Please analyze a portfolio first before generating PDF.")
                
            except Exception as pdf_error:
                progress_bar.empty()
                status_text.empty()
                import traceback
                error_details = traceback.format_exc()
                st.error(f"PDF generation failed: {str(pdf_error)}")
                with st.expander("🔍 Error Details (for debugging)"):
                    st.code(error_details)

    elif input_method == "Upload CSV":
        # Create sample CSV template
        sample_csv = pd.DataFrame({
            'Ticker': ['AAPL', 'RY.TO', 'ZUH'],
            'Shares': [100, 50, 25]
        }).to_csv(index=False).encode('utf-8')
        
        st.download_button(
            label="📥 Download Sample CSV Template",
            data=sample_csv,
            file_name="portfolio_template.csv",
            mime="text/csv"
        )
        
        st.info("Upload a CSV file with two columns: Ticker (first column) and Shares (second column). Header names are ignored.")
        
        uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'],
                                   help='Upload a simple 2-column CSV file. Column 1: Ticker Symbols. Column 2: Number of shares.')
        
        if uploaded_file is not None:
            try:
                # Read the CSV file
                df = pd.read_csv(uploaded_file)
                st.success(f"CSV file loaded successfully! Found {len(df)} rows.")
                
                # Show preview of uploaded data
                with st.expander("📊 Preview uploaded data"):
                    st.dataframe(df.head(10))
                
                if st.button("Analyze Portfolio"):
                    try:
                        # Parse CSV using our extractor
                        portfolio = parse_csv_dataframe(df)
                        
                        if not portfolio:
                            st.error("No valid tickers found in CSV. Please check your file format.")
                        else:
                            st.success(f"Found {len(portfolio)} ticker(s): {', '.join(portfolio.keys())}")
                            
                            with st.spinner("Fetching market data..."):
                                metrics = calculate_portfolio_metrics(portfolio, base_currency)
                        
                        if metrics is None:
                            st.error("Unable to fetch data for the provided tickers. Please verify ticker symbols.")
                        else:
                            # Store metrics in session state for PDF generation
                            st.session_state.current_metrics = metrics
                            st.session_state.current_portfolio = portfolio
                            
                            # Create and store chart for later use
                            pastel_colors = ['#8884d8', '#82ca9d', '#ffc658']
                            chart_fig = px.line(
                                metrics['chart_data'],
                                labels={
                                    "value": "Growth Multiplier",
                                    "index": "Date",
                                    "variable": "Series"
                                },
                                color_discrete_sequence=pastel_colors
                            )
                            chart_fig.update_traces(line=dict(width=3))
                            chart_fig.update_layout(
                                template='plotly_white',
                                paper_bgcolor='rgba(0,0,0,0)',
                                plot_bgcolor='rgba(0,0,0,0)',
                                yaxis_title="Growth Multiplier (Starting at 1.0)",
                                xaxis_title="",
                                showlegend=True,
                                legend=dict(
                                    orientation="h",
                                    yanchor="bottom",
                                    y=1.02,
                                    xanchor="right",
                                    x=1,
                                    font=dict(color='#4a5568')
                                ),
                                hovermode="x unified",
                                margin=dict(l=0, r=0, t=40, b=0),
                                font=dict(color='#4a5568')
                            )
                            chart_fig.update_xaxes(showgrid=False, tickfont=dict(color='#4a5568'))
                            chart_fig.update_yaxes(showgrid=False, tickformat=".1f", tickfont=dict(color='#4a5568'))
                            st.session_state.current_chart = chart_fig
                            
                            st.success("✅ Analysis complete! Your portfolio results are displayed below.")
                    
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")
                
            except Exception as e:
                st.error(f"Error reading CSV file: {str(e)}")
