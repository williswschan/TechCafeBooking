from flask import Flask, render_template, render_template_string, request, jsonify
from datetime import datetime, timedelta
import json
import os
import logging
import csv

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Persistent storage for bookings using JSON file
BOOKINGS_FILE = 'bookings.json'
bookings = {}

def load_bookings():
    """Load bookings from JSON file"""
    global bookings
    try:
        if os.path.exists(BOOKINGS_FILE):
            with open(BOOKINGS_FILE, 'r', encoding='utf-8') as f:
                bookings = json.load(f)
            logger.info(f"Loaded {len(bookings)} bookings from {BOOKINGS_FILE}")
        else:
            bookings = {}
            logger.info("No existing bookings file found, starting with empty bookings")
    except Exception as e:
        logger.error(f"Error loading bookings: {e}")
        bookings = {}

def save_bookings():
    """Save bookings to JSON file"""
    try:
        with open(BOOKINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(bookings, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved {len(bookings)} bookings to {BOOKINGS_FILE}")
    except Exception as e:
        logger.error(f"Error saving bookings: {e}")

def extract_booking_to_csv(slot_key, booking, reason="completed"):
    """Extract a single booking to CSV file (append to date-specific file)"""
    try:
        # Parse slot_key to get date and time
        date_str, time_str = slot_key.split('_')
        
        # Create filename with just date
        filename = f"bookings_{date_str}.csv"
        
        # Check if file exists to determine if we need to write header
        file_exists = os.path.exists(filename)
        
        # Append to CSV file
        with open(filename, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header only if file doesn't exist
            if not file_exists:
                writer.writerow(['Date', 'Time', 'Username', 'Device ID', 'Booked At', 'Extracted At', 'Reason'])
            
            # Write data
            writer.writerow([
                date_str,
                time_str,
                booking.get('username', ''),
                booking.get('device_id', ''),
                booking.get('booked_at', ''),
                datetime.now().isoformat(),
                reason
            ])
        
        logger.info(f"Extracted booking {slot_key} to {filename}")
        return {'success': True, 'filename': filename}
        
    except Exception as e:
        logger.error(f"Error extracting booking to CSV: {e}")
        return {'success': False, 'error': str(e)}


# Load existing bookings on startup
load_bookings()

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
    """Get next 3 business days, skipping weekends (including today if it's a weekend)"""
    today = datetime.now().date()
    dates = []
    current_date = today
    days_added = 0
    
    # Find the next 3 business days (skip weekends)
    while days_added < 3:
        # Skip Saturday (5) and Sunday (6)
        if current_date.weekday() not in [5, 6]:
            dates.append({
                'date': current_date.strftime("%Y-%m-%d"),
                'display': f"{current_date.strftime('%d (%a)')}<br>{current_date.strftime('%b %y')}",
                'short': current_date.strftime("%a %b")
            })
            days_added += 1
        
        # Move to next day
        current_date += timedelta(days=1)
    
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
    
    # Save to file
    save_bookings()
    
    return jsonify({'success': True, 'message': 'Booking confirmed'})

@app.route('/cancel', methods=['POST'])
def cancel_booking():
    data = request.get_json()
    date = data.get('date')
    time = data.get('time')
    device_id = data.get('device_id')
    is_admin = data.get('is_admin', False)
    reason = data.get('reason', 'cancelled')  # Default to 'cancelled', can be 'completed' for admin
    
    if not all([date, time, device_id]):
        return jsonify({'success': False, 'message': 'Missing required fields'})
    
    slot_key = f"{date}_{time}"
    
    if slot_key not in bookings:
        return jsonify({'success': False, 'message': 'No booking found for this slot'})
    
    # Check if the device making the cancellation is the same as the one that made the booking OR if it's an admin
    if bookings[slot_key]['device_id'] != device_id and not is_admin:
        return jsonify({'success': False, 'message': 'You can only cancel your own bookings'})
    
    # Extract booking to CSV before deleting
    booking = bookings[slot_key]
    csv_result = extract_booking_to_csv(slot_key, booking, reason)
    
    # Delete the booking
    del bookings[slot_key]
    
    # Save to file
    save_bookings()
    
    # Return success with CSV extraction info
    response = {'success': True, 'message': 'Booking cancelled'}
    if csv_result['success']:
        response['csv_extracted'] = True
        response['csv_filename'] = csv_result['filename']
    else:
        response['csv_extracted'] = False
        response['csv_error'] = csv_result['error']
    
    return jsonify(response)

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

@app.route('/get_current_dates', methods=['GET'])
def get_current_dates():
    """API endpoint to get current available dates (for day change detection)"""
    dates = get_available_dates()
    return jsonify({'success': True, 'dates': dates})

@app.route('/get_current_time', methods=['GET'])
def get_current_time():
    """API endpoint to get current server time for time visualization"""
    now = datetime.now()
    return jsonify({
        'success': True,
        'time': {
            'hours': now.hour,
            'minutes': now.minute,
            'seconds': now.second,
            'total_minutes': now.hour * 60 + now.minute,
            'iso_string': now.isoformat()
        }
    })

@app.route('/extract_booking', methods=['POST'])
def extract_booking():
    """API endpoint to extract a single booking to CSV"""
    data = request.get_json()
    slot_key = data.get('slot_key')
    reason = data.get('reason', 'extracted')
    
    if not slot_key:
        return jsonify({'success': False, 'error': 'Missing slot_key'})
    
    if slot_key not in bookings:
        return jsonify({'success': False, 'error': 'Booking not found'})
    
    # Extract booking to CSV
    booking = bookings[slot_key]
    csv_result = extract_booking_to_csv(slot_key, booking, reason)
    
    # Remove booking from memory after successful extraction
    if csv_result['success']:
        del bookings[slot_key]
        save_bookings()
    
    return jsonify(csv_result)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
