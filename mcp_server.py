#!/usr/bin/env python3
"""
Main MCP Server Entry Point for Autonomous MCP Agent
"""

import asyncio
import sys
import logging
from typing import Optional

# MCP imports
from mcp.server.stdio import stdio_server
from mcp import types

# Internal imports
from autonomous_mcp.mcp_protocol import MCPProtocolBridge
from autonomous_mcp.real_mcp_discovery import get_discovery_instance
from autonomous_mcp.mcp_chain_executor import get_executor_instance

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mcp_server.log'),
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger(__name__)


class AutonomousMCPServer:
    """Main MCP Server class with real tool integration"""
    
    def __init__(self):
        """Initialize the autonomous MCP server"""
        self.bridge: Optional[MCPProtocolBridge] = None
        self.server_running = False
        self.discovery = None
        self.executor = None
        
    async def initialize(self):
        """Initialize the server and framework components"""
        try:
            logger.info("Initializing Autonomous MCP Server with real tool discovery...")
            
            # Initialize discovery and execution systems
            self.discovery = get_discovery_instance()
            self.executor = get_executor_instance()
            
            # Discover available tools
            discovered_tools = self.discovery.discover_all_tools()
            logger.info(f"[SEARCH] Discovered {len(discovered_tools)} real MCP tools")
            
            # Create the MCP protocol bridge
            self.bridge = MCPProtocolBridge()
            
            # Set up MCP server handlers
            self._setup_server_handlers()
            
            logger.info("[OK] Autonomous MCP Server initialized successfully with real tool integration!")
            return True
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to initialize server: {e}")
            return False
    
    def _setup_server_handlers(self):
        """Set up MCP server message handlers"""
        if not self.bridge:
            raise RuntimeError("Bridge not initialized")
        
        server = self.bridge.server
        
        # Handle list_tools requests
        @server.list_tools()
        async def list_tools() -> list[types.Tool]:
            """Return list of available tools"""
            logger.info("[LIST] Received list_tools request")
            tools = self.bridge.get_tool_list()
            logger.info(f"[LIST] Returning {len(tools)} available tools")
            return tools
        
        # Handle server info requests
        @server.list_resources()
        async def list_resources() -> list[types.Resource]:
            """Return list of available resources"""
            logger.info("[BOOKS] Received list_resources request")
            # Return server information as a resource
            server_info = self.bridge.get_server_info()
            return [
                types.Resource(
                    uri="autonomous-mcp://server-info",
                    name="Server Information",
                    description="Information about the Autonomous MCP Agent server",
                    mimeType="application/json"
                )
            ]
        
        # Handle resource content requests
        @server.read_resource()
        async def read_resource(uri: str) -> str:
            """Return resource content"""
            logger.info(f"📖 Received read_resource request for: {uri}")
            
            if uri == "autonomous-mcp://server-info":
                import json
                server_info = self.bridge.get_server_info()
                return json.dumps(server_info, indent=2)
            else:
                raise ValueError(f"Unknown resource: {uri}")
    
    async def run(self):
        """Run the MCP server"""
        if not self.bridge:
            logger.error("[ERROR] Server not initialized")
            return
        
        try:
            logger.info("[ROCKET] Starting Autonomous MCP Server...")
            logger.info("[LINK] Server ready to accept MCP connections via stdio")
            
            # Update server status
            self.server_running = True
            
            # Run the stdio server
            async with stdio_server() as (read_stream, write_stream):
                await self.bridge.server.run(
                    read_stream,
                    write_stream,
                    self.bridge.server.create_initialization_options()
                )
                
        except KeyboardInterrupt:
            logger.info("⏹️  Server shutdown requested")
        except Exception as e:
            logger.error(f"❌ Server error: {e}")
        finally:
            self.server_running = False
            logger.info("Autonomous MCP Server stopped")


async def main():
    """Main function to start the server"""
    logger.info("=" * 60)
    logger.info("[BOT] AUTONOMOUS MCP AGENT SERVER")
    logger.info("=" * 60)
    logger.info("[TARGET] Intelligent task execution with autonomous planning")
    logger.info("[TOOLS] Tool discovery and chaining capabilities")
    logger.info("[BRAIN] AI-powered execution planning and error recovery")
    logger.info("[CHART] Real-time performance monitoring")
    logger.info("=" * 60)
    
    # Create and initialize server
    server = AutonomousMCPServer()
    
    if await server.initialize():
        # Run the server
        await server.run()
    else:
        logger.error("[ERROR] Failed to start server")
        sys.exit(1)


if __name__ == "__main__":
    # Run the server
    asyncio.run(main())
