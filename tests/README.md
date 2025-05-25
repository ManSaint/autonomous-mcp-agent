# Test Suite

This directory contains comprehensive tests for the Autonomous MCP Agent framework.

## Test Structure

### Core Tests
- `test_autonomous_tools.py` - Tests for all 7 autonomous tools
- `test_integration.py` - Integration tests across components
- `test_performance.py` - Performance and benchmark tests

### Component Tests
- `test_discovery.py` - Tool discovery system tests
- `test_executor.py` - Task execution engine tests
- `test_monitoring.py` - Performance monitoring tests
- `test_planner.py` - Workflow planning tests
- `test_smart_selector.py` - Tool selection tests
- `test_error_recovery.py` - Error handling tests

### Integration Tests
- `test_mcp_server_integration.py` - MCP server integration
- `test_real_integration.py` - Real-world scenario tests
- `test_complete_integration.py` - End-to-end integration tests

## Running Tests

### All Tests
```bash
python -m pytest tests/ -v
```

### Specific Categories
```bash
# Core functionality
python -m pytest tests/test_autonomous_tools.py -v

# Performance tests
python -m pytest tests/test_performance.py -v

# Integration tests
python -m pytest tests/test_integration.py -v
```

### With Coverage
```bash
python -m pytest tests/ --cov=autonomous_mcp --cov-report=html
```

## Test Requirements

- All new features must include tests
- Minimum 80% code coverage
- Tests must pass on Python 3.12+
- Integration tests should be realistic scenarios

## Test Data

Test data and fixtures are located in:
- `fixtures/` - Test data files
- `conftest.py` - Shared test fixtures

## Continuous Integration

Tests run automatically on:
- Pull requests
- Main branch commits
- Release tags

## Writing Tests

Follow these guidelines:
- Use descriptive test names
- Test both success and error cases
- Mock external dependencies
- Keep tests focused and isolated
