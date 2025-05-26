#!/usr/bin/env python3
"""
Minimal MCP Server Test

Just test if the basic MCP server can start and connect to Claude.
"""

import asyncio
import json
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Run minimal test server"""
    logger.info("Testing minimal MCP server startup...")
    
    try:
        # Test basic imports
        from mcp.server.stdio import stdio_server
        from mcp.server import Server
        from mcp import types
        logger.info("✓ MCP imports successful")
        
        # Create server
        server = Server("autonomous-mcp-agent")
        logger.info("✓ Server created")
        
        # Add one simple tool
        @server.list_tools()
        async def list_tools():
            return [
                types.Tool(
                    name="test_tool",
                    description="Simple test tool to verify MCP connection",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "message": {"type": "string", "description": "Test message"}
                        },
                        "required": []
                    }
                )
            ]
        
        @server.call_tool()
        async def call_tool(name: str, arguments: dict):
            logger.info(f"Tool called: {name} with {arguments}")
            result = {
                "success": True,
                "tool": name,
                "message": "MCP server is working!",
                "arguments_received": arguments,
                "timestamp": "2025-05-26T09:00:00Z"
            }
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        
        logger.info("✓ Tool handlers registered")
        logger.info("Starting MCP server on stdio...")
        
        # Run server
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options()
            )
            
    except Exception as e:
        logger.error(f"✗ Server failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped")
    except Exception as e:
        logger.error(f"Failed to start: {e}")
        sys.exit(1)
