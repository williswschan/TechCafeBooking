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

# Load display names from file (cached in memory for performance)
display_names = []

def load_display_names():
    """Load display names from display_name.txt file"""
    global display_names
    try:
        with open('display_name.txt', 'r', encoding='utf-8') as f:
            display_names = [line.strip() for line in f.readlines() if line.strip()]
        logger.info(f"Loaded {len(display_names)} display names")
    except FileNotFoundError:
        logger.warning("display_name.txt not found, using empty list")
        display_names = []
    except Exception as e:
        logger.error(f"Error loading display names: {e}")
        display_names = []

# Load names at startup
load_display_names()

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

@app.route('/get_names', methods=['GET'])
def get_names():
    """API endpoint to get all display names for type-ahead functionality"""
    return jsonify({'success': True, 'names': display_names})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
