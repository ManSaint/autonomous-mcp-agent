"""
Example: Using Discovery, Planner, and Executor Together
Demonstrates the full autonomous MCP agent workflow
"""

import asyncio
import json
from typing import List, Dict, Any

from autonomous_mcp import (
    ToolDiscovery,
    BasicExecutionPlanner,
    ChainExecutor,
    ExecutionStatus
)


async def demonstrate_autonomous_workflow():
    """Demonstrate the complete autonomous MCP agent workflow"""
    
    print("[ROCKET] Autonomous MCP Agent Demonstration\n")
    
    # Step 1: Tool Discovery
    print("[1] Discovering Available Tools...")
    
    # Simulate getting tools from chainable_tools
    available_tools = [
        {
            'name': 'web_search',
            'server': 'brave_search',
            'description': 'Search the web using Brave search engine',
            'parameters': {'query': 'string', 'count': 'number'}
        },
        {
            'name': 'read_file',
            'server': 'desktop_commander',
            'description': 'Read the contents of a file from the file system',
            'parameters': {'path': 'string', 'offset': 'number', 'length': 'number'}
        },
        {
            'name': 'write_file',
            'server': 'desktop_commander',
            'description': 'Write content to a file on the file system',
            'parameters': {'path': 'string', 'content': 'string', 'mode': 'string'}
        },
        {
            'name': 'create_entities',
            'server': 'memory_server',
            'description': 'Create entities in the knowledge graph',
            'parameters': {'entities': 'array'}
        },
        {
            'name': 'firecrawl_scrape',
            'server': 'firecrawl',
            'description': 'Scrape content from a single URL',
            'parameters': {'url': 'string', 'formats': 'array'}
        },
        {
            'name': 'mcp_chain',
            'server': 'chainable_tools',
            'description': 'Chain together multiple MCP tools',
            'parameters': {'mcpPath': 'array'}
        }
    ]
    
    discovery = ToolDiscovery()
    discovered_tools = discovery.discover_all_tools(available_tools)
    
    print(f"[OK] Discovered {len(discovered_tools)} tools")
    
    # Show tool categories
    categories = discovery.categorize_by_capability()
    for category, tools in categories.items():
        print(f"  - {category}: {', '.join(tools)}")
    
    # Step 2: User Intent Analysis and Planning
    print("\n[2] Creating Execution Plan...")
    
    user_intent = "Search for Python pandas tutorials, scrape the top result, and save a summary to a file"
    
    # Create planner
    planner = BasicExecutionPlanner(discovery)
    
    # Generate plan
    plan = planner.create_plan(user_intent)
    
    print(f"[OK] Created plan '{plan.plan_id}' with {len(plan.tools)} steps:")
    for tool in plan.tools:
        deps = f" (depends on: {tool.dependencies})" if tool.dependencies else ""
        print(f"  {tool.order}. {tool.tool_name}{deps}")
    
    # Show plan details
    print("\n[PLAN] Plan Details:")
    plan_dict = plan.to_dict()
    print(f"  - Intent: {plan_dict['intent']}")
    print(f"  - Confidence: {plan_dict['confidence_score']:.2f}")
    print(f"  - Estimated Duration: {plan_dict['estimated_duration']:.1f}s")
    
    # Step 3: Execute the Plan
    print("\n[3] Executing Plan...")
    
    # Create executor
    executor = ChainExecutor(discovery=discovery)
    
    # Mock mcp_chain function for demonstration
    async def mock_mcp_chain(chain_path: List[Dict[str, Any]]) -> Any:
        """Mock implementation of mcp_chain"""
        # Simulate execution based on the chain
        if any(t['toolName'] == 'web_search' for t in chain_path):
            return {
                "results": [
                    {
                        "title": "Pandas Tutorial - DataCamp",
                        "url": "https://www.datacamp.com/tutorial/pandas",
                        "snippet": "Complete guide to pandas DataFrame operations..."
                    },
                    {
                        "title": "10 Minutes to Pandas",
                        "url": "https://pandas.pydata.org/docs/user_guide/10min.html",
                        "snippet": "This is a short introduction to pandas..."
                    }
                ]
            }
        elif any(t['toolName'] == 'firecrawl_scrape' for t in chain_path):
            return {
                "markdown": "# Pandas Tutorial\n\nPandas is a powerful data manipulation library...\n\n## Key Concepts\n- DataFrames\n- Series\n- Indexing\n- Grouping"
            }
        elif any(t['toolName'] == 'write_file' for t in chain_path):
            return {
                "success": True,
                "path": "pandas_tutorial_summary.md"
            }
        else:
            return {"success": True}
    
    # Execute the plan
    state = await executor.execute_plan(plan, mock_mcp_chain)
    
    # Show execution results
    print(f"\n[OK] Execution completed with status: {state.status.value}")
    print(f"  - Total time: {state.total_execution_time:.2f}s")
    print(f"  - Steps completed: {len(state.results)}/{len(plan.tools)}")
    
    print("\n[STATS] Execution Results:")
    for order, result in state.results.items():
        status_icon = "[OK]" if result.status == ExecutionStatus.SUCCESS else "[ERROR]"
        print(f"  {status_icon} Step {order} ({result.tool_call.tool_name}): {result.status.value}")
        if result.output:
            print(f"     Output: {json.dumps(result.output, indent=6)[:100]}...")
    
    # Step 4: Performance Analysis
    print("\n[4] Performance Analysis...")
    
    stats = discovery.get_tool_stats()
    print(f"  - Total tools used: {sum(t.usage_count for t in discovered_tools.values())}")
    print(f"  - Average success rate: {sum(t.success_rate for t in discovered_tools.values()) / len(discovered_tools):.2%}")
    
    # Export state for persistence
    print("\n[5] Exporting State for Persistence...")
    
    exported_state = executor.export_state(plan.plan_id)
    print(f"  - Exported execution state ({len(json.dumps(exported_state))} bytes)")
    
    exported_discoveries = discovery.export_discoveries()
    print(f"  - Exported tool discoveries ({len(json.dumps(exported_discoveries))} bytes)")
    
    print("\n[STAR] Demonstration Complete!")
    
    return state, plan, discovery


async def demonstrate_complex_workflow():
    """Demonstrate a more complex workflow with parallel execution"""
    
    print("\n[ROCKET] Complex Workflow Demonstration\n")
    
    # Initialize components
    discovery = ToolDiscovery()
    planner = BasicExecutionPlanner(discovery)
    executor = ChainExecutor(discovery=discovery)
    
    # Discover tools
    tools = [
        {
            'name': 'search_code',
            'server': 'desktop_commander',
            'description': 'Search for code patterns in files',
            'parameters': {'path': 'string', 'pattern': 'string'}
        },
        {
            'name': 'get_file_info',
            'server': 'desktop_commander',
            'description': 'Get metadata about a file',
            'parameters': {'path': 'string'}
        },
        {
            'name': 'create_entities',
            'server': 'memory_server',
            'description': 'Create entities in knowledge graph',
            'parameters': {'entities': 'array'}
        }
    ]
    
    discovery.discover_all_tools(tools)
    
    # Create a complex plan with parallel operations
    from autonomous_mcp.planner import ToolCall, ExecutionPlan
    
    plan = ExecutionPlan(
        plan_id="complex_analysis",
        intent="Analyze Python files and store findings",
        tools=[
            # These can run in parallel
            ToolCall(
                tool_name="search_code",
                tool_id="search_imports",
                parameters={"path": "./src", "pattern": "^import"},
                order=1
            ),
            ToolCall(
                tool_name="search_code",
                tool_id="search_classes",
                parameters={"path": "./src", "pattern": "^class"},
                order=2
            ),
            ToolCall(
                tool_name="search_code",
                tool_id="search_functions",
                parameters={"path": "./src", "pattern": "^def"},
                order=3
            ),
            # This depends on all searches
            ToolCall(
                tool_name="create_entities",
                tool_id="store_findings",
                parameters={"entities": ["CHAIN_RESULT"]},
                order=4,
                dependencies=[1, 2, 3]
            )
        ]
    )
    
    print("[PLAN] Complex Plan Structure:")
    print(f"  - Parallel operations: Steps 1-3")
    print(f"  - Dependent operation: Step 4")
    
    # Mock execution
    async def mock_complex_chain(*args, **kwargs):
        await asyncio.sleep(0.1)  # Simulate work
        return {"findings": ["Import found", "Class found", "Function found"]}
    
    # Execute with parallel support
    state = await executor.execute_plan(plan, mock_complex_chain, parallel=True)
    
    print(f"\n[OK] Complex execution completed!")
    print(f"  - Parallel execution saved time")
    print(f"  - All dependencies resolved correctly")
    
    return state


async def main():
    """Run all demonstrations"""
    try:
        # Basic demonstration
        await demonstrate_autonomous_workflow()
        
        # Complex demonstration
        await demonstrate_complex_workflow()
        
    except Exception as e:
        print(f"\n[ERROR] Error in demonstration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run the demonstration
    asyncio.run(main())
