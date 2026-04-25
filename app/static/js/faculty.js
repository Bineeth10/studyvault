/* Faculty JS - StudyVault */

document.addEventListener('DOMContentLoaded', () => {
    console.log('Faculty Module Initialized');

    // Confirm deletions
    const deleteBtns = document.querySelectorAll('.btn-delete');
    deleteBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            if (!confirm('Are you sure you want to delete this?')) {
                e.preventDefault();
            }
        });
    });

    // Auto-dismiss alerts
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        }, 3000);
    });

    // Active nav item
    const currentPath = window.location.pathname;
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        if (item.getAttribute('href') === currentPath) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });
    // Notification Side Panel Logic (Drawer)
    const bellBtn = document.getElementById('bellBtn');
    const sideNotifPanel = document.getElementById('sideNotifPanel');
    const closePanel = document.getElementById('closePanel');
    const panelOverlay = document.getElementById('panelOverlay');

    if (bellBtn && sideNotifPanel) {
        bellBtn.addEventListener('click', (e) => {
            e.preventDefault();
            sideNotifPanel.classList.add('active');
            document.body.style.overflow = 'hidden'; // Prevent scrolling
        });

        const closeSidePanel = () => {
            sideNotifPanel.classList.remove('active');
            document.body.style.overflow = ''; // Restore scrolling
        };

        if (closePanel) closePanel.addEventListener('click', closeSidePanel);
        if (panelOverlay) panelOverlay.addEventListener('click', closeSidePanel);

        // ESC key to close
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') closeSidePanel();
        });
    }
});

// ── Toast helper ───────────────────────────────────────────────────
function showFacToast(message, type = 'success') {
    const existing = document.getElementById('fac-notif-toast');
    if (existing) existing.remove();
    const toast = document.createElement('div');
    toast.id = 'fac-notif-toast';
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
    console.log(`[Notifications] Calling POST /faculty/notifications/mark-read for ${notifId}`);
    try {
        const response = await fetch('/faculty/notifications/mark-read', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: `notif_id=${notifId}`
        });
        console.log(`[Notifications] mark-read response: ${response.status}`);

        if (response.ok) {
            if (element) {
                element.classList.remove('unread-item');
                const dot = element.querySelector('.unread-dot');
                if (dot) dot.remove();

                // Update Badge Count
                const badge = document.querySelector('.unread-badge, .sidebar-badge');
                if (badge) {
                    let count = parseInt(badge.innerText);
                    if (count > 0) {
                        count--;
                        if (count === 0) badge.remove();
                        else badge.innerText = count;
                    }
                }
                console.log('[Notifications] UI updated — item marked read');
            } else {
                // Handling for dashboard cards if they still exist
                const card = document.getElementById(`notif-${notifId}`);
                if (card) {
                    card.style.opacity = '0';
                    card.style.transform = 'translateX(20px)';
                    setTimeout(() => card.remove(), 300);
                }
            }
        }
    } catch (err) {
        console.error('[Notifications] mark-read error:', err);
    }
}

async function markAllRead() {
    console.log('[Notifications] Calling POST /faculty/notifications/mark-all-read');
    try {
        const response = await fetch('/faculty/notifications/mark-all-read', { method: 'POST' });
        console.log(`[Notifications] mark-all-read response: ${response.status}`);
        const data = await response.json();
        console.log('[Notifications] mark-all-read data:', data);

        if (response.ok) {
            document.querySelectorAll('.notif-item.unread-item').forEach(item => {
                item.classList.remove('unread-item');
                const dot = item.querySelector('.unread-dot');
                if (dot) dot.remove();
            });
            document.querySelectorAll('.unread-badge, .sidebar-badge').forEach(b => b.remove());
            showFacToast('✓ All notifications marked as read');
            console.log('[Notifications] UI updated — all unread cleared');
        } else {
            showFacToast('Failed to mark all as read', 'error');
        }
    } catch (err) {
        console.error('[Notifications] mark-all-read error:', err);
        showFacToast('Network error', 'error');
    }
}
