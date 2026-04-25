import os

theme_file = r"c:\Users\Lenovo\studyvault\app\static\css\theme_toggle.css"

override_css = """
/* HIGH SPECIFICITY ROOT DARK MODE AND HEADER OVERRIDES */
html.dark body, 
html[data-theme="dark"] body,
body.dark,
body.dark-mode {
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

html.dark .topbar, html[data-theme="dark"] .topbar, body.dark-mode .topbar,
html.dark .bg-light, html[data-theme="dark"] .bg-light, body.dark-mode .bg-light,
html.dark .card-header, html[data-theme="dark"] .card-header, body.dark-mode .card-header,
html.dark .guide-bar, html[data-theme="dark"] .guide-bar, body.dark-mode .guide-bar,
html.dark .header-box, html[data-theme="dark"] .header-box, body.dark-mode .header-box,
html.dark .top-section, html[data-theme="dark"] .top-section, body.dark-mode .top-section,
html.dark .header-wrapper, html[data-theme="dark"] .header-wrapper, body.dark-mode .header-wrapper,
html.dark header, html[data-theme="dark"] header, body.dark-mode header,
html.dark .navbar, html[data-theme="dark"] .navbar, body.dark-mode .navbar {
    background-color: var(--card) !important;
    color: var(--text) !important;
    border-color: var(--border-color, #475569) !important;
}

/* OVERRIDE ALL INLINE BACKGROUNDS IN DARK MODE (USE CAREFULLY) */
html.dark div[style*="background"], 
html[data-theme="dark"] div[style*="background"], 
body.dark-mode div[style*="background"],
html.dark section[style*="background"], 
html[data-theme="dark"] section[style*="background"], 
body.dark-mode section[style*="background"] {
    background-color: var(--card) !important;
    color: var(--text) !important;
}

/* KEEP BADGES FROM GETTING OBLITERATED BY DIV[STYLE] RESET IF THEY ARE DIVS */
html.dark div.badge[style*="background"], 
html[data-theme="dark"] div.badge[style*="background"], 
body.dark-mode div.badge[style*="background"] {
    background-color: transparent !important; /* let specific badge rules take over */
}
"""

with open(theme_file, 'a', encoding='utf-8') as f:
    f.write(override_css)

print("High specificity fixes applied.")
