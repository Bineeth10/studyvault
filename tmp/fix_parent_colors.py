import os, re

dirs_to_check = [r'c:\Users\Lenovo\studyvault\app\static\css', r'c:\Users\Lenovo\studyvault\app\templates']

for d in dirs_to_check:
    for root, _, files in os.walk(d):
        for fname in files:
            if not (fname.endswith('.css') or fname.endswith('.html')): continue
            filepath = os.path.join(root, fname)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Replace #f5f5f5 background with var(--card) or var(--bg)
            content = re.sub(r'background(?:-color)?\s*:\s*#f5f5f5\s*(!important)?\s*;', 'background: var(--bg);', content)
            content = re.sub(r'background(?:-color)?\s*:\s*#f5f7fa\s*(!important)?\s*;', 'background: var(--bg);', content)
            
            # Replace remaining white text backgrounds missing semicola
            content = re.sub(r'background(?:-color)?\s*:\s*(?:white|#fff|#ffffff|#FFF|#FFFFFF)\s*(!important)?(["\'])', r'background: var(--card)\2', content)
            content = re.sub(r'background(?:-color)?\s*:\s*#f5f5f5\s*(!important)?(["\'])', r'background: var(--bg)\2', content)
            
            # Replace very light grey text or faded text with var(--text) or var(--muted)
            content = re.sub(r'color\s*:\s*#aaa(?!a)\s*(!important)?\s*;', 'color: var(--muted);', content)
            content = re.sub(r'color\s*:\s*#bbb(?!b)\s*(!important)?\s*;', 'color: var(--muted);', content)
            content = re.sub(r'color\s*:\s*rgba\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*,\s*0\.[1-9]+\s*\)\s*(!important)?\s*;', 'color: var(--muted);', content)

            if content != original_content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)

print('Background & text replacement complete.')
