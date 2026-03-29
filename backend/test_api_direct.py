import sys
sys.stdout.reconfigure(encoding='utf-8')

# Test if the API response can be serialized
from logic.extractor import parse_pasted_text
from logic.metrics import calculate_portfolio_metrics, generate_investor_summary
import json

text = "AAPL 100"
currency = "CAD"

print("Testing API response serialization...")

portfolio = parse_pasted_text(text)
metrics = calculate_portfolio_metrics(portfolio, currency)

if metrics:
    summary = generate_investor_summary(metrics)
    
    # Convert DataFrames exactly as the API does
    proj_json = None
    if 'projection_df' in metrics and metrics['projection_df'] is not None:
        proj_json = metrics['projection_df'].to_dict(orient='records')
        del metrics['projection_df']
    
    corr_json = None
    if 'correlation_matrix' in metrics and metrics['correlation_matrix'] is not None:
        corr_json = metrics['correlation_matrix'].to_dict()
        del metrics['correlation_matrix']
    
    chart_json = None
    if 'chart_data' in metrics and metrics['chart_data'] is not None:
        metrics['chart_data'].index = metrics['chart_data'].index.astype(str)
        chart_json = metrics['chart_data'].to_dict(orient='index')
        del metrics['chart_data']
    
    # Build the exact response the API would return
    response = {
        "metrics": metrics,
        "summary": summary,
        "projection_df": proj_json,
        "correlation_matrix": corr_json,
        "chart_data": chart_json,
    }
    
    # Try to serialize to JSON
    try:
        json_str = json.dumps(response)
        print("\n✓ SUCCESS: Response can be serialized to JSON")
        print(f"Response size: {len(json_str)} bytes")
        
        # Try to parse it back
        parsed = json.loads(json_str)
        print("✓ SUCCESS: JSON can be parsed back")
        
        # Save to file for inspection
        with open("test_response.json", "w", encoding="utf-8") as f:
            json.dump(response, f, indent=2)
        print("✓ Response saved to test_response.json")
        
    except Exception as e:
        print(f"\n✗ FAILED: Cannot serialize response to JSON")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        
        # Try to find which field is causing the issue
        print("\nTesting individual fields:")
        for key, value in response.items():
            try:
                json.dumps({key: value})
                print(f"  ✓ {key}: OK")
            except Exception as field_error:
                print(f"  ✗ {key}: FAILED - {field_error}")
