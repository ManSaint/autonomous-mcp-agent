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
from .real_mcp_discovery import RealMCPDiscovery
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
        # Use real discovery for actual MCP tools
        self.real_discovery = RealMCPDiscovery()
        self.discovery = self.real_discovery  # For compatibility
        self.executor = ChainExecutor()
        self.planner = AdvancedExecutionPlanner(self.real_discovery)
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
        # Use real discovery for actual MCP tools
        self.real_discovery = RealMCPDiscovery()
        self.discovery = self.real_discovery  # For compatibility
        self.executor = ChainExecutor()
        self.planner = AdvancedExecutionPlanner(self.real_discovery)
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
        
        # Import advanced tools
        from .autonomous_tools import AdvancedAutonomousTools
        self.advanced_tools = AdvancedAutonomousTools()
        
        # 3. Create intelligent workflow
        self._register_tool(
            name="create_intelligent_workflow",
            description="Generate intelligent workflow for complex task execution with advanced planning",
            input_schema={
                "type": "object",
                "properties": {
                    "task_description": {
                        "type": "string",
                        "description": "Natural language task description"
                    },
                    "context": {
                        "type": "object",
                        "description": "Additional context or constraints",
                        "default": {}
                    },
                    "include_analysis": {
                        "type": "boolean",
                        "description": "Include task complexity analysis",
                        "default": True
                    },
                    "include_recommendations": {
                        "type": "boolean",
                        "description": "Include personalized recommendations",
                        "default": True
                    }
                },
                "required": ["task_description"]
            },
            function=self._create_intelligent_workflow
        )
        
        # 4. Analyze task complexity
        self._register_tool(
            name="analyze_task_complexity",
            description="Analyze task complexity and provide detailed recommendations and risk assessment",
            input_schema={
                "type": "object",
                "properties": {
                    "task_description": {
                        "type": "string",
                        "description": "Task to analyze for complexity"
                    },
                    "context": {
                        "type": "object",
                        "description": "Additional context for analysis",
                        "default": {}
                    },
                    "include_tool_recommendations": {
                        "type": "boolean",
                        "description": "Include specific tool recommendations",
                        "default": True
                    }
                },
                "required": ["task_description"]
            },
            function=self._analyze_task_complexity
        )
        
        # 5. Get personalized recommendations
        self._register_tool(
            name="get_personalized_recommendations",
            description="Get ML-powered personalized recommendations based on user preferences and history",
            input_schema={
                "type": "object",
                "properties": {
                    "task_description": {
                        "type": "string",
                        "description": "Task to get recommendations for"
                    },
                    "context": {
                        "type": "object",
                        "description": "Additional context",
                        "default": {}
                    },
                    "preferences": {
                        "type": "object",
                        "description": "User preferences to consider",
                        "default": {}
                    },
                    "include_optimization_tips": {
                        "type": "boolean",
                        "description": "Include optimization tips",
                        "default": True
                    }
                },
                "required": ["task_description"]
            },
            function=self._get_personalized_recommendations
        )
        
        # 6. Monitor agent performance
        self._register_tool(
            name="monitor_agent_performance",
            description="Monitor real-time agent performance with detailed metrics and insights",
            input_schema={
                "type": "object",
                "properties": {
                    "time_range": {
                        "type": "string",
                        "enum": ["1h", "24h", "7d", "30d"],
                        "description": "Time range for performance metrics",
                        "default": "24h"
                    },
                    "include_details": {
                        "type": "boolean",
                        "description": "Include detailed performance breakdown",
                        "default": False
                    },
                    "include_trends": {
                        "type": "boolean",
                        "description": "Include performance trend analysis",
                        "default": True
                    }
                }
            },
            function=self._monitor_agent_performance
        )
        
        # 7. Configure agent preferences
        self._register_tool(
            name="configure_agent_preferences",
            description="Configure agent preferences and personalization settings",
            input_schema={
                "type": "object",
                "properties": {
                    "preferences": {
                        "type": "object",
                        "description": "Preference settings to apply"
                    },
                    "operation": {
                        "type": "string",
                        "enum": ["update", "replace", "reset"],
                        "description": "Configuration operation type",
                        "default": "update"
                    },
                    "validate_preferences": {
                        "type": "boolean",
                        "description": "Validate preferences before applying",
                        "default": True
                    }
                },
                "required": ["preferences"]
            },
            function=self._configure_agent_preferences
        )
        
        logger.info(f"Registered {len(self.mcp_tools)} autonomous agent tools including advanced capabilities")
    
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
            
            # Use the real MCP chain executor instead of basic executor
            from .mcp_chain_executor import RealMCPChainExecutor
            real_executor = RealMCPChainExecutor()
            
            # Convert plan to chain steps format
            chain_steps = []
            for tool_call in plan.tools:
                chain_steps.append({
                    'tool_name': tool_call.tool_name,
                    'parameters': tool_call.parameters,
                    'order': tool_call.order
                })
            
            # Execute chain with monitoring
            with self.monitoring.time_operation("autonomous_execution"):
                result = real_executor.execute_chain(chain_steps, initial_input=task_description)
            
            return {
                'success': result.success,
                'task': task_description,
                'execution_plan': [step for step in chain_steps],
                'result': result.results,
                'error_message': result.error_message,
                'metrics': {
                    'execution_time': result.execution_time,
                    'steps_completed': len(result.step_results) if result.step_results else 0,
                    'performance_metrics': result.performance_metrics
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
            # Refresh tool discovery - get all tools and convert to the expected format
            discovered_tools_dict = self.discovery.discovered_tools
            
            # Convert DiscoveredTool objects to dictionary format for filtering
            discovered_tools = {}
            for name, tool in discovered_tools_dict.items():
                discovered_tools[name] = {
                    'description': tool.description,
                    'categories': [cap.category for cap in tool.capabilities],
                    'capabilities': [cap.subcategory for cap in tool.capabilities],
                    'server': tool.server,
                    'parameters': tool.parameters,
                    'usage_count': tool.usage_count,
                    'success_rate': tool.success_rate,
                    'average_execution_time': tool.average_execution_time
                }
            
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
    
    # Advanced Autonomous Tool Implementations
    
    async def _create_intelligent_workflow(self, task_description: str, context: Dict[str, Any] = None, 
                                         include_analysis: bool = True, include_recommendations: bool = True) -> Dict[str, Any]:
        """Create intelligent workflow implementation"""
        try:
            analysis = None
            recommendations = None
            
            if include_analysis:
                analysis = await self.advanced_tools.analyze_task_complexity(task_description, context or {})
            
            if include_recommendations:
                recommendations = await self.advanced_tools.get_personalized_recommendations(
                    task_description, context or {}, {}
                )
            
            workflow = await self.advanced_tools.create_intelligent_workflow(
                task_description, context, analysis, recommendations
            )
            
            return {
                'success': True,
                'workflow': {
                    'workflow_id': workflow.workflow_id,
                    'title': workflow.title,
                    'description': workflow.description,
                    'total_estimated_duration': workflow.total_estimated_duration,
                    'overall_success_probability': workflow.overall_success_probability,
                    'step_count': len(workflow.steps),
                    'created_at': workflow.created_at.isoformat(),
                    'metadata': workflow.metadata
                },
                'analysis': analysis.__dict__ if analysis else None,
                'recommendations': recommendations
            }
            
        except Exception as e:
            logger.error(f"Intelligent workflow creation failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _analyze_task_complexity(self, task_description: str, context: Dict[str, Any] = None, 
                                     include_tool_recommendations: bool = True) -> Dict[str, Any]:
        """Analyze task complexity implementation"""
        try:
            analysis = await self.advanced_tools.analyze_task_complexity(task_description, context or {})
            
            result = {
                'success': True,
                'complexity_score': analysis.complexity_score,
                'estimated_duration': analysis.estimated_duration,
                'recommended_approach': analysis.recommended_approach,
                'success_probability': analysis.success_probability,
                'risk_factors': analysis.risk_factors
            }
            
            if include_tool_recommendations:
                result['required_tools'] = analysis.required_tools
            
            return result
            
        except Exception as e:
            logger.error(f"Task complexity analysis failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _get_personalized_recommendations(self, task_description: str, context: Dict[str, Any] = None,
                                              preferences: Dict[str, Any] = None, include_optimization_tips: bool = True) -> Dict[str, Any]:
        """Get personalized recommendations implementation"""
        try:
            recommendations = await self.advanced_tools.get_personalized_recommendations(
                task_description, context or {}, preferences or {}
            )
            
            if not include_optimization_tips and 'optimization_tips' in recommendations:
                del recommendations['optimization_tips']
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Personalized recommendations failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _monitor_agent_performance(self, time_range: str = "24h", include_details: bool = False, 
                                       include_trends: bool = True) -> Dict[str, Any]:
        """Monitor agent performance implementation"""
        try:
            performance_data = await self.advanced_tools.monitor_agent_performance(time_range, include_details)
            
            if not include_trends and 'performance_trends' in performance_data.get('metrics', {}):
                del performance_data['metrics']['performance_trends']
            
            return performance_data
            
        except Exception as e:
            logger.error(f"Performance monitoring failed: {e}")
            return {
                'success': False, 
                'error': str(e),
                'basic_metrics': {
                    'status': 'monitoring_unavailable',
                    'basic_health': 'ok'
                }
            }
    
    async def _configure_agent_preferences(self, preferences: Dict[str, Any], operation: str = "update",
                                         validate_preferences: bool = True) -> Dict[str, Any]:
        """Configure agent preferences implementation"""
        try:
            if validate_preferences:
                # Basic validation
                if not isinstance(preferences, dict):
                    return {'success': False, 'error': 'Preferences must be a dictionary'}
            
            config_result = await self.advanced_tools.configure_agent_preferences(preferences, operation)
            return config_result
            
        except Exception as e:
            logger.error(f"Preference configuration failed: {e}")
            return {'success': False, 'error': str(e)}
    
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
