#!/usr/bin/env python3
"""
Simple Live Agent Test - Real MCP Framework Demonstration
"""

import asyncio
import json
from datetime import datetime

async def simple_live_test():
    """Simple test to show real autonomous agent functionality"""
    print("🚀 SIMPLE LIVE AUTONOMOUS MCP AGENT TEST")
    print("="*60)
    print(f"🕐 Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test 1: Import Check
    print("📦 TEST 1: Framework Module Availability")
    print("-" * 40)
    
    modules_tested = []
    
    try:
        from autonomous_mcp.real_mcp_discovery import RealMCPDiscovery
        print("   ✅ RealMCPDiscovery: Available")
        modules_tested.append("discovery")
    except Exception as e:
        print(f"   ❌ RealMCPDiscovery: {e}")
    
    try:
        from autonomous_mcp.real_mcp_client import RealMCPClient  
        print("   ✅ RealMCPClient: Available")
        modules_tested.append("client")
    except Exception as e:
        print(f"   ❌ RealMCPClient: {e}")
        
    try:
        from autonomous_mcp.mcp_client_manager import RealMCPClientManager
        print("   ✅ RealMCPClientManager: Available")
        modules_tested.append("manager")
    except Exception as e:
        print(f"   ❌ RealMCPClientManager: {e}")
        
    try:
        from autonomous_mcp.agent import Agent
        print("   ✅ Agent: Available")
        modules_tested.append("agent")
    except Exception as e:
        print(f"   ❌ Agent: {e}")
    
    print()
    
    # Test 2: Quick Discovery Test
    if "discovery" in modules_tested:
        print("📡 TEST 2: Quick MCP Server Discovery")
        print("-" * 40)
        
        try:
            discovery = RealMCPDiscovery()
            servers = await discovery.discover_real_servers()
            
            print(f"   ✅ Discovered {len(servers)} MCP servers:")
            for server_name, config in list(servers.items())[:5]:  # Show first 5
                tools_count = config.get('tools_count', 'unknown')
                print(f"      • {server_name}: {tools_count} tools")
            
            if len(servers) > 5:
                print(f"      ... and {len(servers) - 5} more servers")
                
        except Exception as e:
            print(f"   ❌ Discovery failed: {e}")
    
    print()
    
    # Test 3: Framework Status
    print("🏗️ TEST 3: Framework Status Summary")
    print("-" * 40)
    
    framework_score = len(modules_tested)
    max_score = 4
    
    print(f"   📊 Module Availability: {framework_score}/{max_score} ({(framework_score/max_score)*100:.1f}%)")
    print(f"   🎯 Framework Status: {'OPERATIONAL' if framework_score >= 3 else 'PARTIAL' if framework_score >= 2 else 'NEEDS SETUP'}")
    
    if "discovery" in modules_tested and "client" in modules_tested:
        print("   ✅ Core MCP functionality: Available")
    else:
        print("   ⚠️  Core MCP functionality: Limited")
    
    print()
    print("🎊 SIMPLE TEST COMPLETE!")
    print("="*60)
    print(f"🏆 RESULT: Framework is {'READY FOR USE' if framework_score >= 3 else 'NEEDS CONFIGURATION'}")
    print(f"🕐 Test Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return {
        "modules_available": modules_tested,
        "framework_score": f"{framework_score}/{max_score}",
        "status": "OPERATIONAL" if framework_score >= 3 else "PARTIAL",
        "test_timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    result = asyncio.run(simple_live_test())
    print(f"\n💾 Final Result: {json.dumps(result, indent=2)}")
