# Test Setup Instructions

## Activate Virtual Environment

Before running tests, make sure you're in the virtual environment:

```bash
# Navigate to project root
cd /Users/jessicazhou/Repositories/destination.ai

# Activate virtual environment
source venv/bin/activate

# You should see (venv) in your prompt
# Example: (venv) jessicazhou@Jessicas-MacBook-Air-4 destination.ai %
```

## Verify Dependencies

```bash
# Check if httpx is installed
python -c "import httpx; print(f'httpx version: {httpx.__version__}')"

# Check if pytest is installed
python -c "import pytest; print(f'pytest version: {pytest.__version__}')"
```

## Install Dependencies (if needed)

```bash
# Make sure you're in the backend directory
cd backend

# Install all dependencies including test dependencies
pip install -r requirements.txt
```

## Run Tests

```bash
# Make sure you're in the backend directory
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html --cov-report=term-missing

# Run specific test file
pytest tests/api/test_main.py -v

# Run tests by category
pytest -m unit      # Unit tests only
pytest -m integration  # Integration tests only
pytest -m api       # API tests only
```

## Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'httpx'`

**Solution**: Activate your virtual environment first:
```bash
source venv/bin/activate
```

### Issue: `ModuleNotFoundError: No module named 'app'`

**Solution**: Make sure you're running pytest from the `backend/` directory:
```bash
cd backend
pytest
```

### Issue: TestClient errors

**Solution**: The test code now handles httpx version differences automatically. If you still see errors, check your httpx version:
```bash
pip show httpx
```

If it's 0.28+, the tests should work. If it's older, you may need to update:
```bash
pip install --upgrade httpx
```

## Quick Test

```bash
# Activate venv
source venv/bin/activate

# Navigate to backend
cd backend

# Run a simple test to verify setup
pytest tests/unit/test_models.py::TestPoint::test_point_creation -v
```

If this test passes, your setup is correct! ✅

