document.addEventListener('DOMContentLoaded', () => {
    const toggleBtn = document.getElementById('themeToggle');
    const body = document.body;

    // Function to check and apply theme
    const applyTheme = (theme) => {
        if (theme === 'dark') {
            body.classList.add('dark-mode');
            body.setAttribute('data-theme', 'dark');
            if (toggleBtn) {
                toggleBtn.innerHTML = '<span class="icon">☀️</span>';
                toggleBtn.title = "Switch to Light Mode";
            }
        } else {
            body.classList.remove('dark-mode');
            body.setAttribute('data-theme', 'light');
            if (toggleBtn) {
                toggleBtn.innerHTML = '<span class="icon">🌙</span>';
                toggleBtn.title = "Switch to Dark Mode";
            }
        }
    };

    // Determine initial theme: priority is localStorage > system preference > default light
    const getPreferredTheme = () => {
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme) {
            return savedTheme;
        }
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    };

    // Apply initial theme
    applyTheme(getPreferredTheme());

    // Listen for system theme changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
        // Only auto-switch if user hasn't manually set a preference
        if (!localStorage.getItem('theme')) {
            applyTheme(e.matches ? 'dark' : 'light');
        }
    });

    // Toggle event
    if (toggleBtn) {
        toggleBtn.addEventListener('click', (e) => {
            e.preventDefault();
            const currentTheme = body.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            localStorage.setItem('theme', newTheme);
            applyTheme(newTheme);
        });
    }
});
