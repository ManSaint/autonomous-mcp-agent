"""
Simple debugging test for complex workflow components
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from autonomous_mcp.discovery import ToolDiscovery
from autonomous_mcp.advanced_planner import AdvancedExecutionPlanner
from autonomous_mcp.smart_selector import SmartToolSelector
from autonomous_mcp.user_preferences import UserPreferenceEngine, PreferenceType
from autonomous_mcp.personalized_selector import PersonalizedToolSelector

async def test_simple_components():
    """Test each component individually"""
    
    print("==> Testing Individual Components")
    
    # Test 1: Tool Discovery
    print("\n1. Testing Tool Discovery...")
    discovery = ToolDiscovery()
    
    # Simple mock tools
    mock_tools = [
        {"name": "web_search", "category": "search", "description": "Search the web"},
        {"name": "text_analyzer", "category": "analysis", "description": "Analyze text"},
        {"name": "code_generator", "category": "development", "description": "Generate code"}
    ]
    
    discovery.discover_all_tools(mock_tools, force_refresh=True)
    all_tools = list(discovery.discovered_tools.values())
    print(f"   Discovered {len(all_tools)} tools: {[t.name for t in all_tools]}")
    
    # Test 2: Smart Tool Selector
    print("\n2. Testing Smart Tool Selector...")
    smart_selector = SmartToolSelector(discovery_system=discovery)
    
    # Create a simple context object
    class SimpleContext:
        def __init__(self, intent):
            self.user_intent = intent
            self.user_id = "test_user"
    
    context = SimpleContext("search for information")
    
    try:
        selected_tools = await smart_selector.select_best_tools(context)
        print(f"   Selected {len(selected_tools)} tools: {[t.tool_name for t in selected_tools]}")
    except Exception as e:
        print(f"   Smart selector error: {e}")
    
    # Test 3: User Preferences
    print("\n3. Testing User Preferences...")
    pref_engine = UserPreferenceEngine()
    
    try:
        pref_engine.create_user_profile("test_user")
        pref_engine.set_current_user("test_user")
        pref_engine.record_explicit_preference(PreferenceType.TOOL_USAGE, "web_search", True, weight=0.9)
        print("   User preferences set successfully")
    except Exception as e:
        print(f"   Preference engine error: {e}")
    
    # Test 4: Personalized Selector
    print("\n4. Testing Personalized Selector...")
    
    try:
        personalized_selector = PersonalizedToolSelector(
            discovery_system=discovery,
            preference_engine=pref_engine
        )
        
        context.user_id = "test_user"
        personalized_tools = await personalized_selector.select_best_tools(context)
        print(f"   Personalized selection: {len(personalized_tools)} tools: {[t.tool_name for t in personalized_tools]}")
    except Exception as e:
        print(f"   Personalized selector error: {e}")
    
    # Test 5: Advanced Planner
    print("\n5. Testing Advanced Planner...")
    
    try:
        advanced_planner = AdvancedExecutionPlanner(discovery_system=discovery)
        
        # Try to create a simple plan
        context = {"user_id": "test_user"}
        plan = await advanced_planner.create_advanced_plan(
            intent="search for information and analyze it",
            context=context
        )
        
        if plan and plan.tools:
            print(f"   Plan created with {len(plan.tools)} steps:")
            for i, tc in enumerate(plan.tools):
                print(f"     {i+1}. {tc.tool_name}")
        else:
            print("   Plan creation failed or returned empty plan")
            
    except Exception as e:
        print(f"   Advanced planner error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_simple_components())
