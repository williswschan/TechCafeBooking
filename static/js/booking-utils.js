// TechCafeBooking - Booking Utilities
// Core booking and device management functions

// Device ID management
function getOrCreateDeviceId() {
    let deviceId = localStorage.getItem('deviceId');
    if (!deviceId) {
        const timestamp = Date.now();
        const random = Math.random().toString(36).substr(2, 9);
        const userAgent = navigator.userAgent.substr(0, 50);
        deviceId = 'device_' + timestamp + '_' + random + '_' + btoa(userAgent).substr(0, 10);
        localStorage.setItem('deviceId', deviceId);
    }
    return deviceId;
}
