import os, re

template_dir = r"c:\Users\Lenovo\studyvault\app\templates"

for root, _, files in os.walk(template_dir):
    for fname in files:
        if not fname.endswith('.html'): continue
        filepath = os.path.join(root, fname)
        
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Replace inline backgrounds
        original_content = content
        
        content = re.sub(r'background(?:-color)?\s*:\s*#f8fafc\s*(!important)?(["\'])', r'background: var(--card)\2', content)
        content = re.sub(r'background(?:-color)?\s*:\s*#f8fafc\s*(!important)?\s*;', 'background: var(--card);', content)
        
        if content != original_content:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)

print("Forum HTML replacement done.")
