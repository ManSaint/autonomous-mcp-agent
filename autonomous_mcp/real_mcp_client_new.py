"""
Real MCP Client Implementation

This module provides a real MCP client that can connect to external MCP servers
using the MCP protocol, discover their tools, and execute operations on them.
"""

import asyncio
import json
import logging
import subprocess
import time
import platform
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import sys
import os
from pathlib import Path

from .mcp_config_reader import get_config_reader, MCPServerConfig


class MCPConnectionState(Enum):
    """MCP server connection states"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"
    TIMEOUT = "timeout"


@dataclass
class MCPServerInstance:
    """Represents a running MCP server instance"""
    config: MCPServerConfig
    process: Optional[subprocess.Popen] = None
    state: MCPConnectionState = MCPConnectionState.DISCONNECTED
    tools: List[str] = field(default_factory=list)
    resources: List[str] = field(default_factory=list)
    prompts: List[str] = field(default_factory=list)
    last_ping: Optional[float] = None
    error_message: Optional[str] = None
    request_id: int = 0
    
    def get_next_request_id(self) -> int:
        """Get next request ID for this server"""
        self.request_id += 1
        return self.request_id


class RealMCPClient:
    """
    Real MCP client that connects to external MCP servers
    
    This class implements the MCP protocol to communicate with external
    servers, discover their capabilities, and execute tool operations.
    """
    
    def __init__(self):
        """Initialize the real MCP client"""
        self.logger = logging.getLogger(__name__)
        self.config_reader = get_config_reader()
        
        # Server management
        self.servers: Dict[str, MCPServerInstance] = {}
        self.connected_servers: Dict[str, MCPServerInstance] = {}
        
        # Discovery cache
        self.all_tools: Dict[str, Dict[str, Any]] = {}
        self.tool_to_server: Dict[str, str] = {}
        
        # Connection settings
        self.connection_timeout = 10.0
        self.response_timeout = 30.0
        self.max_retries = 3
        
        # Performance tracking
        self.performance_metrics = {
            'connections_established': 0,
            'connections_failed': 0,
            'tools_discovered': 0,
            'operations_executed': 0,
            'avg_response_time': 0.0
        }
        
    async def initialize_servers(self, config_source: Optional[str] = None) -> int:
        """
        Initialize connections to all configured MCP servers
        
        Args:
            config_source: Optional custom config file path
            
        Returns:
            Number of successfully connected servers
        """
        self.logger.info("Initializing MCP server connections...")
        
        # Get server configurations
        server_configs = self.config_reader.get_enabled_servers(config_source)
        
        if not server_configs:
            self.logger.warning("No enabled MCP servers found in configuration")
            return 0
        
        # Connect to each server
        connection_tasks = []
        for name, config in server_configs.items():
            task = asyncio.create_task(self._connect_to_server(name, config))
            connection_tasks.append(task)
        
        # Wait for all connections to complete
        results = await asyncio.gather(*connection_tasks, return_exceptions=True)
        
        # Count successful connections
        successful_connections = 0
        for i, result in enumerate(results):
            server_name = list(server_configs.keys())[i]
            if isinstance(result, Exception):
                self.logger.error(f"Failed to connect to {server_name}: {result}")
            elif result:
                successful_connections += 1
                self.logger.info(f"Successfully connected to {server_name}")
            else:
                self.logger.warning(f"Connection to {server_name} failed")
        
        self.logger.info(f"Connected to {successful_connections}/{len(server_configs)} MCP servers")
        return successful_connections
    
    async def _connect_to_server(self, name: str, config: MCPServerConfig) -> bool:
        """
        Connect to a single MCP server
        
        Args:
            name: Server name
            config: Server configuration
            
        Returns:
            True if connection successful
        """
        try:
            self.logger.debug(f"Connecting to MCP server: {name}")
            
            # Create server instance
            server_instance = MCPServerInstance(config=config)
            server_instance.state = MCPConnectionState.CONNECTING
            self.servers[name] = server_instance
            
            # Start the server process
            if not await self._start_server_process(server_instance):
                return False
            
            # Perform MCP handshake
            if not await self._perform_handshake(server_instance):
                return False
            
            # Discover server capabilities
            await self._discover_server_capabilities(server_instance)
            
            # Mark as connected
            server_instance.state = MCPConnectionState.CONNECTED
            self.connected_servers[name] = server_instance
            
            # Update metrics
            self.performance_metrics['connections_established'] += 1
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error connecting to server {name}: {e}")
            if name in self.servers:
                self.servers[name].state = MCPConnectionState.ERROR
                self.servers[name].error_message = str(e)
            
            self.performance_metrics['connections_failed'] += 1
            return False
    
    async def _start_server_process(self, server_instance: MCPServerInstance) -> bool:
        """Start the server process"""
        try:
            config = server_instance.config
            
            # Prepare command
            cmd = [config.command] + config.args
            
            # Prepare environment
            env = os.environ.copy()
            env.update(config.env)
            
            # Start process
            if platform.system() == "Windows":
                # Windows-specific subprocess settings
                server_instance.process = subprocess.Popen(
                    cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    env=env,
                    text=True,
                    bufsize=0,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            else:
                # Unix-like systems
                server_instance.process = subprocess.Popen(
                    cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    env=env,
                    text=True,
                    bufsize=0
                )
            
            # Wait a moment for process to start
            await asyncio.sleep(0.5)
            
            # Check if process is still running
            if server_instance.process.poll() is not None:
                # Process terminated
                stderr_output = server_instance.process.stderr.read() if server_instance.process.stderr else "No error output"
                self.logger.error(f"Server process terminated immediately: {stderr_output}")
                return False
            
            self.logger.debug(f"Server process started successfully: PID {server_instance.process.pid}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting server process: {e}")
            return False
    
    async def _perform_handshake(self, server_instance: MCPServerInstance) -> bool:
        """Perform MCP handshake with the server"""
        try:
            # Send initialize request
            init_request = {
                "jsonrpc": "2.0",
                "id": server_instance.get_next_request_id(),
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {},
                        "resources": {},
                        "prompts": {}
                    },
                    "clientInfo": {
                        "name": "autonomous-mcp-agent",
                        "version": "1.0.0"
                    }
                }
            }
            
            # Send request and get response
            response = await self._send_request(server_instance, init_request)
            
            if not response or "error" in response:
                self.logger.error(f"Handshake failed: {response.get('error', 'Unknown error') if response else 'No response'}")
                return False
            
            # Send initialized notification
            init_notification = {
                "jsonrpc": "2.0",
                "method": "notifications/initialized"
            }
            
            await self._send_notification(server_instance, init_notification)
            
            self.logger.debug("Handshake completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error during handshake: {e}")
            return False
    
    async def _discover_server_capabilities(self, server_instance: MCPServerInstance) -> None:
        """Discover what tools, resources, and prompts the server provides"""
        try:
            # Discover tools
            tools_request = {
                "jsonrpc": "2.0",
                "id": server_instance.get_next_request_id(),
                "method": "tools/list"
            }
            
            tools_response = await self._send_request(server_instance, tools_request)
            if tools_response and "result" in tools_response:
                tools = tools_response["result"].get("tools", [])
                server_instance.tools = [tool["name"] for tool in tools]
                
                # Store tool details
                for tool in tools:
                    tool_name = tool["name"]
                    self.all_tools[tool_name] = {
                        "name": tool_name,
                        "description": tool.get("description", ""),
                        "inputSchema": tool.get("inputSchema", {}),
                        "server": server_instance.config.name
                    }
                    self.tool_to_server[tool_name] = server_instance.config.name
                
                self.logger.debug(f"Discovered {len(tools)} tools from {server_instance.config.name}")
            
            # Discover resources (optional)
            try:
                resources_request = {
                    "jsonrpc": "2.0",
                    "id": server_instance.get_next_request_id(),
                    "method": "resources/list"
                }
                
                resources_response = await self._send_request(server_instance, resources_request)
                if resources_response and "result" in resources_response:
                    resources = resources_response["result"].get("resources", [])
                    server_instance.resources = [res["uri"] for res in resources]
                    self.logger.debug(f"Discovered {len(resources)} resources from {server_instance.config.name}")
            except Exception:
                # Resources are optional
                pass
            
            # Discover prompts (optional)
            try:
                prompts_request = {
                    "jsonrpc": "2.0",
                    "id": server_instance.get_next_request_id(),
                    "method": "prompts/list"
                }
                
                prompts_response = await self._send_request(server_instance, prompts_request)
                if prompts_response and "result" in prompts_response:
                    prompts = prompts_response["result"].get("prompts", [])
                    server_instance.prompts = [prompt["name"] for prompt in prompts]
                    self.logger.debug(f"Discovered {len(prompts)} prompts from {server_instance.config.name}")
            except Exception:
                # Prompts are optional
                pass
                
            # Update metrics
            self.performance_metrics['tools_discovered'] += len(server_instance.tools)
            
        except Exception as e:
            self.logger.warning(f"Error discovering server capabilities: {e}")
    
    async def _send_request(self, server_instance: MCPServerInstance, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send a JSON-RPC request to the server and wait for response"""
        try:
            if not server_instance.process or server_instance.process.poll() is not None:
                self.logger.error("Server process is not running")
                return None
            
            # Send request
            request_line = json.dumps(request) + "\n"
            server_instance.process.stdin.write(request_line)
            server_instance.process.stdin.flush()
            
            # Wait for response with timeout
            response = await asyncio.wait_for(
                self._read_response(server_instance),
                timeout=self.response_timeout
            )
            
            return response
            
        except asyncio.TimeoutError:
            self.logger.error(f"Request timeout for method {request.get('method')}")
            return None
        except Exception as e:
            self.logger.error(f"Error sending request: {e}")
            return None
    
    async def _send_notification(self, server_instance: MCPServerInstance, notification: Dict[str, Any]) -> None:
        """Send a JSON-RPC notification to the server (no response expected)"""
        try:
            if not server_instance.process or server_instance.process.poll() is not None:
                self.logger.error("Server process is not running")
                return
            
            # Send notification
            notification_line = json.dumps(notification) + "\n"
            server_instance.process.stdin.write(notification_line)
            server_instance.process.stdin.flush()
            
        except Exception as e:
            self.logger.error(f"Error sending notification: {e}")
    
    async def _read_response(self, server_instance: MCPServerInstance) -> Optional[Dict[str, Any]]:
        """Read a JSON-RPC response from the server"""
        try:
            # Read line from stdout
            line = server_instance.process.stdout.readline()
            if not line:
                return None
            
            # Parse JSON
            response = json.loads(line.strip())
            return response
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Error parsing JSON response: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error reading response: {e}")
            return None
    
    def get_all_tools(self) -> Dict[str, Dict[str, Any]]:
        """Get all discovered tools from all connected servers"""
        return self.all_tools.copy()
    
    def get_tools_by_server(self, server_name: str) -> List[str]:
        """Get tools from a specific server"""
        if server_name in self.connected_servers:
            return self.connected_servers[server_name].tools.copy()
        return []
    
    def get_connected_servers(self) -> List[str]:
        """Get list of connected server names"""
        return list(self.connected_servers.keys())
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool on the appropriate server
        
        Args:
            tool_name: Name of the tool to execute
            arguments: Tool arguments
            
        Returns:
            Tool execution result
        """
        try:
            # Find which server has this tool
            server_name = self.tool_to_server.get(tool_name)
            if not server_name:
                return {
                    "success": False,
                    "error": f"Tool {tool_name} not found in any connected server"
                }
            
            server_instance = self.connected_servers.get(server_name)
            if not server_instance:
                return {
                    "success": False,
                    "error": f"Server {server_name} is not connected"
                }
            
            # Prepare tool execution request
            exec_request = {
                "jsonrpc": "2.0",
                "id": server_instance.get_next_request_id(),
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }
            
            # Execute tool
            start_time = time.time()
            response = await self._send_request(server_instance, exec_request)
            execution_time = time.time() - start_time
            
            # Update metrics
            self.performance_metrics['operations_executed'] += 1
            current_avg = self.performance_metrics['avg_response_time']
            total_ops = self.performance_metrics['operations_executed']
            self.performance_metrics['avg_response_time'] = (
                (current_avg * (total_ops - 1) + execution_time) / total_ops
            )
            
            if response and "result" in response:
                return {
                    "success": True,
                    "result": response["result"],
                    "execution_time": execution_time,
                    "server": server_name
                }
            else:
                error_msg = response.get("error", "Unknown error") if response else "No response"
                return {
                    "success": False,
                    "error": error_msg,
                    "execution_time": execution_time,
                    "server": server_name
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Tool execution failed: {str(e)}"
            }
    
    def get_client_summary(self) -> Dict[str, Any]:
        """Get summary of client state and performance"""
        return {
            "connected_servers": len(self.connected_servers),
            "total_servers": len(self.servers),
            "total_tools": len(self.all_tools),
            "server_states": {
                name: instance.state.value 
                for name, instance in self.servers.items()
            },
            "tools_by_server": {
                name: len(instance.tools) 
                for name, instance in self.connected_servers.items()
            },
            "performance_metrics": self.performance_metrics.copy()
        }
    
    async def disconnect_all(self) -> None:
        """Disconnect from all servers and clean up resources"""
        self.logger.info("Disconnecting from all MCP servers...")
        
        for name, server_instance in self.servers.items():
            try:
                if server_instance.process and server_instance.process.poll() is None:
                    server_instance.process.terminate()
                    await asyncio.sleep(0.1)
                    if server_instance.process.poll() is None:
                        server_instance.process.kill()
                    
                server_instance.state = MCPConnectionState.DISCONNECTED
                
            except Exception as e:
                self.logger.warning(f"Error disconnecting from {name}: {e}")
        
        # Clear state
        self.connected_servers.clear()
        self.all_tools.clear()
        self.tool_to_server.clear()
        
        self.logger.info("Disconnected from all servers")


# Global instance for singleton access
_mcp_client_instance = None

def get_mcp_client() -> RealMCPClient:
    """Get the global MCP client instance"""
    global _mcp_client_instance
    if _mcp_client_instance is None:
        _mcp_client_instance = RealMCPClient()
    return _mcp_client_instance
