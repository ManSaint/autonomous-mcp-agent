"""
Phase 7.1 Multi-Server Discovery Test

Tests the new multi-server MCP discovery engine to validate:
1. Server discovery from Claude Desktop configuration
2. Multi-server connection establishment 
3. Comprehensive tool discovery across all servers
4. Dynamic tool registry building

Expected outcome: Discovery of 70-95 tools from 19 MCP servers
"""

import asyncio
import json
import time
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def test_multi_server_discovery():
    """Test the complete multi-server discovery process"""
    logger.info("Starting Phase 7.1 Multi-Server Discovery Test")
    
    try:
        # Import the new multi-server discovery components
        from autonomous_mcp.multi_server_discovery import (
            get_client_manager, 
            get_tool_registry
        )
        
        # Get instances
        client_manager = get_client_manager()
        tool_registry = get_tool_registry()
        
        # Step 1: Test server discovery from configuration
        logger.info("Step 1: Discovering MCP servers from configuration...")
        servers = await client_manager.discover_servers_from_config()
        
        logger.info(f"Discovered {len(servers)} MCP servers:")
        for name, server in servers.items():
            logger.info(f"  - {name}: {server.config.get('command', 'Unknown')}")
        
        # Step 2: Test comprehensive multi-server discovery
        logger.info("\nStep 2: Performing comprehensive multi-server discovery...")
        discovery_results = await client_manager.discover_all_servers()
        
        # Step 3: Build dynamic tool registry
        logger.info("\nStep 3: Building dynamic tool registry...")
        connected_servers = {
            name: server for name, server in client_manager.servers.items()
            if server.status == "connected"
        }
        await tool_registry.build_from_servers(connected_servers)
        
        # Step 4: Validate tool availability
        logger.info("\nStep 4: Validating tool availability...")
        validation_results = []
        for tool_name, tool in list(tool_registry.tools.items())[:10]:  # Test first 10 tools
            is_valid = await tool_registry.validate_tool_availability(tool_name, tool.server)
            validation_results.append((tool_name, tool.server, is_valid))
        
        # Generate comprehensive report
        registry_summary = tool_registry.get_registry_summary()
        
        # Display results
        print_discovery_report(discovery_results, registry_summary, validation_results)
        
        # Save results to file
        save_discovery_results(discovery_results, registry_summary, validation_results)
        
        return discovery_results, registry_summary
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        raise


def print_discovery_report(discovery_results, registry_summary, validation_results):
    """Print comprehensive discovery report"""
    print("\n" + "="*80)
    print("🎯 PHASE 7.1 MULTI-SERVER DISCOVERY RESULTS")
    print("="*80)
    
    # Server Discovery Results
    print(f"\n📡 SERVER DISCOVERY:")
    print(f"  Total servers found: {discovery_results['total_servers']}")
    print(f"  Successfully connected: {discovery_results['connected_servers']}")
    print(f"  Failed connections: {discovery_results['failed_servers']}")
    print(f"  Discovery time: {discovery_results['discovery_time']:.2f}s")
    
    # Tool Discovery Results
    print(f"\n🔧 TOOL DISCOVERY:")
    print(f"  Total tools discovered: {registry_summary['total_tools']}")
    print(f"  Tools from {registry_summary['total_servers']} servers")
    print(f"  Validated tools: {registry_summary['validated_tools']}")
    print(f"  Validation failures: {registry_summary['validation_failures']}")
    
    # Server Breakdown
    print(f"\n📊 SERVER BREAKDOWN:")
    for server, tool_count in registry_summary['servers'].items():
        status = discovery_results['servers'].get(server, {}).get('status', 'unknown')
        print(f"  {server}: {tool_count} tools ({status})")
    
    # Category Breakdown
    print(f"\n📋 CATEGORY BREAKDOWN:")
    for category, tool_count in registry_summary['categories'].items():
        print(f"  {category}: {tool_count} tools")
    
    # Sample Validation Results
    print(f"\n✅ SAMPLE VALIDATION RESULTS:")
    for tool_name, server, is_valid in validation_results:
        status = "✅" if is_valid else "❌"
        print(f"  {status} {tool_name} ({server})")
    
    # Success Assessment
    target_tools = 70  # Minimum target from Phase 7 plan
    actual_tools = registry_summary['total_tools']
    success_rate = (actual_tools / target_tools) * 100 if target_tools > 0 else 0
    
    print(f"\n🎯 SUCCESS ASSESSMENT:")
    print(f"  Target tools: {target_tools}+")
    print(f"  Discovered tools: {actual_tools}")
    print(f"  Success rate: {success_rate:.1f}%")
    
    if actual_tools >= target_tools:
        print(f"  🎉 SUCCESS: Phase 7.1 target achieved!")
    else:
        print(f"  ⚠️  PARTIAL: {target_tools - actual_tools} tools short of target")
    
    print("="*80)


def save_discovery_results(discovery_results, registry_summary, validation_results):
    """Save discovery results to JSON file"""
    results = {
        'timestamp': time.time(),
        'phase': '7.1',
        'test_name': 'Multi-Server Discovery Test',
        'discovery_results': discovery_results,
        'registry_summary': registry_summary,
        'validation_results': [
            {'tool': tool, 'server': server, 'valid': valid}
            for tool, server, valid in validation_results
        ],
        'conclusions': {
            'total_tools_discovered': registry_summary['total_tools'],
            'target_achieved': registry_summary['total_tools'] >= 70,
            'servers_connected': discovery_results['connected_servers'],
            'discovery_time': discovery_results['discovery_time']
        }
    }
    
    output_file = Path('phase_7_1_discovery_results.json')
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info(f"💾 Results saved to {output_file}")


async def test_individual_server_discovery():
    """Test discovery of individual servers"""
    logger.info("\n🔍 Testing individual server discovery...")
    
    from autonomous_mcp.multi_server_discovery import get_client_manager
    client_manager = get_client_manager()
    
    # Test a few key servers individually
    test_servers = ['github', 'memory', 'commander', 'brave-search', 'firecrawl']
    
    for server_name in test_servers:
        if server_name in client_manager.servers:
            logger.info(f"\nTesting {server_name}...")
            connectivity = await client_manager.test_server_connectivity(server_name)
            
            if connectivity['connected']:
                logger.info(f"  ✅ {server_name}: {connectivity['tool_count']} tools")
                for tool in connectivity['tools'][:3]:  # Show first 3 tools
                    logger.info(f"    - {tool}")
            else:
                logger.info(f"  ❌ {server_name}: {connectivity['error']}")


if __name__ == "__main__":
    print("Phase 7.1: Multi-Server MCP Discovery Engine Test")
    print("=" * 60)
    
    # Run the comprehensive test
    asyncio.run(test_multi_server_discovery())
    
    # Run individual server tests
    asyncio.run(test_individual_server_discovery())
    
    print("\n✅ Phase 7.1 testing completed!")
