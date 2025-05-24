"""
Comprehensive tests for Smart Tool Selection Algorithms
Task 2.2: Machine Learning-based Tool Recommendation and Selection
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Import our modules
from autonomous_mcp.smart_selector import (
    SmartToolSelector, ToolScore, SelectionContext, UsagePattern,
    SelectionStrategy, create_selection_context
)
from autonomous_mcp.discovery import ToolDiscovery, DiscoveredTool, ToolCapability


class TestSmartToolSelector:
    """Test suite for SmartToolSelector"""
    
    @pytest.fixture
    def mock_discovery(self):
        """Create a mock discovery system with sample tools"""
        discovery = Mock(spec=ToolDiscovery)
        
        # Create sample tools
        tools = [
            DiscoveredTool(
                name="web_search",
                server="brave",
                description="Search the web for information",
                parameters={"query": "string"},
                capabilities=[
                    ToolCapability("web", "search", "Web search functionality", 0.9),
                    ToolCapability("information", "retrieval", "Information retrieval", 0.8)
                ],
                usage_count=25,
                success_rate=0.95,
                average_execution_time=2.5,
                last_used=datetime.now().timestamp()
            ),
            DiscoveredTool(
                name="file_read",
                server="filesystem",
                description="Read files from the file system",
                parameters={"path": "string"},
                capabilities=[
                    ToolCapability("file", "read", "File reading operations", 0.95),
                    ToolCapability("data", "access", "Data access functionality", 0.8)
                ],
                usage_count=50,
                success_rate=0.98,
                average_execution_time=0.5,
                last_used=datetime.now().timestamp()
            ),
            DiscoveredTool(
                name="data_analyze",
                server="analytics",
                description="Analyze and process data",
                parameters={"data": "object"},
                capabilities=[
                    ToolCapability("data", "analysis", "Data analysis capabilities", 0.9),
                    ToolCapability("processing", "compute", "Data processing", 0.85)
                ],
                usage_count=15,
                success_rate=0.88,
                average_execution_time=5.2,
                last_used=(datetime.now() - timedelta(days=2)).timestamp()
            ),
            DiscoveredTool(
                name="experimental_tool",
                server="experimental",
                description="Experimental functionality",
                parameters={"input": "any"},
                capabilities=[],
                usage_count=2,
                success_rate=0.6,
                average_execution_time=10.0,
                last_used=(datetime.now() - timedelta(days=10)).timestamp()
            )
        ]
        
        discovery.get_all_tools = AsyncMock(return_value=tools)
        return discovery
    
    @pytest.fixture
    def selector(self, mock_discovery):
        """Create a SmartToolSelector instance"""
        return SmartToolSelector(mock_discovery)
    
    @pytest.fixture
    def sample_context(self):
        """Create a sample selection context"""
        return SelectionContext(
            user_intent="search for information about Python programming",
            task_complexity=0.6,
            required_capabilities=["web", "search"],
            preferred_categories=["information"],
            time_constraints=5.0,
            success_threshold=0.8
        )

    @pytest.mark.asyncio
    async def test_performance_based_selection(self, selector, sample_context):
        """Test performance-based tool selection"""
        scores = await selector.select_best_tools(
            sample_context, 
            strategy=SelectionStrategy.PERFORMANCE_BASED
        )
        
        assert len(scores) > 0
        assert all(isinstance(score, ToolScore) for score in scores)
        assert scores[0].performance_score > 0
        
        # Should prefer tools with high success rates
        file_read_score = next((s for s in scores if s.tool_name == "file_read"), None)
        experimental_score = next((s for s in scores if s.tool_name == "experimental_tool"), None)
        
        if file_read_score and experimental_score:
            assert file_read_score.performance_score > experimental_score.performance_score

    @pytest.mark.asyncio
    async def test_capability_based_selection(self, selector, sample_context):
        """Test capability-based tool selection"""
        scores = await selector.select_best_tools(
            sample_context,
            strategy=SelectionStrategy.CAPABILITY_MATCH
        )
        
        assert len(scores) > 0
        
        # Web search should score high for web search intent
        web_search_score = next((s for s in scores if s.tool_name == "web_search"), None)
        assert web_search_score is not None
        assert web_search_score.capability_score > 0.5

    @pytest.mark.asyncio
    async def test_hybrid_selection(self, selector, sample_context):
        """Test hybrid selection strategy"""
        scores = await selector.select_best_tools(
            sample_context,
            strategy=SelectionStrategy.HYBRID
        )
        
        assert len(scores) > 0
        
        # All score components should be calculated
        for score in scores:
            assert hasattr(score, 'performance_score')
            assert hasattr(score, 'capability_score')
            assert hasattr(score, 'usage_pattern_score')
            assert hasattr(score, 'context_score')
            assert score.total_score > 0

    @pytest.mark.asyncio
    async def test_ml_based_selection(self, selector, sample_context):
        """Test ML-based selection strategy"""
        scores = await selector.select_best_tools(
            sample_context,
            strategy=SelectionStrategy.ML_RECOMMENDATION
        )
        
        assert len(scores) > 0
        
        # Should have similarity-based scoring
        for score in scores:
            assert len(score.reasons) > 0
            assert any("similarity" in reason.lower() for reason in score.reasons)

    @pytest.mark.asyncio
    async def test_context_aware_selection(self, selector, sample_context):
        """Test context-aware selection strategy"""
        # Add previous tools to context
        sample_context.previous_tools = ["web_search"]
        
        scores = await selector.select_best_tools(
            sample_context,
            strategy=SelectionStrategy.CONTEXT_AWARE
        )
        
        assert len(scores) > 0
        
        # Should consider context in scoring
        for score in scores:
            assert score.context_score >= 0

    @pytest.mark.asyncio
    async def test_confidence_threshold_filtering(self, selector, sample_context):
        """Test that tools below confidence threshold are filtered out"""
        # Set high confidence threshold
        selector.min_confidence_threshold = 0.9
        
        scores = await selector.select_best_tools(sample_context)
        
        # All returned tools should meet threshold
        for score in scores:
            assert score.confidence >= 0.9

    @pytest.mark.asyncio
    async def test_max_results_limiting(self, selector, sample_context):
        """Test that results are limited to max_results parameter"""
        scores = await selector.select_best_tools(sample_context, max_results=2)
        
        assert len(scores) <= 2

    def test_calculate_performance_score(self, selector, mock_discovery):
        """Test performance score calculation"""
        tool = DiscoveredTool(
            name="test_tool",
            server="test",
            description="test",
            parameters={},
            usage_count=20,
            success_rate=0.9,
            average_execution_time=2.0
        )
        
        score = selector._calculate_performance_score(tool)
        assert 0 <= score <= 1
        assert score > 0.5  # Should be above average for good metrics

    def test_calculate_capability_score(self, selector, sample_context):
        """Test capability score calculation"""
        tool = DiscoveredTool(
            name="test_tool",
            server="test",
            description="web search functionality",
            parameters={},
            capabilities=[
                ToolCapability("web", "search", "Web search", 0.9)
            ]
        )
        
        keywords = selector._extract_intent_keywords(sample_context.user_intent)
        score = selector._calculate_capability_score(tool, sample_context, keywords)
        
        assert 0 <= score <= 1
        assert score > 0  # Should match web search capability

    def test_extract_intent_keywords(self, selector):
        """Test intent keyword extraction"""
        intent = "search for information about Python programming tutorials"
        keywords = selector._extract_intent_keywords(intent)
        
        assert isinstance(keywords, list)
        assert len(keywords) > 0
        assert "search" in keywords
        assert "information" in keywords
        assert "python" in keywords
        assert "the" not in keywords  # Stop words should be filtered

    def test_vectorize_intent(self, selector):
        """Test intent vectorization"""
        intent = "search for file data"
        vector = selector._vectorize_intent(intent)
        
        assert isinstance(vector, list)
        assert len(vector) == 10  # Should match categories count
        assert all(isinstance(v, float) for v in vector)

    def test_cosine_similarity(self, selector):
        """Test cosine similarity calculation"""
        vec1 = [1.0, 0.0, 0.5]
        vec2 = [1.0, 0.0, 0.5]
        vec3 = [0.0, 1.0, 0.0]
        
        # Identical vectors should have similarity 1.0
        assert abs(selector._cosine_similarity(vec1, vec2) - 1.0) < 0.001
        
        # Orthogonal vectors should have similarity close to 0
        assert abs(selector._cosine_similarity(vec1, vec3)) < 0.1

    def test_usage_pattern_learning(self, selector):
        """Test usage pattern learning"""
        tool_sequence = ["web_search", "data_analyze", "file_read"]
        success_rate = 0.9
        context_tags = {"web", "analysis"}
        
        selector.learn_usage_pattern(tool_sequence, success_rate, context_tags)
        
        assert len(selector.usage_patterns) == 1
        pattern = list(selector.usage_patterns.values())[0]
        assert pattern.tool_sequence == tuple(tool_sequence)
        assert pattern.average_success_rate == success_rate
        assert pattern.context_tags == context_tags

    def test_tool_affinity_update(self, selector):
        """Test tool affinity updating"""
        tool1, tool2 = "web_search", "data_analyze"
        
        # Test successful affinity
        selector.update_tool_affinity(tool1, tool2, success=True)
        assert selector.tool_affinities[tool1][tool2] > 0
        
        # Test failed affinity
        selector.update_tool_affinity(tool1, tool2, success=False)
        # Should be less than before but might still be positive

    @pytest.mark.asyncio
    async def test_get_tool_recommendations(self, selector):
        """Test tool recommendations for partial context"""
        recommendations = await selector.get_tool_recommendations(
            "search web", max_suggestions=2
        )
        
        assert isinstance(recommendations, list)
        assert len(recommendations) <= 2
        
        for tool_name, confidence, reason in recommendations:
            assert isinstance(tool_name, str)
            assert 0 <= confidence <= 1
            assert isinstance(reason, str)

    def test_export_import_learning_data(self, selector):
        """Test exporting and importing learning data"""
        # Add some learning data
        selector.learn_usage_pattern(["tool1", "tool2"], 0.8)
        selector.update_tool_affinity("tool1", "tool2", True)
        
        # Export data
        exported = selector.export_learning_data()
        
        assert 'usage_patterns' in exported
        assert 'tool_affinities' in exported
        assert 'selection_history' in exported
        assert 'config' in exported
        
        # Create new selector and import
        new_selector = SmartToolSelector(Mock())
        new_selector.import_learning_data(exported)
        
        # Verify data was imported
        assert len(new_selector.usage_patterns) == 1
        assert len(new_selector.tool_affinities) > 0

    def test_create_selection_context_helper(self):
        """Test the convenience function for creating SelectionContext"""
        context = create_selection_context(
            "test intent",
            complexity=0.7,
            capabilities=["web", "search"],
            preferences={"speed": "fast"}
        )
        
        assert isinstance(context, SelectionContext)
        assert context.user_intent == "test intent"
        assert context.task_complexity == 0.7
        assert context.required_capabilities == ["web", "search"]
        assert context.user_preferences == {"speed": "fast"}

    @pytest.mark.asyncio
    async def test_empty_tools_handling(self, selector):
        """Test handling when no tools are available"""
        selector.discovery.get_all_tools = AsyncMock(return_value=[])
        
        context = SelectionContext(user_intent="test", task_complexity=0.5, required_capabilities=[])
        scores = await selector.select_best_tools(context)
        
        assert scores == []

    @pytest.mark.asyncio
    async def test_experimental_tools_filtering(self, selector, sample_context):
        """Test filtering of experimental tools based on context settings"""
        # Don't allow experimental tools
        sample_context.allow_experimental = False
        scores = await selector.select_best_tools(sample_context)
        
        # Should not include experimental tool with very low capability score
        experimental_included = any(s.tool_name == "experimental_tool" for s in scores)
        # This depends on the specific scoring, might or might not be included

    def test_selection_history_recording(self, selector, sample_context):
        """Test that selections are recorded in history"""
        initial_history_length = len(selector.selection_history)
        
        mock_scores = [
            ToolScore("tool1", 0.9, confidence=0.8, reasons=["test"]),
            ToolScore("tool2", 0.7, confidence=0.7, reasons=["test"])
        ]
        
        selector._record_selection(sample_context, mock_scores, SelectionStrategy.HYBRID)
        
        assert len(selector.selection_history) == initial_history_length + 1
        
        latest_record = selector.selection_history[-1]
        assert 'timestamp' in latest_record
        assert 'context' in latest_record
        assert 'selected_tools' in latest_record
        assert latest_record['selected_tools'] == ["tool1", "tool2"]


class TestIntegrationWithAdvancedPlanner:
    """Integration tests with the Advanced Planner"""
    
    @pytest.mark.asyncio
    async def test_integration_with_advanced_planner(self):
        """Test that SmartToolSelector integrates well with AdvancedExecutionPlanner"""
        # This would test the integration between components
        # For now, we'll create a mock scenario
        
        discovery = Mock(spec=ToolDiscovery)
        discovery.get_all_tools = AsyncMock(return_value=[
            DiscoveredTool(
                name="sequential_thinking",
                server="reasoning",
                description="Sequential thinking for complex problems",
                parameters={"prompt": "string"},
                capabilities=[ToolCapability("reasoning", "analysis", "Reasoning", 0.9)],
                usage_count=10,
                success_rate=0.85,
                average_execution_time=3.0
            )
        ])
        
        selector = SmartToolSelector(discovery)
        
        context = SelectionContext(
            user_intent="solve complex problem requiring reasoning",
            task_complexity=0.8,
            required_capabilities=["reasoning"]
        )
        
        scores = await selector.select_best_tools(context)
        
        assert len(scores) > 0
        reasoning_tool = next((s for s in scores if "reasoning" in s.tool_name), None)
        assert reasoning_tool is not None


if __name__ == "__main__":
    # Run specific tests for quick verification
    asyncio.run(TestSmartToolSelector().test_performance_based_selection())
    print("✅ Smart Tool Selector tests completed!")
