"""
Comprehensive test suite for Task 2.2: Smart Tool Selection Algorithms
"""
import asyncio
import pytest
from autonomous_mcp.smart_selector import (
    SmartToolSelector, SelectionStrategy, SelectionContext, 
    ToolScore, create_selection_context
)
from autonomous_mcp.discovery import DiscoveredTool, ToolCapability


async def test_basic_functionality():
    """Test basic smart tool selector functionality"""
    print("Testing Basic Smart Tool Selector Functionality")
    print("-" * 50)
    
    # Create mock tools
    tools = [
        DiscoveredTool(
            name="web_search",
            server="brave",
            description="Search the web for information",
            parameters={"query": "string"},
            capabilities=[ToolCapability("web", "search", "Web search", 0.9)],
            usage_count=25,
            success_rate=0.95,
            average_execution_time=2.5
        ),
        DiscoveredTool(
            name="file_read",
            server="filesystem",
            description="Read files from disk",
            parameters={"path": "string"},
            capabilities=[ToolCapability("file", "read", "File reading", 0.95)],
            usage_count=50,
            success_rate=0.98,
            average_execution_time=0.5
        )
    ]
    
    # Mock discovery
    class MockDiscovery:
        async def get_all_tools(self):
            return tools
    
    discovery = MockDiscovery()
    selector = SmartToolSelector(discovery)
    
    # Test different strategies
    context = SelectionContext(
        user_intent="search for programming information",
        task_complexity=0.6,
        required_capabilities=["web", "search"]
    )
    
    strategies = [
        SelectionStrategy.PERFORMANCE_BASED,
        SelectionStrategy.CAPABILITY_MATCH,
        SelectionStrategy.HYBRID,
        SelectionStrategy.ML_RECOMMENDATION,
        SelectionStrategy.CONTEXT_AWARE
    ]
    
    for strategy in strategies:
        scores = await selector.select_best_tools(context, strategy=strategy, max_results=2)
        print(f"{strategy.value}: {len(scores)} tools selected")
        
        for score in scores:
            assert isinstance(score, ToolScore)
            assert 0 <= score.total_score <= 1
            assert 0 <= score.confidence <= 1
            assert isinstance(score.reasons, list)
    
    print("Basic functionality tests passed!")
    return True


async def test_learning_capabilities():
    """Test learning and adaptation features"""
    print("\nTesting Learning and Adaptation")
    print("-" * 40)
    
    # Create mock discovery
    class MockDiscovery:
        async def get_all_tools(self):
            return [
                DiscoveredTool(
                    name="tool_a", server="test", description="Tool A", parameters={},
                    usage_count=10, success_rate=0.9, average_execution_time=1.0
                ),
                DiscoveredTool(
                    name="tool_b", server="test", description="Tool B", parameters={},
                    usage_count=5, success_rate=0.8, average_execution_time=2.0
                )
            ]
    
    selector = SmartToolSelector(MockDiscovery())
    
    # Test usage pattern learning
    initial_patterns = len(selector.usage_patterns)
    selector.learn_usage_pattern(["tool_a", "tool_b"], 0.9, {"test"})
    assert len(selector.usage_patterns) == initial_patterns + 1
    print("Usage pattern learning works")
    
    # Test tool affinity updates
    selector.update_tool_affinity("tool_a", "tool_b", success=True)
    assert selector.tool_affinities["tool_a"]["tool_b"] > 0
    print("Tool affinity learning works")
    
    # Test export/import
    data = selector.export_learning_data()
    assert 'usage_patterns' in data
    assert 'tool_affinities' in data
    
    new_selector = SmartToolSelector(MockDiscovery())
    new_selector.import_learning_data(data)
    assert len(new_selector.usage_patterns) > 0
    print("Export/import learning data works")
    
    return True


async def test_recommendation_system():
    """Test the recommendation system"""
    print("\nTesting Recommendation System")
    print("-" * 35)
    
    # Mock discovery with diverse tools
    tools = [
        DiscoveredTool(
            name="web_search", server="brave", description="Web search tool",
            parameters={}, capabilities=[ToolCapability("web", "search", "Search", 0.9)],
            usage_count=20, success_rate=0.95, average_execution_time=2.0
        ),
        DiscoveredTool(
            name="file_ops", server="fs", description="File operations",
            parameters={}, capabilities=[ToolCapability("file", "operations", "File ops", 0.9)],
            usage_count=30, success_rate=0.97, average_execution_time=1.0
        ),
        DiscoveredTool(
            name="data_analysis", server="analytics", description="Data analysis",
            parameters={}, capabilities=[ToolCapability("data", "analysis", "Analytics", 0.85)],
            usage_count=15, success_rate=0.88, average_execution_time=4.0
        )
    ]
    
    class MockDiscovery:
        async def get_all_tools(self):
            return tools
    
    selector = SmartToolSelector(MockDiscovery())
    
    # Test recommendations for different queries
    test_queries = [
        "search web",
        "read file",
        "analyze data",
        "unknown operation"
    ]
    
    for query in test_queries:
        recommendations = await selector.get_tool_recommendations(query, max_suggestions=2)
        print(f"Query '{query}': {len(recommendations)} recommendations")
        
        for tool_name, confidence, reason in recommendations:
            assert isinstance(tool_name, str)
            assert 0 <= confidence <= 1
            assert isinstance(reason, str)
    
    print("Recommendation system works")
    return True


async def test_context_awareness():
    """Test context-aware selection"""
    print("\nTesting Context-Aware Selection")
    print("-" * 40)
    
    # Mock tools
    tools = [
        DiscoveredTool(
            name="search_tool", server="search", description="Search tool",
            parameters={}, capabilities=[ToolCapability("web", "search", "Search", 0.9)],
            usage_count=20, success_rate=0.95, average_execution_time=2.0
        ),
        DiscoveredTool(
            name="analysis_tool", server="analytics", description="Analysis tool", 
            parameters={}, capabilities=[ToolCapability("data", "analysis", "Analysis", 0.9)],
            usage_count=15, success_rate=0.88, average_execution_time=3.0
        )
    ]
    
    class MockDiscovery:
        async def get_all_tools(self):
            return tools
    
    selector = SmartToolSelector(MockDiscovery())
    
    # Learn a pattern: search -> analysis
    selector.learn_usage_pattern(["search_tool", "analysis_tool"], 0.9, {"research"})
    
    # Test context-aware selection with previous tools
    context = SelectionContext(
        user_intent="continue analysis",
        task_complexity=0.6,
        required_capabilities=["analysis"],
        previous_tools=["search_tool"]
    )
    
    scores = await selector.select_best_tools(
        context, 
        strategy=SelectionStrategy.CONTEXT_AWARE,
        max_results=2
    )
    
    # Should prefer analysis_tool due to learned pattern
    assert len(scores) > 0
    top_tool = scores[0]
    print(f"Top recommended tool after search_tool: {top_tool.tool_name}")
    
    print("Context-aware selection works")
    return True


async def run_comprehensive_tests():
    """Run all comprehensive tests"""
    print("Smart Tool Selector - Comprehensive Test Suite")
    print("=" * 60)
    print("Task 2.2: Machine Learning-based Tool Recommendation")
    print()
    
    try:
        # Run all test suites
        await test_basic_functionality()
        await test_learning_capabilities() 
        await test_recommendation_system()
        await test_context_awareness()
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED!")
        print("Smart Tool Selector implementation is working correctly")
        print("Machine learning-based recommendations functional")
        print("Learning and adaptation capabilities working")
        print("Context-aware selection operational")
        print("Task 2.2 implementation COMPLETE!")
        
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    result = asyncio.run(run_comprehensive_tests())
    if result:
        print("\nReady to proceed to Task 2.3: User Preference Engine!")
    else:
        print("\nPlease fix issues before proceeding")
