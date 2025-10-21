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
