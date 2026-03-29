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
    
    # Uncomment all print statements
    modified_content = re.sub(
        r'^(\s*)# print\(',
        r'\1print(',
        content,
        flags=re.MULTILINE
    )
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(modified_content)
    
    print(f"  Uncommented print statements in {filepath}")

print("\nDone! All print statements have been uncommented.")
print("Note: Print output will be suppressed by the API using contextlib.redirect_stdout")
