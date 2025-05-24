"""
Test suite for Advanced Execution Planner
Task 2.1: Tests for Sequential Thinking integration and advanced planning features
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from autonomous_mcp.advanced_planner import (
    AdvancedExecutionPlanner, 
    EnhancedExecutionPlan, 
    ReasoningStep
)
from autonomous_mcp.planner import ToolCall, ExecutionPlan


class TestAdvancedExecutionPlanner:
    """Test cases for the AdvancedExecutionPlanner class"""
    
    @pytest.fixture
    def mock_discovery_system(self):
        """Mock discovery system for testing"""
        mock_discovery = Mock()
        
        # Mock tool with required attributes
        mock_tool = Mock()
        mock_tool.name = "test_tool"
        mock_tool.description = "Test tool description"
        mock_tool.capabilities = [Mock(confidence=0.8)]
        mock_tool.__dict__ = {
            'name': 'test_tool',
            'category': 'test',
            'description': 'Test tool'
        }
        
        mock_discovery.get_tools_for_intent.return_value = [mock_tool]
        mock_discovery.tools = {'test_tool': {'name': 'test_tool'}}
        
        return mock_discovery
    
    @pytest.fixture
    def mock_sequential_thinking(self):
        """Mock sequential thinking tool for testing"""
        async def mock_thinking(**kwargs):
            return {
                'thought': f"Mock thought: {kwargs.get('thought', 'default')}",
                'nextThoughtNeeded': kwargs.get('thoughtNumber', 1) < kwargs.get('totalThoughts', 1),
                'thoughtNumber': kwargs.get('thoughtNumber', 1),
                'totalThoughts': kwargs.get('totalThoughts', 1)
            }
        
        return mock_thinking
    
    @pytest.fixture
    def advanced_planner(self, mock_discovery_system, mock_sequential_thinking):
        """Create AdvancedExecutionPlanner instance for testing"""
        return AdvancedExecutionPlanner(
            discovery_system=mock_discovery_system,
            sequential_thinking_tool=mock_sequential_thinking
        )
    
    def test_init(self, advanced_planner):
        """Test planner initialization"""
        assert advanced_planner.complexity_threshold == 0.6
        assert advanced_planner.reasoning_timeout == 30.0
        assert len(advanced_planner.complex_keywords) > 0
        assert len(advanced_planner.complexity_patterns) > 0
    
    @pytest.mark.asyncio
    async def test_analyze_intent_complexity_simple(self, advanced_planner):
        """Test complexity analysis for simple intents"""
        simple_intent = "read a file"
        
        complexity = await advanced_planner.analyze_intent_complexity(simple_intent)
        
        assert complexity['score'] < 0.6  # Should be below threshold
        assert not complexity['requires_advanced_planning']
        assert 'factors' in complexity
        assert 'reasoning' in complexity
    
    @pytest.mark.asyncio
    async def test_analyze_intent_complexity_complex(self, advanced_planner):
        """Test complexity analysis for complex intents"""
        complex_intent = "Research and analyze multiple sources, then create a comprehensive report comparing different approaches and synthesize recommendations"
        
        complexity = await advanced_planner.analyze_intent_complexity(complex_intent)
        
        assert complexity['score'] >= 0.6  # Should be above threshold
        assert complexity['requires_advanced_planning']
        assert complexity['factors']['complex_keywords'] > 0
        assert complexity['factors']['length_complexity'] > 0
    
    @pytest.mark.asyncio
    async def test_analyze_intent_complexity_with_context(self, advanced_planner):
        """Test complexity analysis with additional context"""
        intent = "analyze data"
        context = {'data_sources': ['api1', 'api2'], 'output_format': 'report'}
        
        complexity = await advanced_planner.analyze_intent_complexity(intent, context)
        
        assert 'context_complexity' in complexity['factors']
        assert complexity['factors']['context_complexity'] > 0
    
    @pytest.mark.asyncio
    async def test_create_advanced_plan_simple(self, advanced_planner):
        """Test creating an advanced plan for simple intent"""
        simple_intent = "list files"
        
        plan = await advanced_planner.create_advanced_plan(simple_intent)
        
        assert isinstance(plan, EnhancedExecutionPlan)
        assert plan.planning_method == "basic"
        assert plan.complexity_score < 0.6
        assert len(plan.reasoning_steps) == 0
    
    @pytest.mark.asyncio
    async def test_create_advanced_plan_complex(self, advanced_planner):
        """Test creating an advanced plan for complex intent"""
        complex_intent = "Research AI developments, analyze impact, and create comprehensive recommendations"
        
        plan = await advanced_planner.create_advanced_plan(complex_intent)
        
        assert isinstance(plan, EnhancedExecutionPlan)
        assert plan.planning_method == "sequential_thinking"
        assert plan.complexity_score >= 0.6
        assert len(plan.reasoning_steps) > 0
    
    @pytest.mark.asyncio
    async def test_create_reasoning_based_plan(self, advanced_planner):
        """Test creating a plan with reasoning"""
        intent = "Analyze and compare multiple data sources"
        context = {'sources': ['api1', 'api2']}
        complexity_analysis = {'score': 0.8, 'factors': {}, 'reasoning': 'Complex task'}
        
        plan = await advanced_planner.create_reasoning_based_plan(intent, context, complexity_analysis)
        
        assert isinstance(plan, EnhancedExecutionPlan)
        assert plan.planning_method == "sequential_thinking"
        assert len(plan.reasoning_steps) == 3  # decomposition, tool selection, execution order
        assert plan.complexity_score == 0.8
    
    @pytest.mark.asyncio
    async def test_reason_about_task_decomposition(self, advanced_planner):
        """Test task decomposition reasoning"""
        intent = "Research and analyze AI trends"
        context = {'timeframe': '2024'}
        
        reasoning_step = await advanced_planner._reason_about_task_decomposition(intent, context)
        
        assert isinstance(reasoning_step, ReasoningStep)
        assert reasoning_step.step_number == 1
        assert len(reasoning_step.thought) > 0
        assert len(reasoning_step.conclusion) > 0
        assert 0 <= reasoning_step.confidence <= 1
    
    @pytest.mark.asyncio
    async def test_reason_about_tool_selection(self, advanced_planner):
        """Test tool selection reasoning"""
        subtasks = "Task 1: Research, Task 2: Analyze, Task 3: Report"
        intent = "Research AI trends"
        context = {}
        
        reasoning_step = await advanced_planner._reason_about_tool_selection(subtasks, intent, context)
        
        assert isinstance(reasoning_step, ReasoningStep)
        assert reasoning_step.step_number == 2
        assert reasoning_step.confidence > 0
    
    @pytest.mark.asyncio
    async def test_reason_about_execution_order(self, advanced_planner):
        """Test execution order reasoning"""
        tool_selection = "Use search tool, then analysis tool, then report tool"
        subtasks = "Task 1, Task 2, Task 3"
        
        reasoning_step = await advanced_planner._reason_about_execution_order(tool_selection, subtasks)
        
        assert isinstance(reasoning_step, ReasoningStep)
        assert reasoning_step.step_number == 3
        assert reasoning_step.confidence > 0
    
    @pytest.mark.asyncio
    async def test_call_sequential_thinking(self, advanced_planner):
        """Test calling sequential thinking tool"""
        prompt = "Test reasoning prompt"
        max_thoughts = 2
        
        result = await advanced_planner._call_sequential_thinking(prompt, max_thoughts)
        
        assert 'thoughts' in result
        assert 'final_thought' in result
        assert 'total_steps' in result
        assert len(result['thoughts']) <= max_thoughts
    
    @pytest.mark.asyncio
    async def test_call_sequential_thinking_timeout(self, advanced_planner):
        """Test sequential thinking timeout handling"""
        # Mock a slow sequential thinking function
        async def slow_thinking(**kwargs):
            await asyncio.sleep(100)  # Longer than timeout
            return {'thought': 'slow'}
        
        advanced_planner.sequential_thinking_tool = slow_thinking
        advanced_planner.reasoning_timeout = 0.1  # Very short timeout
        
        result = await advanced_planner._call_sequential_thinking("test prompt", 1)
        
        assert 'error' in result
        assert 'Timeout' in result['error']
    
    def test_create_tool_calls_from_reasoning(self, advanced_planner):
        """Test creating tool calls from reasoning steps"""
        reasoning_steps = [
            ReasoningStep(1, "Decompose task", "Task 1, Task 2", 0.8),
            ReasoningStep(2, "Select tools", "Use tool A, tool B", 0.7),
            ReasoningStep(3, "Order execution", "A then B", 0.9)
        ]
        intent = "Test intent"
        context = {}
        
        tool_calls = advanced_planner._create_tool_calls_from_reasoning(reasoning_steps, intent, context)
        
        assert isinstance(tool_calls, list)
        assert len(tool_calls) > 0
        for tool_call in tool_calls:
            assert isinstance(tool_call, ToolCall)
    
    def test_calculate_reasoning_confidence(self, advanced_planner):
        """Test reasoning confidence calculation"""
        reasoning_steps = [
            ReasoningStep(1, "thought1", "conclusion1", 0.8),
            ReasoningStep(2, "thought2", "conclusion2", 0.6),
            ReasoningStep(3, "thought3", "conclusion3", 0.9)
        ]
        
        confidence = advanced_planner._calculate_reasoning_confidence(reasoning_steps)
        
        assert confidence == (0.8 + 0.6 + 0.9) / 3
    
    def test_calculate_reasoning_confidence_empty(self, advanced_planner):
        """Test reasoning confidence calculation with empty steps"""
        confidence = advanced_planner._calculate_reasoning_confidence([])
        assert confidence == 0.0
    
    def test_convert_to_enhanced_plan(self, advanced_planner):
        """Test converting basic plan to enhanced plan"""
        basic_plan = ExecutionPlan(
            plan_id="test_plan",
            intent="test intent",
            tools=[]
        )
        complexity_analysis = {'score': 0.5, 'reasoning': 'Test'}
        
        enhanced_plan = advanced_planner._convert_to_enhanced_plan(basic_plan, complexity_analysis)
        
        assert isinstance(enhanced_plan, EnhancedExecutionPlan)
        assert enhanced_plan.plan_id == basic_plan.plan_id
        assert enhanced_plan.intent == basic_plan.intent
        assert enhanced_plan.complexity_score == 0.5
        assert enhanced_plan.planning_method == "basic"
    
    @pytest.mark.asyncio
    async def test_optimize_advanced_plan(self, advanced_planner):
        """Test optimizing an advanced plan"""
        plan = EnhancedExecutionPlan(
            plan_id="test_plan",
            intent="test intent",
            tools=[
                ToolCall("tool1", "tool1", {}, 0),
                ToolCall("tool2", "tool2", {}, 1, [0])
            ]
        )
        
        optimized_plan = await advanced_planner.optimize_advanced_plan(plan)
        
        assert isinstance(optimized_plan, EnhancedExecutionPlan)
        assert hasattr(optimized_plan, 'adaptability_score')
        assert 0 <= optimized_plan.adaptability_score <= 1
    
    def test_calculate_adaptability_score(self, advanced_planner):
        """Test adaptability score calculation"""
        plan = EnhancedExecutionPlan(
            plan_id="test_plan",
            intent="test intent",
            tools=[
                ToolCall("tool1", "tool1", {}, 0),
                ToolCall("tool2", "tool2", {}, 1, [0])
            ],
            reasoning_steps=[
                ReasoningStep(1, "thought", "conclusion", 0.8)
            ],
            confidence_score=0.7
        )
        
        score = advanced_planner._calculate_adaptability_score(plan)
        
        assert 0 <= score <= 1
        assert isinstance(score, float)
    
    @pytest.mark.asyncio
    async def test_adapt_plan_dynamically(self, advanced_planner):
        """Test dynamic plan adaptation"""
        original_plan = EnhancedExecutionPlan(
            plan_id="test_plan",
            intent="test intent",
            tools=[ToolCall("tool1", "tool1", {}, 0)],
            planning_method="sequential_thinking",
            adaptability_score=0.8
        )
        new_context = {'priority': 'high', 'deadline': '2024-01-01'}
        
        adapted_plan = await advanced_planner.adapt_plan_dynamically(original_plan, new_context)
        
        assert isinstance(adapted_plan, EnhancedExecutionPlan)
        assert 'adapted_context' in adapted_plan.metadata
    
    @pytest.mark.asyncio
    async def test_adapt_plan_low_adaptability(self, advanced_planner):
        """Test plan adaptation with low adaptability score"""
        original_plan = EnhancedExecutionPlan(
            plan_id="test_plan",
            intent="test intent",
            tools=[ToolCall("tool1", "tool1", {}, 0)],
            adaptability_score=0.2  # Low adaptability
        )
        new_context = {'change': 'significant'}
        
        adapted_plan = await advanced_planner.adapt_plan_dynamically(original_plan, new_context)
        
        # Should return original plan unchanged
        assert adapted_plan.plan_id == original_plan.plan_id
    
    def test_simple_adaptation(self, advanced_planner):
        """Test simple plan adaptation"""
        original_plan = EnhancedExecutionPlan(
            plan_id="test_plan",
            intent="test intent",
            tools=[ToolCall("tool1", "tool1", {}, 0)]
        )
        new_context = {'update': 'minor'}
        
        adapted_plan = advanced_planner._simple_adaptation(original_plan, new_context)
        
        assert isinstance(adapted_plan, EnhancedExecutionPlan)
        assert 'adapted_context' in adapted_plan.metadata
        assert adapted_plan.plan_id.endswith('_simple_adapted')


class TestEnhancedExecutionPlan:
    """Test cases for the EnhancedExecutionPlan class"""
    
    def test_enhanced_plan_creation(self):
        """Test creating an enhanced execution plan"""
        plan = EnhancedExecutionPlan(
            plan_id="test_plan",
            intent="test intent",
            tools=[ToolCall("tool1", "tool1", {}, 0)],
            reasoning_steps=[ReasoningStep(1, "thought", "conclusion", 0.8)],
            complexity_score=0.7,
            planning_method="sequential_thinking"
        )
        
        assert plan.plan_id == "test_plan"
        assert plan.complexity_score == 0.7
        assert plan.planning_method == "sequential_thinking"
        assert len(plan.reasoning_steps) == 1
    
    def test_enhanced_plan_to_dict(self):
        """Test converting enhanced plan to dictionary"""
        plan = EnhancedExecutionPlan(
            plan_id="test_plan",
            intent="test intent",
            tools=[ToolCall("tool1", "tool1", {}, 0)],
            reasoning_steps=[ReasoningStep(1, "thought", "conclusion", 0.8)],
            complexity_score=0.7,
            planning_method="sequential_thinking"
        )
        
        plan_dict = plan.to_dict()
        
        assert 'reasoning_steps' in plan_dict
        assert 'complexity_score' in plan_dict
        assert 'planning_method' in plan_dict
        assert 'adaptability_score' in plan_dict
        assert plan_dict['complexity_score'] == 0.7
        assert plan_dict['planning_method'] == "sequential_thinking"


class TestReasoningStep:
    """Test cases for the ReasoningStep class"""
    
    def test_reasoning_step_creation(self):
        """Test creating a reasoning step"""
        step = ReasoningStep(
            step_number=1,
            thought="This is a test thought",
            conclusion="This is the conclusion",
            confidence=0.8,
            metadata={'source': 'test'}
        )
        
        assert step.step_number == 1
        assert step.thought == "This is a test thought"
        assert step.conclusion == "This is the conclusion"
        assert step.confidence == 0.8
        assert step.metadata['source'] == 'test'


# Integration tests
class TestAdvancedPlannerIntegration:
    """Integration tests for the advanced planner"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_planning_simple(self):
        """Test end-to-end planning for simple intent"""
        # Mock sequential thinking
        async def mock_thinking(**kwargs):
            return {
                'thought': f"Mock thought for: {kwargs.get('thought', '')}",
                'nextThoughtNeeded': False
            }
        
        # Mock discovery
        mock_discovery = Mock()
        mock_tool = Mock()
        mock_tool.name = "simple_tool"
        mock_tool.description = "Simple test tool"
        mock_tool.capabilities = [Mock(confidence=0.7)]
        mock_tool.__dict__ = {'name': 'simple_tool', 'category': 'test'}
        mock_discovery.get_tools_for_intent.return_value = [mock_tool]
        
        planner = AdvancedExecutionPlanner(
            discovery_system=mock_discovery,
            sequential_thinking_tool=mock_thinking
        )
        
        plan = await planner.create_advanced_plan("read a file")
        
        assert isinstance(plan, EnhancedExecutionPlan)
        assert plan.planning_method == "basic"  # Simple intent uses basic planning
    
    @pytest.mark.asyncio
    async def test_end_to_end_planning_complex(self):
        """Test end-to-end planning for complex intent"""
        # Mock sequential thinking
        async def mock_thinking(**kwargs):
            return {
                'thought': f"Complex reasoning: {kwargs.get('thought', '')}",
                'nextThoughtNeeded': kwargs.get('thoughtNumber', 1) < 2
            }
        
        # Mock discovery
        mock_discovery = Mock()
        mock_tool = Mock()
        mock_tool.name = "complex_tool"
        mock_tool.description = "Complex analysis tool"
        mock_tool.capabilities = [Mock(confidence=0.9)]
        mock_tool.__dict__ = {'name': 'complex_tool', 'category': 'analysis'}
        mock_discovery.get_tools_for_intent.return_value = [mock_tool]
        
        planner = AdvancedExecutionPlanner(
            discovery_system=mock_discovery,
            sequential_thinking_tool=mock_thinking
        )
        
        complex_intent = "Research AI developments, analyze trends, and create comprehensive recommendations"
        plan = await planner.create_advanced_plan(complex_intent)
        
        assert isinstance(plan, EnhancedExecutionPlan)
        assert plan.planning_method == "sequential_thinking"  # Complex intent uses advanced planning
        assert len(plan.reasoning_steps) > 0
        assert plan.complexity_score >= 0.6


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__])
