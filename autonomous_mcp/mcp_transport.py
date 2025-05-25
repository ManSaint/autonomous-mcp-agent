"""
MCP Transport Layer Implementation

This module handles MCP communication transport, providing robust subprocess
management and message handling for the real MCP client.
"""

import asyncio
import json
import logging
import subprocess
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
import os
import signal
import sys


@dataclass
class TransportConfig:
    """Configuration for MCP transport"""
    command: List[str]
    env: Optional[Dict[str, str]] = None
    timeout: float = 30.0
    max_retries: int = 3
    retry_delay: float = 1.0


class MCPTransport:
    """
    Handle MCP communication transport
    
    Manages subprocess lifecycle, message serialization/deserialization,
    and provides robust error handling and recovery mechanisms.
    """
    
    def __init__(self, server_name: str, config: TransportConfig, logger: Optional[logging.Logger] = None):
        self.server_name = server_name
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        self.process: Optional[subprocess.Popen] = None
        self.is_running = False
        self._message_queue = asyncio.Queue()
        self._response_queue = asyncio.Queue()
        self._writer_task: Optional[asyncio.Task] = None
        self._reader_task: Optional[asyncio.Task] = None
        
    async def start_subprocess(self, command: List[str], args: List[str], env: Optional[Dict[str, str]] = None) -> bool:
        """
        Start MCP server subprocess
        
        Args:
            command: Base command to execute
            args: Command arguments
            env: Environment variables
            
        Returns:
            True if subprocess started successfully, False otherwise
        """
        try:
            full_command = command + args
            self.logger.info(f"Starting MCP server subprocess: {' '.join(full_command)}")
            
            # Prepare environment
            server_env = os.environ.copy()
            if env:
                server_env.update(env)
            if self.config.env:
                server_env.update(self.config.env)
            
            # Start process
            self.process = subprocess.Popen(
                full_command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=server_env,
                text=True,
                bufsize=0,  # Unbuffered
                cwd=None,
                preexec_fn=None if sys.platform == "win32" else os.setsid
            )
            
            # Wait a moment to check if process started correctly
            await asyncio.sleep(0.1)
            
            if self.process.poll() is not None:
                # Process terminated immediately
                stderr_output = ""
                if self.process.stderr:
                    stderr_output = self.process.stderr.read()
                self.logger.error(f"MCP server process failed to start: {stderr_output}")
                return False
            
            self.is_running = True
            self.logger.info(f"✅ MCP server subprocess started (PID: {self.process.pid})")
            
            # Start message handling tasks
            self._writer_task = asyncio.create_task(self._message_writer())
            self._reader_task = asyncio.create_task(self._message_reader())
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start subprocess: {e}")
            return False
    
    async def send_message(self, message: Dict[str, Any]) -> bool:
        """
        Send JSON-RPC message to server
        
        Args:
            message: Message dictionary to send
            
        Returns:
            True if message was queued successfully, False otherwise
        """
        if not self.is_running or not self.process:
            self.logger.error("Cannot send message: transport not running")
            return False
        
        try:
            await self._message_queue.put(message)
            return True
        except Exception as e:
            self.logger.error(f"Failed to queue message: {e}")
            return False
    
    async def receive_message(self) -> Optional[Dict[str, Any]]:
        """
        Receive and parse JSON-RPC response
        
        Returns:
            Parsed message dictionary or None if no message available
        """
        if not self.is_running:
            return None
        
        try:
            # Wait for message with timeout
            message = await asyncio.wait_for(
                self._response_queue.get(),
                timeout=self.config.timeout
            )
            return message
        except asyncio.TimeoutError:
            self.logger.warning("Message receive timeout")
            return None
        except Exception as e:
            self.logger.error(f"Failed to receive message: {e}")
            return None
    
    async def _message_writer(self):
        """Background task to write messages to subprocess stdin"""
        if not self.process or not self.process.stdin:
            return
        
        try:
            while self.is_running and self.process.poll() is None:
                try:
                    # Wait for message to send
                    message = await asyncio.wait_for(
                        self._message_queue.get(),
                        timeout=1.0
                    )
                    
                    # Serialize and send
                    message_json = json.dumps(message) + "\n"
                    self.process.stdin.write(message_json)
                    self.process.stdin.flush()
                    
                    self.logger.debug(f"Sent message: {message.get('method', 'response')}")
                    
                except asyncio.TimeoutError:
                    # No message to send, continue
                    continue
                except Exception as e:
                    self.logger.error(f"Error writing message: {e}")
                    break
                    
        except Exception as e:
            self.logger.error(f"Message writer error: {e}")
        finally:
            self.logger.debug("Message writer task ended")
    
    async def _message_reader(self):
        """Background task to read messages from subprocess stdout"""
        if not self.process or not self.process.stdout:
            return
        
        try:
            while self.is_running and self.process.poll() is None:
                try:
                    line = self.process.stdout.readline()
                    if not line:
                        # EOF reached
                        break
                    
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Parse JSON message
                    try:
                        message = json.loads(line)
                        await self._response_queue.put(message)
                        self.logger.debug(f"Received message: {message.get('method', 'response')}")
                    except json.JSONDecodeError as e:
                        self.logger.warning(f"Invalid JSON received: {line}")
                        
                except Exception as e:
                    self.logger.error(f"Error reading message: {e}")
                    break
                    
        except Exception as e:
            self.logger.error(f"Message reader error: {e}")
        finally:
            self.logger.debug("Message reader task ended")
    
    async def health_check(self) -> bool:
        """
        Check if transport is healthy
        
        Returns:
            True if transport is healthy, False otherwise
        """
        if not self.is_running or not self.process:
            return False
        
        # Check if process is still running
        if self.process.poll() is not None:
            return False
        
        # Check if tasks are still running
        if self._writer_task and self._writer_task.done():
            return False
        
        if self._reader_task and self._reader_task.done():
            return False
        
        return True
    
    async def close(self):
        """Clean subprocess shutdown"""
        try:
            self.is_running = False
            
            # Cancel background tasks
            if self._writer_task and not self._writer_task.done():
                self._writer_task.cancel()
                try:
                    await self._writer_task
                except asyncio.CancelledError:
                    pass
            
            if self._reader_task and not self._reader_task.done():
                self._reader_task.cancel()
                try:
                    await self._reader_task
                except asyncio.CancelledError:
                    pass
            
            # Clear queues
            while not self._message_queue.empty():
                try:
                    self._message_queue.get_nowait()
                except asyncio.QueueEmpty:
                    break
            
            while not self._response_queue.empty():
                try:
                    self._response_queue.get_nowait()
                except asyncio.QueueEmpty:
                    break
            
            # Terminate subprocess
            if self.process:
                try:
                    # Try graceful termination first
                    if sys.platform == "win32":
                        self.process.terminate()
                    else:
                        self.process.send_signal(signal.SIGTERM)
                    
                    # Wait for process to terminate
                    try:
                        await asyncio.wait_for(
                            asyncio.create_task(self._wait_for_termination()),
                            timeout=5.0
                        )
                    except asyncio.TimeoutError:
                        self.logger.warning("Process didn't terminate gracefully, forcing kill")
                        if sys.platform == "win32":
                            self.process.kill()
                        else:
                            self.process.send_signal(signal.SIGKILL)
                        
                        # Wait a bit more for force kill
                        try:
                            await asyncio.wait_for(
                                asyncio.create_task(self._wait_for_termination()),
                                timeout=2.0
                            )
                        except asyncio.TimeoutError:
                            self.logger.error("Failed to terminate process even with force kill")
                    
                except Exception as e:
                    self.logger.error(f"Error terminating subprocess: {e}")
                finally:
                    self.process = None
            
            self.logger.info(f"✅ MCP transport closed: {self.server_name}")
            
        except Exception as e:
            self.logger.error(f"Error closing transport: {e}")
    
    async def _wait_for_termination(self):
        """Wait for process termination"""
        if self.process:
            while self.process.poll() is None:
                await asyncio.sleep(0.1)
    
    def get_status(self) -> Dict[str, Any]:
        """Get transport status information"""
        status = {
            "server_name": self.server_name,
            "is_running": self.is_running,
            "process_pid": self.process.pid if self.process else None,
            "process_running": self.process.poll() is None if self.process else False,
            "writer_task_running": not self._writer_task.done() if self._writer_task else False,
            "reader_task_running": not self._reader_task.done() if self._reader_task else False,
            "message_queue_size": self._message_queue.qsize(),
            "response_queue_size": self._response_queue.qsize()
        }
        return status
