# Check proxy tool classification
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from autonomous_mcp.mcp_protocol import MCPProtocolBridge

async def check_proxy_classification():
    bridge = MCPProtocolBridge()
    discovery_result = await bridge._discover_tools(include_performance=True)
    
    tools = discovery_result.get('tools', {})
    
    proxy_tools = []
    internal_tools = []
    
    for name, tool_info in tools.items():
        if tool_info.get('is_proxy', False):
            proxy_tools.append(name)
        else:
            internal_tools.append(name)
    
    print(f"Total tools: {len(tools)}")
    print(f"Internal tools: {len(internal_tools)}")
    print(f"Proxy tools: {len(proxy_tools)}")
    
    print(f"\nProxy tools ({len(proxy_tools)}):")
    for tool in proxy_tools[:10]:
        print(f"  - {tool}")
    
    print(f"\nInternal tools ({len(internal_tools)}):")
    for tool in internal_tools[:10]:
        print(f"  - {tool}")

if __name__ == "__main__":
    asyncio.run(check_proxy_classification())
