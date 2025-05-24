"""
Test Real MCP Discovery System

This script demonstrates the real MCP tool discovery and chain execution
capabilities of the autonomous agent framework.
"""

import logging
import sys
import os
import json
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from autonomous_mcp.real_mcp_discovery import get_discovery_instance, ToolCategory
from autonomous_mcp.mcp_chain_executor import get_executor_instance

def setup_logging():
    """Setup logging for the test"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def test_tool_discovery():
    """Test the real tool discovery system"""
    print("Testing Real MCP Tool Discovery...")
    
    discovery = get_discovery_instance()
    
    # Discover all available tools
    tools = discovery.discover_all_tools()
    
    print(f"Discovered {len(tools)} MCP tools")
    
    # Show discovery summary
    summary = discovery.get_discovery_summary()
    print(f"Discovery Summary:")
    print(f"   - Total servers: {summary['total_servers']}")
    print(f"   - Tool categories: {len([cat for cat, count in summary['categories'].items() if count > 0])}")
    print(f"   - Discovery time: {summary['metrics']['discovery_time']:.2f}s")
    
    # Show category breakdown
    print("\nTools by Category:")
    for category, count in summary['categories'].items():
        if count > 0:
            print(f"   - {category}: {count} tools")
    
    # Show top servers
    print("\nTop Servers:")
    for server_name, tool_count in summary['top_servers']:
        print(f"   - {server_name}: {tool_count} tools")
    
    return tools

def test_tool_categorization():
    """Test tool categorization capabilities"""
    print("\n🏷️  Testing Tool Categorization...")
    
    discovery = get_discovery_instance()
    
    # Test each category
    categories = [ToolCategory.SEARCH, ToolCategory.DEVELOPMENT, ToolCategory.MEMORY]
    
    for category in categories:
        tools = discovery.get_tools_by_category(category)
        if tools:
            print(f"\n{category.value.upper()} Tools ({len(tools)}):")
            for tool in tools[:3]:  # Show first 3
                print(f"   - {tool.name} (complexity: {tool.complexity_score:.1f})")
            if len(tools) > 3:
                print(f"   ... and {len(tools) - 3} more")

def test_tool_recommendations():
    """Test tool recommendation system"""
    print("\n💡 Testing Tool Recommendations...")
    
    discovery = get_discovery_instance()
    
    # Test different task types
    test_tasks = [
        "Search for information about AI trends",
        "Create a new GitHub repository",
        "Store knowledge in memory graph",
        "Analyze project performance"
    ]
    
    for task in test_tasks:
        print(f"\nTask: '{task}'")
        recommendations = discovery.get_recommended_tools(task, limit=3)
        
        if recommendations:
            print("   Recommended tools:")
            for tool in recommendations:
                print(f"   - {tool.name} ({tool.category.value})")
        else:
            print("   No specific recommendations")

def test_chain_execution_simulation():
    """Test chain execution with simulated workflow"""
    print("\n⛓️  Testing Chain Execution...")
    
    executor = get_executor_instance()
    
    # Create a simple test chain
    test_chain = [
        {
            "toolName": "brave_web_search",
            "toolArgs": '{"query": "MCP autonomous agents"}',
            "outputPath": "$.results"
        },
        {
            "toolName": "memory_create_entities", 
            "toolArgs": '{"entities": [{"name": "search_result", "entityType": "information", "observations": ["CHAIN_RESULT"]}]}',
            "inputPath": "$[0]"
        }
    ]
    
    print("Executing test chain:")
    for i, step in enumerate(test_chain):
        print(f"   Step {i+1}: {step['toolName']}")
    
    # Execute the chain
    result = executor.execute_chain(test_chain, "MCP search query")
    
    print(f"\nChain Execution Results:")
    print(f"   Success: {result.success}")
    print(f"   Execution time: {result.execution_time:.2f}s")
    print(f"   Steps completed: {len(result.step_results) if result.step_results else 0}")
    
    if result.error_message:
        print(f"   Error: {result.error_message}")
    
    if result.performance_metrics:
        print(f"   Performance metrics: {result.performance_metrics}")

def main():
    """Run all discovery tests"""
    setup_logging()
    
    print("Real MCP Discovery System Test")
    print("=" * 50)
    
    try:
        # Run all tests
        tools = test_tool_discovery()
        test_tool_categorization()
        test_tool_recommendations()
        test_chain_execution_simulation()
        test_tool_metrics()
        export_tool_catalog()
        
        print("\nAll tests completed successfully!")
        print(f"Final Summary: {len(tools)} tools discovered and tested")
        
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
        
    return 0

if __name__ == "__main__":
    exit(main())
