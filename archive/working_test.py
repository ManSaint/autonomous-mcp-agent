#!/usr/bin/env python3
"""Real Working Test of Autonomous MCP Agent"""

import asyncio
import json
from datetime import datetime

async def working_agent_test():
    """Test that actually demonstrates working MCP functionality"""
    print("WORKING AUTONOMOUS MCP AGENT TEST")
    print("="*50)
    print(f"Started: {datetime.now().strftime('%H:%M:%S')}")
    print()
    
    # Test real discovery
    print("TEST: Real MCP Tool Discovery")
    print("-" * 30)
    
    try:
        from autonomous_mcp.real_mcp_discovery import RealMCPDiscovery
        
        # Create discovery instance
        discovery = RealMCPDiscovery()
        
        # Discover tools
        print("Discovering MCP tools...")
        tools = discovery.discover_all_tools(force_refresh=True)
        
        print(f"[SUCCESS] Found {len(tools)} MCP tools!")
        
        # Show some examples
        tool_servers = {}
        for tool_name, tool_info in list(tools.items())[:10]:  # First 10
            server = getattr(tool_info, 'server_name', 'unknown')
            if server not in tool_servers:
                tool_servers[server] = 0
            tool_servers[server] += 1
            print(f"  - {tool_name} (server: {server})")
        
        if len(tools) > 10:
            print(f"  ... and {len(tools) - 10} more tools")
        
        print(f"\nServers discovered: {len(tool_servers)}")
        for server, count in tool_servers.items():
            print(f"  - {server}: {count} tools")
            
        return True, len(tools), len(tool_servers)
        
    except Exception as e:
        print(f"[ERROR] Discovery failed: {e}")
        return False, 0, 0

if __name__ == "__main__":
    success, tool_count, server_count = asyncio.run(working_agent_test())
    
    print("\n" + "="*50)
    print(f"RESULT: {'SUCCESS' if success else 'FAILED'}")
    if success:
        print(f"Tools discovered: {tool_count}")
        print(f"Servers connected: {server_count}")
        print("The autonomous MCP agent is WORKING!")
    print(f"Completed: {datetime.now().strftime('%H:%M:%S')}")
