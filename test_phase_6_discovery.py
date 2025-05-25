# Phase 6.2 Discovery Test
# Test the fixed discovery system with proxy tools

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from autonomous_mcp.mcp_protocol import MCPProtocolBridge

async def test_discovery_fix():
    """Test that the discovery bug is fixed and proxy tools are available"""
    
    print("PHASE 6.2 Discovery Test - Testing Fixed Discovery System")
    print("=" * 70)
    
    try:
        # Initialize the MCP protocol bridge
        print("1. Initializing MCP Protocol Bridge...")
        bridge = MCPProtocolBridge()
        print("   SUCCESS: Bridge initialized successfully")
        
        # Test the fixed discovery function
        print("\n2. Testing Fixed Discovery Function...")
        discovery_result = await bridge._discover_tools(include_performance=True)
        
        print(f"   Discovery Success: {discovery_result.get('success', False)}")
        print(f"   Total Tools Found: {discovery_result.get('total_tools', 0)}")
        
        # Check for internal autonomous tools
        tools = discovery_result.get('tools', {})
        internal_tools = [name for name, info in tools.items() if not info.get('is_proxy', False)]
        proxy_tools = [name for name, info in tools.items() if info.get('is_proxy', False)]
        
        print(f"\n3. Tool Analysis:")
        print(f"   Internal Autonomous Tools: {len(internal_tools)}")
        print(f"   Proxy Tools: {len(proxy_tools)}")
        
        print(f"\n4. Sample Internal Tools:")
        for tool in internal_tools[:3]:
            print(f"   - {tool}")
            
        print(f"\n5. Sample Proxy Tools:")
        for tool in proxy_tools[:5]:
            print(f"   - {tool}")
            
        # Performance test
        import time
        start_time = time.time()
        discovery_result_2 = await bridge._discover_tools()
        end_time = time.time()
        discovery_time = end_time - start_time
        
        print(f"\n6. Performance Test:")
        print(f"   Discovery Time: {discovery_time:.2f} seconds")
        print(f"   Target: <2 seconds {'PASS' if discovery_time < 2 else 'FAIL'}")
        
        # Summary
        total_tools = discovery_result.get('total_tools', 0)
        expected_min = 20  # 7 internal + at least 13 proxy tools
        
        print(f"\n7. Phase 6.2 Test Results:")
        print(f"   Tool Availability: {total_tools} tools ({'PASS' if total_tools >= expected_min else 'FAIL'})")
        
        if total_tools >= expected_min and discovery_result.get('success') and len(proxy_tools) > 0:
            print(f"\nPHASE 6.2 SUCCESS: Discovery Engine Redesign Complete!")
            return True
        else:
            print(f"\nPHASE 6.2 ISSUES DETECTED - Further investigation needed")
            return False
            
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Run the test
    result = asyncio.run(test_discovery_fix())
    exit(0 if result else 1)
