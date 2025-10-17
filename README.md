# TechCafe Booking Portal

A professional, responsive web portal for booking time slots at TechCafe. The portal features a modern, mobile-first design that works seamlessly across desktop, tablet, and mobile devices.

## Features

- **Responsive Design**: Optimized for desktop, iPad, and mobile devices
- **Time Slot Management**: 15-minute slots from 09:00 to 18:00
- **Multi-Day Booking**: Shows today, tomorrow, and day after tomorrow
- **Interactive Booking**: Click to book or cancel time slots
- **Real-time Updates**: Instant visual feedback for booking status
- **Modern UI**: Professional gradient design with smooth animations
- **User-Friendly**: Simple username-based booking system

## Installation

1. **Clone or download the project files**

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```

4. **Open your browser and navigate to:**
   ```
   http://localhost:5000
   ```

## Usage

### Booking a Time Slot
1. Select a date using the date tabs at the top
2. Click on an available time slot (blue slots)
3. Enter your name in the popup modal
4. Click "Confirm Booking"
5. The slot will turn yellow and show your name

### Cancelling a Booking
1. Click on a booked time slot (yellow slots)
2. Click "Yes, Cancel" in the confirmation dialog
3. The slot will return to available status

### Device Compatibility
- **Desktop**: Full grid layout with hover effects
- **Tablet**: Optimized grid with touch-friendly buttons
- **Mobile**: Compact 2-column layout for easy thumb navigation

## Technical Details

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Storage**: In-memory (for demo purposes)
- **Responsive**: CSS Grid and Flexbox
- **Icons**: Font Awesome
- **Fonts**: Inter (Google Fonts)

## File Structure

```
TechCafeBooking/
├── app.py                 # Flask application
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Main HTML template
└── README.md            # This file
```

## Customization

### Time Slots
Modify the `get_time_slots()` function in `app.py` to change:
- Start time (currently 09:00)
- End time (currently 18:00)
- Slot duration (currently 15 minutes)

### Number of Days
Change the range in `get_available_dates()` function to show more or fewer days.

### Styling
All CSS is contained within the HTML template for easy customization. Key areas:
- Color scheme: Modify CSS custom properties
- Layout: Adjust grid columns and spacing
- Animations: Customize transition effects

## Production Considerations

For production deployment, consider:
- Replacing in-memory storage with a database (SQLite, PostgreSQL, etc.)
- Adding user authentication
- Implementing admin features
- Adding email notifications
- Setting up proper logging
- Using environment variables for configuration

## Browser Support

- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+
- Mobile browsers (iOS Safari, Chrome Mobile)

## License

This project is open source and available under the MIT License.
