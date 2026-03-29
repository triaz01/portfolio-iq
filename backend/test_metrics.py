import sys
sys.stdout.reconfigure(encoding='utf-8')

from logic.extractor import parse_pasted_text
from logic.metrics import calculate_portfolio_metrics

# Test the parsing
text = "AAPL 100"
print(f"Testing with: {text}")

portfolio = parse_pasted_text(text)
print(f"Parsed portfolio: {portfolio}")

if portfolio:
    print("\nCalling calculate_portfolio_metrics...")
    metrics = calculate_portfolio_metrics(portfolio, "USD")
    print(f"\nMetrics result: {metrics is not None}")
    if metrics is None:
        print("ERROR: Metrics returned None!")
else:
    print("ERROR: No portfolio parsed!")
