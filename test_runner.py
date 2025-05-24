"""
Simple integration test that works with the actual API
"""
import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

if __name__ == "__main__":
    print("Starting integration testing...")
    
    try:
        from autonomous_mcp.discovery import ToolDiscovery
        from autonomous_mcp.planner import BasicExecutionPlanner
        from autonomous_mcp.executor import ChainExecutor
        
        print("[OK] All components imported successfully")
        
        # Test basic integration
        discovery = ToolDiscovery()
        planner = BasicExecutionPlanner()
        executor = ChainExecutor()
        
        print("[OK] All components instantiated successfully")
        
        # Test with sample tool data
        print("\nTesting tool discovery...")
        sample_tools = [
            {
                'name': 'brave_web_search',
                'server': 'brave_search',
                'description': 'Search the web using Brave search engine',
                'parameters': {'query': 'string', 'count': 'number'}
            },
            {
                'name': 'create_entities',
                'server': 'memory_server',
                'description': 'Create entities in the knowledge graph',
                'parameters': {'entities': 'array'}
            },
            {
                'name': 'github_search_repositories',
                'server': 'github_api',
                'description': 'Search for repositories on GitHub',
                'parameters': {'q': 'string', 'sort': 'string'}
            }
        ]
        
        tools = discovery.discover_all_tools(sample_tools)
        print(f"[OK] Discovered {len(tools)} tools")
        
        # Test category distribution
        categories = {}
        for tool in tools.values():
            for cap in tool.capabilities:
                categories[cap.category] = categories.get(cap.category, 0) + 1
        
        print(f"[OK] Tools distributed across {len(categories)} categories:")
        for category, count in sorted(categories.items()):
            print(f"  - {category}: {count} capabilities")
        
        # Test intent matching
        print("\nTesting intent matching...")
        search_intent = "search for information online"
        relevant_tools = discovery.get_tools_for_intent(search_intent)
        print(f"[OK] Found {len(relevant_tools)} tools for '{search_intent}'")
        
        if len(relevant_tools) > 0:
            print(f"  Top tool: {relevant_tools[0].name}")
        
        # Test plan creation
        print("\nTesting plan creation...")
        if len(relevant_tools) > 0:
            # Create a planner with the discovery system
            planner_with_discovery = BasicExecutionPlanner(discovery)
            plan = planner_with_discovery.create_plan(search_intent)
            print(f"[OK] Created plan with {len(plan.tools)} steps")
            
            if len(plan.tools) > 0:
                print(f"  First tool: {plan.tools[0].tool_name}")
        else:
            print("[INFO] No relevant tools found for plan creation")
        
        print("\n[SUCCESS] Integration testing completed successfully!")
        print("Phase 1 Task 1.4 - Integration Testing: COMPLETE")
        
    except Exception as e:
        print(f"[ERROR] Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
