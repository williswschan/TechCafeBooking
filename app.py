from flask import Flask, render_template, render_template_string, request, jsonify, send_file
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_socketio import SocketIO, emit, join_room, leave_room
from datetime import datetime, timedelta
import json
import os
import logging
import csv
import re
import bleach

app = Flask(__name__)

# Disable all caching for immediate changes
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.jinja_env.auto_reload = True

# Initialize SocketIO for real-time updates
socketio = SocketIO(app, cors_allowed_origins="*")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure CSRF protection
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'techcafe-booking-secret-key-2025')
app.config['WTF_CSRF_ENABLED'] = False  # Temporarily disabled for testing
app.config['WTF_CSRF_TIME_LIMIT'] = 3600  # 1 hour

# Initialize security components
# csrf = CSRFProtect(app)  # Temporarily disabled
csrf = None
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["10000 per hour", "5000 per minute"]
)
limiter.init_app(app)

# Admin password configuration
ADMIN_PASSWORD = os.getenv('TECHCAFE_ADMIN_PASSWORD', 'Nomura2025!')

# Application version - update this when making changes
APP_VERSION = "3.9"

# Debug mode for client-side logging (set to False in production)
DEBUG_MODE = os.getenv('TECHCAFE_DEBUG', 'false').lower() == 'true'

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

# WebSocket event handlers for real-time updates
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info(f"Client connected: {request.sid}")
    emit('connected', {'message': 'Connected to real-time updates'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info(f"Client disconnected: {request.sid}")

@socketio.on('join_date')
def handle_join_date(data):
    """Join a specific date room for real-time updates"""
    date = data.get('date')
    if date:
        join_room(f"date_{date}")
        logger.info(f"Client {request.sid} joined date room: {date}")
        emit('joined_date', {'date': date})

@socketio.on('leave_date')
def handle_leave_date(data):
    """Leave a specific date room"""
    date = data.get('date')
    if date:
        leave_room(f"date_{date}")
        logger.info(f"Client {request.sid} left date room: {date}")

def broadcast_booking_update(date, slot_key, booking_data, action='update'):
    """Broadcast booking update to all clients viewing this date"""
    room = f"date_{date}"
    socketio.emit('booking_update', {
        'date': date,
        'slot_key': slot_key,
        'booking_data': booking_data,
        'action': action  # 'book', 'cancel', 'update'
    }, room=room)
    logger.info(f"Broadcasted {action} for {slot_key} on {date} to room {room}")

def broadcast_time_update():
    """Broadcast current time to all connected clients"""
    now = datetime.now()
    time_data = {
        'hours': now.hour,
        'minutes': now.minute,
        'seconds': now.second,
        'total_minutes': now.hour * 60 + now.minute,
        'iso_string': now.isoformat()
    }
    socketio.emit('time_update', time_data)
    logger.info(f"Broadcasted time update: {now.strftime('%H:%M:%S')}")

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

# Load bad words list
bad_words = []
def load_bad_words():
    """Load bad words from file"""
    global bad_words
    try:
        with open('bad_words.txt', 'r', encoding='utf-8') as f:
            bad_words = [line.strip() for line in f.readlines() if line.strip() and not line.strip().startswith('#')]
        logger.info(f"Loaded {len(bad_words)} bad words")
    except FileNotFoundError:
        logger.warning("bad_words.txt not found, using empty list")
        bad_words = []
    except Exception as e:
        logger.error(f"Error loading bad words: {e}")
        bad_words = []

# Load bad words at startup
load_bad_words()

# Security functions
def sanitize_username(username):
    """Clean and validate username input"""
    if not username:
        return None
    
    logger.info(f"Original username: {repr(username)}")
    
    # Allow bad words to pass through - they will be masked on the client side for display
    # This maintains the original behavior where bad words are accepted but displayed as ***
    
    # Temporarily disable HTML escaping to test bad word issue
    # import html
    # username = html.escape(username, quote=False)
    username = username.strip()
    
    logger.info(f"After HTML escaping: {repr(username)}")
    
    # Validate length (allow bad words to pass through)
    if len(username) < 1 or len(username) > 50:
        logger.info(f"Username length invalid: {len(username)}")
        return None
    
    logger.info(f"Final sanitized username: {repr(username)}")
    return username

def sanitize_device_id(device_id):
    """Clean and validate device ID"""
    if not device_id:
        return None
    
    # Only allow alphanumeric, underscores, and hyphens
    if not re.match(r'^[a-zA-Z0-9_-]+$', device_id):
        return None
    
    # Validate length
    if len(device_id) < 10 or len(device_id) > 100:
        return None
    
    return device_id

def is_bad_word(text):
    """Check if text contains bad words"""
    if not text:
        return False
    
    text_lower = text.lower()
    for bad_word in bad_words:
        if bad_word.lower() in text_lower:
            return True
    return False


def validate_date_format(date_str):
    """Validate date format (YYYY-MM-DD)"""
    if not date_str:
        return False
    return re.match(r'^\d{4}-\d{2}-\d{2}$', date_str) is not None

def validate_time_format(time_str):
    """Validate time format (HH:MM)"""
    if not time_str:
        return False
    return re.match(r'^\d{2}:\d{2}$', time_str) is not None


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
    
    try:
        if app.config.get('WTF_CSRF_ENABLED', False):
            from flask_wtf.csrf import generate_csrf
            csrf_token = generate_csrf()
        else:
            csrf_token = ""
        return render_template('index.html', 
                             time_slots=time_slots,
                             morning_slots=morning_slots,
                             afternoon_slots=afternoon_slots,
                             dates=get_available_dates(),
                             version=APP_VERSION,
                             csrf_token=csrf_token,
                             debug_mode=DEBUG_MODE)
    except Exception as e:
        logger.error(f"Error generating CSRF token: {e}")
        return render_template('index.html', 
                             time_slots=time_slots,
                             morning_slots=morning_slots,
                             afternoon_slots=afternoon_slots,
                             dates=get_available_dates(),
                             version=APP_VERSION,
                             csrf_token="",
                             debug_mode=DEBUG_MODE)

@app.route('/book', methods=['POST'])
@limiter.limit("1000 per minute")
def book_slot():
    data = request.get_json()
    
    # Validate CSRF token (temporarily disabled for testing)
    # csrf_token = request.headers.get('X-CSRFToken')
    # if not csrf_token or not csrf.validate():
    #     return jsonify({'success': False, 'message': 'Invalid CSRF token'})
    
    # Get raw inputs
    raw_username = data.get('username')
    raw_device_id = data.get('device_id')
    date = data.get('date')
    time = data.get('time')
    kiosk = bool(data.get('kiosk', False))
    
    # Validate required fields
    if not all([date, time, raw_device_id]):
        return jsonify({'success': False, 'message': 'Missing required fields'})
    
    # Validate date and time formats
    if not validate_date_format(date):
        return jsonify({'success': False, 'message': 'Invalid date format'})
    
    if not validate_time_format(time):
        return jsonify({'success': False, 'message': 'Invalid time format'})
    
    # Sanitize and validate inputs
    username = sanitize_username(raw_username)
    device_id = sanitize_device_id(raw_device_id)
    
    # Check if device ID validation failed
    if device_id is None:
        return jsonify({'success': False, 'message': 'Invalid device ID format'})
    
    # Check if username validation failed (only if username was provided)
    # Temporarily disable username validation to debug bad word issue
    # if raw_username and username is None:
    #     return jsonify({'success': False, 'message': 'Invalid username format'})
    
    
    slot_key = f"{date}_{time}"
    
    if slot_key in bookings:
        return jsonify({'success': False, 'message': 'Slot already booked'})
    
    bookings[slot_key] = {
        'username': raw_username or username,  # Use raw username for now to test bad word masking
        'device_id': device_id,
        'booked_at': datetime.now().isoformat(),
        'kiosk': kiosk
    }
    
    # Extract booking to CSV for logging
    booking = bookings[slot_key]
    csv_result = extract_booking_to_csv(slot_key, booking, "booked")
    
    # Save to file
    save_bookings()
    
    # Broadcast real-time update to all clients viewing this date
    broadcast_booking_update(date, slot_key, bookings[slot_key], 'book')
    
    return jsonify({'success': True, 'message': 'Booking confirmed'})

@app.route('/cancel', methods=['POST'])
@limiter.limit("1000 per minute")
def cancel_booking():
    data = request.get_json()
    
    # Validate CSRF token (temporarily disabled for testing)
    # csrf_token = request.headers.get('X-CSRFToken')
    # if not csrf_token or not csrf.validate():
    #     return jsonify({'success': False, 'message': 'Invalid CSRF token'})
    
    # Get raw inputs
    raw_device_id = data.get('device_id')
    date = data.get('date')
    time = data.get('time')
    is_admin = data.get('is_admin', False)
    reason = data.get('reason', 'cancelled')  # Default to 'cancelled', can be 'completed' for admin
    
    # Validate required fields
    if not all([date, time, raw_device_id]):
        return jsonify({'success': False, 'message': 'Missing required fields'})
    
    # Validate date and time formats
    if not validate_date_format(date):
        return jsonify({'success': False, 'message': 'Invalid date format'})
    
    if not validate_time_format(time):
        return jsonify({'success': False, 'message': 'Invalid time format'})
    
    # Sanitize and validate inputs
    device_id = sanitize_device_id(raw_device_id)
    
    # Check if device ID validation failed
    if device_id is None:
        return jsonify({'success': False, 'message': 'Invalid device ID format'})
    
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
    
    # Broadcast real-time update to all clients viewing this date
    broadcast_booking_update(date, slot_key, None, 'cancel')
    
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
    
    response = jsonify({'success': True, 'bookings': date_bookings})
    
    # Add cache-busting headers for proxy/CDN compatibility
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    return response

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
    response = jsonify({
        'success': True,
        'time': {
            'hours': now.hour,
            'minutes': now.minute,
            'seconds': now.second,
            'total_minutes': now.hour * 60 + now.minute,
            'iso_string': now.isoformat()
        }
    })
    
    # Add cache-busting headers for proxy/CDN compatibility
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    logger.info(f"Added cache-busting headers to time response")
    
    return response

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
    try:
        if app.config.get('WTF_CSRF_ENABLED', False):
            from flask_wtf.csrf import generate_csrf
            csrf_token = generate_csrf()
        else:
            csrf_token = ""
        return render_template('admin.html', version=APP_VERSION, csrf_token=csrf_token, debug_mode=DEBUG_MODE)
    except Exception as e:
        logger.error(f"Error rendering admin page: {e}")
        return render_template('admin.html', version=APP_VERSION, csrf_token="", debug_mode=DEBUG_MODE)

@app.route('/readme')
def readme():
    """Readme page showing usage and features"""
    return render_template('readme.html', version=APP_VERSION)

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

# Security headers
@app.after_request
def after_request(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response

if __name__ == '__main__':
    # Debug mode should be False in production
    # Set FLASK_DEBUG=True environment variable for development
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Start time broadcast timer for real-time updates
    import threading
    import time
    
    def time_broadcast_timer():
        """Broadcast time updates every 5 seconds"""
        while True:
            try:
                broadcast_time_update()
                time.sleep(5)  # Broadcast every 5 seconds
            except Exception as e:
                logger.error(f"Error in time broadcast timer: {e}")
                time.sleep(5)
    
    # Start time broadcast in background thread
    timer_thread = threading.Thread(target=time_broadcast_timer, daemon=True)
    timer_thread.start()
    logger.info("Started time broadcast timer")
    
    # Run with SocketIO for real-time capabilities
    socketio.run(app, debug=debug_mode, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
