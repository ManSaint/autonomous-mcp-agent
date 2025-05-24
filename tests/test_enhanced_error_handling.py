"""
Test Suite for Enhanced Error Handling System

Comprehensive tests for production-grade error handling, tool substitution,
circuit breakers, and health monitoring capabilities.
"""

import asyncio
import pytest
import time
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from autonomous_mcp.enhanced_error_handling import (
    EnhancedErrorHandler, ErrorContext, ErrorCategory, ErrorSeverity,
    ToolSubstitutionEngine, CircuitBreakerState, ToolHealthMetrics
)
from autonomous_mcp.enhanced_executor import EnhancedChainExecutor
from autonomous_mcp.discovery import ToolDiscovery, DiscoveredTool
from autonomous_mcp.planner import ExecutionPlan, ToolCall
from autonomous_mcp.executor import ExecutionStatus


class TestEnhancedErrorHandler:
    """Test enhanced error handling capabilities"""
    
    @pytest.fixture
    def mock_discovery_system(self):
        """Create mock discovery system with test tools"""
        discovery = MagicMock(spec=ToolDiscovery)
        
        # Mock tools for testing
        web_search_tool = DiscoveredTool(
            name="brave_web_search",
            category="web_interaction",
            description="Search the web using Brave",
            capabilities=["search", "web"]
        )
        
        alt_search_tool = DiscoveredTool(
            name="duckduckgo_web_search", 
            category="web_interaction",
            description="Search using DuckDuckGo",
            capabilities=["search", "web"]
        )
        
        file_tool = DiscoveredTool(
            name="read_file",
            category="file_system",
            description="Read file contents",
            capabilities=["file", "read"]
        )
        
        discovery.get_tool_by_name.side_effect = lambda name: {
            "brave_web_search": web_search_tool,
            "duckduckgo_web_search": alt_search_tool,
            "read_file": file_tool
        }.get(name)
        
        discovery.find_tools_by_capabilities.return_value = [alt_search_tool]
        discovery.get_tools_by_category.return_value = [web_search_tool, alt_search_tool]
        
        return discovery
    
    @pytest.fixture
    def error_handler(self, mock_discovery_system):
        """Create error handler instance"""
        return EnhancedErrorHandler(mock_discovery_system)
    
    def test_error_categorization(self, error_handler):
        """Test intelligent error categorization"""
        # Network errors
        timeout_error = TimeoutError("Connection timeout")
        assert error_handler.categorize_error(timeout_error) == ErrorCategory.CONNECTION_TIMEOUT
        
        connection_error = ConnectionError("Network unavailable")
        assert error_handler.categorize_error(connection_error) == ErrorCategory.CONNECTION_TIMEOUT
        
        # Rate limiting
        rate_limit_error = Exception("Too many requests - rate limited")
        assert error_handler.categorize_error(rate_limit_error) == ErrorCategory.RATE_LIMITED
        
        # Tool errors
        tool_error = Exception("Tool not found: unknown_tool")
        assert error_handler.categorize_error(tool_error) == ErrorCategory.TOOL_NOT_FOUND
        
        arg_error = ValueError("Invalid argument: missing parameter")
        assert error_handler.categorize_error(arg_error) == ErrorCategory.INVALID_ARGUMENTS
        
        # Permission errors
        perm_error = PermissionError("Permission denied")
        assert error_handler.categorize_error(perm_error) == ErrorCategory.PERMISSION_DENIED
        
        # Default case
        generic_error = Exception("Something went wrong")
        assert error_handler.categorize_error(generic_error) == ErrorCategory.TOOL_EXECUTION_ERROR
    
    def test_severity_determination(self, error_handler):
        """Test error severity assessment"""
        assert error_handler.determine_severity(ErrorCategory.RESOURCE_EXHAUSTED) == ErrorSeverity.CRITICAL
        assert error_handler.determine_severity(ErrorCategory.CONFIGURATION_ERROR) == ErrorSeverity.CRITICAL
        assert error_handler.determine_severity(ErrorCategory.PERMISSION_DENIED) == ErrorSeverity.HIGH
        assert error_handler.determine_severity(ErrorCategory.CONNECTION_TIMEOUT) == ErrorSeverity.MEDIUM
        assert error_handler.determine_severity(ErrorCategory.TOOL_EXECUTION_ERROR) == ErrorSeverity.LOW
    
    def test_recovery_suggestions(self, error_handler):
        """Test intelligent recovery suggestion generation"""
        # Connection timeout
        timeout_context = ErrorContext(
            category=ErrorCategory.CONNECTION_TIMEOUT,
            severity=ErrorSeverity.MEDIUM,
            message="Connection timeout",
            tool_name="brave_web_search"
        )
        suggestions = error_handler.generate_recovery_suggestions(timeout_context)
        assert "Check network connectivity" in suggestions
        assert "Retry with increased timeout" in suggestions
        
        # Rate limited
        rate_context = ErrorContext(
            category=ErrorCategory.RATE_LIMITED,
            severity=ErrorSeverity.MEDIUM,
            message="Rate limited",
            tool_name="api_tool"
        )
        suggestions = error_handler.generate_recovery_suggestions(rate_context)
        assert "Wait before retrying" in suggestions
        assert "Reduce request frequency" in suggestions
        
        # Tool not found
        tool_context = ErrorContext(
            category=ErrorCategory.TOOL_NOT_FOUND,
            severity=ErrorSeverity.HIGH,
            message="Tool not found",
            tool_name="missing_tool"
        )
        suggestions = error_handler.generate_recovery_suggestions(tool_context)
        assert "Verify tool name spelling" in suggestions
        assert "Use alternative tool" in suggestions
    
    def test_error_context_creation(self, error_handler):
        """Test comprehensive error context creation"""
        test_error = ConnectionError("Network timeout")
        tool_call = ToolCall(tool_name="brave_web_search", arguments={"query": "test"})
        
        context = error_handler.create_error_context(
            test_error, "brave_web_search", tool_call
        )
        
        assert context.category == ErrorCategory.CONNECTION_TIMEOUT
        assert context.severity == ErrorSeverity.MEDIUM
        assert context.tool_name == "brave_web_search"
        assert context.tool_call == tool_call
        assert context.original_exception == test_error
        assert len(context.recovery_suggestions) > 0
        assert len(context.alternative_tools) > 0
        assert isinstance(context.timestamp, datetime)
    
    def test_retry_decision_logic(self, error_handler):
        """Test intelligent retry decision making"""
        # Should retry
        assert error_handler._should_retry(ErrorCategory.CONNECTION_TIMEOUT) == True
        assert error_handler._should_retry(ErrorCategory.RATE_LIMITED) == True
        assert error_handler._should_retry(ErrorCategory.TOOL_EXECUTION_ERROR) == True
        
        # Should not retry
        assert error_handler._should_retry(ErrorCategory.PERMISSION_DENIED) == False
        assert error_handler._should_retry(ErrorCategory.INVALID_ARGUMENTS) == False
        assert error_handler._should_retry(ErrorCategory.CONFIGURATION_ERROR) == False
        assert error_handler._should_retry(ErrorCategory.TOOL_NOT_FOUND) == False
    
    def test_tool_metrics_recording(self, error_handler):
        """Test tool performance metrics recording"""
        tool_name = "test_tool"
        
        # Record successful execution
        error_handler.record_tool_execution(tool_name, True, 0.5)
        
        metrics = error_handler.tool_metrics[tool_name]
        assert metrics.total_calls == 1
        assert metrics.successful_calls == 1
        assert metrics.failed_calls == 0
        assert metrics.success_rate == 100.0
        assert metrics.average_response_time == 0.5
        assert metrics.is_healthy == True
        
        # Record failed execution
        test_error = Exception("Test error")
        error_handler.record_tool_execution(tool_name, False, 1.0, test_error)
        
        assert metrics.total_calls == 2
        assert metrics.successful_calls == 1
        assert metrics.failed_calls == 1
        assert metrics.success_rate == 50.0
        assert len(metrics.recent_errors) == 1


class TestCircuitBreakerState:
    """Test circuit breaker functionality"""
    
    def test_circuit_breaker_states(self):
        """Test circuit breaker state transitions"""
        cb = CircuitBreakerState(failure_threshold=3, recovery_timeout=timedelta(seconds=1))
        
        # Initial state - closed
        assert cb.state == "closed"
        assert cb.should_allow_request() == True
        
        # Record failures
        cb.record_failure()
        cb.record_failure()
        assert cb.state == "closed"  # Still under threshold
        
        # Trigger circuit breaker
        cb.record_failure()
        assert cb.state == "open"
        assert cb.should_allow_request() == False
        
        # Test recovery after timeout
        time.sleep(1.1)  # Wait for recovery timeout
        assert cb.should_allow_request() == True
        assert cb.state == "half_open"
        
        # Record success - should close circuit
        cb.record_success()
        assert cb.state == "closed"
        assert cb.failure_count == 0


class TestToolSubstitutionEngine:
    """Test intelligent tool substitution system"""
    
    @pytest.fixture
    def substitution_engine(self, mock_discovery_system):
        """Create substitution engine"""
        return ToolSubstitutionEngine(mock_discovery_system)
    
    def test_predefined_substitution_rules(self, substitution_engine):
        """Test predefined tool substitution rules"""
        alternatives = substitution_engine.find_alternatives("brave_web_search")
        
        assert len(alternatives) > 0
        alt_names = [tool.name for tool in alternatives]
        assert "duckduckgo_web_search" in alt_names
    
    def test_capability_based_substitution(self, substitution_engine):
        """Test capability-based tool substitution"""
        alternatives = substitution_engine.find_alternatives(
            "unknown_search_tool", 
            required_capabilities=["search", "web"]
        )
        
        assert len(alternatives) > 0
        # Should find tools with similar capabilities
    
    def test_category_based_substitution(self, substitution_engine):
        """Test category-based tool substitution"""
        # Should find tools in same category
        alternatives = substitution_engine.find_alternatives("brave_web_search")
        
        # Should include tools from same category
        assert len(alternatives) > 0


class TestEnhancedChainExecutor:
    """Test enhanced chain executor with error handling"""
    
    @pytest.fixture
    def mock_discovery_system(self):
        """Create comprehensive mock discovery system"""
        discovery = MagicMock(spec=ToolDiscovery)
        
        # Create test tools
        tools = {
            "working_tool": DiscoveredTool(
                name="working_tool",
                category="test",
                description="A tool that works",
                capabilities=["test"]
            ),
            "failing_tool": DiscoveredTool(
                name="failing_tool", 
                category="test",
                description="A tool that fails",
                capabilities=["test"]
            ),
            "backup_tool": DiscoveredTool(
                name="backup_tool",
                category="test", 
                description="A backup tool",
                capabilities=["test"]
            )
        }
        
        discovery.get_tool_by_name.side_effect = lambda name: tools.get(name)
        discovery.find_tools_by_capabilities.return_value = [tools["backup_tool"]]
        discovery.get_tools_by_category.return_value = list(tools.values())
        discovery.discover_tools.return_value = list(tools.values())
        
        return discovery
    
    @pytest.fixture
    def enhanced_executor(self, mock_discovery_system):
        """Create enhanced executor instance"""
        return EnhancedChainExecutor(mock_discovery_system)
    
    @pytest.mark.asyncio
    async def test_successful_execution_with_monitoring(self, enhanced_executor):
        """Test successful execution with health monitoring"""
        # Mock successful tool execution
        with patch.object(enhanced_executor, '_execute_single_tool', new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = {"result": "success"}
            
            plan = ExecutionPlan(tools=[
                ToolCall(tool_name="working_tool", arguments={"param": "value"})
            ])
            
            result = await enhanced_executor.execute_plan_with_enhanced_handling(plan)
            
            assert result.status == ExecutionStatus.SUCCESS
            assert "working_tool" in result.results
            assert len(result.errors) == 0
            
            # Check metrics recording
            metrics = enhanced_executor.error_handler.tool_metrics["working_tool"]
            assert metrics.total_calls >= 1
            assert metrics.successful_calls >= 1
    
    @pytest.mark.asyncio
    async def test_tool_substitution_on_failure(self, enhanced_executor):
        """Test automatic tool substitution when tool fails"""
        call_count = 0
        
        async def mock_execute(tool_call, results):
            nonlocal call_count
            call_count += 1
            if tool_call.tool_name == "failing_tool":
                raise ConnectionError("Tool failed")
            return {"result": "success from backup"}
        
        with patch.object(enhanced_executor, '_execute_single_tool', side_effect=mock_execute):
            plan = ExecutionPlan(tools=[
                ToolCall(tool_name="failing_tool", arguments={"param": "value"})
            ])
            
            result = await enhanced_executor.execute_plan_with_enhanced_handling(plan)
            
            # Should succeed due to substitution
            assert result.status == ExecutionStatus.SUCCESS
            assert "failing_tool" in result.results
            assert "substituted_tools" in result.metadata
            assert "failing_tool" in result.metadata["substituted_tools"]
    
    @pytest.mark.asyncio
    async def test_partial_execution_mode(self, enhanced_executor):
        """Test partial execution when some tools fail"""
        enhanced_executor.enable_partial_execution = True
        
        async def mock_execute(tool_call, results):
            if tool_call.tool_name == "failing_tool":
                raise Exception("Permanent failure")
            return {"result": "success"}
        
        with patch.object(enhanced_executor, '_execute_single_tool', side_effect=mock_execute):
            # Mock no alternatives available
            enhanced_executor.error_handler.substitution_engine.find_alternatives = MagicMock(return_value=[])
            
            plan = ExecutionPlan(tools=[
                ToolCall(tool_name="working_tool", arguments={}),
                ToolCall(tool_name="failing_tool", arguments={}),
                ToolCall(tool_name="working_tool", arguments={})
            ])
            
            result = await enhanced_executor.execute_plan_with_enhanced_handling(plan)
            
            # Should have partial success
            assert result.status == ExecutionStatus.PARTIAL_SUCCESS
            assert len(result.results) == 2  # 2 successful tools
            assert len(result.errors) == 1   # 1 failed tool
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_integration(self, enhanced_executor):
        """Test circuit breaker prevents repeated tool failures"""
        # Trigger circuit breaker by recording failures
        tool_name = "failing_tool"
        metrics = enhanced_executor.error_handler.tool_metrics[tool_name]
        
        # Force circuit breaker to open
        for _ in range(6):  # Exceed failure threshold
            metrics.circuit_breaker.record_failure()
        
        plan = ExecutionPlan(tools=[
            ToolCall(tool_name=tool_name, arguments={})
        ])
        
        result = await enhanced_executor.execute_plan_with_enhanced_handling(plan)
        
        # Should fail due to circuit breaker
        assert result.status == ExecutionStatus.FAILED
        assert len(result.errors) > 0
        assert "circuit breaker" in result.errors[0].lower()
    
    def test_health_report_generation(self, enhanced_executor):
        """Test comprehensive health report generation"""
        # Record some metrics
        enhanced_executor.error_handler.record_tool_execution("tool1", True, 0.5)
        enhanced_executor.error_handler.record_tool_execution("tool1", False, 1.0, Exception("test"))
        enhanced_executor.error_handler.record_tool_execution("tool2", True, 0.3)
        
        report = enhanced_executor.get_enhanced_health_report()
        
        assert "tool_health" in report
        assert "error_metrics" in report
        assert "configuration" in report
        assert "system_summary" in report
        
        # Check configuration
        config = report["configuration"]
        assert config["smart_substitution"] == True
        assert config["partial_execution"] == True
        
        # Check system summary
        summary = report["system_summary"]
        assert "healthy_tools" in summary
        assert "total_tools" in summary
        assert "overall_health_percentage" in summary


if __name__ == "__main__":
    # Run specific test categories
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        # Quick test mode - run basic functionality tests
        pytest.main([__file__ + "::TestEnhancedErrorHandler::test_error_categorization", "-v"])
        pytest.main([__file__ + "::TestCircuitBreakerState::test_circuit_breaker_states", "-v"])
        pytest.main([__file__ + "::TestToolSubstitutionEngine::test_predefined_substitution_rules", "-v"])
    else:
        # Full test suite
        pytest.main([__file__, "-v"])
