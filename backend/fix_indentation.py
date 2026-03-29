import re

# Read the file
with open('logic/metrics.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix pattern: else: followed by only commented print and then code at lower indent
# Replace with else: followed by commented print and pass
pattern = r'(else:)\s*\n(\s*)(# print\([^)]+\))\s*\n(?=\s{0,' + r'}\S)'

def add_pass(match):
    indent = match.group(2)
    return f"{match.group(1)}\n{indent}{match.group(3)}\n{indent}pass\n"

# This won't work perfectly with regex, so let's do it line by line
lines = content.split('\n')
fixed_lines = []
i = 0

while i < len(lines):
    line = lines[i]
    fixed_lines.append(line)
    
    # Check if line ends with colon
    if line.rstrip().endswith(':'):
        # Check if next line exists and is only a commented print
        if i + 1 < len(lines):
            next_line = lines[i + 1]
            stripped = next_line.strip()
            
            if stripped.startswith('# print(') and stripped.endswith(')'):
                # Get the indentation of the next line
                indent = len(next_line) - len(next_line.lstrip())
                
                # Check if the line after that has less or equal indentation (meaning the block is empty)
                if i + 2 < len(lines):
                    line_after = lines[i + 2]
                    if line_after.strip():  # Not empty
                        indent_after = len(line_after) - len(line_after.lstrip())
                        if indent_after <= indent:
                            # Need to add pass after the commented print
                            fixed_lines.append(next_line)
                            fixed_lines.append(' ' * indent + 'pass')
                            i += 2
                            continue
    
    i += 1

# Write back
with open('logic/metrics.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(fixed_lines))

print("Fixed indentation errors")
