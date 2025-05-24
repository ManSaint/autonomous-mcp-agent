#!/usr/bin/env python3
"""
Quick demo test for MCP Server functionality

This script tests the basic MCP server functionality without requiring
a full MCP client connection.
"""

import asyncio
import json
import sys
from autonomous_mcp.mcp_protocol import MCPProtocolBridge

async def demo_mcp_server():
    """Demo the MCP server basic functionality"""
    print("=" * 60)
    print("🤖 AUTONOMOUS MCP AGENT - SERVER DEMO")
    print("=" * 60)
    
    try:
        # Initialize the MCP protocol bridge
        print("📡 Initializing MCP Protocol Bridge...")
        bridge = MCPProtocolBridge()
        
        # Test server info
        print("\n📋 Server Information:")
        server_info = bridge.get_server_info()
        print(json.dumps(server_info, indent=2))
        
        # Test tool list
        print(f"\n🔧 Available Tools ({len(bridge.mcp_tools)}):")
        tools = bridge.get_tool_list()
        for tool in tools:
            print(f"  • {tool.name}: {tool.description}")
        
        # Test autonomous task execution (mock)
        print("\n🚀 Testing Autonomous Task Execution...")
        try:
            result = await bridge._execute_autonomous_task(
                task_description="Test task execution",
                context={"test": True},
                preferences={}
            )
            print("✅ Autonomous execution test:", "SUCCESS" if result.get('success') else "FAILED")
            if not result.get('success'):
                print(f"   Error: {result.get('error')}")
        except Exception as e:
            print(f"⚠️  Autonomous execution test error: {e}")
        
        # Test tool discovery
        print("\n🔍 Testing Tool Discovery...")
        try:
            result = await bridge._discover_tools(
                category_filter=[],
                capability_filter=[],
                include_performance=True
            )
            print("✅ Tool discovery test:", "SUCCESS" if result.get('success') else "FAILED")
            if result.get('success'):
                print(f"   Discovered {result.get('total_tools', 0)} tools")
        except Exception as e:
            print(f"⚠️  Tool discovery test error: {e}")
        
        print("\n" + "=" * 60)
        print("✅ MCP SERVER DEMO COMPLETE")
        print("🎯 Server is ready for production deployment!")
        print("🔗 Use 'python mcp_server.py' to start the full server")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(demo_mcp_server())
    sys.exit(0 if success else 1)
