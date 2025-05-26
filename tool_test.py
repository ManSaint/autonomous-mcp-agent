#!/usr/bin/env python3
"""Real Tool Execution Test"""

import asyncio
from datetime import datetime

async def execute_real_tool():
    """Execute a real MCP tool to prove it's working"""
    print("REAL TOOL EXECUTION TEST")
    print("="*40)
    print(f"Started: {datetime.now().strftime('%H:%M:%S')}")
    print()
    
    try:
        # Test using the brave web search which we know is available
        from autonomous_mcp.real_mcp_client import RealMCPClient
        from autonomous_mcp.mcp_client_manager import RealMCPClientManager
        
        print("Initializing MCP client manager...")
        manager = RealMCPClientManager()
        
        # Try to get a client for brave search (which we saw in the discovery)
        print("Getting brave search client...")
        client = await manager.get_or_create_client("brave-search")
        
        if client:
            print("[SUCCESS] Got brave search client!")
            
            # Try to list available tools
            tools_response = await client.list_tools()
            if hasattr(tools_response, 'tools'):
                print(f"Available tools: {len(tools_response.tools)}")
                for tool in tools_response.tools:
                    print(f"  - {tool.name}: {tool.description}")
                
                # Try to execute a simple search
                if tools_response.tools:
                    search_tool = tools_response.tools[0]  # First tool
                    print(f"\nExecuting {search_tool.name}...")
                    
                    # Simple search query
                    result = await client.call_tool(search_tool.name, {
                        "query": "autonomous agents"
                    })
                    
                    print("[SUCCESS] Tool executed!")
                    print(f"Result type: {type(result)}")
                    if hasattr(result, 'content'):
                        print(f"Content preview: {str(result.content)[:200]}...")
                    
                    return True
            else:
                print("[WARN] No tools found in response")
        else:
            print("[WARN] Could not get client")
        
        return False
        
    except Exception as e:
        print(f"[ERROR] Tool execution failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(execute_real_tool())
    print(f"\nRESULT: {'TOOLS ARE WORKING!' if success else 'Need configuration'}")
    print(f"Completed: {datetime.now().strftime('%H:%M:%S')}")
