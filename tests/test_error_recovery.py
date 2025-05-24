"""
Test Suite for Error Recovery System

Comprehensive tests for production-grade error handling, recovery mechanisms,
and intelligent fallback strategies.
"""

import asyncio
import pytest
import time
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from autonomous_mcp.error_recovery import (
    ErrorRecoverySystem, ErrorContext, ErrorCategory, ErrorSeverity, RecoveryStrategy
)
from autonomous_mcp.discovery import ToolDiscovery, DiscoveredTool


class TestErrorRecoverySystem:
    """Test error recovery system functionality"""
    
    @pytest.fixture
    def recovery_system(self):
        """Create error recovery system for testing"""
        return ErrorRecoverySystem()
    
    @pytest.fixture
    def mock_discovery(self):
        """Create mock discovery system"""
        discovery = MagicMock(spec=ToolDiscovery)
        discovery.available_tools = {
            'web_search': DiscoveredTool(
                name='web_search',
                category='web_interaction',
                description='Search the web',
                capabilities=['search', 'web']
            ),
            'file_read': DiscoveredTool(
                name='file_read',
                category='file_system',
                description='Read files',
                capabilities=['read', 'file']
            )
        }
        return discovery
    
    def test_initialization(self, recovery_system):
        """Test recovery system initialization"""
        assert recovery_system is not None
        assert len(recovery_system.recovery_strategies) > 0
        assert 'network_retry' in recovery_system.recovery_strategies
        assert 'tool_substitution' in recovery_system.recovery_strategies
        assert recovery_system.error_history == []
    
    def test_error_categorization(self, recovery_system):
        """Test intelligent error categorization"""
        # Network errors
        network_error = ConnectionError("Connection timeout")
        category = recovery_system.categorize_error(network_error)
        assert category == ErrorCategory.CONNECTION_TIMEOUT
        
        # Rate limit errors
        rate_error = Exception("Rate limit exceeded")
        category = recovery_system.categorize_error(rate_error)
        assert category == ErrorCategory.RATE_LIMITED
        
        # Authentication errors
        auth_error = Exception("Unauthorized access")
        category = recovery_system.categorize_error(auth_error)
        assert category == ErrorCategory.AUTHENTICATION_ERROR
        
        # Tool errors
        tool_error = Exception("Tool not found")
        category = recovery_system.categorize_error(tool_error, "missing_tool")
        assert category == ErrorCategory.TOOL_NOT_FOUND
        
        # Unknown errors
        unknown_error = Exception("Mysterious error")
        category = recovery_system.categorize_error(unknown_error)
        assert category == ErrorCategory.UNKNOWN_ERROR
    
    def test_severity_determination(self, recovery_system):
        """Test error severity assessment"""
        # Critical severity
        critical_context = ErrorContext(
            error_type="ResourceError",
            error_message="Out of memory",
            category=ErrorCategory.RESOURCE_EXHAUSTED,
            severity=ErrorSeverity.LOW,  # Will be overridden
            timestamp=datetime.now()
        )
        severity = recovery_system.determine_severity(critical_context)
        assert severity == ErrorSeverity.CRITICAL
        
        # High severity
        high_context = ErrorContext(
            error_type="AuthError",
            error_message="Authentication failed",
            category=ErrorCategory.AUTHENTICATION_ERROR,
            severity=ErrorSeverity.LOW,
            timestamp=datetime.now()
        )
        severity = recovery_system.determine_severity(high_context)
        assert severity == ErrorSeverity.HIGH
        
        # Medium severity
        medium_context = ErrorContext(
            error_type="ToolError",
            error_message="Tool unavailable",
            category=ErrorCategory.TOOL_UNAVAILABLE,
            severity=ErrorSeverity.LOW,
            timestamp=datetime.now()
        )
        severity = recovery_system.determine_severity(medium_context)
        assert severity == ErrorSeverity.MEDIUM
        
        # Low severity
        low_context = ErrorContext(
            error_type="NetworkError",
            error_message="Temporary network issue",
            category=ErrorCategory.NETWORK_ERROR,
            severity=ErrorSeverity.LOW,
            timestamp=datetime.now()
        )
        severity = recovery_system.determine_severity(low_context)
        assert severity == ErrorSeverity.LOW
    
    def test_error_context_creation(self, recovery_system):
        """Test comprehensive error context creation"""
        error = ConnectionError("Connection timed out")
        tool_args = {"url": "https://example.com", "timeout": 30}
        
        context = recovery_system.create_error_context(
            error=error,
            tool_name="web_search",
            tool_args=tool_args
        )
        
        assert context.error_type == "ConnectionError"
        assert context.error_message == "Connection timed out"
        assert context.category == ErrorCategory.CONNECTION_TIMEOUT
        assert context.severity == ErrorSeverity.LOW
        assert context.tool_name == "web_search"
        assert context.tool_args == tool_args
        assert context.retry_count == 0
        assert context.recoverable is True
        assert context.suggested_recovery is not None
        assert context.human_explanation is not None
        assert context.stack_trace is not None
    
    def test_recovery_strategy_applicability(self, recovery_system):
        """Test recovery strategy selection"""
        # Network retry strategy
        network_strategy = recovery_system.recovery_strategies['network_retry']
        network_context = ErrorContext(
            error_type="ConnectionError",
            error_message="Network timeout",
            category=ErrorCategory.CONNECTION_TIMEOUT,
            severity=ErrorSeverity.LOW,
            timestamp=datetime.now()
        )
        assert network_strategy.is_applicable(network_context)
        
        # Tool substitution strategy
        tool_strategy = recovery_system.recovery_strategies['tool_substitution']
        tool_context = ErrorContext(
            error_type="ToolError",
            error_message="Tool not found",
            category=ErrorCategory.TOOL_NOT_FOUND,
            severity=ErrorSeverity.MEDIUM,
            timestamp=datetime.now()
        )
        assert tool_strategy.is_applicable(tool_context)
        
        # Rate limit strategy
        rate_strategy = recovery_system.recovery_strategies['rate_limit_backoff']
        rate_context = ErrorContext(
            error_type="RateLimitError",
            error_message="Too many requests",
            category=ErrorCategory.RATE_LIMITED,
            severity=ErrorSeverity.MEDIUM,
            timestamp=datetime.now()
        )
        assert rate_strategy.is_applicable(rate_context)
    
    def test_should_retry_logic(self, recovery_system):
        """Test retry decision logic"""
        # Should retry for recoverable errors within limits
        recoverable_context = ErrorContext(
            error_type="NetworkError",
            error_message="Temporary issue",
            category=ErrorCategory.NETWORK_ERROR,
            severity=ErrorSeverity.LOW,
            timestamp=datetime.now(),
            retry_count=1
        )
        assert recovery_system.should_retry(recoverable_context)
        
        # Should not retry critical errors
        critical_context = ErrorContext(
            error_type="CriticalError",
            error_message="System failure",
            category=ErrorCategory.RESOURCE_EXHAUSTED,
            severity=ErrorSeverity.CRITICAL,
            timestamp=datetime.now()
        )
        assert not recovery_system.should_retry(critical_context)
        
        # Should not retry when circuit breaker is active
        recovery_system.circuit_breakers['failing_tool'] = True
        circuit_context = ErrorContext(
            error_type="ToolError",
            error_message="Tool failure",
            category=ErrorCategory.TOOL_EXECUTION_ERROR,
            severity=ErrorSeverity.MEDIUM,
            timestamp=datetime.now(),
            tool_name='failing_tool'
        )
        assert not recovery_system.should_retry(circuit_context)
    
    @pytest.mark.asyncio
    async def test_successful_recovery(self, recovery_system):
        """Test successful error recovery"""
        
        async def succeeding_action():
            return "Success!"
        
        error_context = ErrorContext(
            error_type="ConnectionError",
            error_message="Temporary network issue",
            category=ErrorCategory.NETWORK_ERROR,
            severity=ErrorSeverity.LOW,
            timestamp=datetime.now(),
            retry_count=0
        )
        
        success, result, new_context = await recovery_system.attempt_recovery(
            error_context, succeeding_action
        )
        
        assert success is True
        assert result == "Success!"
        assert new_context is None
    
    @pytest.mark.asyncio
    async def test_failed_recovery(self, recovery_system):
        """Test failed recovery attempt"""
        async def always_failing_action():
            raise ConnectionError("Persistent network issue")
        
        error_context = ErrorContext(
            error_type="ConnectionError",
            error_message="Persistent network issue",
            category=ErrorCategory.NETWORK_ERROR,
            severity=ErrorSeverity.LOW,
            timestamp=datetime.now(),
            retry_count=2,
            tool_name="test_tool"
        )
        
        success, result, new_context = await recovery_system.attempt_recovery(
            error_context, always_failing_action
        )
        
        assert success is False
        assert result is None
        assert new_context is not None
        assert new_context.retry_count == 3
        assert recovery_system.tool_failure_counts["test_tool"] >= 1
    
    def test_circuit_breaker_activation(self, recovery_system):
        """Test circuit breaker activation after repeated failures"""
        tool_name = "unreliable_tool"
        
        # Simulate multiple failures
        for i in range(6):  # More than the threshold of 5
            recovery_system.record_recovery_failure(
                ErrorContext(
                    error_type="ToolError",
                    error_message="Tool keeps failing",
                    category=ErrorCategory.TOOL_EXECUTION_ERROR,
                    severity=ErrorSeverity.MEDIUM,
                    timestamp=datetime.now(),
                    tool_name=tool_name
                ),
                recovery_system.recovery_strategies['tool_substitution']
            )
        
        # Circuit breaker should be active
        assert recovery_system.circuit_breakers[tool_name] is True
        assert recovery_system.tool_failure_counts[tool_name] >= 5
    
    def test_recovery_success_resets_circuit_breaker(self, recovery_system):
        """Test that successful recovery resets circuit breaker"""
        tool_name = "recovering_tool"
        
        # Set up circuit breaker
        recovery_system.circuit_breakers[tool_name] = True
        recovery_system.tool_failure_counts[tool_name] = 5
        
        # Record successful recovery
        recovery_system.record_recovery_success(
            ErrorContext(
                error_type="ToolError",
                error_message="Tool working again",
                category=ErrorCategory.TOOL_EXECUTION_ERROR,
                severity=ErrorSeverity.MEDIUM,
                timestamp=datetime.now(),
                tool_name=tool_name
            ),
            recovery_system.recovery_strategies['tool_substitution']
        )
        
        # Circuit breaker should be reset
        assert recovery_system.circuit_breakers[tool_name] is False
        assert recovery_system.tool_failure_counts[tool_name] == 0
    
    def test_error_recording_and_history(self, recovery_system):
        """Test error recording and history management"""
        error_context = ErrorContext(
            error_type="TestError",
            error_message="Test error message",
            category=ErrorCategory.NETWORK_ERROR,
            severity=ErrorSeverity.LOW,
            timestamp=datetime.now()
        )
        
        recovery_system.record_error(error_context)
        
        assert len(recovery_system.error_history) == 1
        assert recovery_system.error_history[0] == error_context
    
    def test_error_statistics(self, recovery_system):
        """Test error statistics generation"""
        # Add some test errors
        errors = [
            ErrorContext(
                error_type="NetworkError",
                error_message="Network issue 1",
                category=ErrorCategory.NETWORK_ERROR,
                severity=ErrorSeverity.LOW,
                timestamp=datetime.now(),
                tool_name="tool1"
            ),
            ErrorContext(
                error_type="NetworkError",
                error_message="Network issue 2",
                category=ErrorCategory.NETWORK_ERROR,
                severity=ErrorSeverity.MEDIUM,
                timestamp=datetime.now(),
                tool_name="tool1"
            ),
            ErrorContext(
                error_type="ToolError",
                error_message="Tool issue",
                category=ErrorCategory.TOOL_NOT_FOUND,
                severity=ErrorSeverity.HIGH,
                timestamp=datetime.now(),
                tool_name="tool2"
            )
        ]
        
        for error in errors:
            recovery_system.record_error(error)
        
        stats = recovery_system.get_error_statistics()
        
        assert stats['total_errors'] == 3
        assert stats['by_category']['network_error'] == 2
        assert stats['by_category']['tool_not_found'] == 1
        assert stats['by_severity']['low'] == 1
        assert stats['by_severity']['medium'] == 1
        assert stats['by_severity']['high'] == 1
        assert stats['by_tool']['tool1'] == 2
        assert stats['by_tool']['tool2'] == 1
    
    def test_error_report_export(self, recovery_system):
        """Test comprehensive error report export"""
        # Add test error
        error_context = ErrorContext(
            error_type="TestError",
            error_message="Test error",
            category=ErrorCategory.NETWORK_ERROR,
            severity=ErrorSeverity.LOW,
            timestamp=datetime.now(),
            tool_name="test_tool"
        )
        recovery_system.record_error(error_context)
        
        # Set up some tool health data
        recovery_system.tool_failure_counts["test_tool"] = 2
        recovery_system.circuit_breakers["test_tool"] = False
        
        report = recovery_system.export_error_report()
        
        assert 'statistics' in report
        assert 'recent_errors' in report
        assert 'recovery_strategies' in report
        assert 'tool_health' in report
        
        assert report['statistics']['total_errors'] == 1
        assert len(report['recent_errors']) == 1
        assert len(report['recovery_strategies']) > 0
        assert 'test_tool' in report['tool_health']
        assert report['tool_health']['test_tool']['failure_count'] == 2
        assert report['tool_health']['test_tool']['circuit_breaker_active'] is False
    
    def test_recovery_suggestion_generation(self, recovery_system):
        """Test intelligent recovery suggestion generation"""
        network_context = ErrorContext(
            error_type="NetworkError",
            error_message="Connection failed",
            category=ErrorCategory.NETWORK_ERROR,
            severity=ErrorSeverity.LOW,
            timestamp=datetime.now()
        )
        
        suggestion = recovery_system.generate_recovery_suggestion(network_context)
        assert "network connectivity" in suggestion.lower()
        assert "retry" in suggestion.lower()
        
        tool_context = ErrorContext(
            error_type="ToolError",
            error_message="Tool not found",
            category=ErrorCategory.TOOL_NOT_FOUND,
            severity=ErrorSeverity.MEDIUM,
            timestamp=datetime.now()
        )
        
        suggestion = recovery_system.generate_recovery_suggestion(tool_context)
        assert "alternative" in suggestion.lower()
    
    def test_human_explanation_generation(self, recovery_system):
        """Test human-readable explanation generation"""
        rate_context = ErrorContext(
            error_type="RateLimit",
            error_message="Too many requests",
            category=ErrorCategory.RATE_LIMITED,
            severity=ErrorSeverity.MEDIUM,
            timestamp=datetime.now(),
            tool_name="api_tool"
        )
        
        explanation = recovery_system.generate_human_explanation(rate_context)
        assert "api_tool" in explanation
        assert "rate limit" in explanation.lower()
        assert explanation.startswith("api_tool")
    
    def test_recovery_strategy_finding(self, recovery_system):
        """Test finding appropriate recovery strategies"""
        network_context = ErrorContext(
            error_type="NetworkError",
            error_message="Network issue",
            category=ErrorCategory.NETWORK_ERROR,
            severity=ErrorSeverity.LOW,
            timestamp=datetime.now()
        )
        
        strategy = recovery_system.find_recovery_strategy(network_context)
        assert strategy is not None
        assert strategy.name == "network_retry"
        
        unknown_context = ErrorContext(
            error_type="WeirdError",
            error_message="Unknown issue",
            category=ErrorCategory.UNKNOWN_ERROR,
            severity=ErrorSeverity.LOW,
            timestamp=datetime.now()
        )
        
        strategy = recovery_system.find_recovery_strategy(unknown_context)
        # Should return None for unknown errors with no applicable strategy
        assert strategy is None


class TestErrorContext:
    """Test ErrorContext functionality"""
    
    def test_error_context_creation(self):
        """Test creating error context"""
        context = ErrorContext(
            error_type="TestError",
            error_message="Test message",
            category=ErrorCategory.NETWORK_ERROR,
            severity=ErrorSeverity.MEDIUM,
            timestamp=datetime.now(),
            tool_name="test_tool",
            retry_count=2
        )
        
        assert context.error_type == "TestError"
        assert context.error_message == "Test message"
        assert context.category == ErrorCategory.NETWORK_ERROR
        assert context.severity == ErrorSeverity.MEDIUM
        assert context.tool_name == "test_tool"
        assert context.retry_count == 2
        assert context.recoverable is True
    
    def test_error_context_to_dict(self):
        """Test converting error context to dictionary"""
        timestamp = datetime.now()
        context = ErrorContext(
            error_type="TestError",
            error_message="Test message",
            category=ErrorCategory.VALIDATION_ERROR,
            severity=ErrorSeverity.HIGH,
            timestamp=timestamp,
            tool_name="validator",
            tool_args={"input": "test"},
            retry_count=1,
            suggested_recovery="Fix validation",
            human_explanation="Data validation failed"
        )
        
        result = context.to_dict()
        
        assert result['error_type'] == "TestError"
        assert result['error_message'] == "Test message"
        assert result['category'] == "validation_error"
        assert result['severity'] == "high"
        assert result['timestamp'] == timestamp.isoformat()
        assert result['tool_name'] == "validator"
        assert result['tool_args'] == {"input": "test"}
        assert result['retry_count'] == 1
        assert result['suggested_recovery'] == "Fix validation"
        assert result['human_explanation'] == "Data validation failed"


class TestRecoveryStrategy:
    """Test RecoveryStrategy functionality"""
    
    def test_recovery_strategy_creation(self):
        """Test creating recovery strategy"""
        strategy = RecoveryStrategy(
            name="test_strategy",
            description="Test recovery strategy",
            max_retries=3,
            backoff_factor=2.0,
            timeout_seconds=30.0,
            applicable_categories={ErrorCategory.NETWORK_ERROR, ErrorCategory.API_UNAVAILABLE},
            recovery_actions=["retry", "backoff"]
        )
        
        assert strategy.name == "test_strategy"
        assert strategy.description == "Test recovery strategy"
        assert strategy.max_retries == 3
        assert strategy.backoff_factor == 2.0
        assert strategy.timeout_seconds == 30.0
        assert ErrorCategory.NETWORK_ERROR in strategy.applicable_categories
        assert ErrorCategory.API_UNAVAILABLE in strategy.applicable_categories
        assert "retry" in strategy.recovery_actions
        assert "backoff" in strategy.recovery_actions
    
    def test_strategy_applicability(self):
        """Test strategy applicability checking"""
        strategy = RecoveryStrategy(
            name="network_strategy",
            description="Network recovery",
            max_retries=2,
            backoff_factor=1.5,
            timeout_seconds=15.0,
            applicable_categories={ErrorCategory.NETWORK_ERROR, ErrorCategory.CONNECTION_TIMEOUT},
            recovery_actions=["retry"]
        )
        
        # Should apply to network errors
        network_context = ErrorContext(
            error_type="NetworkError",
            error_message="Network issue",
            category=ErrorCategory.NETWORK_ERROR,
            severity=ErrorSeverity.LOW,
            timestamp=datetime.now()
        )
        assert strategy.is_applicable(network_context)
        
        # Should apply to connection timeouts
        timeout_context = ErrorContext(
            error_type="TimeoutError",
            error_message="Connection timeout",
            category=ErrorCategory.CONNECTION_TIMEOUT,
            severity=ErrorSeverity.MEDIUM,
            timestamp=datetime.now()
        )
        assert strategy.is_applicable(timeout_context)
        
        # Should not apply to tool errors
        tool_context = ErrorContext(
            error_type="ToolError",
            error_message="Tool not found",
            category=ErrorCategory.TOOL_NOT_FOUND,
            severity=ErrorSeverity.HIGH,
            timestamp=datetime.now()
        )
        assert not strategy.is_applicable(tool_context)
