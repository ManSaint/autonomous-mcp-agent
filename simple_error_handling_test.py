#!/usr/bin/env python3
"""
Simple Enhanced Error Handling Test

Quick test to verify our enhanced error handling system works.
"""

import asyncio
from autonomous_mcp.enhanced_error_handling import (
    EnhancedErrorHandler, ErrorCategory, ErrorSeverity, CircuitBreakerState,
    ToolSubstitutionEngine
)

def test_error_categorization():
    """Test basic error categorization functionality"""
    print("Testing error categorization...")
    
    # Create a mock discovery system for the error handler
    from unittest.mock import MagicMock
    mock_discovery = MagicMock()
    
    handler = EnhancedErrorHandler(mock_discovery)
    
    # Test different error types
    timeout_error = TimeoutError("Connection timeout")
    category = handler.categorize_error(timeout_error)
    print(f"  TimeoutError -> {category}")
    assert category == ErrorCategory.CONNECTION_TIMEOUT
    
    connection_error = ConnectionError("Network unavailable")
    category = handler.categorize_error(connection_error)
    print(f"  ConnectionError -> {category}")
    assert category == ErrorCategory.CONNECTION_TIMEOUT
    
    rate_error = Exception("Too many requests - rate limited")
    category = handler.categorize_error(rate_error)
    print(f"  Rate limit error -> {category}")
    assert category == ErrorCategory.RATE_LIMITED
    
    tool_error = Exception("Tool not found: unknown_tool")
    category = handler.categorize_error(tool_error)
    print(f"  Tool not found -> {category}")
    assert category == ErrorCategory.TOOL_NOT_FOUND
    
    print("  OK Error categorization working correctly!")


def test_circuit_breaker():
    """Test circuit breaker functionality"""
    print("\nTesting circuit breaker...")
    
    cb = CircuitBreakerState(failure_threshold=3, recovery_timeout=None)
    
    # Initial state
    assert cb.state == "closed"
    assert cb.should_allow_request() == True
    print("  OK Initial state: closed")
    
    # Record failures
    cb.record_failure()
    cb.record_failure()
    assert cb.state == "closed"
    print("  OK Under threshold: still closed")
    
    # Trigger circuit breaker
    cb.record_failure()
    assert cb.state == "open"
    assert cb.should_allow_request() == False
    print("  OK Threshold exceeded: circuit breaker open")
    
    # Record success to close
    cb.record_success()
    assert cb.state == "closed"
    assert cb.failure_count == 0
    print("  OK Success recorded: circuit breaker closed")


def test_tool_metrics():
    """Test tool metrics recording"""
    print("\nTesting tool metrics...")
    
    from unittest.mock import MagicMock
    mock_discovery = MagicMock()
    
    handler = EnhancedErrorHandler(mock_discovery)
    
    tool_name = "test_tool"
    
    # Record successful execution
    handler.record_tool_execution(tool_name, True, 0.5)
    
    metrics = handler.tool_metrics[tool_name]
    assert metrics.total_calls == 1
    assert metrics.successful_calls == 1
    assert metrics.success_rate == 100.0
    assert metrics.is_healthy == True
    print("  OK Success metrics recorded correctly")
    
    # Record failed execution
    handler.record_tool_execution(tool_name, False, 1.0, Exception("Test error"))
    
    assert metrics.total_calls == 2
    assert metrics.success_rate == 50.0
    assert len(metrics.recent_errors) == 1
    print("  OK Failure metrics recorded correctly")


def test_error_context_creation():
    """Test error context creation with suggestions"""
    print("\nTesting error context creation...")
    
    from unittest.mock import MagicMock
    mock_discovery = MagicMock()
    
    handler = EnhancedErrorHandler(mock_discovery)
    
    test_error = ConnectionError("Network timeout")
    context = handler.create_error_context(test_error, "test_tool")
    
    assert context.category == ErrorCategory.CONNECTION_TIMEOUT
    assert context.severity == ErrorSeverity.MEDIUM
    assert context.tool_name == "test_tool"
    assert len(context.recovery_suggestions) > 0
    print("  OK Error context created with suggestions")
    
    # Test human readable format
    readable = context.to_human_readable()
    assert "MEDIUM" in readable
    assert "Network timeout" in readable
    assert "Suggested actions:" in readable
    print("  OK Human-readable format working")


def main():
    """Run all enhanced error handling tests"""
    print("ENHANCED ERROR HANDLING SYSTEM TESTS")
    print("=" * 50)
    
    try:
        test_error_categorization()
        test_circuit_breaker()
        test_tool_metrics()
        test_error_context_creation()
        
        print("\n" + "=" * 50)
        print("ALL TESTS PASSED!")
        print("OK Enhanced error handling system working correctly")
        print("OK Circuit breaker protection functional")
        print("OK Tool metrics recording operational")
        print("OK Error context and suggestions working")
        print("\nTask 1B.3: Enhanced Error Handling - COMPLETE!")
        print("Ready for Phase 3: Advanced Resilience Features")
        
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
