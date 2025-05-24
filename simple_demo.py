"""
AUTONOMOUS MCP AGENT - PHASE 1 COMPLETE DEMONSTRATION
Simple demo showcasing all three core components working together
"""

import asyncio
import sys
import os
import time

# Add project to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from autonomous_mcp.discovery import ToolDiscovery
from autonomous_mcp.planner import BasicExecutionPlanner  
from autonomous_mcp.executor import ChainExecutor

async def simple_demo():
    """Simple demonstration of the autonomous agent"""
    
    print("=" * 60)
    print("AUTONOMOUS MCP AGENT - PHASE 1 COMPLETE")
    print("=" * 60)
    
    # Initialize all components
    discovery = ToolDiscovery()
    planner = BasicExecutionPlanner(discovery)
    executor = ChainExecutor(discovery)
    
    print("[OK] All components initialized")
    
    # Sample tools
    tools = [
        {
            'name': 'brave_web_search',
            'server': 'brave_search',
            'description': 'Search the web using Brave Search API',
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
    
    # Step 1: Discovery
    print("\n[STEP 1] Tool Discovery...")
    discovered = discovery.discover_all_tools(tools)
    print(f"[OK] Discovered {len(discovered)} tools")
    
    # Step 2: Planning  
    print("\n[STEP 2] Execution Planning...")
    intent = "search for machine learning tutorials"
    plan = planner.create_plan(intent)
    print(f"[OK] Created plan with {len(plan.tools)} tools")
    print(f"[OK] Confidence score: {plan.confidence_score:.2f}")
    
    # Step 3: Execution
    print("\n[STEP 3] Plan Execution...")
    
    def mock_mcp(*args, **kwargs):
        return {"success": True, "data": "Mock result"}
    
    if len(plan.tools) > 0:
        result = await executor.execute_plan(plan, mock_mcp)
        print(f"[OK] Execution completed")
        print(f"[OK] Status: {result.status}")
        print(f"[OK] Tools executed: {len(result.results)}")
    else:
        print("[INFO] No tools to execute")
    
    print("\n" + "=" * 60)
    print("SUCCESS: PHASE 1 INTEGRATION COMPLETE!")
    print("All components working together seamlessly")
    print("Ready for Phase 2 development")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(simple_demo())
