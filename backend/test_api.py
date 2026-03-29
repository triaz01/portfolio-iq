import sys
sys.stdout.reconfigure(encoding='utf-8')

from logic.extractor import parse_pasted_text
from logic.metrics import calculate_portfolio_metrics, generate_investor_summary
import json

# Test the full API flow
text = "AAPL 100"
currency = "CAD"

print(f"Testing API flow with: {text}, currency: {currency}")

# Step 1: Parse
portfolio = parse_pasted_text(text)
print(f"\n1. Parsed portfolio: {portfolio}")

# Step 2: Calculate metrics
metrics = calculate_portfolio_metrics(portfolio, currency)
print(f"\n2. Metrics calculated: {metrics is not None}")

if metrics:
    # Step 3: Generate summary
    try:
        summary = generate_investor_summary(metrics)
        print(f"\n3. Summary generated: {summary[:100]}...")
    except Exception as e:
        print(f"\n3. ERROR generating summary: {e}")
        import traceback
        traceback.print_exc()
    
    # Step 4: Try to serialize to JSON (this is where the API might be failing)
    try:
        # Convert projection_df
        proj_json = None
        if 'projection_df' in metrics and metrics['projection_df'] is not None:
            proj_json = metrics['projection_df'].to_dict(orient='records')
            del metrics['projection_df']
        
        # Convert correlation_matrix
        corr_json = None
        if 'correlation_matrix' in metrics and metrics['correlation_matrix'] is not None:
            corr_json = metrics['correlation_matrix'].to_dict()
            del metrics['correlation_matrix']
        
        # Convert chart_data
        chart_json = None
        if 'chart_data' in metrics and metrics['chart_data'] is not None:
            metrics['chart_data'].index = metrics['chart_data'].index.astype(str)
            chart_json = metrics['chart_data'].to_dict(orient='index')
            del metrics['chart_data']
        
        # Try to serialize the response
        response = {
            "metrics": metrics,
            "summary": summary,
            "projection_df": proj_json,
            "correlation_matrix": corr_json,
            "chart_data": chart_json,
        }
        
        json_str = json.dumps(response, default=str)
        print(f"\n4. JSON serialization successful! Length: {len(json_str)} bytes")
        
    except Exception as e:
        print(f"\n4. ERROR during JSON serialization: {e}")
        import traceback
        traceback.print_exc()
