# Development Branch Information

## Branch Details
- **Branch Name:** `development`
- **Version:** 3.2
- **Location:** `/script/cursor/TechCafeBooking-Copilot`
- **Status:** Active development branch

## What's Different from Main (v2.2)

### Major Changes in Development Branch:
1. **CSS Extraction** - All CSS has been moved from `index.html` to separate files:
   - `static/css/main.css` - Main styles
   - `static/css/time-slots.css` - Time slot specific styles
   - `static/css/modals.css` - Modal dialog styles
   - `static/css/footer.css` - Footer styles
   - `static/css/responsive.css` - Responsive design styles

2. **Font Management** - Local font files added:
   - Inter font family (Regular, Medium, SemiBold, Bold)
   - Font Awesome icons (local copies)

3. **File Structure** - New organization:
   - `static/` directory with CSS and font files
   - `templates_backup/` for safety backups
   - `app_backup.py` for code safety

4. **Version Management** - Updated to 3.2:
   - `APP_VERSION = "3.2"` in templates/index.html
   - Version display shows "Version 3.2" in admin page

## Branch Strategy

### Main Branch (v2.2)
- **Purpose:** Stable, production-ready code
- **Version:** 2.2
- **Location:** `/script/cursor/TechCafeBooking`
- **Status:** Production use

### Development Branch (v3.2)
- **Purpose:** Major changes and improvements
- **Version:** 3.2
- **Location:** `/script/cursor/TechCafeBooking-Copilot`
- **Status:** Active development

## Switching Between Branches

### To work on Development (v3.2):
```bash
cd /script/cursor/TechCafeBooking-Copilot
git checkout development
```

### To work on Main (v2.2):
```bash
cd /script/cursor/TechCafeBooking
git checkout main
```

## Next Steps
1. Continue development on the `development` branch
2. Test all functionality with extracted CSS
3. When ready, merge back to main branch
4. Update version numbers as needed

## Notes
- Both branches are independent
- Development branch has all the latest changes
- Main branch remains stable for production use
- Version 3.2 includes README update to remove hardcoded port references
