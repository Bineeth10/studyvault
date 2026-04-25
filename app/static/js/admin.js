// Admin Module JavaScript
document.addEventListener('DOMContentLoaded', () => {
    console.log('Admin Module Initialized');

    // Bell Toggle Logic
    const bellBtn = document.getElementById('bellBtn');
    const notifDropdown = document.getElementById('notifDropdown');

    if (bellBtn && notifDropdown) {
        bellBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            notifDropdown.classList.toggle('show');
        });

        // Close when clicking outside
        document.addEventListener('click', (e) => {
            if (!notifDropdown.contains(e.target) && e.target !== bellBtn) {
                notifDropdown.classList.remove('show');
            }
        });
    }
});

// Mark notification as read
async function markRead(notifId, element) {
    const formData = new URLSearchParams();
    formData.append('notif_id', notifId);

    try {
        const response = await fetch('/admin/notifications/mark-read', {
            method: 'POST',
            body: formData
        });

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
            }
        }
    } catch (err) {
        console.error('Error marking notification read:', err);
    }
}

async function markAllRead() {
    try {
        const response = await fetch('/admin/notifications/mark-all-read', {
            method: 'POST'
        });

        if (response.ok) {
            document.querySelectorAll('.notif-item.unread-item').forEach(item => {
                item.classList.remove('unread-item');
                const dot = item.querySelector('.unread-dot');
                if (dot) dot.remove();
            });
            const badge = document.querySelector('.unread-badge');
            if (badge) badge.remove();
        }
    } catch (err) {
        console.error('Error marking all as read:', err);
    }
}
