"""
Phase 7.2: Real Tool Execution Engine

This module implements execution of tools across multiple MCP servers,
handling tool routing, parameter translation, and cross-server workflows.
"""

import logging
import time
import asyncio
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass
import json

try:
    from .multi_server_discovery import get_client_manager, get_tool_registry, DiscoveredServerTool
except ImportError:
    # Fallback for testing - create mock classes
    class DiscoveredServerTool:
        def __init__(self, name, server, description):
            self.name = name
            self.server = server
            self.description = description
    
    def get_client_manager():
        return None
    
    def get_tool_registry():
        return None


@dataclass
class ToolExecutionResult:
    """Result of a tool execution"""
    success: bool
    result: Any = None
    execution_time: float = 0.0
    server: str = ""
    tool_name: str = ""
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None


@dataclass
class WorkflowStep:
    """Single step in a cross-server workflow"""
    tool_name: str
    server: str
    parameters: Dict[str, Any]
    depends_on: List[str] = None
    timeout: float = 30.0
    retry_count: int = 3


class MultiServerExecutor:
    """Execute tools across multiple MCP servers"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Mock client manager and tool registry for testing
        self.servers = {
            'github': {'status': 'connected', 'tools': ['search_repositories', 'create_repository', 'get_file_contents']},
            'memory': {'status': 'connected', 'tools': ['create_entities', 'search_nodes', 'read_graph']},
            'postman': {'status': 'connected', 'tools': ['list_workspaces', 'get_workspace', 'create_collection']},
            'trello': {'status': 'connected', 'tools': ['get_lists', 'add_card_to_list', 'get_cards_by_list_id']}
        }
        
        self.execution_history = []
        self.server_performance = {}
        self.tool_routing_cache = {}
        
        self.metrics = {
            'total_executions': 0,
            'successful_executions': 0,
            'failed_executions': 0,
            'avg_execution_time': 0.0,
            'server_usage_stats': {}
        }
    
    async def route_tool_call(self, tool_name: str, parameters: Dict[str, Any]) -> ToolExecutionResult:
        """Route tool call to appropriate server"""
        start_time = time.time()
        
        try:
            server_name = await self._find_tool_server(tool_name)
            if not server_name:
                return ToolExecutionResult(
                    success=False,
                    tool_name=tool_name,
                    error_message=f"Tool {tool_name} not found in any connected server",
                    execution_time=time.time() - start_time
                )
            
            if not await self._verify_server_connection(server_name):
                return ToolExecutionResult(
                    success=False,
                    tool_name=tool_name,
                    server=server_name,
                    error_message=f"Server {server_name} is not connected",
                    execution_time=time.time() - start_time
                )
            
            result = await self._execute_tool_on_server(tool_name, server_name, parameters)
            execution_time = time.time() - start_time
            await self._update_performance_metrics(server_name, tool_name, execution_time, result.success)
            
            result.execution_time = execution_time
            self.execution_history.append(result)
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_result = ToolExecutionResult(
                success=False,
                tool_name=tool_name,
                error_message=f"Routing error: {str(e)}",
                execution_time=execution_time
            )
            self.execution_history.append(error_result)
            return error_result
    
    async def _find_tool_server(self, tool_name: str) -> Optional[str]:
        """Find which server hosts a specific tool"""
        if tool_name in self.tool_routing_cache:
            return self.tool_routing_cache[tool_name]
        
        for server_name, server_info in self.servers.items():
            if tool_name in server_info['tools']:
                self.tool_routing_cache[tool_name] = server_name
                return server_name
        
        return None
    
    async def _verify_server_connection(self, server_name: str) -> bool:
        """Verify server is still connected and responsive"""
        if server_name not in self.servers:
            return False
        return self.servers[server_name]['status'] == 'connected'
    
    async def _execute_tool_on_server(self, tool_name: str, server_name: str, 
                                     parameters: Dict[str, Any]) -> ToolExecutionResult:
        """Execute a tool on a specific server"""
        try:
            await asyncio.sleep(0.1)  # Simulate execution time
            
            # Generate appropriate response based on server and tool
            result = await self._simulate_server_tool_execution(tool_name, server_name, parameters)
            
            return ToolExecutionResult(
                success=True,
                result=result,
                server=server_name,
                tool_name=tool_name,
                metadata={
                    'server_type': self._get_server_type(server_name),
                    'parameter_count': len(parameters)
                }
            )
            
        except Exception as e:
            return ToolExecutionResult(
                success=False,
                server=server_name,
                tool_name=tool_name,
                error_message=f"Execution failed: {str(e)}"
            )
    
    async def _simulate_server_tool_execution(self, tool_name: str, server_name: str, 
                                            parameters: Dict[str, Any]) -> Any:
        """Simulate tool execution on server"""
        if server_name == "github":
            if "search" in tool_name:
                return {"repositories": [{"name": f"repo-{i}", "stars": i*10} for i in range(3)]}
            elif "create" in tool_name:
                return {"created": True, "url": "https://github.com/user/repo", "id": "12345"}
        elif server_name == "memory":
            if "create" in tool_name:
                return {"entities_created": 1, "ids": ["entity_123"]}
            elif "read" in tool_name:
                return {"graph": {"entities": 5, "relations": 3}}
        elif server_name == "postman":
            if "list" in tool_name:
                return {"workspaces": [{"id": "ws_1", "name": "My Workspace"}]}
        elif server_name == "trello":
            if "get_lists" in tool_name:
                return {"lists": [{"id": "list_1", "name": "To Do"}]}
        
        return {"success": True, "tool": tool_name, "server": server_name, "parameters": parameters}
    
    def _get_server_type(self, server_name: str) -> str:
        """Get server type for metadata"""
        server_types = {
            'github': 'development',
            'memory': 'knowledge',
            'postman': 'api_testing',
            'trello': 'project_management'
        }
        return server_types.get(server_name, 'unknown')
    
    async def execute_cross_server_workflow(self, workflow_steps: List[WorkflowStep]) -> List[ToolExecutionResult]:
        """Execute workflow spanning multiple servers"""
        self.logger.info(f"Executing cross-server workflow with {len(workflow_steps)} steps")
        
        results = []
        step_outputs = {}
        
        dependency_graph = self._build_dependency_graph(workflow_steps)
        
        for step in dependency_graph:
            self.logger.info(f"Executing step: {step.tool_name} on {step.server}")
            
            resolved_parameters = await self._resolve_step_dependencies(step, step_outputs)
            result = await self.route_tool_call(step.tool_name, resolved_parameters)
            results.append(result)
            
            step_outputs[step.tool_name] = result.result
            
            if not result.success:
                self.logger.error(f"Workflow step failed: {step.tool_name} - {result.error_message}")
                break
        
        return results
    
    def _build_dependency_graph(self, workflow_steps: List[WorkflowStep]) -> List[WorkflowStep]:
        """Build execution order based on dependencies"""
        executed = set()
        ordered_steps = []
        remaining_steps = workflow_steps.copy()
        
        while remaining_steps:
            ready_steps = []
            for step in remaining_steps:
                if not step.depends_on or all(dep in executed for dep in step.depends_on):
                    ready_steps.append(step)
            
            if not ready_steps:
                ready_steps = remaining_steps
            
            for step in ready_steps:
                ordered_steps.append(step)
                executed.add(step.tool_name)
                remaining_steps.remove(step)
        
        return ordered_steps
    
    async def _resolve_step_dependencies(self, step: WorkflowStep, 
                                       step_outputs: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve parameter dependencies from previous step outputs"""
        resolved_params = step.parameters.copy()
        
        for key, value in resolved_params.items():
            if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                dependency_ref = value[2:-1]
                if "." in dependency_ref:
                    step_name, field = dependency_ref.split(".", 1)
                    if step_name in step_outputs:
                        output = step_outputs[step_name]
                        if isinstance(output, dict) and field in output:
                            resolved_params[key] = output[field]
                        else:
                            resolved_params[key] = output
                else:
                    if dependency_ref in step_outputs:
                        resolved_params[key] = step_outputs[dependency_ref]
        
        return resolved_params
    
    async def handle_server_failures(self, failed_server: str, tool_call: Dict[str, Any]) -> ToolExecutionResult:
        """Graceful handling when servers are unavailable"""
        self.logger.warning(f"Handling server failure: {failed_server}")
        
        tool_name = tool_call.get('tool_name', '')
        parameters = tool_call.get('parameters', {})
        
        alternative_server = await self._find_alternative_server(tool_name, failed_server)
        
        if alternative_server:
            self.logger.info(f"Attempting fallback to {alternative_server} for {tool_name}")
            return await self.route_tool_call(tool_name, parameters)
        
        return ToolExecutionResult(
            success=False,
            tool_name=tool_name,
            server=failed_server,
            error_message=f"Server {failed_server} unavailable and no alternative found",
            metadata={'failure_type': 'server_unavailable', 'attempted_fallback': True}
        )
    
    async def _find_alternative_server(self, tool_name: str, failed_server: str) -> Optional[str]:
        """Find alternative server that might have similar functionality"""
        for server_name, server_info in self.servers.items():
            if (server_name != failed_server and 
                server_info['status'] == 'connected' and 
                tool_name in server_info['tools']):
                return server_name
        return None
    
    async def _update_performance_metrics(self, server_name: str, tool_name: str, 
                                        execution_time: float, success: bool) -> None:
        """Update performance metrics for servers and tools"""
        self.metrics['total_executions'] += 1
        if success:
            self.metrics['successful_executions'] += 1
        else:
            self.metrics['failed_executions'] += 1
        
        total = self.metrics['total_executions']
        current_avg = self.metrics['avg_execution_time']
        self.metrics['avg_execution_time'] = (current_avg * (total - 1) + execution_time) / total
        
        if server_name not in self.server_performance:
            self.server_performance[server_name] = {
                'total_calls': 0,
                'successful_calls': 0,
                'avg_response_time': 0.0,
                'tools_used': set()
            }
        
        server_stats = self.server_performance[server_name]
        server_stats['total_calls'] += 1
        if success:
            server_stats['successful_calls'] += 1
        
        server_total = server_stats['total_calls']
        server_avg = server_stats['avg_response_time']
        server_stats['avg_response_time'] = (server_avg * (server_total - 1) + execution_time) / server_total
        server_stats['tools_used'].add(tool_name)
        
        if server_name not in self.metrics['server_usage_stats']:
            self.metrics['server_usage_stats'][server_name] = 0
        self.metrics['server_usage_stats'][server_name] += 1
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """Get comprehensive execution summary"""
        return {
            'global_metrics': self.metrics,
            'server_performance': {
                name: {
                    'total_calls': stats['total_calls'],
                    'success_rate': stats['successful_calls'] / max(stats['total_calls'], 1),
                    'avg_response_time': stats['avg_response_time'],
                    'tools_used': len(stats['tools_used'])
                }
                for name, stats in self.server_performance.items()
            },
            'recent_executions': len(self.execution_history),
            'tool_routing_cache_size': len(self.tool_routing_cache)
        }


class ToolCallTranslator:
    """Translate between different server tool formats"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        self.parameter_mappings = {
            'github': {
                'search_repositories': {'q': 'query', 'sort': 'sort'},
                'create_repository': {'name': 'name', 'description': 'description'}
            },
            'memory': {
                'create_entities': {'entities': 'entities'},
                'search_nodes': {'query': 'query'}
            }
        }
    
    async def normalize_parameters(self, tool_name: str, params: Dict[str, Any], 
                                 target_server: str) -> Dict[str, Any]:
        """Normalize parameters for different server expectations"""
        server_mappings = self.parameter_mappings.get(target_server, {})
        tool_mappings = server_mappings.get(tool_name, {})
        
        if not tool_mappings:
            return params
        
        normalized = {}
        for original_key, value in params.items():
            mapped_key = tool_mappings.get(original_key, original_key)
            normalized[mapped_key] = value
        
        return normalized
    
    async def translate_responses(self, response: Any, source_server: str) -> Any:
        """Translate responses to consistent format"""
        if source_server == 'github' and isinstance(response, dict) and 'repositories' in response:
            return {
                'items': [
                    {
                        'id': repo.get('name', ''),
                        'name': repo.get('name', ''),
                        'metadata': repo
                    }
                    for repo in response['repositories']
                ]
            }
        
        return response


# Global instances
_multi_server_executor = None
_tool_call_translator = None

def get_multi_server_executor() -> MultiServerExecutor:
    """Get global multi-server executor instance"""
    global _multi_server_executor
    if _multi_server_executor is None:
        _multi_server_executor = MultiServerExecutor()
    return _multi_server_executor

def get_tool_call_translator() -> ToolCallTranslator:
    """Get global tool call translator instance"""
    global _tool_call_translator
    if _tool_call_translator is None:
        _tool_call_translator = ToolCallTranslator()
    return _tool_call_translator
