import os, re

template_dir = r"c:\Users\Lenovo\studyvault\app\templates"

for root, _, files in os.walk(template_dir):
    for fname in files:
        if not fname.endswith('.html'): continue
        filepath = os.path.join(root, fname)
        
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Replace inline backgrounds
        content = re.sub(r'background(?:-color)?\s*:\s*(?:white|#fff|#ffffff|#FFF|#FFFFFF)\s*(!important)?\s*;', 'background: var(--card);', content)
        content = re.sub(r'background(?:-color)?\s*:\s*#f5f7fa\s*(!important)?\s*;', 'background: var(--bg);', content)
        content = re.sub(r'background(?:-color)?\s*:\s*#f9f9f9\s*(!important)?\s*;', 'background: var(--card);', content)
        
        # Replace text colors
        content = re.sub(r'color\s*:\s*(?:black|#000|#000000|#333|#333333)\s*(!important)?\s*;', 'color: var(--text);', content)
        content = re.sub(r'color\s*:\s*(?:#666|#666666|#999|#999999|#777|#888|#888888|#777777)\s*(!important)?\s*;', 'color: var(--muted);', content)
        
        # Also remove inline background-color: white if missing a semicolon
        content = re.sub(r'background(?:-color)?\s*:\s*(?:white|#fff|#ffffff|#FFF|#FFFFFF)\s*(!important)?(["\'])', r'background: var(--card)\2', content)
        content = re.sub(r'color\s*:\s*(?:black|#000|#000000|#333|#333333)\s*(!important)?(["\'])', r'color: var(--text)\2', content)
        
        # Ensure cards, tables, rows, badges, notification panels use dark mode
        # By replacing classes or adding styles? The CSS script already changed CSS variables,
        # so any class like .card, .table, etc. that previously had background: white in CSS now uses var(--card)
        # Any inline style in HTML will be caught above.

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

print("HTML replacement done.")
