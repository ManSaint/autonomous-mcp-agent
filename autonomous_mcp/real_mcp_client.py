"""
Real MCP Client Implementation

This module provides a true MCP protocol client implementation that replaces
simulation-based connections with actual JSON-RPC 2.0 over stdio communication
with MCP servers.
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
import subprocess
import sys
import os
from datetime import datetime


@dataclass
class MCPMessage:
    """Represents an MCP protocol message"""
    jsonrpc: str = "2.0"
    id: Optional[Union[str, int]] = None
    method: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None


@dataclass
class MCPServerCapabilities:
    """Represents MCP server capabilities"""
    tools: Dict[str, Any] = field(default_factory=dict)
    resources: Dict[str, Any] = field(default_factory=dict)
    prompts: Dict[str, Any] = field(default_factory=dict)
    
    
@dataclass
class MCPInitializeParams:
    """Parameters for MCP initialize request"""
    protocolVersion: str = "2024-11-05"
    capabilities: MCPServerCapabilities = field(default_factory=MCPServerCapabilities)
    clientInfo: Dict[str, str] = field(default_factory=lambda: {
        "name": "autonomous-mcp-agent",
        "version": "8.0.0"
    })


class RealMCPClient:
    """
    Real MCP protocol client implementation
    
    Provides actual JSON-RPC 2.0 communication with MCP servers over stdio,
    implementing the complete MCP protocol handshake and tool interaction.
    """
    
    def __init__(self, server_name: str, logger: Optional[logging.Logger] = None):
        self.server_name = server_name
        self.logger = logger or logging.getLogger(__name__)
        self.process: Optional[subprocess.Popen] = None
        self.is_connected = False
        self.is_initialized = False
        self.server_info: Optional[Dict[str, Any]] = None
        self.capabilities: Optional[MCPServerCapabilities] = None
        self.request_id = 1
        self._response_handlers: Dict[Union[str, int], asyncio.Future] = {}
        self._tools_cache: Optional[List[Dict[str, Any]]] = None
        self._reader_task: Optional[asyncio.Task] = None
        
    async def connect_stdio(self, command: List[str], env: Optional[Dict[str, str]] = None) -> bool:
        """
        Establish real subprocess stdio MCP connection
        
        Args:
            command: Command and arguments to start MCP server
            env: Environment variables for the subprocess
            
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.logger.info(f"Starting MCP server process: {' '.join(command)}")
            
            # Prepare environment
            server_env = os.environ.copy()
            if env:
                server_env.update(env)
            
            # Start the MCP server process
            self.process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=server_env,
                text=True,
                bufsize=0  # Unbuffered for real-time communication
            )
            
            # Verify process started successfully
            if self.process.poll() is not None:
                stderr_output = self.process.stderr.read() if self.process.stderr else "No error output"
                self.logger.error(f"MCP server process failed to start: {stderr_output}")
                return False
            
            self.is_connected = True
            self.logger.info(f"✅ MCP server process started successfully (PID: {self.process.pid})")
            
            # Start background reader task
            self._reader_task = asyncio.create_task(self._read_responses())
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start MCP server: {e}")
            return False
    
    async def send_initialize(self) -> bool:
        """
        Send MCP initialize handshake
        
        Returns:
            True if initialization successful, False otherwise
        """
        if not self.is_connected:
            self.logger.error("Cannot initialize: not connected to server")
            return False
        
        try:
            # Create initialize request
            init_params = MCPInitializeParams()
            
            # Send initialize request
            response = await self.send_request("initialize", asdict(init_params))
            
            if response and "result" in response:
                self.server_info = response["result"]
                server_capabilities = response["result"].get("capabilities", {})
                self.capabilities = MCPServerCapabilities(**server_capabilities)
                
                # Send initialized notification
                await self.send_notification("initialized", {})
                
                self.is_initialized = True
                self.logger.info(f"✅ MCP server initialized successfully")
                self.logger.debug(f"Server info: {self.server_info}")
                
                return True
            else:
                self.logger.error(f"Initialize failed: {response}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to initialize MCP server: {e}")
            return False
    
    async def send_request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Send JSON-RPC 2.0 request and wait for response
        
        Args:
            method: RPC method name
            params: Method parameters
            
        Returns:
            Response dictionary or None if failed
        """
        if not self.is_connected or not self.process:
            self.logger.error("Cannot send request: not connected")
            return None
        
        try:
            # Create message with unique ID
            message_id = self.request_id
            self.request_id += 1
            
            message = MCPMessage(
                id=message_id,
                method=method,
                params=params
            )
            
            # Prepare response future
            response_future = asyncio.Future()
            self._response_handlers[message_id] = response_future
            
            # Send message
            message_json = json.dumps(asdict(message)) + "\n"
            self.process.stdin.write(message_json)
            self.process.stdin.flush()
            
            self.logger.debug(f"Sent MCP request: {method} (ID: {message_id})")
            
            # Wait for response with timeout
            try:
                response = await asyncio.wait_for(response_future, timeout=30.0)
                return response
            except asyncio.TimeoutError:
                self.logger.error(f"Request timeout: {method} (ID: {message_id})")
                self._response_handlers.pop(message_id, None)
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to send request {method}: {e}")
            return None
    
    async def send_notification(self, method: str, params: Optional[Dict[str, Any]] = None) -> bool:
        """
        Send JSON-RPC 2.0 notification (no response expected)
        
        Args:
            method: RPC method name
            params: Method parameters
            
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.is_connected or not self.process:
            self.logger.error("Cannot send notification: not connected")
            return False
        
        try:
            message = MCPMessage(
                method=method,
                params=params
            )
            
            # Remove ID for notifications
            message_dict = asdict(message)
            message_dict.pop('id', None)
            message_dict.pop('result', None)
            message_dict.pop('error', None)
            
            message_json = json.dumps(message_dict) + "\n"
            self.process.stdin.write(message_json)
            self.process.stdin.flush()
            
            self.logger.debug(f"Sent MCP notification: {method}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send notification {method}: {e}")
            return False
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """
        Get list of tools from MCP server via real protocol call
        
        Returns:
            List of tool definitions
        """
        if not self.is_initialized:
            self.logger.error("Cannot list tools: server not initialized")
            return []
        
        try:
            response = await self.send_request("tools/list", {})
            
            if response and "result" in response:
                tools = response["result"].get("tools", [])
                self._tools_cache = tools
                self.logger.info(f"✅ Discovered {len(tools)} tools from {self.server_name}")
                return tools
            else:
                self.logger.error(f"Failed to list tools: {response}")
                return []
                
        except Exception as e:
            self.logger.error(f"Failed to list tools: {e}")
            return []
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Execute tool via real MCP protocol call
        
        Args:
            name: Tool name
            arguments: Tool arguments
            
        Returns:
            Tool execution result or None if failed
        """
        if not self.is_initialized:
            self.logger.error("Cannot call tool: server not initialized")
            return None
        
        try:
            params = {
                "name": name,
                "arguments": arguments
            }
            
            self.logger.info(f"Calling tool '{name}' with args: {arguments}")
            response = await self.send_request("tools/call", params)
            
            if response and "result" in response:
                result = response["result"]
                self.logger.info(f"✅ Tool '{name}' executed successfully")
                return result
            else:
                self.logger.error(f"Tool call failed: {response}")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to call tool '{name}': {e}")
            return None
    
    async def _read_responses(self):
        """Background task to read and handle responses from the server"""
        if not self.process or not self.process.stdout:
            return
        
        try:
            while self.is_connected and self.process.poll() is None:
                line = self.process.stdout.readline()
                if not line:
                    break
                
                try:
                    message = json.loads(line.strip())
                    await self._handle_message(message)
                except json.JSONDecodeError as e:
                    self.logger.warning(f"Invalid JSON received: {line.strip()}")
                except Exception as e:
                    self.logger.error(f"Error handling message: {e}")
                    
        except Exception as e:
            self.logger.error(f"Error in response reader: {e}")
        finally:
            self.logger.debug("Response reader task ended")
    
    async def _handle_message(self, message: Dict[str, Any]):
        """Handle incoming message from server"""
        try:
            message_id = message.get("id")
            
            if message_id is not None and message_id in self._response_handlers:
                # This is a response to a request
                future = self._response_handlers.pop(message_id)
                if not future.done():
                    future.set_result(message)
            else:
                # This is a notification or unexpected message
                method = message.get("method")
                if method:
                    self.logger.debug(f"Received notification: {method}")
                else:
                    self.logger.debug(f"Received unexpected message: {message}")
                    
        except Exception as e:
            self.logger.error(f"Error handling message: {e}")
    
    async def health_check(self) -> bool:
        """
        Check if the MCP server is healthy and responsive
        
        Returns:
            True if server is healthy, False otherwise
        """
        if not self.is_connected or not self.process:
            return False
        
        # Check if process is still running
        if self.process.poll() is not None:
            self.logger.warning(f"MCP server process has terminated")
            return False
        
        try:
            # Send a simple ping request (list tools is a good health check)
            response = await self.send_request("tools/list", {})
            return response is not None and "result" in response
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False
    
    async def close(self):
        """Clean up connection and terminate server process"""
        try:
            self.is_connected = False
            self.is_initialized = False
            
            # Cancel reader task
            if self._reader_task and not self._reader_task.done():
                self._reader_task.cancel()
                try:
                    await self._reader_task
                except asyncio.CancelledError:
                    pass
            
            # Clean up pending response handlers
            for future in self._response_handlers.values():
                if not future.done():
                    future.cancel()
            self._response_handlers.clear()
            
            # Terminate process
            if self.process:
                try:
                    self.process.terminate()
                    
                    # Wait for graceful shutdown
                    try:
                        await asyncio.wait_for(
                            asyncio.create_task(self._wait_for_process()),
                            timeout=5.0
                        )
                    except asyncio.TimeoutError:
                        self.logger.warning("Process didn't terminate gracefully, killing...")
                        self.process.kill()
                        
                except Exception as e:
                    self.logger.error(f"Error terminating process: {e}")
                finally:
                    self.process = None
            
            self.logger.info(f"✅ MCP client connection closed: {self.server_name}")
            
        except Exception as e:
            self.logger.error(f"Error closing MCP client: {e}")
    
    async def _wait_for_process(self):
        """Wait for process to terminate"""
        if self.process:
            while self.process.poll() is None:
                await asyncio.sleep(0.1)


def asdict(obj):
    """Convert dataclass to dictionary, filtering out None values"""
    if hasattr(obj, '__dataclass_fields__'):
        result = {}
        for field_name, field_value in obj.__dict__.items():
            if field_value is not None:
                if hasattr(field_value, '__dataclass_fields__'):
                    result[field_name] = asdict(field_value)
                else:
                    result[field_name] = field_value
        return result
    return obj
