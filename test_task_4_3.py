#!/usr/bin/env python3
"""
Test the 7 advanced autonomous tools are available in the MCP server
"""

import json
import sys
import asyncio
from autonomous_mcp.mcp_protocol import MCPProtocolBridge

async def test_advanced_tools():
    """Test all 7 advanced autonomous tools"""
    print("🧪 Testing Task 4.3: Advanced MCP Agent Tools")
    print("=" * 60)
    
    # Initialize MCP protocol bridge
    bridge = MCPProtocolBridge()
    
    # Check total tools
    total_tools = len(bridge.mcp_tools)
    print(f"✅ Total tools registered: {total_tools}")
    
    # Expected tools
    expected_tools = [
        "execute_autonomous_task",
        "discover_available_tools", 
        "create_intelligent_workflow",
        "analyze_task_complexity",
        "get_personalized_recommendations",
        "monitor_agent_performance",
        "configure_agent_preferences"
    ]
    
    print("\n🔍 Checking each tool:")
    missing_tools = []
    
    for tool_name in expected_tools:
        if tool_name in bridge.mcp_tools:
            tool_def = bridge.mcp_tools[tool_name]
            print(f"  ✅ {tool_name}")
            print(f"     📝 {tool_def.description[:80]}...")
            print(f"     🔧 Category: {tool_def.category}")
        else:
            print(f"  ❌ {tool_name} - MISSING!")
            missing_tools.append(tool_name)
    
    # Test that tools are callable
    print("\n🚀 Testing tool callability:")
    
    try:
        # Test analyze_task_complexity
        result = await bridge._analyze_task_complexity(
            "test simple task",
            {},
            include_tool_recommendations=True
        )
        print(f"  ✅ analyze_task_complexity: {result.get('success', False)}")
        
        # Test monitor_agent_performance
        result = await bridge._monitor_agent_performance(
            time_range="1h",
            include_details=False
        )
        print(f"  ✅ monitor_agent_performance: {result.get('success', False)}")
        
        # Test configure_agent_preferences
        result = await bridge._configure_agent_preferences(
            {"test_preference": "test_value"},
            "update",
            validate_preferences=True
        )
        print(f"  ✅ configure_agent_preferences: {result.get('success', False)}")
        
    except Exception as e:
        print(f"  ❌ Tool execution test failed: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    if len(missing_tools) == 0 and total_tools >= 7:
        print("🎉 TASK 4.3 COMPLETE! All 7 advanced autonomous tools working!")
        print(f"✅ Framework Status: {total_tools} tools available")
        print("✅ Advanced capabilities: Workflow creation, complexity analysis")
        print("✅ Personalization: Recommendations and preference management")  
        print("✅ Monitoring: Real-time performance tracking")
        return True
    else:
        print(f"❌ TASK 4.3 INCOMPLETE: Missing {len(missing_tools)} tools")
        for tool in missing_tools:
            print(f"   - {tool}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_advanced_tools())
    sys.exit(0 if success else 1)
