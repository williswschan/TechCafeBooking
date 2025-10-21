from flask import Flask, render_template, render_template_string, request, jsonify, send_file
from datetime import datetime, timedelta
import json
import os
import logging
import csv

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Admin password configuration
ADMIN_PASSWORD = os.getenv('TECHCAFE_ADMIN_PASSWORD', 'Nomura2025!')

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
                writer.writerow(['Date', 'Time', 'Booked By', 'Device ID', 'Booked At', 'Updated At', 'Reason', 'Kiosk'])
            
            # Write data
            writer.writerow([
                date_str,
                time_str,
                booking.get('username', ''),
                booking.get('device_id', ''),
                booking.get('booked_at', ''),
                datetime.now().isoformat(),
                reason,
                'yes' if booking.get('kiosk') else 'no'
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
    # Check if it's a mobile device
    user_agent = request.headers.get('User-Agent', '').lower()
    is_mobile = any(device in user_agent for device in ['iphone', 'ipad', 'android', 'mobile'])
    
    time_slots = get_time_slots()
    morning_slots = [slot for slot in time_slots if 9 <= int(slot.split(':')[0]) < 12]
    afternoon_slots = [slot for slot in time_slots if 14 <= int(slot.split(':')[0]) < 18]
    
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
    kiosk = bool(data.get('kiosk', False))
    
    if not all([date, time, device_id]) or username is None:
        return jsonify({'success': False, 'message': 'Missing required fields'})
    
    
    slot_key = f"{date}_{time}"
    
    if slot_key in bookings:
        return jsonify({'success': False, 'message': 'Slot already booked'})
    
    bookings[slot_key] = {
        'username': username,
        'device_id': device_id,
        'booked_at': datetime.now().isoformat(),
        'kiosk': kiosk
    }
    
    # Extract booking to CSV for logging
    booking = bookings[slot_key]
    csv_result = extract_booking_to_csv(slot_key, booking, "booked")
    
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
    
    # If the booking was made in kiosk mode, only admin can cancel
    if bookings[slot_key].get('kiosk') and not is_admin:
        return jsonify({'success': False, 'message': 'Kiosk bookings can only be cancelled by admin'})

    # Otherwise, require same-device or admin
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

@app.route('/get_server_date')
def get_server_date():
    """Get current server date in YYYY-MM-DD format"""
    current_date = datetime.now().strftime('%Y-%m-%d')
    return jsonify({'date': current_date})

@app.route('/admin')
def admin_page():
    """Admin page with password protection"""
    return render_template('admin.html')

@app.route('/readme')
def readme():
    """Readme page showing usage and features"""
    return render_template('readme.html')

@app.route('/admin/verify', methods=['POST'])
def verify_admin_password():
    """Verify admin password"""
    data = request.get_json()
    password = data.get('password', '').strip()
    
    if password == ADMIN_PASSWORD:
        return jsonify({'success': True, 'message': 'Admin access granted'})
    else:
        return jsonify({'success': False, 'message': 'Invalid admin password'})

@app.route('/admin/download_csv')
def download_csv():
    """Download CSV files - list available CSV files"""
    try:
        csv_files = []
        for filename in os.listdir('.'):
            if filename.startswith('bookings_') and filename.endswith('.csv'):
                file_path = os.path.join('.', filename)
                file_size = os.path.getsize(file_path)
                file_date = os.path.getmtime(file_path)
                
                # Extract date from filename (bookings_YYYY-MM-DD.csv)
                try:
                    date_part = filename.replace('bookings_', '').replace('.csv', '')
                    file_date_from_name = datetime.strptime(date_part, '%Y-%m-%d').date()
                except ValueError:
                    # If date parsing fails, use a very old date as fallback
                    file_date_from_name = datetime(1900, 1, 1).date()
                
                csv_files.append({
                    'filename': filename,
                    'size': file_size,
                    'date': datetime.fromtimestamp(file_date).strftime('%Y-%m-%d %H:%M:%S'),
                    'sort_date': file_date_from_name
                })
        
        # Sort by date in filename (newest first)
        csv_files.sort(key=lambda x: x['sort_date'], reverse=True)
        
        return jsonify({'success': True, 'files': csv_files})
    except Exception as e:
        logger.error(f"Error listing CSV files: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/download_csv/<filename>')
def download_specific_csv(filename):
    """Download a specific CSV file"""
    try:
        # Security check - only allow CSV files that start with 'bookings_'
        if not filename.startswith('bookings_') or not filename.endswith('.csv'):
            return jsonify({'success': False, 'error': 'Invalid file type'})
        
        file_path = os.path.join('.', filename)
        if not os.path.exists(file_path):
            return jsonify({'success': False, 'error': 'File not found'})
        
        return send_file(file_path, as_attachment=True, download_name=filename)
    except Exception as e:
        logger.error(f"Error downloading CSV file {filename}: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/download_bad_words')
def download_bad_words():
    """Download the bad_words.txt file"""
    try:
        file_path = os.path.join('.', 'bad_words.txt')
        
        if not os.path.exists(file_path):
            return jsonify({'success': False, 'error': 'Bad words file not found'})
        
        return send_file(file_path, as_attachment=True, download_name='bad_words.txt')
    except Exception as e:
        logger.error(f"Error downloading bad_words.txt: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/upload_display_names', methods=['POST'])
def upload_display_names():
    """Upload new display_name.txt file"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'})
        
        if file.filename != 'display_name.txt':
            return jsonify({'success': False, 'error': 'File must be named display_name.txt'})
        
        # Save the uploaded file
        file.save('display_name.txt')
        
        # Reload display names
        load_display_names()
        
        return jsonify({
            'success': True, 
            'message': f'Display names updated successfully. Loaded {len(display_names)} names.',
            'count': len(display_names),
            'refresh_required': True  # Signal that client should refresh type-ahead
        })
    except Exception as e:
        logger.error(f"Error uploading display names: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/upload_bad_words', methods=['POST'])
def upload_bad_words():
    """Upload new bad_words.txt file"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'})
        
        if file.filename != 'bad_words.txt':
            return jsonify({'success': False, 'error': 'File must be named bad_words.txt'})
        
        # Save the uploaded file
        file.save('bad_words.txt')
        
        # Count the number of bad words loaded
        try:
            with open('bad_words.txt', 'r', encoding='utf-8') as f:
                bad_words_count = len([line.strip() for line in f if line.strip() and not line.strip().startswith('#')])
        except:
            bad_words_count = 0
        
        return jsonify({
            'success': True, 
            'message': f'Bad words filter updated successfully. Loaded {bad_words_count} words.',
            'count': bad_words_count,
            'refresh_required': True  # Signal that client should refresh bad words
        })
    except Exception as e:
        logger.error(f"Error uploading bad words: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/delete_csv/<filename>', methods=['DELETE'])
def delete_csv(filename):
    """Delete a specific CSV file"""
    try:
        # Security check - only allow CSV files that start with 'bookings_'
        if not filename.startswith('bookings_') or not filename.endswith('.csv'):
            return jsonify({'success': False, 'error': 'Invalid file type'})
        
        file_path = os.path.join('.', filename)
        if not os.path.exists(file_path):
            return jsonify({'success': False, 'error': 'File not found'})
        
        # Delete the file
        os.remove(file_path)
        logger.info(f"Deleted CSV file: {filename}")
        
        return jsonify({'success': True, 'message': f'File "{filename}" deleted successfully'})
    except Exception as e:
        logger.error(f"Error deleting CSV file {filename}: {e}")
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
