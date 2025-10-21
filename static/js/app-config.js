// TechCafeBooking - Application Configuration
// Version: 3.9

// Version management functions
function getCurrentVersion() {
    // Get version from global variable set by template
    return window.APP_VERSION || "3.9";
}

function incrementVersion() {
    const versionParts = getCurrentVersion().split('.');
    const major = parseInt(versionParts[0]);
    const minor = parseFloat(versionParts[1]) + 0.1;
    return `${major}.${minor.toFixed(1)}`;
}

// Logging functions
function errorLog(message, ...args) {
    console.error(message, ...args);
}

// Browser configuration utilities
function updateBrowserConfig() {
    const configElement = document.getElementById('browserConfig');
    if (configElement) {
        const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
        const screenInfo = `${window.innerWidth}x${window.innerHeight}`;
        const deviceType = isMobile ? 'Mobile' : 'Desktop';
        configElement.textContent = `${deviceType} - ${screenInfo}`;
    }
}

// Text processing utilities
function highlightText(text, query) {
    if (!query) return text;
    const regex = new RegExp(`(${query})`, 'gi');
    return text.replace(regex, '<mark>$1</mark>');
}

// Notification utilities
function checkNotificationLimit() {
    const maxNotifications = 3;
    const notifications = document.querySelectorAll('.toast-notification');
    
    if (notifications.length >= maxNotifications) {
        // Remove oldest notification (first in the list)
        const oldestNotification = notifications[0];
        if (oldestNotification) {
            oldestNotification.remove();
        }
    }
}

// Make function globally available
window.checkNotificationLimit = checkNotificationLimit;
