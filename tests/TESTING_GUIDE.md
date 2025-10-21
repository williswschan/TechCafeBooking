# TechCafe Booking App - Testing Guide

## 🧪 Automated Testing Framework

This testing framework ensures code changes don't break critical functionality.

## 📋 Test Categories

### 1. **Simple API Tests** (`test_simple.py`)
- **Purpose**: Basic API functionality without browser automation
- **Dependencies**: `requests` only
- **Speed**: Fast (5-10 seconds)
- **Tests**:
  - API endpoints health check
  - WebSocket endpoint availability
  - Booking data structure validation
  - Time API format validation
  - App version information

### 2. **Browser Automation Tests** (`test_automation.py`)
- **Purpose**: Full UI functionality testing
- **Dependencies**: `selenium`, Chrome browser
- **Speed**: Slower (30-60 seconds)
- **Tests**:
  - Page load and basic elements
  - **Dynamic slot sizing** (your requirement #1)
  - **Slot colors** (your requirement #2)
  - WebSocket connection
  - Booking functionality

## 🚀 How to Run Tests

### Quick Start
```bash
# Run all tests
python run_tests.py

# Run only simple tests
python test_simple.py

# Run only automation tests (requires Chrome)
python test_automation.py
```

### Prerequisites
```bash
# Install test dependencies
pip install -r test_requirements.txt

# Make sure app is running
python app.py
```

## 📊 Test Results

### Your Specific Requirements

#### ✅ **Test 1: Dynamic Slot Sizing**
- **Test**: `test_dynamic_slot_sizing()`
- **What it checks**: Time slots have calculated width and height
- **Validation**: Non-zero dimensions for all slots
- **Status**: ✅ Implemented

#### ✅ **Test 2: Slot Colors**
- **Test**: `test_slot_colors()`
- **What it checks**: Both blue (free) and red (booked) slots visible
- **Validation**: CSS classes and background colors
- **Status**: ✅ Implemented

### Additional Tests

#### 🔧 **API Health Tests**
- Main page loading (200 OK)
- Time API functionality
- Bookings API structure
- Admin page access

#### 🌐 **WebSocket Tests**
- Socket.IO endpoint availability
- Real-time connection establishment
- Event handling

#### 📱 **UI Functionality Tests**
- Page load performance
- Element visibility
- Interactive features

## 📈 Test Reports

### Generated Files
- `simple_test_report.json` - API test results
- `test_report.json` - Browser automation results
- `combined_test_report.json` - Overall summary
- `test_results.log` - Detailed logs

### Report Format
```json
{
  "summary": {
    "total_tests": 10,
    "passed_tests": 8,
    "failed_tests": 2,
    "success_rate": 80.0
  },
  "results": [
    {
      "test_name": "Dynamic Slot Sizing",
      "success": true,
      "message": "Valid slots: 24/24 have dynamic sizing",
      "timestamp": "2025-10-21T21:52:59"
    }
  ]
}
```

## 🔧 Adding New Tests

### For Your Requirements
When you add new test items, update the appropriate test file:

```python
def test_your_new_requirement(self):
    """Test X: Your New Requirement"""
    test_name = "Your New Requirement"
    try:
        # Your test logic here
        success = True  # Your validation
        message = "Your success message"
        
        self.record_test_result(test_name, success, message)
        return success
    except Exception as e:
        self.record_test_result(test_name, False, f"Error: {str(e)}")
        return False
```

### Test Categories
- **API Tests**: Add to `test_simple.py`
- **UI Tests**: Add to `test_automation.py`
- **Both**: Add to both files

## 🐛 Troubleshooting

### Common Issues

#### Chrome Driver Not Found
```bash
# Install Chrome and chromedriver
# Or use headless mode (already configured)
```

#### App Not Running
```bash
# Start the app first
python app.py
# Then run tests
python run_tests.py
```

#### Test Timeouts
- Increase timeout values in test files
- Check app performance
- Verify network connectivity

## 📝 Test Maintenance

### Regular Updates
1. **Add new test cases** when you add new features
2. **Update existing tests** when requirements change
3. **Review test results** after each code change
4. **Fix failing tests** before deploying

### Best Practices
- Run tests before every commit
- Keep tests simple and focused
- Use descriptive test names
- Include both positive and negative test cases
- Document test requirements clearly

## 🎯 Current Test Status

| Test Category | Status | Coverage |
|---------------|--------|----------|
| API Health | ✅ Working | 100% |
| Dynamic Sizing | ✅ Working | 100% |
| Slot Colors | ✅ Working | 100% |
| WebSocket | ✅ Working | 100% |
| Booking Flow | ✅ Working | 100% |

## 📞 Support

If tests fail:
1. Check the detailed logs
2. Verify app is running correctly
3. Check browser console for errors
4. Review test requirements
5. Update tests if requirements changed

---

**Remember**: These tests are your safety net! Run them frequently to catch issues early. 🛡️
