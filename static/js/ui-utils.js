// TechCafeBooking - UI Utilities
// UI helper functions and display management

// Display refresh utilities
function refreshDisplay() {
    updateTimeSlots();
}

// Loading state management
function showLoading(show) {
    document.getElementById('loading').style.display = show ? 'block' : 'none';
}

// Make function globally available
window.showLoading = showLoading;
