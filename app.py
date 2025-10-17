from flask import Flask, render_template, render_template_string, request, jsonify
from datetime import datetime, timedelta
import json
import os
import logging

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory storage for bookings (in production, use a database)
bookings = {}

def get_time_slots():
    """Generate time slots from 09:00 to 18:00 with 15-minute intervals, excluding lunch hours (12:00-14:00)"""
    slots = []
    start_time = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
    lunch_start = datetime.now().replace(hour=12, minute=0, second=0, microsecond=0)
    lunch_end = datetime.now().replace(hour=14, minute=0, second=0, microsecond=0)
    end_time = datetime.now().replace(hour=18, minute=0, second=0, microsecond=0)
    
    # Morning slots (09:00-12:00)
    current_time = start_time
    while current_time < lunch_start:
        slots.append(current_time.strftime("%H:%M"))
        current_time += timedelta(minutes=15)
    
    # Afternoon slots (14:00-18:00)
    current_time = lunch_end
    while current_time < end_time:
        slots.append(current_time.strftime("%H:%M"))
        current_time += timedelta(minutes=15)
    
    return slots

def get_available_dates():
    """Get today, tomorrow, and day after tomorrow"""
    today = datetime.now().date()
    dates = []
    for i in range(3):
        date = today + timedelta(days=i)
        dates.append({
            'date': date.strftime("%Y-%m-%d"),
            'display': date.strftime("%A, %B %d"),
            'short': date.strftime("%a %d")
        })
    return dates

@app.route('/')
def index():
    logger.info("=== INDEX ROUTE CALLED ===")
    logger.info(f"Request headers: {dict(request.headers)}")
    logger.info(f"User agent: {request.headers.get('User-Agent', 'Unknown')}")
    logger.info(f"Request method: {request.method}")
    logger.info(f"Request URL: {request.url}")
    
    # Check if it's a mobile device
    user_agent = request.headers.get('User-Agent', '').lower()
    is_mobile = any(device in user_agent for device in ['iphone', 'ipad', 'android', 'mobile'])
    logger.info(f"Mobile device detected: {is_mobile}")
    
    time_slots = get_time_slots()
    morning_slots = [slot for slot in time_slots if 9 <= int(slot.split(':')[0]) < 12]
    afternoon_slots = [slot for slot in time_slots if 14 <= int(slot.split(':')[0]) < 18]
    
    logger.info(f"Generated {len(time_slots)} time slots")
    logger.info(f"Morning slots: {len(morning_slots)}")
    logger.info(f"Afternoon slots: {len(afternoon_slots)}")
    
    return render_template('index.html', 
                         time_slots=time_slots,
                         morning_slots=morning_slots,
                         afternoon_slots=afternoon_slots,
                         dates=get_available_dates())

@app.route('/book', methods=['POST'])
def book_slot():
    data = request.get_json()
    date = data.get('date')
    time = data.get('time')
    username = data.get('username')
    device_id = data.get('device_id')
    
    if not all([date, time, device_id]) or username is None:
        return jsonify({'success': False, 'message': 'Missing required fields'})
    
    slot_key = f"{date}_{time}"
    
    if slot_key in bookings:
        return jsonify({'success': False, 'message': 'Slot already booked'})
    
    bookings[slot_key] = {
        'username': username,
        'device_id': device_id,
        'booked_at': datetime.now().isoformat()
    }
    
    return jsonify({'success': True, 'message': 'Booking confirmed'})

@app.route('/cancel', methods=['POST'])
def cancel_booking():
    data = request.get_json()
    date = data.get('date')
    time = data.get('time')
    device_id = data.get('device_id')
    is_admin = data.get('is_admin', False)
    
    if not all([date, time, device_id]):
        return jsonify({'success': False, 'message': 'Missing required fields'})
    
    slot_key = f"{date}_{time}"
    
    if slot_key not in bookings:
        return jsonify({'success': False, 'message': 'No booking found for this slot'})
    
    # Check if the device making the cancellation is the same as the one that made the booking OR if it's an admin
    if bookings[slot_key]['device_id'] != device_id and not is_admin:
        return jsonify({'success': False, 'message': 'You can only cancel your own bookings'})
    
    del bookings[slot_key]
    return jsonify({'success': True, 'message': 'Booking cancelled'})

@app.route('/get_bookings', methods=['GET', 'POST'])
def get_bookings():
    # Try to get date from both args and form data
    date = request.args.get('date') or request.form.get('date')
    
    if not date:
        return jsonify({'success': False, 'message': 'Date required'})
    
    date_bookings = {}
    for slot_key, booking in bookings.items():
        if slot_key.startswith(date):
            time = slot_key.split('_')[1]
            date_bookings[time] = booking
    
    return jsonify({'success': True, 'bookings': date_bookings})


@app.route('/test')
def test_page():
    return render_template_string('''
<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body>
    <h1>Test Page</h1>
    <button onclick="test()">Click Me</button>
    <div id="result"></div>
    <script>
        function test() {
            document.getElementById('result').innerHTML = 'Working!';
            alert('JavaScript working!');
        }
        alert('Page loaded!');
    </script>
</body>
</html>
    ''')

@app.route('/minimal')
def minimal_test():
    return render_template_string('''
<!DOCTYPE html>
<html>
<head><title>Minimal Test</title></head>
<body>
    <h1>Minimal Click Test</h1>
    <div class="time-slot" data-time="09:00" style="width:100px;height:50px;background:lightblue;margin:10px;cursor:pointer;display:inline-block;text-align:center;line-height:50px;border:2px solid blue;">09:00</div>
    <div class="time-slot" data-time="09:15" style="width:100px;height:50px;background:lightblue;margin:10px;cursor:pointer;display:inline-block;text-align:center;line-height:50px;border:2px solid blue;">09:15</div>
    
    <script>
        alert('Script starting...');
        
        document.addEventListener('click', function(e) {
            alert('Click detected on: ' + e.target.tagName);
            if (e.target.classList.contains('time-slot')) {
                const time = e.target.getAttribute('data-time');
                alert('Time slot clicked: ' + time);
            }
        });
        
        alert('Script loaded completely');
    </script>
</body>
</html>
    ''')

@app.route('/test-portrait')
def test_portrait():
    with open('test_portrait.html', 'r') as f:
        return f.read()

@app.route('/debug')
def debug_page():
    return render_template_string('''
<!DOCTYPE html>
<html>
<head><title>Debug Test</title></head>
<body>
    <h1>Debug Test - Portrait Mode Fixes</h1>
    <div id="admin-btn" class="admin-btn" style="position:absolute;top:20px;right:20px;background:red;color:white;padding:10px;border-radius:5px;">
        <i class="fas fa-user-shield"></i>
        <span>Admin</span>
    </div>
    
    <div style="margin-top:100px;">
        <h2>Time Slots Test</h2>
        <div class="time-slot" data-time="09:00" style="width:100px;height:50px;background:lightblue;margin:10px;cursor:pointer;display:inline-block;text-align:center;line-height:50px;border:2px solid blue;">09:00</div>
        <div class="time-slot" data-time="09:15" style="width:100px;height:50px;background:lightblue;margin:10px;cursor:pointer;display:inline-block;text-align:center;line-height:50px;border:2px solid blue;">09:15</div>
        <div class="time-slot" data-time="09:30" style="width:100px;height:50px;background:lightblue;margin:10px;cursor:pointer;display:inline-block;text-align:center;line-height:50px;border:2px solid blue;">09:30</div>
    </div>
    
    <div id="status" style="margin-top:20px;padding:10px;background:#f0f0f0;"></div>
    
    <script>
        function forcePortraitFixes() {
            document.getElementById('status').innerHTML += '<p>🔧 FORCE PORTRAIT FIXES FUNCTION IS RUNNING 🔧</p>';
            
            // Force Admin button to be circular
            const adminBtn = document.getElementById('admin-btn');
            if (adminBtn) {
                document.getElementById('status').innerHTML += '<p>Admin button found: true</p>';
                adminBtn.style.width = '50px';
                adminBtn.style.height = '50px';
                adminBtn.style.borderRadius = '50%';
                adminBtn.style.padding = '0';
                adminBtn.style.display = 'flex';
                adminBtn.style.alignItems = 'center';
                adminBtn.style.justifyContent = 'center';
                
                // Hide text
                const adminText = adminBtn.querySelector('span');
                if (adminText) {
                    adminText.style.display = 'none';
                    document.getElementById('status').innerHTML += '<p>Admin text hidden</p>';
                }
                
                document.getElementById('status').innerHTML += '<p>Admin button styled as circular</p>';
            } else {
                document.getElementById('status').innerHTML += '<p>ERROR: Admin button not found!</p>';
            }
            
            // Force time slot height calculation
            const allTimeSlots = document.querySelectorAll('.time-slot');
            document.getElementById('status').innerHTML += '<p>Found time slots: ' + allTimeSlots.length + '</p>';
            
            allTimeSlots.forEach((slot, index) => {
                slot.style.width = '120px';
                slot.style.height = '80px';
                slot.style.minHeight = '80px';
                document.getElementById('status').innerHTML += '<p>Slot ' + index + ' styled: ' + slot.dataset.time + '</p>';
            });
        }
        
        // Run the function immediately
        document.getElementById('status').innerHTML += '<p>Page loaded, running forcePortraitFixes()...</p>';
        forcePortraitFixes();
        
        // Also run it after a delay
        setTimeout(() => {
            document.getElementById('status').innerHTML += '<p>Running forcePortraitFixes() after delay...</p>';
            forcePortraitFixes();
        }, 1000);
    </script>
</body>
</html>
    ''')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
