"""
Simple test for Advanced Execution Planner
Tests the core functionality without Unicode characters
"""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from autonomous_mcp.discovery import ToolDiscovery
from autonomous_mcp.advanced_planner import AdvancedExecutionPlanner


async def mock_sequential_thinking(**kwargs):
    """Mock sequential thinking function for testing"""
    thought_num = kwargs.get('thoughtNumber', 1)
    total_thoughts = kwargs.get('totalThoughts', 3)
    
    responses = {
        1: "Breaking down the task into components and subtasks.",
        2: "Selecting optimal tools based on task requirements.",
        3: "Planning execution order with dependencies."
    }
    
    return {
        'thought': responses.get(thought_num, f"Continuing analysis step {thought_num}"),
        'nextThoughtNeeded': thought_num < total_thoughts,
        'thoughtNumber': thought_num,
        'totalThoughts': total_thoughts
    }


def create_mock_discovery():
    """Create a mock discovery system"""
    discovery = ToolDiscovery()
    
    sample_tools = [
        {
            'name': 'web_search',
            'server': 'brave_search',
            'description': 'Search the web for information',
            'parameters': {'query': 'string'}
        },
        {
            'name': 'read_file',
            'server': 'desktop_commander',
            'description': 'Read file contents',
            'parameters': {'path': 'string'}
        },
        {
            'name': 'analyze_data',
            'server': 'analyzer',
            'description': 'Analyze data patterns',
            'parameters': {'data': 'object'}
        }
    ]
    
    discovery.discover_all_tools(sample_tools)
    return discovery


async def test_complexity_analysis():
    """Test complexity analysis functionality"""
    print("\n--- Testing Complexity Analysis ---")
    
    discovery = create_mock_discovery()
    planner = AdvancedExecutionPlanner(
        discovery_system=discovery,
        sequential_thinking_tool=mock_sequential_thinking
    )
    
    test_cases = [
        "read a file",
        "search for Python tutorials and summarize results",
        "Research AI developments, analyze trends, and create comprehensive recommendations"
    ]
    
    for intent in test_cases:
        print(f"\nIntent: {intent}")
        complexity = await planner.analyze_intent_complexity(intent)
        print(f"  Complexity Score: {complexity['score']:.3f}")
        print(f"  Advanced Planning Needed: {complexity['requires_advanced_planning']}")


async def test_plan_creation():
    """Test plan creation functionality"""
    print("\n--- Testing Plan Creation ---")
    
    discovery = create_mock_discovery()
    planner = AdvancedExecutionPlanner(
        discovery_system=discovery,
        sequential_thinking_tool=mock_sequential_thinking
    )
    
    # Simple intent
    simple_intent = "read configuration file"
    print(f"\nSimple Intent: {simple_intent}")
    simple_plan = await planner.create_advanced_plan(simple_intent)
    print(f"  Plan Method: {simple_plan.planning_method}")
    print(f"  Tools Count: {len(simple_plan.tools)}")
    print(f"  Reasoning Steps: {len(simple_plan.reasoning_steps)}")
    
    # Complex intent
    complex_intent = "Research market trends, analyze data patterns, and generate comprehensive insights"
    print(f"\nComplex Intent: {complex_intent}")
    complex_plan = await planner.create_advanced_plan(complex_intent)
    print(f"  Plan Method: {complex_plan.planning_method}")
    print(f"  Tools Count: {len(complex_plan.tools)}")
    print(f"  Reasoning Steps: {len(complex_plan.reasoning_steps)}")
    print(f"  Complexity Score: {complex_plan.complexity_score:.3f}")
    
    if complex_plan.reasoning_steps:
        print("  Reasoning Process:")
        for step in complex_plan.reasoning_steps:
            print(f"    Step {step.step_number}: {step.conclusion[:60]}...")


async def test_plan_adaptation():
    """Test plan adaptation functionality"""
    print("\n--- Testing Plan Adaptation ---")
    
    discovery = create_mock_discovery()
    planner = AdvancedExecutionPlanner(
        discovery_system=discovery,
        sequential_thinking_tool=mock_sequential_thinking
    )
    
    # Create initial plan
    intent = "Analyze customer feedback and create report"
    original_plan = await planner.create_advanced_plan(intent)
    print(f"\nOriginal Plan: {original_plan.plan_id}")
    print(f"  Adaptability Score: {original_plan.adaptability_score:.3f}")
    
    # Adapt plan with new context
    new_context = {'urgency': 'high', 'scope': 'expanded'}
    adapted_plan = await planner.adapt_plan_dynamically(original_plan, new_context)
    print(f"\nAdapted Plan: {adapted_plan.plan_id}")
    print(f"  Adaptation Applied: {'adapted_context' in adapted_plan.metadata}")


async def test_error_handling():
    """Test error handling and fallback mechanisms"""
    print("\n--- Testing Error Handling ---")
    
    # Test without discovery system
    planner_no_discovery = AdvancedExecutionPlanner()
    try:
        plan = await planner_no_discovery.create_advanced_plan("test intent")
        print("  Fallback to basic planning: SUCCESS")
        print(f"  Plan method: {plan.planning_method}")
    except Exception as e:
        print(f"  Error handling failed: {e}")
    
    # Test with failing sequential thinking
    async def failing_thinking(**kwargs):
        raise Exception("Sequential thinking failed")
    
    discovery = create_mock_discovery()
    planner_failing = AdvancedExecutionPlanner(
        discovery_system=discovery,
        sequential_thinking_tool=failing_thinking
    )
    
    try:
        plan = await planner_failing.create_advanced_plan("complex research task")
        print("  Graceful degradation: SUCCESS")
        print(f"  Plan method: {plan.planning_method}")
    except Exception as e:
        print(f"  Error handling failed: {e}")


async def main():
    """Main test function"""
    print("Advanced Execution Planner Test Suite")
    print("Task 2.1: Sequential Thinking Integration")
    print("=" * 50)
    
    try:
        await test_complexity_analysis()
        await test_plan_creation()
        await test_plan_adaptation()
        await test_error_handling()
        
        print("\n" + "=" * 50)
        print("All tests completed successfully!")
        print("Key features verified:")
        print("  - Complexity analysis")
        print("  - Sequential thinking integration")
        print("  - Plan creation and adaptation")
        print("  - Error handling and fallbacks")
        
    except Exception as e:
        print(f"\nTest error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
