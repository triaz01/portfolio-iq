import os
import re

# Files to modify
files = [
    'logic/extractor.py',
    'logic/metrics.py',
    'logic/ips_engine.py'
]

for filepath in files:
    if not os.path.exists(filepath):
        print(f"Skipping {filepath} - not found")
        continue
    
    print(f"Processing {filepath}...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Comment out all print statements
    # Match print(...) including multiline
    modified_content = re.sub(
        r'^(\s*)print\(',
        r'\1# print(',
        content,
        flags=re.MULTILINE
    )
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(modified_content)
    
    print(f"  Disabled print statements in {filepath}")

print("\nDone! All print statements have been commented out.")
