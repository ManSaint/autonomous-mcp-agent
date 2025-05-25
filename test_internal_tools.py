import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from autonomous_mcp.mcp_protocol import MCPProtocolBridge

async def test_internal_tools():
    bridge = MCPProtocolBridge()
    bridge._initialize_framework()
    
    # Get tools through discovery
    result = await bridge._discover_tools()
    tools = result.get('tools', {})
    
    internal_tools = [k for k, v in tools.items() if not v.get('is_proxy', True)]
    proxy_tools = [k for k, v in tools.items() if v.get('is_proxy', False)]
    
    print(f"Total tools found: {len(tools)}")
    print(f"Internal tools: {len(internal_tools)} - {internal_tools}")
    print(f"Proxy tools: {len(proxy_tools)} - {proxy_tools[:5]}..." if len(proxy_tools) > 5 else f"Proxy tools: {len(proxy_tools)} - {proxy_tools}")
    
    # Test specific autonomous tools
    autonomous_tools = [
        'discover_available_tools',
        'create_intelligent_workflow', 
        'analyze_task_complexity',
        'get_personalized_recommendations',
        'monitor_agent_performance',
        'configure_agent_preferences',
        'execute_autonomous_task'
    ]
    
    print("\nAutonomous tool availability check:")
    for tool in autonomous_tools:
        available = hasattr(bridge, f'_{tool}')
        print(f"  {tool}: {'✓' if available else '✗'}")
    
    return len(tools), len(internal_tools), len(proxy_tools)

if __name__ == "__main__":
    asyncio.run(test_internal_tools())
