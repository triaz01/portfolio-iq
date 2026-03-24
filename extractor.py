import re

def parse_pasted_text(text):
    print("\n" + "="*40)
    print("🚀 STARTING EXTRACTOR DEBUG LOG")
    print("="*40)
    
    try:
        if not text or not isinstance(text, str):
            print("❌ Error: Input text is empty or not a string.")
            return {}
        
        print(f"1️⃣ RAW TEXT RECEIVED:\n{text}\n")
        
        text = text.upper()
        print(f"2️⃣ TEXT AFTER UPPERCASE:\n{text}\n")
        
        pattern = r'\b((?:TSE:|TSX:|CVE:)?[A-Z]{1,5}(?:\.[A-Z]{1,2})?(?:\.TO|:CA|-CA|\.VN|\.V)?)\b[^\d]{0,30}?([\d,]+(?:\.\d+)?)'
        print(f"3️⃣ REGEX PATTERN USED:\n{pattern}\n")
        
        matches = re.findall(pattern, text)
        print(f"4️⃣ RAW MATCHES FOUND: {matches}\n")
        
        portfolio = {}
        for raw_ticker, shares in matches:
            print(f"  👉 Processing Match: Ticker='{raw_ticker}', Shares='{shares}'")
            shares_clean = shares.replace(',', '')
            share_count = int(float(shares_clean))
            
            normalized_ticker = normalize_ticker(raw_ticker)
            print(f"  ✅ Normalized '{raw_ticker}' ---> '{normalized_ticker}'\n")
            
            if normalized_ticker in portfolio:
                portfolio[normalized_ticker] += share_count
            else:
                portfolio[normalized_ticker] = share_count
        
        print(f"5️⃣ FINAL PORTFOLIO DICTIONARY: {portfolio}")
        print("="*40 + "\n")
        return portfolio
    
    except Exception as e:
        print(f"❌ FATAL ERROR IN PARSER: {e}")
        return {}

def normalize_ticker(raw_ticker):
    ticker = raw_ticker.upper()
    print(f"      [Normalizing] Started with: {ticker}")
    
    had_tsx_prefix = False
    had_venture_prefix = False
    
    # Check and strip prefixes
    if ticker.startswith('TSE:') or ticker.startswith('TSX:'):
        had_tsx_prefix = True
        ticker = ticker.split(':', 1)
        print(f"      [Normalizing] Stripped TSX prefix. Now: {ticker}")
    elif ticker.startswith('CVE:'):
        had_venture_prefix = True
        ticker = ticker.split(':', 1)
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
    
    print(f"      [Normalizing] No Canadian tags found. Returning: {ticker}")
    return ticker

def parse_csv_dataframe(df):
    print("\n" + "="*40)
    print("📊 STARTING CSV PARSER")
    print("="*40)
    
    try:
        if df is None or df.empty:
            print("❌ Error: DataFrame is empty or None.")
            return {}
        
        print(f"1️⃣ CSV DataFrame shape: {df.shape}")
        print(f"2️⃣ CSV columns: {list(df.columns)}")
        
        portfolio = {}
        
        # Use first column for tickers, second column for shares
        for index, row in df.iterrows():
            try:
                raw_ticker = str(row.iloc[0]).strip()
                shares_raw = str(row.iloc[1]).strip()
                
                # Skip empty rows
                if not raw_ticker or raw_ticker.lower() in ['nan', 'none', '']:
                    continue
                
                print(f"  👉 Processing Row {index}: Ticker='{raw_ticker}', Shares='{shares_raw}'")
                
                # Clean shares data
                shares_clean = shares_raw.replace(',', '')
                share_count = int(float(shares_clean))
                
                # Normalize ticker using existing function
                normalized_ticker = normalize_ticker(raw_ticker)
                print(f"  ✅ Normalized '{raw_ticker}' ---> '{normalized_ticker}'\n")
                
                # Aggregate shares if ticker already exists
                if normalized_ticker in portfolio:
                    portfolio[normalized_ticker] += share_count
                else:
                    portfolio[normalized_ticker] = share_count
                    
            except Exception as e:
                print(f"  ⚠️ Skipping row {index} due to error: {e}")
                continue
        
        print(f"3️⃣ FINAL PORTFOLIO DICTIONARY: {portfolio}")
        print("="*40 + "\n")
        return portfolio
    
    except Exception as e:
        print(f"❌ FATAL ERROR IN CSV PARSER: {e}")
        return {}