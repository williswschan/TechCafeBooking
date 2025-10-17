# TechCafe Booking Portal Elements

## 1. Red Background (Body)
- Linear gradient background (light red to dark red)
- Full viewport height and width
- CSS: `background: linear-gradient(135deg, #f87171 0%, #dc2626 100%)`

## 2. Main White Container
- White background with rounded corners (20px radius)
- Box shadow effect for depth
- **Responsive sizing**: `screen width - 40px` × `screen height - 40px`
- **Landscape**: Absolute positioning, centered in viewport
- **Portrait**: Relative positioning with 20px margins
- Contains all other elements

## 3. Container Elements

### a. Red Header/Banner
- Red gradient background with rounded top corners
- **Landscape**: Full width with admin button on right
- **Portrait**: Admin button becomes circular (icon only, no text)
- Components:
  * Portal title with calendar icon
  * Subtitle text
  * Admin button (responsive design)

### b. Date Selection Section
- **Portrait**: Single row layout with equal-width tabs
- **Landscape**: Single row layout with equal-width tabs
- Components:
  * Three date tabs (Today, Tomorrow, Day After)
  * Active state highlighting (red background)
  * Border bottom separator
  * Responsive text sizing

### c. Morning Slots Section
- Section title with sun icon
- Time range: 09:00-12:00
- **Dynamic sizing**: Buttons automatically resize to fill available space
- Layout:
  * Grid layout with 12 slots total (3 hours × 4 slots/hour)
  * 15-minute intervals
  * Responsive columns:
    - Landscape: 6 columns × 2 rows (dynamic height)
    - Portrait: 4 columns × 3 rows (scrollable if needed)

### d. Lunch Break Section
- **Perfect alignment**: Width matches time slot grid exactly
- Visual:
  * Dashed border with utensils icon
  * Light gradient background
  * Centered text
- Time range: 12:00-14:00

### e. Afternoon Slots Section
- Section title with moon icon
- Time range: 14:00-18:00
- **Dynamic sizing**: Buttons automatically resize to fill available space
- Layout:
  * Grid layout with 16 slots total (4 hours × 4 slots/hour)
  * 15-minute intervals
  * Responsive columns:
    - Landscape: 6 columns × 3 rows (dynamic height, no scrollbar)
    - Portrait: 4 columns × 4 rows (scrollable if needed)

### f. Red Footer Section
- **Red gradient background** (matches header)
- **Rounded bottom corners** (matches container)
- **Perfect alignment**: Full width of container
- **Fixed positioning**: Always at bottom of container
- Content:
  * Copyright text: "© 2024 MYMSNGROUP. All rights reserved."
  * White text on red background

## Responsive Design
The portal uses a simplified 2-configuration responsive design based on orientation:

### Landscape Configuration
- **Container**: Full viewport with absolute positioning (`screen width - 40px` × `screen height - 40px`)
- **Time slots**: 6 columns grid layout with dynamic height calculation
- **No scrolling**: All content fits within container bounds
- **Admin button**: Rectangular with icon and text
- **Optimized for**: Desktop and tablet landscape orientation

### Portrait Configuration  
- **Container**: Centered with 20px margins (`screen width - 40px` × `screen height - 40px`)
- **Time slots**: 4 columns grid layout with scrollable content if needed
- **Scrollable content**: Usable space between header and footer
- **Admin button**: Circular with icon only (no text)
- **Optimized for**: Mobile and tablet portrait orientation

## Key Features

### Dynamic Layout System
- **Smart sizing**: Time slot buttons automatically resize to fill available space
- **No overflow**: Landscape mode ensures all content fits without scrolling
- **Perfect alignment**: Lunch break section aligns exactly with time slot grid edges
- **Responsive admin button**: Adapts from rectangular (landscape) to circular (portrait)

### Space Optimization
- **Usable space calculation**: `container height - header height - footer height`
- **Content distribution**: Date selector, time slots, and lunch break within usable space
- **Footer positioning**: Always at bottom of container with proper alignment

### User Experience
- **Touch-optimized**: Large, easy-to-tap time slot buttons
- **Visual feedback**: Hover effects and active states
- **Privacy-friendly**: Optional name field with clear privacy notice
- **Admin functionality**: Easy access to booking management

## Element Relationships
- All elements are contained within the main white container
- **Header and footer**: Fixed positioning, always visible
- **Scrollable content**: Date selector, time slots, and lunch break in middle section
- **Perfect alignment**: Lunch break width matches time slot grid exactly
- **Responsive behavior**: Adapts layout based on device orientation
