"""
Real MCP Client Manager

This module manages real MCP client connections and integrates with the existing
framework, replacing simulation-based connections with actual MCP protocol implementation.
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import os

from .real_mcp_client import RealMCPClient
from .mcp_transport import MCPTransport, TransportConfig


@dataclass
class ServerConnectionInfo:
    """Information about an MCP server connection"""
    name: str
    client: Optional[RealMCPClient] = None
    status: str = "disconnected"  # disconnected, connecting, connected, error
    tools: List[Dict[str, Any]] = field(default_factory=list)
    capabilities: Optional[Dict[str, Any]] = None
    last_health_check: Optional[float] = None
    connection_time: Optional[float] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    config: Optional[Dict[str, Any]] = None


class RealMCPClientManager:
    """
    Manages real MCP client connections
    
    Provides unified interface for connecting to multiple MCP servers,
    discovering tools, and executing commands via real MCP protocol.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.servers: Dict[str, ServerConnectionInfo] = {}
        self.is_running = False
        self._health_check_task: Optional[asyncio.Task] = None
        self._health_check_interval = 30.0  # seconds
        
    async def start(self):
        """Start the client manager"""
        if self.is_running:
            return
        
        self.is_running = True
        self.logger.info("✅ Real MCP Client Manager started")
        
        # Start health check task
        self._health_check_task = asyncio.create_task(self._health_check_loop())
        
    async def stop(self):
        """Stop the client manager and close all connections"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        # Cancel health check task
        if self._health_check_task and not self._health_check_task.done():
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
        
        # Close all server connections
        for server_name in list(self.servers.keys()):
            await self._disconnect_server(server_name)
        
        self.logger.info("✅ Real MCP Client Manager stopped")
    
    async def connect_to_server(self, server_name: str, server_config: Dict[str, Any]) -> bool:
        """
        Establish real MCP server connection
        
        Args:
            server_name: Name of the server
            server_config: Server configuration dictionary
            
        Returns:
            True if connection successful, False otherwise
        """
        self.logger.info(f"Connecting to MCP server: {server_name}")
        
        try:
            # Create server connection info
            conn_info = ServerConnectionInfo(
                name=server_name,
                config=server_config,
                status="connecting"
            )
            self.servers[server_name] = conn_info
            
            # Parse server configuration
            command = server_config.get('command', '')
            args = server_config.get('args', [])
            env = server_config.get('env', {})
            
            if not command:
                conn_info.status = "error"
                conn_info.error_message = "No command specified in server config"
                self.logger.error(f"Failed to connect to {server_name}: No command specified")
                return False
            
            # Create real MCP client
            client = RealMCPClient(server_name, self.logger)
            conn_info.client = client
            
            # Parse command into executable and arguments
            if isinstance(command, str):
                command_parts = command.split()
            else:
                command_parts = command
            
            if isinstance(args, str):
                args_parts = args.split()
            else:
                args_parts = args if args else []
            
            full_command = command_parts + args_parts
            
            # Connect via stdio
            start_time = time.time()
            if await client.connect_stdio(full_command, env):
                # Initialize MCP protocol
                if await client.send_initialize():
                    conn_info.status = "connected"
                    conn_info.connection_time = time.time() - start_time
                    conn_info.last_health_check = time.time()
                    
                    self.logger.info(f"✅ Connected to {server_name} ({conn_info.connection_time:.3f}s)")
                    return True
                else:
                    conn_info.status = "error"
                    conn_info.error_message = "Failed to initialize MCP protocol"
                    await client.close()
            else:
                conn_info.status = "error"
                conn_info.error_message = "Failed to establish stdio connection"
            
            return False
            
        except Exception as e:
            if server_name in self.servers:
                self.servers[server_name].status = "error"
                self.servers[server_name].error_message = str(e)
            self.logger.error(f"Failed to connect to {server_name}: {e}")
            return False
        if conn_info.status != "connected" or not conn_info.client:
            return False
        
        try:
            is_healthy = await conn_info.client.health_check()
            conn_info.last_health_check = time.time()
            
            if not is_healthy:
                conn_info.status = "error"
                conn_info.error_message = "Health check failed"
                self.logger.warning(f"Health check failed for {server_name}")
            
            return is_healthy
            
        except Exception as e:
            conn_info.status = "error"
            conn_info.error_message = f"Health check error: {e}"
            self.logger.error(f"Health check error for {server_name}: {e}")
            return False
    
    async def _health_check_loop(self):
        """Background task for periodic health checks"""
        while self.is_running:
            try:
                # Check all connected servers
                for server_name, conn_info in self.servers.items():
                    if conn_info.status == "connected":
                        await self.health_check(server_name)
                
                # Wait for next check
                await asyncio.sleep(self._health_check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in health check loop: {e}")
                await asyncio.sleep(5.0)  # Brief pause before retrying
    
    async def _disconnect_server(self, server_name: str):
        """Disconnect from a specific server"""
        if server_name not in self.servers:
            return
        
        conn_info = self.servers[server_name]
        
        if conn_info.client:
            try:
                await conn_info.client.close()
            except Exception as e:
                self.logger.error(f"Error closing client for {server_name}: {e}")
        
        conn_info.status = "disconnected"
        conn_info.client = None
        
        self.logger.info(f"✅ Disconnected from {server_name}")
    
    def get_connected_servers(self) -> List[str]:
        """Get list of currently connected server names"""
        return [
            name for name, conn_info in self.servers.items()
            if conn_info.status == "connected"
        ]
    
    def get_server_status(self, server_name: str) -> Optional[Dict[str, Any]]:
        """Get status information for a specific server"""
        if server_name not in self.servers:
            return None
        
        conn_info = self.servers[server_name]
        
        return {
            "name": server_name,
            "status": conn_info.status,
            "tool_count": len(conn_info.tools),
            "connection_time": conn_info.connection_time,
            "last_health_check": conn_info.last_health_check,
            "error_message": conn_info.error_message,
            "retry_count": conn_info.retry_count,
            "has_client": conn_info.client is not None
        }
    
    def get_all_server_status(self) -> Dict[str, Any]:
        """Get status information for all servers"""
        return {
            name: self.get_server_status(name)
            for name in self.servers.keys()
        }
    
    async def discover_all_tools(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Discover tools from all connected servers
        
        Returns:
            Dictionary mapping server names to their tool lists
        """
        all_tools = {}
        
        for server_name, conn_info in self.servers.items():
            if conn_info.status == "connected":
                tools = await self.get_server_tools(server_name)
                all_tools[server_name] = tools
        
        total_tools = sum(len(tools) for tools in all_tools.values())
        self.logger.info(f"✅ Discovered {total_tools} total tools from {len(all_tools)} servers")
        
        return all_tools
    
    async def reconnect_server(self, server_name: str) -> bool:
        """
        Attempt to reconnect to a server
        
        Args:
            server_name: Name of the server to reconnect
            
        Returns:
            True if reconnection successful, False otherwise
        """
        if server_name not in self.servers:
            self.logger.error(f"Cannot reconnect: server {server_name} not found")
            return False
        
        conn_info = self.servers[server_name]
        
        # Close existing connection if any
        await self._disconnect_server(server_name)
        
        # Increment retry count
        conn_info.retry_count += 1
        
        # Attempt reconnection
        if conn_info.config:
            return await self.connect_to_server(server_name, conn_info.config)
        else:
            self.logger.error(f"Cannot reconnect {server_name}: no config available")
            return False
