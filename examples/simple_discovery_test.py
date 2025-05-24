"""
Simple Real MCP Discovery Test

This script tests the real MCP tool discovery system without Unicode issues.
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

def main():
    """Test the real MCP discovery system"""
    setup_logging()
    
    print("Real MCP Discovery System Test")
    print("=" * 40)
    
    try:
        print("\n1. Testing Tool Discovery...")
        discovery = get_discovery_instance()
        tools = discovery.discover_all_tools()
        
        print(f"SUCCESS: Discovered {len(tools)} MCP tools")
        
        # Show discovery summary
        summary = discovery.get_discovery_summary()
        print(f"\nDiscovery Summary:")
        print(f"  - Total servers: {summary['total_servers']}")
        print(f"  - Tool categories: {len([cat for cat, count in summary['categories'].items() if count > 0])}")
        print(f"  - Discovery time: {summary['metrics']['discovery_time']:.3f}s")
        
        # Show category breakdown
        print(f"\nTools by Category:")
        for category, count in summary['categories'].items():
            if count > 0:
                print(f"  - {category}: {count} tools")
        
        # Show top servers
        print(f"\nTop Servers:")
        for server_name, tool_count in summary['top_servers']:
            print(f"  - {server_name}: {tool_count} tools")
        
        print("\n2. Testing Tool Categorization...")
        search_tools = discovery.get_tools_by_category(ToolCategory.SEARCH)
        print(f"  - Search tools: {len(search_tools)}")
        
        dev_tools = discovery.get_tools_by_category(ToolCategory.DEVELOPMENT)
        print(f"  - Development tools: {len(dev_tools)}")
        
        memory_tools = discovery.get_tools_by_category(ToolCategory.MEMORY)
        print(f"  - Memory tools: {len(memory_tools)}")
        
        print("\n3. Testing Tool Recommendations...")
        recommendations = discovery.get_recommended_tools("search for information", limit=3)
        print(f"  - Recommendations for 'search for information': {len(recommendations)}")
        for tool in recommendations:
            print(f"    * {tool.name} ({tool.category.value})")
        
        print("\n4. Testing Chain Executor...")
        executor = get_executor_instance()
        
        # Use an actual discovered tool
        test_chain = [
            {
                "toolName": "brave_web_search",
                "toolArgs": {"query": "test"},
            }
        ]
        
        result = executor.execute_chain(test_chain, "test input")
        print(f"  - Chain execution: {'SUCCESS' if result.success else 'FAILED'}")
        print(f"  - Execution time: {result.execution_time:.3f}s")
        
        if result.error_message:
            print(f"  - Error: {result.error_message}")
        else:
            print(f"  - Results: {len(result.results)} steps completed")
        
        print("\n5. Exporting Tool Catalog...")
        catalog = discovery.export_tool_catalog()
        output_file = project_root / "examples" / "tool_catalog.json"
        output_file.parent.mkdir(exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(catalog, f, indent=2)
        
        print(f"  - Catalog exported to: {output_file}")
        print(f"  - Contains {len(catalog['tools'])} tools across {len(catalog['servers'])} servers")
        
        print("\nSUCCESS: All tests completed!")
        print(f"Final Summary: {len(tools)} tools discovered and tested")
        
        return 0
        
    except Exception as e:
        print(f"\nFAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
