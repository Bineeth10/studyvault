// Student Module JavaScript

// Global utility functions
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 25px;
        background: ${type === 'success' ? '#4caf50' : type === 'error' ? '#f44336' : '#2196f3'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Add animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Auto-hide alerts
document.addEventListener('DOMContentLoaded', () => {
    const alerts = document.querySelectorAll('.alert, .success, .error');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s ease';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });
});

// Confirm before logout
document.addEventListener('DOMContentLoaded', () => {
    const logoutLink = document.querySelector('a[href="/logout"]');
    if (logoutLink) {
        logoutLink.addEventListener('click', (e) => {
            if (!confirm('Are you sure you want to logout?')) {
                e.preventDefault();
            }
        });
    }
});

// Smooth scroll to top button
const scrollTopBtn = document.createElement('button');
scrollTopBtn.innerHTML = '↑';
scrollTopBtn.style.cssText = `
    position: fixed;
    bottom: 30px;
    right: 30px;
    width: 50px;
    height: 50px;
    border-radius: 50%;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    font-size: 1.5em;
    cursor: pointer;
    display: none;
    z-index: 1000;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    transition: all 0.3s ease;
`;

scrollTopBtn.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
});

document.body.appendChild(scrollTopBtn);

window.addEventListener('scroll', () => {
    if (window.scrollY > 300) {
        scrollTopBtn.style.display = 'block';
    } else {
        scrollTopBtn.style.display = 'none';
    }
});

// Form validation helper
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return true;

    const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');
    let isValid = true;

    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.style.borderColor = '#f44336';
            isValid = false;
        } else {
            input.style.borderColor = '#e0e0e0';
        }
    });

    return isValid;
}

// Copy to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Copied to clipboard!', 'success');
    }).catch(() => {
        showNotification('Failed to copy', 'error');
    });
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// Search functionality
function initSearch(inputId, itemsClass) {
    const searchInput = document.getElementById(inputId);
    if (!searchInput) return;

    searchInput.addEventListener('input', (e) => {
        const searchTerm = e.target.value.toLowerCase();
        const items = document.querySelectorAll(`.${itemsClass}`);

        items.forEach(item => {
            const text = item.textContent.toLowerCase();
            item.style.display = text.includes(searchTerm) ? '' : 'none';
        });
    });
}

// Notification Side Panel Logic
document.addEventListener('DOMContentLoaded', () => {
    const bellBtn = document.getElementById('bellBtn');
    const sideNotifPanel = document.getElementById('sideNotifPanel');
    const closePanel = document.getElementById('closePanel');
    const panelOverlay = document.getElementById('panelOverlay');

    if (bellBtn && sideNotifPanel) {
        // Open Panel
        bellBtn.addEventListener('click', (e) => {
            e.preventDefault();
            sideNotifPanel.classList.add('active');
            document.body.style.overflow = 'hidden'; // Prevent background scroll
        });

        // Close functions
        const closeSidePanel = () => {
            sideNotifPanel.classList.remove('active');
            document.body.style.overflow = ''; // Re-enable background scroll
        };

        if (closePanel) closePanel.addEventListener('click', closeSidePanel);
        if (panelOverlay) panelOverlay.addEventListener('click', closeSidePanel);

        // Close on ESC
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && sideNotifPanel.classList.contains('active')) {
                closeSidePanel();
            }
        });
    }
});

// ── Toast helper (used by notification functions) ──────────────────────────
function showNotifToast(message, type = 'success') {
    const existing = document.getElementById('sv-notif-toast');
    if (existing) existing.remove();
    const toast = document.createElement('div');
    toast.id = 'sv-notif-toast';
    toast.textContent = message;
    toast.style.cssText = `
        position:fixed;top:24px;right:24px;z-index:99999;
        padding:14px 22px;border-radius:10px;font-weight:600;
        background:${type==='success'?'#2ecc71':type==='error'?'#e74c3c':'#3498db'};
        color:white;box-shadow:0 6px 20px rgba(0,0,0,0.25);
    `;
    document.body.appendChild(toast);
    setTimeout(() => { toast.style.opacity='0'; toast.style.transition='opacity 0.4s'; setTimeout(()=>toast.remove(),450); }, 3000);
}

// Mark notification as read
async function markRead(notifId, element) {
    console.log(`[Notifications] Calling POST /student/notifications/mark-read for ${notifId}`);
    const formData = new URLSearchParams();
    formData.append('notif_id', notifId);

    try {
        const response = await fetch('/student/notifications/mark-read', {
            method: 'POST',
            body: formData
        });
        console.log(`[Notifications] mark-read response: ${response.status}`);

        if (response.ok) {
            if (element) {
                element.classList.remove('unread-item');
                const dot = element.querySelector('.unread-dot');
                if (dot) dot.remove();

                // Update Badge Count
                const badge = document.querySelector('.unread-badge');
                if (badge) {
                    let count = parseInt(badge.innerText);
                    if (count > 0) {
                        count--;
                        if (count === 0) badge.remove();
                        else badge.innerText = count;
                    }
                }
                console.log('[Notifications] UI updated — item marked read');
            }
        }
    } catch (err) {
        console.error('[Notifications] mark-read error:', err);
    }
}

async function markAllRead() {
    console.log('[Notifications] Calling POST /student/notifications/mark-all-read');
    try {
        const response = await fetch('/student/notifications/mark-all-read', { method: 'POST' });
        console.log(`[Notifications] mark-all-read response: ${response.status}`);
        const data = await response.json();
        console.log('[Notifications] mark-all-read data:', data);

        if (response.ok) {
            document.querySelectorAll('.notif-item.unread-item').forEach(item => {
                item.classList.remove('unread-item');
                const dot = item.querySelector('.unread-dot');
                if (dot) dot.remove();
            });
            document.querySelectorAll('.unread-badge').forEach(b => b.remove());
            showNotifToast('✓ All notifications marked as read');
            console.log('[Notifications] UI updated — all unread cleared');
        } else {
            showNotifToast('Failed to mark all as read', 'error');
        }
    } catch (err) {
        console.error('[Notifications] mark-all-read error:', err);
        showNotifToast('Network error', 'error');
    }
}
