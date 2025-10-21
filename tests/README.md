# TechCafe Booking App - Testing Suite

This folder contains all testing-related files for the TechCafe Booking App.

## 📁 File Structure

```
tests/
├── README.md                 # This file
├── run_tests.py             # Main test runner (run from tests folder)
├── test_simple.py           # Simple API tests (no browser needed)
├── test_automation.py       # Browser automation tests (requires Chrome)
├── test_requirements.txt    # Python dependencies for testing
└── TESTING_GUIDE.md         # Comprehensive testing documentation
```

## 🚀 Quick Start

### From Project Root (Recommended)
```bash
# Run all tests
python run_tests.py

# Run only simple tests
python tests/test_simple.py
```

### From Tests Folder
```bash
cd tests

# Run all tests
python run_tests.py

# Run only simple tests
python test_simple.py
```

## 📋 Test Categories

### 1. **Simple API Tests** (`test_simple.py`)
- **Purpose**: API functionality testing
- **Dependencies**: `requests` only
- **Speed**: Fast (5-10 seconds)
- **Requirements**: App must be running on localhost:5000
- **Perfect for**: SSH/remote development environments

## 📊 Test Reports

Test results are saved in the tests folder:
- `simple_test_report.json` - API test results
- `combined_test_report.json` - Overall summary
- `simple_test_results.log` - Detailed logs

## 🔧 Prerequisites

### Install Dependencies
```bash
pip install -r tests/test_requirements.txt
```

### Start the App
```bash
python app.py
```

## 📝 Adding New Tests

### For API Tests
Add new test functions to `test_simple.py`:

```python
def test_your_new_feature(self):
    """Test X: Your New Feature"""
    test_name = "Your New Feature"
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


## 🐛 Troubleshooting

### Common Issues

1. **App Not Running**
   - Error: "App is not running on localhost:5000"
   - Solution: Start the app with `python app.py`

2. **Chrome Driver Not Found**
   - Error: "Failed to setup Chrome driver"
   - Solution: Install Chrome browser or use headless mode

3. **Test Timeouts**
   - Error: "Test timed out"
   - Solution: Increase timeout values or check app performance

4. **Import Errors**
   - Error: "Module not found"
   - Solution: Install dependencies with `pip install -r test_requirements.txt`

## 📞 Support

For detailed testing documentation, see `TESTING_GUIDE.md` in this folder.

---

**Remember**: Run tests frequently to catch issues early! 🛡️
