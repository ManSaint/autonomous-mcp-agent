"""
Integration test for Smart Tool Selector with Advanced Planner
"""
import asyncio
from autonomous_mcp.discovery import ToolDiscovery, DiscoveredTool, ToolCapability
from autonomous_mcp.smart_selector import SmartToolSelector
from autonomous_mcp.advanced_planner import AdvancedExecutionPlanner


async def test_integration():
    """Test integration between Smart Tool Selector and Advanced Planner"""
    print("Integration Test: Smart Tool Selector + Advanced Planner")
    print("=" * 60)
    
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
            name="sequential_thinking", 
            server="reasoning",
            description="Advanced reasoning tool",
            parameters={"prompt": "string"},
            capabilities=[ToolCapability("reasoning", "analysis", "Reasoning", 0.9)],
            usage_count=10,
            success_rate=0.87,
            average_execution_time=5.0
        )
    ]
    
    # Mock discovery
    class MockDiscovery:
        async def get_all_tools(self):
            return tools
        
        def get_tools_for_intent(self, intent):
            return tools
    
    # Mock sequential thinking
    async def mock_sequential_thinking(**kwargs):
        return {
            'final_thought': f"Analyzed: {kwargs.get('prompt', 'unknown')[:50]}...",
            'thought': 'Mock reasoning process'
        }
    
    # Create components
    discovery = MockDiscovery()
    smart_selector = SmartToolSelector(discovery)
    
    # Create advanced planner with smart selector
    planner = AdvancedExecutionPlanner(
        discovery_system=discovery,
        sequential_thinking_tool=mock_sequential_thinking,
        smart_selector=smart_selector
    )
    
    # Test planning with smart selection
    intent = "research Python programming best practices and analyze trends"
    print(f"Intent: {intent}")
    
    plan = await planner.create_advanced_plan(intent)
    
    print(f"Plan ID: {plan.plan_id}")
    print(f"Planning Method: {plan.planning_method}")
    print(f"Complexity Score: {plan.complexity_score:.3f}")
    print(f"Tools Selected: {len(plan.tools)}")
    
    for i, tool in enumerate(plan.tools, 1):
        print(f"  {i}. {tool.tool_name}")
    
    print(f"Reasoning Steps: {len(plan.reasoning_steps)}")
    for step in plan.reasoning_steps:
        print(f"  Step {step.step_number}: {step.conclusion[:100]}...")
        if 'smart_recommendations' in step.metadata:
            recs = step.metadata['smart_recommendations']
            print(f"    Smart recommendations: {len(recs)} tools")
    
    print("\nIntegration Test Complete!")
    print("Smart Tool Selector successfully integrated with Advanced Planner!")


if __name__ == "__main__":
    asyncio.run(test_integration())
