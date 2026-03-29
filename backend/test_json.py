import sys
import json
sys.stdout.reconfigure(encoding='utf-8')

from logic.extractor import parse_pasted_text
from logic.metrics import calculate_portfolio_metrics, generate_investor_summary

# Test JSON serialization
text = "AAPL 100"
currency = "CAD"

portfolio = parse_pasted_text(text)
metrics = calculate_portfolio_metrics(portfolio, currency)

if metrics:
    print("\n=== Testing JSON Serialization ===")
    
    # Test each component
    print("\n1. Testing metrics dict...")
    try:
        # Check for non-serializable objects
        for key, value in metrics.items():
            try:
                json.dumps({key: value})
                print(f"  ✓ {key}: OK")
            except Exception as e:
                print(f"  ✗ {key}: FAILED - {type(value)} - {str(e)[:100]}")
    except Exception as e:
        print(f"  ERROR: {e}")
    
    print("\n2. Testing summary...")
    try:
        summary = generate_investor_summary(metrics)
        json.dumps(summary)
        print(f"  ✓ Summary: OK")
    except Exception as e:
        print(f"  ✗ Summary: FAILED - {e}")
    
    print("\n3. Testing projection_df conversion...")
    try:
        if 'projection_df' in metrics and metrics['projection_df'] is not None:
            proj_json = metrics['projection_df'].to_dict(orient='records')
            json.dumps(proj_json)
            print(f"  ✓ projection_df: OK")
    except Exception as e:
        print(f"  ✗ projection_df: FAILED - {e}")
    
    print("\n4. Testing correlation_matrix conversion...")
    try:
        if 'correlation_matrix' in metrics and metrics['correlation_matrix'] is not None:
            corr_json = metrics['correlation_matrix'].to_dict()
            json.dumps(corr_json)
            print(f"  ✓ correlation_matrix: OK")
    except Exception as e:
        print(f"  ✗ correlation_matrix: FAILED - {e}")
    
    print("\n5. Testing chart_data conversion...")
    try:
        if 'chart_data' in metrics and metrics['chart_data'] is not None:
            chart_data_copy = metrics['chart_data'].copy()
            chart_data_copy.index = chart_data_copy.index.astype(str)
            chart_json = chart_data_copy.to_dict(orient='index')
            json.dumps(chart_json)
            print(f"  ✓ chart_data: OK")
    except Exception as e:
        print(f"  ✗ chart_data: FAILED - {e}")
    
    print("\n=== All tests complete ===")
