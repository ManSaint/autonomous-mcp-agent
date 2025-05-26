# Quick Debug Discovery Test
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from autonomous_mcp.mcp_protocol import MCPProtocolBridge

async def debug_discovery():
    bridge = MCPProtocolBridge()
    discovery_result = await bridge._discover_tools(include_performance=True)
    
    print("Discovery Result Keys:", discovery_result.keys())
    tools = discovery_result.get('tools', {})
    
    print(f"\nTotal tools: {len(tools)}")
    
    for name, tool_info in list(tools.items())[:5]:
        print(f"\nTool: {name}")
        print(f"  Info keys: {tool_info.keys()}")
        print(f"  Description: {tool_info.get('description', 'N/A')}")
        if 'is_proxy' in str(tool_info):
            print(f"  Contains is_proxy reference")
        else:
            print(f"  No is_proxy reference found")

if __name__ == "__main__":
    asyncio.run(debug_discovery())
