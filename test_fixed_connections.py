"""
Critical Server Connection Fix Test
Tests all 15 fixed server configurations to achieve 100% connectivity

NOTE: This is a template file. Replace placeholder values with your actual API keys.
"""

import asyncio
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_fixed_server_connections():
    """Test all fixed server configurations"""
    logger.info("🚀 TESTING ALL FIXED SERVER CONFIGURATIONS FOR 100% CONNECTIVITY")
    
    try:
        from autonomous_mcp.multi_server_discovery import get_discovery_engine
        
        # Override config to use fixed configurations
        # NOTE: Replace placeholder values with your actual API keys
        fixed_config = {
            "commander": {
                "command": "node",
                "args": ["C:\\Users\\manu_\\AppData\\Roaming\\npm\\node_modules\\@wonderwhy-er\\desktop-commander\\dist\\index.js"]
            },
            "context7": {
                "command": "npx",
                "args": ["-y", "@upstash/context7-mcp"]
            },
            "duckduckgo": {
                "command": "npx", 
                "args": ["-y", "duckduckgo-mcp-server"]
            },
            "magicui": {
                "command": "npx",
                "args": ["-y", "@magicuidesign/mcp"]
            },
            "puppeteer": {
                "command": "node",
                "args": ["C:\\Users\\manu_\\AppData\\Roaming\\npm\\node_modules\\@modelcontextprotocol\\server-puppeteer\\dist\\index.js"]
            },
            "brave-search": {
                "command": "node",
                "args": ["C:\\Users\\manu_\\AppData\\Roaming\\npm\\node_modules\\@modelcontextprotocol\\server-brave-search\\dist\\index.js"],
                "env": {"BRAVE_API_KEY": "your_brave_api_key_here"}
            },
            "firecrawl": {
                "command": "node",
                "args": ["C:\\Users\\manu_\\AppData\\Roaming\\npm\\node_modules\\mcp-server-firecrawl\\dist\\index.js"],
                "env": {"FIRECRAWL_API_KEY": "your_firecrawl_api_key_here"}
            },
            "sequential-thinking": {
                "command": "node",
                "args": ["C:\\Users\\manu_\\AppData\\Roaming\\npm\\node_modules\\@modelcontextprotocol\\server-sequential-thinking\\dist\\index.js"]
            },
            "memory": {
                "command": "node",
                "args": ["C:\\Users\\manu_\\AppData\\Roaming\\npm\\node_modules\\@modelcontextprotocol\\server-memory\\dist\\index.js"],
                "env": {"MEMORY_PERSIST": "true", "MEMORY_PATH": "./memory.json"}
            },
            "youtube": {
                "command": "node",
                "args": ["C:\\Users\\manu_\\AppData\\Roaming\\npm\\node_modules\\@kimtaeyoon83\\mcp-server-youtube-transcript\\dist\\index.js"],
                "env": {"YOUTUBE_API_KEY": "your_youtube_api_key_here"}
            },
            "tmdb": {
                "command": "node",
                "args": ["D:\\Development\\MCP\\mcp-server-tmdb\\dist\\index.js"],
                "env": {"TMDB_API_KEY": "your_tmdb_api_key_here"}
            },
            "github": {
                "command": "node",
                "args": ["C:\\Users\\manu_\\AppData\\Roaming\\npm\\node_modules\\@modelcontextprotocol\\server-github\\dist\\index.js"],
                "env": {"GITHUB_PERSONAL_ACCESS_TOKEN": "your_github_token_here"}
            },
            "postman": {
                "command": "node",
                "args": ["D:\\Development\\MCP\\postman-mcp-server\\build\\index.js"],
                "env": {"POSTMAN_API_KEY": "your_postman_api_key_here"}
            },
            "taskmaster-ai": {
                "command": "node",
                "args": ["C:\\Users\\manu_\\AppData\\Roaming\\npm\\node_modules\\task-master-ai\\dist\\mcp-server.js"],
                "env": {"API_MODE": "false", "LOCAL_ONLY": "true", "DISABLE_RESEARCH": "true"}
            },
            "trello": {
                "command": "node",
                "args": ["C:\\Users\\manu_\\AppData\\Roaming\\npm\\node_modules\\@delorenj\\mcp-server-trello\\dist\\index.js"],
                "env": {
                    "TRELLO_API_KEY": "your_trello_api_key_here",
                    "TRELLO_TOKEN": "your_trello_token_here",
                    "TRELLO_BOARD_ID": "your_trello_board_id_here"
                }
            },
            "autonomous-mcp-agent": {
                "command": "python",
                "args": ["D:\\Development\\Autonomous-MCP-Agent\\mcp_server.py"],
                "env": {
                    "PYTHONPATH": "D:\\Development\\Autonomous-MCP-Agent",
                    "MCP_AGENT_LOG_LEVEL": "INFO",
                    "MCP_AGENT_CONFIG_PATH": "D:\\Development\\Autonomous-MCP-Agent\\user_preferences.json"
                }
            }
        }
        
        discovery_engine = get_discovery_engine()
        
        # Override the discovery to use fixed config
        discovery_engine.servers = fixed_config
        
        logger.info("Testing all 16 servers with fixed configurations...")
        
        results = await discovery_engine.discover_all_servers()
        
        connected_servers = results['connected_servers']
        total_servers = len(fixed_config)
        connection_rate = connected_servers / total_servers
        
        logger.info("\n" + "="*80)
        logger.info("🎯 FIXED SERVER CONNECTION RESULTS")
        logger.info("="*80)
        
        logger.info(f"✅ Connected Servers: {connected_servers}/{total_servers}")
        logger.info(f"📊 Connection Rate: {connection_rate:.1%}")
        logger.info(f"🔧 Tools Discovered: {results['total_tools']}")
        
        if connection_rate >= 0.9:  # 90%+ connection rate
            logger.info("🎉 TARGET ACHIEVED: >90% server connectivity!")
        elif connection_rate >= 0.8:  # 80%+ connection rate
            logger.info("🟡 GOOD: >80% server connectivity achieved")
        else:
            logger.info("❌ NEEDS MORE FIXES: <80% server connectivity")
        
        # List successful connections
        logger.info("\n🟢 SUCCESSFUL CONNECTIONS:")
        for server_name, client in discovery_engine.client_manager.servers.items():
            if client:
                logger.info(f"  ✅ {server_name}")
        
        # List failed connections
        failed_servers = []
        for server_name in fixed_config.keys():
            if server_name not in discovery_engine.client_manager.servers:
                failed_servers.append(server_name)
        
        if failed_servers:
            logger.info("\n🔴 FAILED CONNECTIONS:")
            for server_name in failed_servers:
                logger.info(f"  ❌ {server_name}")
        
        logger.info("\n" + "="*80)
        
        return {
            'connected_servers': connected_servers,
            'total_servers': total_servers,
            'connection_rate': connection_rate,
            'total_tools': results['total_tools'],
            'target_achieved': connection_rate >= 0.9
        }
        
    except Exception as e:
        logger.error(f"Fixed server connection test failed: {e}")
        raise


if __name__ == "__main__":
    print("🚀 CRITICAL SERVER CONNECTION FIX TEST")
    print("="*60)
    print("NOTE: Replace placeholder API keys with your actual keys before running")
    
    results = asyncio.run(test_fixed_server_connections())
    
    if results['target_achieved']:
        print(f"\n🎉 SUCCESS: {results['connection_rate']:.1%} server connectivity achieved!")
        print(f"🔧 Tools Available: {results['total_tools']}")
    else:
        print(f"\n🔄 PROGRESS: {results['connection_rate']:.1%} connectivity, need more fixes")
