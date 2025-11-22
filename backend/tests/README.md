## Quick Start Guide for Testing

This directory contains the comprehensive test suite for the Destination AI backend.

## Installation

```bash
# Activate virtual environment
source venv/bin/activate  # macOS/Linux

# Navigate to backend directory
cd backend

# Install dependencies (including test dependencies)
pip install -r requirements.txt

```

## Running Tests

### Run All Tests
```bash
pytest
```

### Run with Coverage Report
```bash
pytest --cov=app --cov-report=html --cov-report=term-missing
```

### Run Specific Test File
```bash
pytest tests/unit/test_models.py
```

### Run Specific Test
```bash
pytest tests/unit/test_models.py::TestPoint::test_point_distance_calculation_vancouver_to_ubc
```

### Run Tests by Category
```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# API tests only
pytest -m api

# Skip slow tests
pytest -m "not slow"
```

## View Coverage Report

After running tests with coverage:
```bash
# Open HTML report
open htmlcov/index.html  # macOS
```

