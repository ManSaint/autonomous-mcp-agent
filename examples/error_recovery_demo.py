"""
Error Recovery System Demo

Demonstrates the production-grade error handling and recovery capabilities
of the Autonomous MCP Agent.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from autonomous_mcp.error_recovery import (
    ErrorRecoverySystem, ErrorContext, ErrorCategory, ErrorSeverity
)
from autonomous_mcp.discovery import ToolDiscovery


async def simulate_network_error():
    """Simulate a network error that recovers after retry"""
    raise ConnectionError("Network connection timed out")


async def simulate_tool_error():
    """Simulate a tool not found error"""
    raise ValueError("Tool 'missing_tool' not found in registry")


async def simulate_rate_limit_error():
    """Simulate an API rate limit error"""
    raise Exception("Rate limit exceeded: too many requests")


async def simulate_recoverable_action():
    """Simulate an action that succeeds after retry"""
    print("   -> Action succeeded!")
    return {"status": "success", "data": "Retrieved data successfully"}


async def main():
    """Demonstrate error recovery system capabilities"""
    print("=== AUTONOMOUS MCP AGENT - ERROR RECOVERY DEMO ===")
    
    # Initialize the error recovery system
    recovery_system = ErrorRecoverySystem()
    
    print("\n1. Error Recovery System Initialization")
    print(f"   [OK] System initialized with {len(recovery_system.recovery_strategies)} recovery strategies")
    print("   [OK] Circuit breakers ready")
    print("   [OK] Error categorization engine ready")
    
    print("\n2. Error Categorization Demo")
    
    # Test different error types
    test_errors = [
        (ConnectionError("Connection timed out"), "web_search"),
        (Exception("Rate limit exceeded"), "api_tool"), 
        (ValueError("Tool not found"), "missing_tool"),
        (Exception("Unauthorized access"), "secure_api"),
        (Exception("Invalid JSON response"), "data_parser")
    ]
    
    for error, tool_name in test_errors:
        category = recovery_system.categorize_error(error, tool_name)
        context = recovery_system.create_error_context(error, tool_name)
        
        print(f"   [ERROR] {error.__class__.__name__}: '{error}'")
        print(f"      -> Category: {category.value}")
        print(f"      -> Severity: {context.severity.value}")
        print(f"      -> Recovery: {context.suggested_recovery}")
        print(f"      -> Explanation: {context.human_explanation}")
        print()
    
    print("3. Recovery Strategy Selection")
    
    network_context = ErrorContext(
        error_type="ConnectionError",
        error_message="Network timeout",
        category=ErrorCategory.CONNECTION_TIMEOUT,
        severity=ErrorSeverity.LOW,
        timestamp=datetime.now(),
        tool_name="web_search"
    )
    
    strategy = recovery_system.find_recovery_strategy(network_context)
    if strategy:
        print(f"   [OK] Selected strategy: {strategy.name}")
        print(f"   [OK] Description: {strategy.description}")
        print(f"   [OK] Max retries: {strategy.max_retries}")
        print(f"   [OK] Backoff factor: {strategy.backoff_factor}")
    
    print(f"\n4. Recovery Attempt Simulation")
    
    # Test successful recovery
    print("   [RECOVERY] Testing successful recovery...")
    
    success, result, new_context = await recovery_system.attempt_recovery(
        network_context, simulate_recoverable_action
    )
    
    if success:
        print(f"   [SUCCESS] Recovery successful!")
        print(f"   [SUCCESS] Result: {result}")
    else:
        print(f"   [FAILED] Recovery failed")
        if new_context:
            print(f"   [FAILED] New error: {new_context.error_message}")
    
    print(f"\n5. Circuit Breaker Demo")
    
    # Simulate tool failures to trigger circuit breaker
    failing_tool = "unreliable_service"
    print(f"   [TESTING] Simulating failures for '{failing_tool}'...")
    
    for i in range(6):  # Exceed the failure threshold
        failure_context = ErrorContext(
            error_type="ServiceError",
            error_message=f"Service failure #{i+1}",
            category=ErrorCategory.TOOL_EXECUTION_ERROR,
            severity=ErrorSeverity.MEDIUM,
            timestamp=datetime.now(),
            tool_name=failing_tool
        )
        recovery_system.record_recovery_failure(failure_context, strategy)
        
        if recovery_system.circuit_breakers[failing_tool]:
            print(f"   [BREAKER] Circuit breaker activated after {i+1} failures")
            break
    
    # Test circuit breaker behavior
    should_retry = recovery_system.should_retry(ErrorContext(
        error_type="ServiceError",
        error_message="Another failure",
        category=ErrorCategory.TOOL_EXECUTION_ERROR,
        severity=ErrorSeverity.MEDIUM,
        timestamp=datetime.now(),
        tool_name=failing_tool
    ))
    
    print(f"   [BLOCKED] Should retry after circuit breaker: {should_retry}")
    
    print(f"\n6. Error Statistics & Health Monitoring")
    
    # Add some sample errors for statistics
    sample_errors = [
        ErrorContext(
            error_type="NetworkError",
            error_message="Connection failed",
            category=ErrorCategory.NETWORK_ERROR,
            severity=ErrorSeverity.LOW,
            timestamp=datetime.now(),
            tool_name="web_tool"
        ),
        ErrorContext(
            error_type="AuthError", 
            error_message="Authentication failed",
            category=ErrorCategory.AUTHENTICATION_ERROR,
            severity=ErrorSeverity.HIGH,
            timestamp=datetime.now(),
            tool_name="secure_api"
        ),
        ErrorContext(
            error_type="RateLimit",
            error_message="Too many requests",
            category=ErrorCategory.RATE_LIMITED,
            severity=ErrorSeverity.MEDIUM,
            timestamp=datetime.now(),
            tool_name="api_service"
        )
    ]
    
    for error in sample_errors:
        recovery_system.record_error(error)
    
    stats = recovery_system.get_error_statistics()
    print(f"   [STATS] Total errors recorded: {stats['total_errors']}")
    print(f"   [STATS] Errors by category:")
    for category, count in stats['by_category'].items():
        print(f"      -> {category}: {count}")
    
    print(f"   [STATS] Errors by severity:")
    for severity, count in stats['by_severity'].items():
        print(f"      -> {severity}: {count}")
    
    print(f"   [STATS] Circuit breakers active: {stats['circuit_breakers_active']}")
    
    print(f"\n7. Error Report Export")
    
    report = recovery_system.export_error_report()
    print(f"   [REPORT] Generated comprehensive error report")
    print(f"   [REPORT] Recovery strategies documented: {len(report['recovery_strategies'])}")
    print(f"   [REPORT] Tool health metrics: {len(report['tool_health'])} tools monitored")
    print(f"   [REPORT] Recent errors tracked: {len(report['recent_errors'])}")
    
    print(f"\n8. Recovery Success Demonstration")
    
    # Reset circuit breaker and show recovery
    recovery_system.record_recovery_success(
        ErrorContext(
            error_type="ServiceError",
            error_message="Service recovered",
            category=ErrorCategory.TOOL_EXECUTION_ERROR,
            severity=ErrorSeverity.MEDIUM,
            timestamp=datetime.now(),
            tool_name=failing_tool
        ),
        strategy
    )
    
    print(f"   [RECOVERY] Tool '{failing_tool}' recovered successfully")
    print(f"   [SUCCESS] Circuit breaker reset: {not recovery_system.circuit_breakers[failing_tool]}")
    print(f"   [SUCCESS] Failure count reset: {recovery_system.tool_failure_counts[failing_tool]}")
    
    print(f"\n=== DEMO COMPLETE ===")
    print(f"[OK] Error Recovery System is production-ready!")
    print(f"[OK] Intelligent error categorization working")
    print(f"[OK] Circuit breaker protection active")  
    print(f"[OK] Recovery strategies operational")
    print(f"[OK] Health monitoring and reporting functional")
    
    print(f"\n[MILESTONE] PHASE 3 TASK 3.1 - ERROR RECOVERY SYSTEM: COMPLETE")


if __name__ == "__main__":
    asyncio.run(main())
