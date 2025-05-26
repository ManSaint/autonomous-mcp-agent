#!/usr/bin/env python3
"""
Phase 8.9 Integration Test

Tests the real MCP integration by first connecting to servers,
then testing discovery and tool execution.
"""

import asyncio
import json
import sys
import time
from pathlib import Path

# Add the autonomous_mcp directory to the path
sys.path.insert(0, str(Path(__file__).parent / 'autonomous_mcp'))

async def run_integration_test():
    """Run the complete integration test"""
    print("Phase 8.9 Real MCP Integration Test")
    print("=" * 50)
    
    results = {
        'mcp_connection': False,
        'discovery_integration': False,
        'tool_execution_test': False
    }
    
    try:
        # Step 1: Test MCP Client Connection
        print("\n[STEP 1] Testing MCP Client Connection")
        from autonomous_mcp.real_mcp_client_new import get_mcp_client
        
        mcp_client = get_mcp_client()
        connected_count = await mcp_client.initialize_servers()
        
        if connected_count > 0:
            print(f"SUCCESS: Connected to {connected_count} external MCP servers")
            print(f"Available tools: {len(mcp_client.get_all_tools())}")
            results['mcp_connection'] = True
        else:
            print("FAILED: No external servers connected")
            return results
        
        # Step 2: Test Discovery Integration
        print("\n[STEP 2] Testing Discovery System Integration")
        from autonomous_mcp.real_mcp_discovery import get_discovery_instance
        
        discovery = get_discovery_instance()
        discovered_tools = discovery.discover_all_tools(force_refresh=True)
        
        external_tools = []
        autonomous_tools = []
        
        for tool_name, tool in discovered_tools.items():
            if tool.server == 'autonomous_agent':
                autonomous_tools.append(tool_name)
            else:
                external_tools.append(tool_name)
        
        print(f"Discovery results:")
        print(f"  External tools: {len(external_tools)}")
        print(f"  Autonomous tools: {len(autonomous_tools)}")
        print(f"  Total tools: {len(discovered_tools)}")
        
        if len(external_tools) > 0 or len(autonomous_tools) > 0:
            print("SUCCESS: Discovery system working")
            results['discovery_integration'] = True
        else:
            print("FAILED: No tools discovered")
            return results
        
        # Step 3: Test Tool Execution
        print("\n[STEP 3] Testing Tool Execution")
        
        # Try to execute a simple tool
        all_tools = mcp_client.get_all_tools()
        if all_tools:
            # Find a simple tool to test
            test_tool = None
            for tool_name, tool_info in all_tools.items():
                if 'list' in tool_name.lower() or 'get' in tool_name.lower():
                    test_tool = tool_name
                    break
            
            if test_tool:
                print(f"Testing tool execution: {test_tool}")
                try:
                    result = await mcp_client.execute_tool(test_tool, {})
                    if result.get('success'):
                        print("SUCCESS: Tool execution working")
                        results['tool_execution_test'] = True
                    else:
                        print(f"Tool execution failed: {result.get('error', 'Unknown error')}")
                except Exception as e:
                    print(f"Tool execution error: {e}")
            else:
                print("No suitable tool found for execution test")
        
        return results
        
    except Exception as e:
        print(f"Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return results

def main():
    """Main entry point"""
    try:
        results = asyncio.run(run_integration_test())
        
        # Summary
        print("\n" + "=" * 50)
        print("INTEGRATION TEST RESULTS")
        print("=" * 50)
        
        passed = sum(1 for r in results.values() if r)
        total = len(results)
        
        for test_name, passed_test in results.items():
            status = "[PASS]" if passed_test else "[FAIL]"
            print(f"{status} {test_name.replace('_', ' ').title()}")
        
        success_rate = (passed / total) * 100
        print(f"\nSuccess Rate: {passed}/{total} ({success_rate:.1f}%)")
        
        # Save results
        test_data = {
            'timestamp': time.time(),
            'phase': '8.9',
            'integration_test_results': results,
            'success_rate': success_rate,
            'integration_working': passed >= 2
        }
        
        with open('phase_8_9_integration_test.json', 'w') as f:
            json.dump(test_data, f, indent=2)
        
        print(f"\nTest results saved to: phase_8_9_integration_test.json")
        
        if passed >= 2:
            print("\nPHASE 8.9 INTEGRATION: SUCCESS")
            print("The autonomous agent can now connect to real MCP servers!")
        else:
            print("\nPHASE 8.9 INTEGRATION: NEEDS WORK")
        
        return passed >= 2
        
    except Exception as e:
        print(f"Test execution failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
