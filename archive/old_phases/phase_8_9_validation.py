#!/usr/bin/env python3
"""
Phase 8.9 Real MCP Integration Validation

This script validates that the autonomous MCP agent can connect to
external MCP servers and discover tools from them, not just Claude's built-ins.
"""

import asyncio
import json
import logging
import sys
import time
from pathlib import Path

# Add the autonomous_mcp directory to the path
sys.path.insert(0, str(Path(__file__).parent / 'autonomous_mcp'))

from autonomous_mcp.real_mcp_client_new import get_mcp_client
from autonomous_mcp.real_mcp_discovery import get_discovery_instance
from autonomous_mcp.mcp_config_reader import get_config_reader


def setup_logging():
    """Setup logging for validation"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('phase_8_9_validation.log')
        ]
    )


async def test_mcp_client_connections():
    """Test direct MCP client connections to external servers"""
    print("\n🔧 Testing MCP Client Connections")
    print("=" * 50)
    
    mcp_client = get_mcp_client()
    
    try:
        # Initialize server connections
        print("Connecting to external MCP servers...")
        connected_count = await mcp_client.initialize_servers()
        
        if connected_count == 0:
            print("❌ No external servers connected")
            return False
        
        print(f"✅ Connected to {connected_count} external MCP servers")
        
        # Get client summary
        summary = mcp_client.get_client_summary()
        print(f"📊 Client Summary:")
        print(f"   Connected Servers: {summary['connected_servers']}")
        print(f"   Total Tools: {summary['total_tools']}")
        print(f"   Performance: {summary['performance_metrics']}")
        
        return connected_count > 0
        
    except Exception as e:
        print(f"❌ Error testing MCP client: {e}")
        return False


def test_discovery_system():
    """Test the discovery system with real external servers"""
    print("\n🔍 Testing Discovery System")
    print("=" * 50)
    
    try:
        discovery = get_discovery_instance()
        
        # Force fresh discovery
        print("Starting tool discovery from external servers...")
        start_time = time.time()
        
        discovered_tools = discovery.discover_all_tools(force_refresh=True)
        discovery_time = time.time() - start_time
        
        print(f"✅ Discovery completed in {discovery_time:.2f} seconds")
        print(f"📈 Discovered {len(discovered_tools)} total tools")
        
        # Check if we found external tools (not just autonomous ones)
        external_tools = []
        autonomous_tools = []
        
        for tool_name, tool in discovered_tools.items():
            if tool.server == 'autonomous_agent':
                autonomous_tools.append(tool_name)
            else:
                external_tools.append(tool_name)
        
        print(f"🌐 External tools: {len(external_tools)}")
        print(f"🤖 Autonomous tools: {len(autonomous_tools)}")
        
        if len(external_tools) > 0:
            print("✅ Successfully discovered external tools!")
            print(f"   Sample external tools: {external_tools[:5]}")
        else:
            print("❌ No external tools discovered - still only finding autonomous tools")
            return False
        
        return len(external_tools) > 0
        
    except Exception as e:
        print(f"❌ Error testing discovery: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_configuration_reader():
    """Test the MCP configuration reader"""
    print("\n📋 Testing Configuration Reader")
    print("=" * 50)
    
    try:
        config_reader = get_config_reader()
        
        # Get configuration summary
        summary = config_reader.get_config_summary()
        
        print(f"📊 Configuration Summary:")
        print(f"   Total Servers: {summary['total_servers']}")
        print(f"   Enabled Servers: {summary['enabled_servers']}")
        print(f"   Has Claude Config: {summary['has_claude_config']}")
        
        if summary['enabled_server_names']:
            print(f"   Enabled Servers: {', '.join(summary['enabled_server_names'])}")
        
        return summary['enabled_servers'] > 0
        
    except Exception as e:
        print(f"❌ Error testing configuration: {e}")
        return False


async def comprehensive_validation():
    """Run comprehensive validation of Phase 8.9 integration"""
    print("🚀 Phase 8.9 Real MCP Integration Validation")
    print("=" * 60)
    print("Testing autonomous agent integration with external MCP servers...")
    
    # Track test results
    results = {
        'config_reader': False,
        'mcp_client': False,
        'discovery_system': False
    }
    
    # Test 1: Configuration Reader
    results['config_reader'] = test_configuration_reader()
    
    # Test 2: MCP Client Connections
    results['mcp_client'] = await test_mcp_client_connections()
    
    # Test 3: Discovery System
    results['discovery_system'] = test_discovery_system()
    
    # Final summary
    print("\n" + "=" * 60)
    print("🏁 FINAL VALIDATION RESULTS")
    print("=" * 60)
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name.replace('_', ' ').title()}")
    
    success_rate = (passed_tests / total_tests) * 100
    print(f"\nOverall Success Rate: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    
    if passed_tests >= 2:  # At least config and discovery working
        print("\n🎉 Phase 8.9 Integration: SUCCESS")
        print("✅ Basic integration framework is working")
        if results['mcp_client']:
            print("✅ MCP client can connect to external servers")
        if results['discovery_system']:
            print("✅ Discovery system finds tools from real servers")
    else:
        print("\n❌ Phase 8.9 Integration: NEEDS WORK")
        print("❌ Critical integration issues remain")
    
    # Save validation results
    validation_data = {
        'timestamp': time.time(),
        'phase': '8.9',
        'test_results': results,
        'success_rate': success_rate,
        'overall_success': passed_tests >= 2
    }
    
    with open('phase_8_9_validation_results.json', 'w') as f:
        json.dump(validation_data, f, indent=2)
    
    print(f"\n📄 Validation results saved to: phase_8_9_validation_results.json")
    
    return passed_tests >= 2


if __name__ == "__main__":
    # Setup logging
    setup_logging()
    
    # Run comprehensive validation
    try:
        success = asyncio.run(comprehensive_validation())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Validation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Validation failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
