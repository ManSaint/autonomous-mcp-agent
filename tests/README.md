# Tests for Autonomous MCP Agent

This directory contains all unit tests for the autonomous MCP agent components.

## Test Files

- `test_discovery.py` - Tests for tool discovery system
- `test_planner.py` - Tests for execution planner
- `test_executor.py` - Tests for chain executor
- `test_integration.py` - Integration tests (coming in Task 1.4)

## Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_executor.py

# Run with coverage
pytest --cov=autonomous_mcp tests/
```
