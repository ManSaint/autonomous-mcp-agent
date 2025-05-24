"""
Test Suite for Fallback Management System

Comprehensive tests for intelligent fallback mechanisms including tool alternatives,
plan modifications, and graceful degradation strategies.
"""

import asyncio
import pytest
import time
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch, call

from autonomous_mcp.fallback_manager import (
    FallbackManager, FallbackOption, FallbackChain, FallbackLevel, FallbackReason,
    ToolFallbackStrategy, PlanFallbackStrategy, GracefulDegradationStrategy,
    FallbackExecutionResult
)
from autonomous_mcp.discovery import ToolDiscovery, DiscoveredTool
from autonomous_mcp.planner import ToolCall, ExecutionPlan, BasicExecutionPlanner
from autonomous_mcp.executor import ChainExecutor, ExecutionStatus, ExecutionResult, ExecutionState
from autonomous_mcp.error_recovery import ErrorRecoverySystem


class TestFallbackOption:
    """Test fallback option data structure"""
    
    def test_fallback_option_creation(self):
        """Test creating fallback options"""
        option = FallbackOption(
            level=FallbackLevel.TOOL,
            reason=FallbackReason.TOOL_FAILURE,
            alternative="backup_tool",
            confidence=0.8,
            estimated_cost=1.5,
            description="Backup tool for primary failure",
            success_rate=0.9
        )
        
        assert option.level == FallbackLevel.TOOL
        assert option.reason == FallbackReason.TOOL_FAILURE
        assert option.alternative == "backup_tool"
        assert option.confidence == 0.8
        assert option.estimated_cost == 1.5
        assert option.success_rate == 0.9
    
    def test_fallback_option_to_dict(self):
        """Test converting fallback option to dictionary"""
        option = FallbackOption(
            level=FallbackLevel.PLAN,
            reason=FallbackReason.PERFORMANCE_DEGRADATION,
            alternative="alternative_plan",
            confidence=0.7,
            estimated_cost=2.0,
            description="Alternative execution plan",
            prerequisites=["tool_a", "tool_b"],
            metadata={"strategy": "simplified"}
        )
        
        result = option.to_dict()
        
        assert result['level'] == 'plan'
        assert result['reason'] == 'performance_degradation'
        assert result['alternative'] == 'alternative_plan'
        assert result['confidence'] == 0.7
        assert result['estimated_cost'] == 2.0
        assert result['prerequisites'] == ["tool_a", "tool_b"]
        assert result['metadata'] == {"strategy": "simplified"}


class TestFallbackChain:
    """Test fallback chain functionality"""
    
    def test_fallback_chain_creation(self):
        """Test creating fallback chains"""
        options = [
            FallbackOption(
                level=FallbackLevel.TOOL,
                reason=FallbackReason.TOOL_FAILURE,
                alternative="tool_b",
                confidence=0.8,
                estimated_cost=1.0,
                description="Alternative tool"
            ),
            FallbackOption(
                level=FallbackLevel.PLAN,
                reason=FallbackReason.STRATEGY,
                alternative="plan_b",
                confidence=0.6,
                estimated_cost=2.0,
                description="Alternative plan"
            )
        ]
        
        chain = FallbackChain(
            primary_target="tool_a",
            fallback_options=options,
            total_confidence=0.7,
            execution_order=[0, 1]
        )
        
        assert chain.primary_target == "tool_a"
        assert len(chain.fallback_options) == 2
        assert chain.total_confidence == 0.7
        assert chain.execution_order == [0, 1]
        assert chain.usage_count == 0
        assert chain.success_count == 0
    
    def test_fallback_chain_success_rate(self):
        """Test fallback chain success rate calculation"""
        chain = FallbackChain(
            primary_target="test_target",
            fallback_options=[],
            total_confidence=0.5,
            execution_order=[]
        )
        
        # Initial success rate should be 0
        assert chain.get_success_rate() == 0.0
        
        # Update with some successes and failures
        chain.update_performance(True)
        assert chain.get_success_rate() == 1.0
        
        chain.update_performance(False)
        assert chain.get_success_rate() == 0.5
        
        chain.update_performance(True)
        assert abs(chain.get_success_rate() - 2/3) < 0.001


class TestToolFallbackStrategy:
    """Test tool fallback strategy"""
    
    @pytest.fixture
    def mock_discovery(self):
        """Create mock discovery system with tools"""
        discovery = MagicMock(spec=ToolDiscovery)
        discovery.available_tools = {
            'web_search': DiscoveredTool(
                name='web_search',
                server='test_server',
                description='Search the web for information',
                parameters={},
                capabilities=['search', 'web', 'information']
            ),
            'brave_search': DiscoveredTool(
                name='brave_search',
                server='test_server',
                description='Brave search engine',
                parameters={},
                capabilities=['search', 'web', 'privacy']
            ),
            'file_read': DiscoveredTool(
                name='file_read',
                server='test_server',
                description='Read file contents',
                parameters={},
                capabilities=['read', 'file', 'text']
            ),
            'read_file': DiscoveredTool(
                name='read_file',
                server='test_server',
                description='Alternative file reader',
                parameters={},
                capabilities=['read', 'file', 'binary']
            )
        }
        discovery.performance_data = {
            'brave_search': {
                'success_rate': 0.95,
                'avg_execution_time': 0.8
            },
            'read_file': {
                'success_rate': 0.98,
                'avg_execution_time': 0.2
            }
        }
        return discovery
    
    @pytest.mark.asyncio
    async def test_find_tool_alternatives_by_name(self, mock_discovery):
        """Test finding alternatives for a tool by name"""
        strategy = ToolFallbackStrategy()
        alternatives = await strategy.find_alternatives(
            "web_search", {}, mock_discovery
        )
        
        assert len(alternatives) > 0
        # Should find brave_search as alternative
        alt_names = [alt.alternative for alt in alternatives]
        assert 'brave_search' in alt_names
        
        # Check the alternative properties
        brave_alt = next(alt for alt in alternatives if alt.alternative == 'brave_search')
        assert brave_alt.level == FallbackLevel.TOOL
        assert brave_alt.reason == FallbackReason.TOOL_FAILURE
        assert brave_alt.confidence > 0
        assert brave_alt.success_rate == 0.95
    
    @pytest.mark.asyncio
    async def test_find_tool_alternatives_by_toolcall(self, mock_discovery):
        """Test finding alternatives for a ToolCall"""
        strategy = ToolFallbackStrategy()
        tool_call = ToolCall(
            tool_name="file_read", 
            tool_id="file_read_1",
            parameters={"path": "/test.txt"},
            order=1
        )
        
        alternatives = await strategy.find_alternatives(
            tool_call, {}, mock_discovery
        )
        
        assert len(alternatives) > 0
        alt_names = [alt.alternative for alt in alternatives]
        assert 'read_file' in alt_names
    
    @pytest.mark.asyncio
    async def test_no_alternatives_for_unknown_tool(self, mock_discovery):
        """Test that no alternatives are found for unknown tools"""
        strategy = ToolFallbackStrategy()
        alternatives = await strategy.find_alternatives(
            "unknown_tool", {}, mock_discovery
        )
        
        assert len(alternatives) == 0
    
    @pytest.mark.asyncio
    async def test_alternatives_sorted_by_confidence(self, mock_discovery):
        """Test that alternatives are sorted by confidence"""
        strategy = ToolFallbackStrategy()
        alternatives = await strategy.find_alternatives(
            "web_search", {}, mock_discovery
        )
        
        if len(alternatives) > 1:
            # Should be sorted in descending order of confidence
            for i in range(len(alternatives) - 1):
                assert alternatives[i].confidence >= alternatives[i + 1].confidence


class TestPlanFallbackStrategy:
    """Test plan fallback strategy"""
    
    @pytest.fixture
    def mock_discovery(self):
        """Create mock discovery with performance data"""
        discovery = MagicMock(spec=ToolDiscovery)
        discovery.available_tools = {
            'tool_a': DiscoveredTool(name='tool_a', server='test', description='Tool A', parameters={}),
            'tool_b': DiscoveredTool(name='tool_b', server='test', description='Tool B', parameters={}),
            'tool_c': DiscoveredTool(name='tool_c', server='test', description='Tool C', parameters={})
        }
        discovery.performance_data = {
            'tool_a': {'avg_execution_time': 1.0},
            'tool_b': {'avg_execution_time': 1.5},
            'tool_c': {'avg_execution_time': 0.8}
        }
        return discovery
    
    @pytest.mark.asyncio
    async def test_find_plan_alternatives_with_failed_tools(self, mock_discovery):
        """Test finding plan alternatives when tools have failed"""
        strategy = PlanFallbackStrategy()
        
        # Create a plan with some steps
        plan = ExecutionPlan(
            plan_id="test_plan",
            intent="test execution",
            tools=[
                ToolCall(tool_name="tool_a", tool_id="tool_a_1", parameters={}, order=1),
                ToolCall(tool_name="tool_b", tool_id="tool_b_1", parameters={}, order=2, dependencies=[1]),
                ToolCall(tool_name="tool_c", tool_id="tool_c_1", parameters={}, order=3, dependencies=[2])
            ]
        )
        
        context = {"failed_tools": {"tool_b"}}
        
        with patch.object(ToolFallbackStrategy, 'find_alternatives') as mock_tool_fallback:
            mock_tool_fallback.return_value = [
                FallbackOption(
                    level=FallbackLevel.TOOL,
                    reason=FallbackReason.TOOL_FAILURE,
                    alternative="tool_d",
                    confidence=0.8,
                    estimated_cost=1.2,
                    description="Alternative for tool_b"
                )
            ]
            
            alternatives = await strategy.find_alternatives(plan, context, mock_discovery)
            
            assert len(alternatives) > 0
            # Should have created modified plans
            modified_plan = alternatives[0].alternative
            assert isinstance(modified_plan, ExecutionPlan)
            assert len(modified_plan.tools) == 3
            assert modified_plan.tools[1].tool_name == "tool_d"  # Replaced tool_b
    
    @pytest.mark.asyncio
    async def test_simplify_plan_fallback(self, mock_discovery):
        """Test plan simplification fallback"""
        strategy = PlanFallbackStrategy()
        
        # Create a plan with optional steps (no dependencies pointing to them)
        plan = ExecutionPlan(
            plan_id="test_plan_2",
            intent="test simplification",
            tools=[
                ToolCall(tool_name="tool_a", tool_id="tool_a_1", parameters={}, order=1),  # Essential (has dependent)
                ToolCall(tool_name="tool_b", tool_id="tool_b_1", parameters={}, order=2),  # Optional (no dependents)
                ToolCall(tool_name="tool_c", tool_id="tool_c_1", parameters={}, order=3, dependencies=[1])  # Essential (final step)
            ]
        )
        
        alternatives = await strategy.find_alternatives(plan, {}, mock_discovery)
        
        # Should include simplified plan option
        simplified_options = [alt for alt in alternatives if 'simplified' in alt.description.lower()]
        assert len(simplified_options) > 0
        
        simplified_plan = simplified_options[0].alternative
        assert isinstance(simplified_plan, ExecutionPlan)
        assert len(simplified_plan.tools) < len(plan.tools)
    
    @pytest.mark.asyncio
    async def test_no_plan_alternatives_for_non_plan(self, mock_discovery):
        """Test that plan strategy doesn't work on non-plans"""
        strategy = PlanFallbackStrategy()
        alternatives = await strategy.find_alternatives(
            "just_a_string", {}, mock_discovery
        )
        
        assert len(alternatives) == 0


class TestGracefulDegradationStrategy:
    """Test graceful degradation strategy"""
    
    @pytest.mark.asyncio
    async def test_manual_intervention_option(self):
        """Test manual intervention fallback option"""
        strategy = GracefulDegradationStrategy()
        mock_discovery = MagicMock()
        
        alternatives = await strategy.find_alternatives(
            "any_target", {}, mock_discovery
        )
        
        assert len(alternatives) > 0
        
        # Should include manual intervention option
        manual_options = [alt for alt in alternatives if 'manual' in alt.alternative]
        assert len(manual_options) > 0
        
        manual_option = manual_options[0]
        assert manual_option.level == FallbackLevel.GRACEFUL
        assert manual_option.confidence == 0.9  # High confidence for manual intervention
        assert manual_option.estimated_cost == float('inf')
    
    @pytest.mark.asyncio
    async def test_partial_results_option(self):
        """Test partial results fallback option"""
        strategy = GracefulDegradationStrategy()
        mock_discovery = MagicMock()
        
        context = {
            'partial_results': {'data': 'some partial data'},
            'completion_percentage': 60
        }
        
        alternatives = await strategy.find_alternatives(
            "any_target", context, mock_discovery
        )
        
        # Should include partial results option
        partial_options = [alt for alt in alternatives if 'partial' in alt.alternative]
        assert len(partial_options) > 0
        
        partial_option = partial_options[0]
        assert partial_option.level == FallbackLevel.GRACEFUL
        assert partial_option.estimated_cost == 0.0
        assert 'partial_data' in partial_option.metadata
    
    @pytest.mark.asyncio
    async def test_alternative_approach_suggestion(self):
        """Test alternative approach suggestion"""
        strategy = GracefulDegradationStrategy()
        mock_discovery = MagicMock()
        
        alternatives = await strategy.find_alternatives(
            "any_target", {}, mock_discovery
        )
        
        # Should include suggestion option
        suggestion_options = [alt for alt in alternatives if 'suggest' in alt.alternative]
        assert len(suggestion_options) > 0
        
        suggestion_option = suggestion_options[0]
        assert suggestion_option.level == FallbackLevel.GRACEFUL
        assert 'suggestions' in suggestion_option.metadata
        assert len(suggestion_option.metadata['suggestions']) > 0


class TestFallbackManager:
    """Test the main fallback manager"""
    
    @pytest.fixture
    def mock_discovery(self):
        """Create comprehensive mock discovery"""
        discovery = MagicMock(spec=ToolDiscovery)
        discovery.available_tools = {
            'primary_tool': DiscoveredTool(
                name='primary_tool',
                server='test',
                description='Primary tool',
                parameters={},
                capabilities=['primary', 'test']
            ),
            'backup_tool': DiscoveredTool(
                name='backup_tool',
                server='test',
                description='Backup tool',
                parameters={},
                capabilities=['backup', 'test']
            )
        }
        discovery.performance_data = {
            'primary_tool': {'success_rate': 0.9, 'avg_execution_time': 1.0},
            'backup_tool': {'success_rate': 0.8, 'avg_execution_time': 1.2}
        }
        return discovery
    
    @pytest.fixture
    def fallback_manager(self, mock_discovery):
        """Create fallback manager for testing"""
        return FallbackManager(discovery=mock_discovery)
    
    def test_fallback_manager_initialization(self, fallback_manager):
        """Test fallback manager initialization"""
        assert fallback_manager is not None
        assert len(fallback_manager.strategies) >= 3  # Should have default strategies
        assert 'tool' in fallback_manager.strategies
        assert 'plan' in fallback_manager.strategies
        assert 'graceful' in fallback_manager.strategies
    
    @pytest.mark.asyncio
    async def test_create_fallback_chain(self, fallback_manager):
        """Test creating fallback chains"""
        chain = await fallback_manager.create_fallback_chain(
            "primary_tool", {"test": "context"}
        )
        
        assert isinstance(chain, FallbackChain)
        assert chain.primary_target == "primary_tool"
        assert len(chain.fallback_options) > 0
        assert chain.total_confidence >= 0.0
        assert len(chain.execution_order) == len(chain.fallback_options)
    
    @pytest.mark.asyncio
    async def test_execute_with_fallback_success(self, fallback_manager):
        """Test successful execution with fallback manager"""
        mock_executor = AsyncMock(spec=ChainExecutor)
        mock_mcp_chain = AsyncMock()
        
        # Create a mock ExecutionState that represents success
        mock_state = MagicMock(spec=ExecutionState)
        mock_state.status = ExecutionStatus.SUCCESS
        mock_state.total_execution_time = 1.0
        mock_state.results = {}
        
        # Create a mock plan
        mock_plan = MagicMock()
        mock_plan.plan_id = "test_plan"
        mock_state.plan = mock_plan
        
        mock_executor.execute_plan.return_value = mock_state
        
        result = await fallback_manager.execute_with_fallback(
            "primary_tool", {}, mock_executor, mock_mcp_chain
        )
        
        assert result.status == ExecutionStatus.SUCCESS
        assert mock_executor.execute_plan.call_count == 1
    
    @pytest.mark.asyncio
    async def test_execute_with_fallback_uses_alternatives(self, fallback_manager):
        """Test that fallback alternatives are used when primary fails"""
        mock_executor = AsyncMock(spec=ChainExecutor)
        mock_mcp_chain = AsyncMock()
        
        # Create mock ExecutionState that represents success
        mock_success_state = MagicMock(spec=ExecutionState)
        mock_success_state.status = ExecutionStatus.SUCCESS
        mock_success_state.total_execution_time = 1.5
        mock_success_state.results = {}
        
        # Create a mock plan
        mock_plan = MagicMock()
        mock_plan.plan_id = "fallback_plan"
        mock_success_state.plan = mock_plan
        
        # First call fails, second succeeds
        mock_executor.execute_plan.side_effect = [
            Exception("Primary failed"),
            mock_success_state
        ]
        
        result = await fallback_manager.execute_with_fallback(
            "primary_tool", {}, mock_executor, mock_mcp_chain
        )
        
        assert result.status == ExecutionStatus.SUCCESS
        assert mock_executor.execute_plan.call_count >= 2
        assert 'fallback_used' in result.metadata
    
    @pytest.mark.asyncio
    async def test_execute_with_all_fallbacks_failing(self, fallback_manager):
        """Test behavior when all fallbacks fail"""
        mock_executor = AsyncMock(spec=ChainExecutor)
        mock_mcp_chain = AsyncMock()
        mock_executor.execute_plan.side_effect = Exception("All failed")
        
        result = await fallback_manager.execute_with_fallback(
            "primary_tool", {}, mock_executor, mock_mcp_chain
        )
        
        assert result.status == ExecutionStatus.FAILED
        assert "exhausted" in result.error_message.lower()
    
    def test_get_fallback_statistics(self, fallback_manager):
        """Test getting fallback statistics"""
        # Add some usage data
        fallback_manager.fallback_usage['tool'] = 10
        fallback_manager.fallback_success['tool'] = 8
        fallback_manager.fallback_usage['plan'] = 5
        fallback_manager.fallback_success['plan'] = 3
        
        stats = fallback_manager.get_fallback_statistics()
        
        assert 'total_fallback_usage' in stats
        assert 'total_fallback_success' in stats
        assert 'overall_fallback_success_rate' in stats
        assert 'usage_by_level' in stats
        assert 'success_by_level' in stats
        assert 'success_rates_by_level' in stats
        
        assert stats['total_fallback_usage'] == 15
        assert stats['total_fallback_success'] == 11
        assert abs(stats['overall_fallback_success_rate'] - 11/15) < 0.001
        assert stats['success_rates_by_level']['tool'] == 0.8
        assert stats['success_rates_by_level']['plan'] == 0.6
    
    def test_add_custom_strategy(self, fallback_manager):
        """Test adding custom fallback strategies"""
        class CustomStrategy(ToolFallbackStrategy):
            def get_strategy_name(self):
                return "custom_strategy"
        
        custom_strategy = CustomStrategy()
        fallback_manager.add_custom_strategy("custom", custom_strategy)
        
        assert "custom" in fallback_manager.strategies
        assert fallback_manager.strategies["custom"] == custom_strategy
    
    def test_remove_strategy(self, fallback_manager):
        """Test removing fallback strategies"""
        initial_count = len(fallback_manager.strategies)
        fallback_manager.remove_strategy("tool")
        
        assert "tool" not in fallback_manager.strategies
        assert len(fallback_manager.strategies) == initial_count - 1
    
    def test_clear_cache(self, fallback_manager):
        """Test clearing fallback chain cache"""
        # Add some cached chains
        fallback_manager.fallback_chains["test1"] = MagicMock()
        fallback_manager.fallback_chains["test2"] = MagicMock()
        
        assert len(fallback_manager.fallback_chains) == 2
        
        fallback_manager.clear_cache()
        
        assert len(fallback_manager.fallback_chains) == 0


if __name__ == '__main__':
    pytest.main([__file__])
