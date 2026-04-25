import os, re

css_dir = r"c:\Users\Lenovo\studyvault\app\static\css"
files_to_process = ["student.css", "faculty.css", "admin.css", "auth.css", "theme_toggle.css"]

# Add the requested variables to theme_toggle.css
theme_file = os.path.join(css_dir, "theme_toggle.css")
if os.path.exists(theme_file):
    with open(theme_file, "r", encoding="utf-8") as f:
        theme_content = f.read()

    variables_block = """/* Required Dark Mode Variables */
:root {
  --bg: #f5f7fa;
  --text: #333333;
  --card: #ffffff;
  --muted: #6b7280;
}

[data-theme="dark"], .dark, body.dark-mode {
  --bg: #0f172a;
  --text: #e2e8f0;
  --card: #1e293b;
  --muted: #94a3b8;
}

"""
    if ":root {" in theme_content and "--bg:" not in theme_content:
        theme_content = variables_block + theme_content
        with open(theme_file, "w", encoding="utf-8") as f:
            f.write(theme_content)

for fname in files_to_process:
    filepath = os.path.join(css_dir, fname)
    if not os.path.exists(filepath): continue
    
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Replace white backgrounds
    content = re.sub(r"background(?:-color)?\s*:\s*(?:white|#fff|#ffffff|#FFF|#FFFFFF)\s*(!important)?;", r"background: var(--card) \1;", content)
    # Replace background: #f5f7fa (body bg)
    content = re.sub(r"background(?:-color)?\s*:\s*#f5f7fa\s*(!important)?;", r"background: var(--bg) \1;", content)
    # Replace background: #f9f9f9 (upload area, cards bg etc)
    content = re.sub(r"background(?:-color)?\s*:\s*#f9f9f9\s*(!important)?;", r"background: var(--card) \1;", content)
    
    # Replace text colors
    content = re.sub(r"color\s*:\s*(?:black|#000|#000000|#333|#333333)\s*(!important)?;", r"color: var(--text) \1;", content)
    
    # Replace low contrast text colors
    content = re.sub(r"color\s*:\s*(?:#666|#666666|#999|#999999|#777|#888|#888888|#777777)\s*(!important)?;", r"color: var(--muted) \1;", content)
    
    # Replace rgba text
    content = re.sub(r"color\s*:\s*rgba\(\s*0\s*,\s*0\s*,\s*0\s*,\s*[0-9.]+\s*\)\s*(!important)?;", r"color: var(--text) \1;", content)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
print("CSS replacement done.")
