"""
Demo script for Advanced Execution Planner
Task 2.1: Demonstrates Sequential Thinking integration and advanced planning
"""

import asyncio
import json
from autonomous_mcp.discovery import ToolDiscovery
from autonomous_mcp.advanced_planner import AdvancedExecutionPlanner


async def mock_sequential_thinking(**kwargs):
    """
    Mock sequential thinking function for demonstration
    In production, this would call the actual sequential thinking tool
    """
    thought_num = kwargs.get('thoughtNumber', 1)
    total_thoughts = kwargs.get('totalThoughts', 3)
    prompt = kwargs.get('thought', '')
    
    # Simulate different reasoning based on thought number
    responses = {
        1: f"Breaking down the task: {prompt[:100]}... I need to identify the main components and subtasks.",
        2: f"Selecting tools: Based on the task breakdown, I should use search tools, analysis tools, and output tools in sequence.",
        3: f"Planning execution: The optimal order is: 1) Gather information, 2) Process and analyze, 3) Generate output."
    }
    
    return {
        'thought': responses.get(thought_num, f"Continuing analysis for step {thought_num}"),
        'nextThoughtNeeded': thought_num < total_thoughts,
        'thoughtNumber': thought_num,
        'totalThoughts': total_thoughts
    }


async def create_mock_discovery_system():
    """Create a mock discovery system with sample tools"""
    discovery = ToolDiscovery()
    
    # Mock some tools for demonstration
    sample_tools = [
        {
            'name': 'web_search',
            'server': 'brave_search',
            'description': 'Search the web for information',
            'parameters': {'query': 'string', 'count': 'number'}
        },
        {
            'name': 'read_file',
            'server': 'desktop_commander',
            'description': 'Read contents of a file',
            'parameters': {'path': 'string'}
        },
        {
            'name': 'create_document',
            'server': 'document_generator',
            'description': 'Create a structured document',
            'parameters': {'content': 'string', 'format': 'string'}
        },
        {
            'name': 'analyze_data',
            'server': 'data_analyzer',
            'description': 'Analyze and process data',
            'parameters': {'data': 'object', 'analysis_type': 'string'}
        }
    ]
    
    # Initialize discovery with mock tools
    tools_dict = discovery.discover_all_tools(sample_tools)
    print(f"✅ Discovered {len(tools_dict)} mock tools for testing")
    
    return discovery


async def demo_complexity_analysis(planner):
    """Demonstrate complexity analysis for different types of intents"""
    print("\n" + "="*60)
    print("🧠 COMPLEXITY ANALYSIS DEMO")
    print("="*60)
    
    test_intents = [
        # Simple intents
        "read a file",
        "search for Python tutorials",
        
        # Medium complexity
        "search for AI news and create a summary",
        "analyze the data in report.csv and generate insights",
        
        # High complexity
        "Research the latest AI developments, analyze their impact on software engineering, compare different approaches, and create a comprehensive report with recommendations",
        "Investigate multiple data sources, synthesize the findings, evaluate different methodologies, and produce a detailed analysis with visual charts"
    ]
    
    for intent in test_intents:
        print(f"\n📝 Intent: '{intent}'")
        
        complexity = await planner.analyze_intent_complexity(intent)
        
        print(f"   🎯 Complexity Score: {complexity['score']:.3f}")
        print(f"   🚀 Advanced Planning: {'Yes' if complexity['requires_advanced_planning'] else 'No'}")
        print(f"   💭 Reasoning: {complexity['reasoning']}")
        
        # Show factor breakdown for complex intents
        if complexity['score'] > 0.5:
            factors = complexity['factors']
            print(f"   📊 Factor Breakdown:")
            for factor, value in factors.items():
                print(f"      • {factor}: {value:.3f}")


async def demo_plan_creation(planner):
    """Demonstrate plan creation for different complexity levels"""
    print("\n" + "="*60)
    print("🏗️  PLAN CREATION DEMO")
    print("="*60)
    
    test_cases = [
        {
            'intent': "read a configuration file",
            'context': {'file_path': '/config/app.json'},
            'expected_method': 'basic'
        },
        {
            'intent': "Research AI safety protocols, analyze current implementations, and create comprehensive recommendations for enterprise adoption",
            'context': {'domain': 'enterprise', 'urgency': 'high'},
            'expected_method': 'sequential_thinking'
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n🔧 Test Case {i}: {case['intent'][:50]}...")
        
        # Create the plan
        plan = await planner.create_advanced_plan(
            intent=case['intent'],
            context=case['context']
        )
        
        print(f"   📋 Plan ID: {plan.plan_id}")
        print(f"   ⚙️  Planning Method: {plan.planning_method}")
        print(f"   🎯 Complexity Score: {plan.complexity_score:.3f}")
        print(f"   🔧 Tools Count: {len(plan.tools)}")
        print(f"   🧠 Reasoning Steps: {len(plan.reasoning_steps)}")
        print(f"   ⏱️  Estimated Duration: {plan.estimated_duration:.1f}s")
        print(f"   📊 Confidence: {plan.confidence_score:.3f}")
        print(f"   🔄 Adaptability: {plan.adaptability_score:.3f}")
        
        # Show reasoning steps for complex plans
        if plan.reasoning_steps:
            print(f"   💭 Reasoning Process:")
            for step in plan.reasoning_steps:
                print(f"      Step {step.step_number}: {step.conclusion[:80]}...")
        
        # Show tools in the plan
        if plan.tools:
            print(f"   🛠️  Execution Plan:")
            for tool in plan.tools:
                deps = f" (depends on: {tool.dependencies})" if tool.dependencies else ""
                print(f"      {tool.order}. {tool.tool_name}{deps}")


async def demo_plan_adaptation(planner):
    """Demonstrate dynamic plan adaptation"""
    print("\n" + "="*60)
    print("🔄 PLAN ADAPTATION DEMO")
    print("="*60)
    
    # Create an initial plan
    initial_intent = "Research market trends and create a business report"
    initial_context = {'market': 'technology', 'timeframe': 'Q4 2024'}
    
    print(f"📝 Initial Intent: {initial_intent}")
    print(f"🎯 Initial Context: {initial_context}")
    
    original_plan = await planner.create_advanced_plan(initial_intent, initial_context)
    
    print(f"\n📋 Original Plan:")
    print(f"   Method: {original_plan.planning_method}")
    print(f"   Tools: {len(original_plan.tools)}")
    print(f"   Adaptability: {original_plan.adaptability_score:.3f}")
    
    # Simulate new context that requires adaptation
    new_context = {
        'urgency': 'critical',
        'scope_change': 'include_competitor_analysis',
        'deadline': '2024-12-31',
        'additional_requirements': ['charts', 'executive_summary']
    }
    
    print(f"\n🔄 New Context Requires Adaptation:")
    for key, value in new_context.items():
        print(f"   • {key}: {value}")
    
    # Adapt the plan
    adapted_plan = await planner.adapt_plan_dynamically(original_plan, new_context)
    
    print(f"\n📋 Adapted Plan:")
    print(f"   Plan ID: {adapted_plan.plan_id}")
    print(f"   Adaptation Applied: {'Yes' if 'adaptation_applied' in adapted_plan.metadata else 'No'}")
    print(f"   New Reasoning Steps: {len(adapted_plan.reasoning_steps) - len(original_plan.reasoning_steps)}")
    
    if 'adaptation_reasoning' in adapted_plan.metadata:
        reasoning = adapted_plan.metadata['adaptation_reasoning']
        print(f"   Adaptation Reasoning: {reasoning[:100]}...")


async def demo_performance_comparison(planner):
    """Compare basic vs advanced planning performance"""
    print("\n" + "="*60)
    print("⚡ PERFORMANCE COMPARISON DEMO")
    print("="*60)
    
    test_intent = "Analyze customer feedback data, identify key themes, and generate actionable insights"
    
    # Time basic planning
    import time
    
    print("🔧 Testing Basic Planning...")
    start_time = time.time()
    basic_plan = planner.create_plan(test_intent)
    basic_time = time.time() - start_time
    
    print("🚀 Testing Advanced Planning...")
    start_time = time.time()
    advanced_plan = await planner.create_advanced_plan(test_intent)
    advanced_time = time.time() - start_time
    
    print(f"\n📊 Performance Results:")
    print(f"   Basic Planning:")
    print(f"      Time: {basic_time:.3f}s")
    print(f"      Tools: {len(basic_plan.tools)}")
    print(f"      Confidence: {basic_plan.confidence_score:.3f}")
    
    print(f"   Advanced Planning:")
    print(f"      Time: {advanced_time:.3f}s")
    print(f"      Tools: {len(advanced_plan.tools)}")
    print(f"      Confidence: {advanced_plan.confidence_score:.3f}")
    print(f"      Reasoning Steps: {len(advanced_plan.reasoning_steps)}")
    print(f"      Complexity Score: {advanced_plan.complexity_score:.3f}")
    
    print(f"\n💡 Insights:")
    print(f"   Time Overhead: {((advanced_time - basic_time) / basic_time * 100):.1f}%")
    print(f"   Confidence Improvement: {((advanced_plan.confidence_score - basic_plan.confidence_score) * 100):.1f}%")


async def main():
    """Main demo function"""
    print("🚀 Advanced Execution Planner Demo")
    print("Task 2.1: Sequential Thinking Integration")
    print("="*60)
    
    # Setup
    print("\n⚙️  Setting up demo environment...")
    discovery = await create_mock_discovery_system()
    
    # Create advanced planner with mock sequential thinking
    planner = AdvancedExecutionPlanner(
        discovery_system=discovery,
        sequential_thinking_tool=mock_sequential_thinking
    )
    
    print(f"✅ Advanced planner initialized with sequential thinking support")
    
    # Run demonstrations
    try:
        await demo_complexity_analysis(planner)
        await demo_plan_creation(planner)
        await demo_plan_adaptation(planner)
        await demo_performance_comparison(planner)
        
        print("\n" + "="*60)
        print("✅ Demo completed successfully!")
        print("🎯 Key Features Demonstrated:")
        print("   • Intelligent complexity analysis")
        print("   • Sequential thinking integration")
        print("   • Advanced plan creation")
        print("   • Dynamic plan adaptation")
        print("   • Performance comparison")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
