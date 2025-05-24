"""
MCP Protocol Implementation for Autonomous MCP Agent

This module provides the MCP protocol layer that bridges the autonomous agent framework
with the Model Context Protocol specification, enabling tool discovery and execution.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import dataclass, asdict
from datetime import datetime

# MCP imports
from mcp import types
from mcp.server import Server
from mcp.server.stdio import stdio_server

# Internal framework imports
from .discovery import ToolDiscovery
from .executor import ChainExecutor
from .advanced_planner import AdvancedExecutionPlanner
from .error_recovery import ErrorRecoverySystem
from .monitoring import MonitoringSystem
from .user_preferences import UserPreferenceEngine

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class MCPToolDefinition:
    """Represents a tool definition in MCP format"""
    name: str
    description: str
    input_schema: Dict[str, Any]
    function: Optional[Callable] = None
    category: Optional[str] = None
    confidence: float = 1.0
    performance_score: float = 1.0


class MCPProtocolBridge:
    """
    Bridges the autonomous agent framework with MCP protocol
    """
    
    def __init__(self):
        """Initialize the MCP protocol bridge"""
        self.server = Server("autonomous-mcp-agent")
        self.discovery = ToolDiscovery()
        self.executor = ChainExecutor()
        self.planner = AdvancedExecutionPlanner(self.discovery)
        self.error_recovery = ErrorRecoverySystem()
        self.monitoring = MonitoringSystem()
        self.preferences = UserPreferenceEngine()
        
        # Tool registry for MCP tools
        self.mcp_tools: Dict[str, MCPToolDefinition] = {}
        
        # Performance tracking
        self.execution_stats = {
            'total_requests': 0,
            'successful_executions': 0,
            'failed_executions': 0,
            'average_response_time': 0.0
        }
        
        # Initialize framework components
        self._initialize_framework()
        self._register_core_tools()
        
    def _initialize_framework(self):
        """Initialize the autonomous agent framework components"""
        try:
            # Initialize monitoring system (it starts automatically in __init__)
            logger.info("Monitoring system ready")
            
            # Initialize user preferences (loads automatically in __init__)
            logger.info("User preferences initialized")
            
            # Initialize tool discovery
            # Note: Tool discovery will happen automatically when tools are requested
            logger.info("Tool discovery system ready")
            
            # Set up error recovery (initializes automatically in __init__)
            logger.info("Error recovery system ready")
            
            logger.info("Framework components initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize framework: {e}")
            raise
    
    def __init__(self):
        """Initialize the MCP protocol bridge"""
        self.server = Server("autonomous-mcp-agent")
        self.discovery = ToolDiscovery()
        self.executor = ChainExecutor()
        self.planner = AdvancedExecutionPlanner(self.discovery)
        self.error_recovery = ErrorRecoverySystem()
        self.monitoring = MonitoringSystem()
        self.preferences = UserPreferenceEngine()
        
        # Tool registry for MCP tools
        self.mcp_tools: Dict[str, MCPToolDefinition] = {}
        
        # Performance tracking
        self.execution_stats = {
            'total_requests': 0,
            'successful_executions': 0,
            'failed_executions': 0,
            'average_response_time': 0.0
        }
        
        # Initialize framework components
        self._initialize_framework()
        self._register_core_tools()
        
    def _initialize_framework(self):
        """Initialize the autonomous agent framework components"""
        try:
            # Initialize monitoring system (it starts automatically in __init__)
            logger.info("Monitoring system ready")
            
            # Initialize user preferences (loads automatically in __init__)
            logger.info("User preferences initialized")
            
            # Initialize tool discovery
            # Note: Tool discovery will happen automatically when tools are requested
            logger.info("Tool discovery system ready")
            
            # Set up error recovery (initializes automatically in __init__)
            logger.info("Error recovery system ready")
            
            logger.info("Framework components initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize framework: {e}")
            raise
    
    def _register_core_tools(self):
        """Register core autonomous agent tools with MCP server"""
        
        # 1. Autonomous task execution tool
        self._register_tool(
            name="execute_autonomous_task",
            description="Execute a complex task autonomously using intelligent planning",
            input_schema={
                "type": "object",
                "properties": {
                    "task_description": {
                        "type": "string",
                        "description": "Natural language description of the task to execute"
                    },
                    "context": {
                        "type": "object",
                        "description": "Additional context or constraints for the task",
                        "default": {}
                    },
                    "preferences": {
                        "type": "object", 
                        "description": "User preferences to consider during execution",
                        "default": {}
                    }
                },
                "required": ["task_description"]
            },
            function=self._execute_autonomous_task
        )
        
        # 2. Intelligent tool discovery
        self._register_tool(
            name="discover_available_tools",
            description="Discover and categorize all available tools with intelligent filtering",
            input_schema={
                "type": "object",
                "properties": {
                    "category_filter": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Filter tools by categories",
                        "default": []
                    },
                    "capability_filter": {
                        "type": "array", 
                        "items": {"type": "string"},
                        "description": "Filter tools by capabilities",
                        "default": []
                    },
                    "include_performance": {
                        "type": "boolean",
                        "description": "Include performance metrics in results",
                        "default": False
                    }
                }
            },
            function=self._discover_tools
        )
        
        logger.info(f"Registered core autonomous agent tools")
    
    def _register_tool(self, name: str, description: str, input_schema: Dict[str, Any], 
                      function: Callable, category: str = "autonomous"):
        """Register a tool with the MCP server"""
        
        # Create tool definition
        tool_def = MCPToolDefinition(
            name=name,
            description=description,
            input_schema=input_schema,
            function=function,
            category=category
        )
        
        # Store in registry
        self.mcp_tools[name] = tool_def
        
        # Register with MCP server
        @self.server.call_tool()
        async def handle_tool_call(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
            """Handle tool calls from MCP clients"""
            return await self._handle_tool_call(name, arguments)
    
    async def _handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle incoming tool calls with comprehensive error handling and monitoring"""
        start_time = datetime.now()
        self.execution_stats['total_requests'] += 1
        
        try:
            # Record monitoring metrics
            with self.monitoring.time_operation("tool_execution"):
                
                # Get tool definition
                if tool_name not in self.mcp_tools:
                    raise ValueError(f"Tool '{tool_name}' not found")
                
                tool_def = self.mcp_tools[tool_name]
                
                # Validate arguments
                self._validate_tool_arguments(tool_def, arguments)
                
                # Execute tool function
                logger.info(f"Executing tool: {tool_name} with arguments: {arguments}")
                result = await tool_def.function(**arguments)
                
                # Track successful execution
                self.execution_stats['successful_executions'] += 1
                
                # Update performance metrics
                execution_time = (datetime.now() - start_time).total_seconds()
                self._update_performance_stats(execution_time)
                
                # Return result as MCP content
                return [types.TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
                
        except Exception as e:
            # Handle errors with recovery system
            self.execution_stats['failed_executions'] += 1
            error_result = await self._handle_tool_error(tool_name, arguments, e)
            
            return [types.TextContent(type="text", text=json.dumps(error_result, indent=2, default=str))]
    
    def _validate_tool_arguments(self, tool_def: MCPToolDefinition, arguments: Dict[str, Any]):
        """Validate tool arguments against schema"""
        # Basic validation - could be enhanced with jsonschema
        required_fields = tool_def.input_schema.get("required", [])
        for field in required_fields:
            if field not in arguments:
                raise ValueError(f"Required field '{field}' missing")
    
    async def _handle_tool_error(self, tool_name: str, arguments: Dict[str, Any], error: Exception) -> Dict[str, Any]:
        """Handle tool execution errors with recovery attempts"""
        try:
            # Use error recovery system
            error_context = self.error_recovery.create_error_context(
                error=error,
                context={
                    'tool_name': tool_name,
                    'arguments': arguments,
                    'timestamp': datetime.now().isoformat()
                }
            )
            
            # Attempt recovery
            recovery_result = await self.error_recovery.attempt_recovery(error_context)
            
            if recovery_result.success:
                logger.info(f"Successfully recovered from error in tool '{tool_name}'")
                return {
                    'success': True,
                    'result': recovery_result.result,
                    'recovered': True,
                    'recovery_strategy': recovery_result.strategy_used
                }
            else:
                logger.error(f"Failed to recover from error in tool '{tool_name}': {error}")
                return {
                    'success': False,
                    'error': str(error),
                    'error_type': type(error).__name__,
                    'recovery_attempted': True,
                    'recovery_failed': True,
                    'suggestions': recovery_result.suggestions
                }
                
        except Exception as recovery_error:
            logger.error(f"Error recovery failed for tool '{tool_name}': {recovery_error}")
            return {
                'success': False,
                'error': str(error),
                'error_type': type(error).__name__,
                'recovery_error': str(recovery_error)
            }
    
    def _update_performance_stats(self, execution_time: float):
        """Update performance statistics"""
        total_executions = self.execution_stats['successful_executions'] + self.execution_stats['failed_executions']
        if total_executions > 0:
            # Update average response time
            current_avg = self.execution_stats['average_response_time']
            self.execution_stats['average_response_time'] = (
                (current_avg * (total_executions - 1) + execution_time) / total_executions
            )
    
    # Tool Implementation Functions
    
    async def _execute_autonomous_task(self, task_description: str, context: Dict = None, 
                                     preferences: Dict = None) -> Dict[str, Any]:
        """Execute a task autonomously using the full framework capabilities"""
        try:
            # Apply user preferences if provided
            if preferences:
                self.preferences.update_preferences(preferences)
            
            # Create advanced execution plan
            plan = await self.planner.create_advanced_plan(
                intent=task_description,
                context=context or {}
            )
            
            # Execute plan with monitoring
            with self.monitoring.time_operation("autonomous_execution"):
                result = await self.executor.execute_plan(plan)
            
            return {
                'success': True,
                'task': task_description,
                'execution_plan': plan.to_dict() if hasattr(plan, 'to_dict') else str(plan),
                'result': result,
                'metrics': {
                    'tools_used': len(plan.tool_calls) if hasattr(plan, 'tool_calls') else 0,
                    'execution_time': result.get('execution_time', 0),
                    'success_rate': result.get('success_rate', 0)
                }
            }
            
        except Exception as e:
            logger.error(f"Autonomous task execution failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'task': task_description
            }
    
    async def _discover_tools(self, category_filter: List[str] = None, 
                            capability_filter: List[str] = None,
                            include_performance: bool = False) -> Dict[str, Any]:
        """Discover available tools with intelligent filtering"""
        try:
            # Refresh tool discovery
            discovered_tools = self.discovery.discover_tools()
            
            # Apply filters
            filtered_tools = discovered_tools
            if category_filter:
                filtered_tools = {
                    name: tool for name, tool in filtered_tools.items()
                    if any(cat in tool.get('categories', []) for cat in category_filter)
                }
            
            if capability_filter:
                filtered_tools = {
                    name: tool for name, tool in filtered_tools.items()
                    if any(cap in tool.get('capabilities', []) for cap in capability_filter)
                }
            
            # Format results
            tools_info = {}
            for name, tool in filtered_tools.items():
                tool_info = {
                    'name': name,
                    'description': tool.get('description', 'No description available'),
                    'categories': tool.get('categories', []),
                    'capabilities': tool.get('capabilities', [])
                }
                
                if include_performance:
                    stats = self.discovery.get_tool_stats(name)
                    tool_info['performance'] = stats
                
                tools_info[name] = tool_info
            
            return {
                'success': True,
                'total_tools': len(filtered_tools),
                'tools': tools_info,
                'discovery_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Tool discovery failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_tool_list(self) -> List[types.Tool]:
        """Get list of available tools for MCP list_tools request"""
        tools = []
        
        for name, tool_def in self.mcp_tools.items():
            tools.append(types.Tool(
                name=name,
                description=tool_def.description,
                inputSchema=tool_def.input_schema
            ))
        
        return tools
    
    def get_server_info(self) -> Dict[str, Any]:
        """Get server information"""
        return {
            "name": "autonomous-mcp-agent",
            "version": "1.0.0",
            "description": "Autonomous MCP Agent - Intelligent task execution with tool discovery and planning",
            "capabilities": [
                "autonomous_task_execution",
                "intelligent_tool_discovery", 
                "advanced_execution_planning",
                "error_recovery",
                "performance_monitoring",
                "user_personalization"
            ],
            "total_tools": len(self.mcp_tools),
            "framework_status": "operational"
        }


# Export key classes
__all__ = ['MCPProtocolBridge', 'MCPToolDefinition']
