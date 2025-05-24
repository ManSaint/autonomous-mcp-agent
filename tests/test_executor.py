"""
Unit tests for Chain Executor
Tests async execution, retry logic, and state tracking
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
from autonomous_mcp.executor import ChainExecutor, ExecutionStatus
from autonomous_mcp.planner import ExecutionPlan, ToolCall


class TestChainExecutor:
    """Test the ChainExecutor system"""
    
    def setup_method(self):
        """Setup test instance"""
        self.executor = ChainExecutor()
    
    @pytest.mark.asyncio
    async def test_basic_execution(self):
        """Test basic plan execution"""
        # Create simple plan
        plan = ExecutionPlan(
            id="test_plan",
            description="Test plan",
            tool_calls=[
                ToolCall(
                    tool_name="brave_web_search",
                    tool_id="search_1", 
                    parameters={"query": "test"},
                    order=1
                )
            ]
        )
        
        # Mock mcp_chain response
        mock_response = {"success": True, "data": "test result"}
        
        with patch('autonomous_mcp.executor.mcp_chain') as mock_mcp:
            mock_mcp.return_value = mock_response
            
            result = await self.executor.execute_plan(plan)
            
            assert result.overall_status == ExecutionStatus.SUCCESS
            assert len(result.tool_results) == 1    
    @pytest.mark.asyncio
    async def test_retry_logic(self):
        """Test retry logic on failures"""
        plan = ExecutionPlan(
            id="retry_test",
            description="Retry test",
            tool_calls=[
                ToolCall(
                    tool_name="test_tool",
                    tool_id="retry_1",
                    parameters={"param": "value"}, 
                    order=1
                )
            ]
        )
        
        # Mock failure then success
        with patch('autonomous_mcp.executor.mcp_chain') as mock_mcp:
            mock_mcp.side_effect = [
                Exception("First failure"),
                {"success": True, "data": "success after retry"}
            ]
            
            result = await self.executor.execute_plan(plan)
            
            assert result.overall_status == ExecutionStatus.SUCCESS
            assert mock_mcp.call_count == 2  # Original + 1 retry
    
    @pytest.mark.asyncio 
    async def test_timeout_handling(self):
        """Test timeout handling"""
        plan = ExecutionPlan(
            id="timeout_test",
            description="Timeout test",
            tool_calls=[
                ToolCall(
                    tool_name="slow_tool",
                    tool_id="timeout_1",
                    parameters={"param": "value"},
                    order=1,
                    timeout=0.1  # Very short timeout
                )
            ]
        )
        
        with patch('autonomous_mcp.executor.mcp_chain') as mock_mcp:
            # Simulate slow operation
            async def slow_operation(*args, **kwargs):
                await asyncio.sleep(1.0)  # Longer than timeout
                return {"success": True}
            
            mock_mcp.side_effect = slow_operation
            
            result = await self.executor.execute_plan(plan)
            
            assert result.overall_status == ExecutionStatus.FAILED