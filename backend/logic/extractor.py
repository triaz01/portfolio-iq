import re
import yfinance as yf

def parse_pasted_text(text):
    print("\n" + "="*40)
    print("[EXTRACTOR] STARTING EXTRACTOR DEBUG LOG")
    print("="*40)
    
    try:
        if not text or not isinstance(text, str):
            print("[ERROR] Input text is empty or not a string.")
            return {}
        
        print(f"[1] RAW TEXT RECEIVED:\n{text}\n")
        
        text = text.upper()
        print(f"[2] TEXT AFTER UPPERCASE:\n{text}\n")
        
        pattern = r'\b((?:TSE:|TSX:|CVE:)?[A-Z]{1,5}(?:\.[A-Z]{1,2})?(?:\.TO|:CA|-CA|\.VN|\.V)?)\b[^\d]{0,30}?([\d,]+(?:\.\d+)?)'
        print(f"[3] REGEX PATTERN USED:\n{pattern}\n")
        
        matches = re.findall(pattern, text)
        print(f"[4] RAW MATCHES FOUND: {matches}\n")
        
        portfolio = {}
        for raw_ticker, shares in matches:
            print(f"  [>] Processing Match: Ticker='{raw_ticker}', Shares='{shares}'")
            shares_clean = shares.replace(',', '')
            share_count = int(float(shares_clean))
            
            normalized_ticker = normalize_ticker(raw_ticker)
            print(f"  [OK] Normalized '{raw_ticker}' ---> '{normalized_ticker}'\n")
            
            if normalized_ticker in portfolio:
                portfolio[normalized_ticker] += share_count
            else:
                portfolio[normalized_ticker] = share_count
        
        print(f"[5] FINAL PORTFOLIO DICTIONARY: {portfolio}")
        print("="*40 + "\n")
        return portfolio
    
    except Exception as e:
        print(f"[ERROR] FATAL ERROR IN PARSER: {e}")
        return {}

def normalize_ticker(raw_ticker):
    ticker = raw_ticker.upper().strip()
    print(f"      [Normalizing] Started with: {ticker}")
    
    had_tsx_prefix = False
    had_venture_prefix = False
    
    # Check and strip prefixes
    if ticker.startswith('TSE:') or ticker.startswith('TSX:'):
        had_tsx_prefix = True
        ticker = ticker.split(':', 1)[1]
        print(f"      [Normalizing] Stripped TSX prefix. Now: {ticker}")
    elif ticker.startswith('CVE:'):
        had_venture_prefix = True
        ticker = ticker.split(':', 1)[1]
        print(f"      [Normalizing] Stripped CVE prefix. Now: {ticker}")
    
    # Check and translate TSX suffixes
    if had_tsx_prefix or ticker.endswith('.TO') or ticker.endswith(':CA') or ticker.endswith('-CA'):
        base_ticker = ticker.replace('.TO', '').replace(':CA', '').replace('-CA', '')
        result = f"{base_ticker}.TO"
        print(f"      [Normalizing] Applied TSX rule. Returning: {result}")
        return result
    
    # Check and translate Venture suffixes
    if had_venture_prefix or ticker.endswith('.V') or ticker.endswith('.VN'):
        base_ticker = ticker.replace('.V', '').replace('.VN', '')
        result = f"{base_ticker}.V"
        print(f"      [Normalizing] Applied Venture rule. Returning: {result}")
        return result
    
    # Smart auto-correction: If no Canadian tags found, check if it's a valid US ticker
    # If not, try .TO suffix for TSX
    if '.' not in ticker:
        print(f"      [Smart Correction] No dot found. Checking US exchanges...")
        try:
            hist = yf.Ticker(ticker).history(period='1d')
            if not hist.empty:
                print(f"      [Smart Correction] Valid US ticker. Returning: {ticker}")
                return ticker
        except:
            pass
        
        # Try .TO suffix for TSX
        print(f"      [Smart Correction] US ticker invalid. Trying .TO suffix...")
        try:
            tsx_ticker = ticker + '.TO'
            hist_tsx = yf.Ticker(tsx_ticker).history(period='1d')
            if not hist_tsx.empty:
                print(f"      [Smart Correction] Valid TSX ticker. Returning: {tsx_ticker}")
                return tsx_ticker
        except:
            pass
    
    print(f"      [Normalizing] No Canadian tags found and auto-correction failed. Returning: {ticker}")
    return ticker

def parse_csv_dataframe(df):
    print("\n" + "="*40)
    print("[CSV] STARTING CSV PARSER")
    print("="*40)
    
    try:
        if df is None or df.empty:
            print("[ERROR] DataFrame is empty or None.")
            return {}
        
        print(f"[1] CSV DataFrame shape: {df.shape}")
        print(f"[2] CSV columns: {list(df.columns)}")
        
        portfolio = {}
        
        # Use first column for tickers, second column for shares
        for index, row in df.iterrows():
            try:
                raw_ticker = str(row.iloc[0]).strip()
                shares_raw = str(row.iloc[1]).strip()
                
                # Skip empty rows
                if not raw_ticker or raw_ticker.lower() in ['nan', 'none', '']:
                    continue
                
                print(f"  [>] Processing Row {index}: Ticker='{raw_ticker}', Shares='{shares_raw}'")
                
                # Clean shares data
                shares_clean = shares_raw.replace(',', '')
                share_count = int(float(shares_clean))
                
                # Normalize ticker using existing function
                normalized_ticker = normalize_ticker(raw_ticker)
                print(f"  [OK] Normalized '{raw_ticker}' ---> '{normalized_ticker}'\n")
                
                # Aggregate shares if ticker already exists
                if normalized_ticker in portfolio:
                    portfolio[normalized_ticker] += share_count
                else:
                    portfolio[normalized_ticker] = share_count
                    
            except Exception as e:
                print(f"  [WARN] Skipping row {index} due to error: {e}")
                continue
        
        print(f"[3] FINAL PORTFOLIO DICTIONARY: {portfolio}")
        print("="*40 + "\n")
        return portfolio
    
    except Exception as e:
        print(f"[ERROR] FATAL ERROR IN CSV PARSER: {e}")
        return {}
