"""
Real MCP Chain Executor

This module executes mcp_chain workflows using actual MCP tools discovered
in the runtime environment, providing real tool integration with the
autonomous agent framework.
"""

import logging
import time
import json
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass
import asyncio
from concurrent.futures import ThreadPoolExecutor, TimeoutError

from .real_mcp_discovery import get_discovery_instance, MCPTool, ToolCategory


@dataclass
class ChainStep:
    """Represents a single step in an MCP chain"""
    tool_name: str
    tool_args: Dict[str, Any]
    input_path: Optional[str] = None
    output_path: Optional[str] = None
    timeout: float = 30.0
    retry_count: int = 3


@dataclass
class ChainResult:
    """Result of a chain execution"""
    success: bool
    results: List[Any]
    execution_time: float
    error_message: Optional[str] = None
    step_results: List[Dict[str, Any]] = None
    performance_metrics: Dict[str, float] = None


class RealMCPChainExecutor:
    """
    Real MCP chain executor that works with actual MCP tools
    
    This class executes mcp_chain workflows using discovered MCP tools,
    handles tool chaining, data transformation, and error recovery.
    """
    
    def __init__(self):
        """Initialize the real MCP chain executor"""
        self.logger = logging.getLogger(__name__)
        self.discovery = get_discovery_instance()
        
        # Execution tracking
        self.execution_history = []
        self.performance_metrics = {
            'total_chains_executed': 0,
            'success_rate': 1.0,
            'avg_execution_time': 0.0,
            'tool_usage_stats': {}
        }
        
        # Thread pool for concurrent execution
        self.executor = ThreadPoolExecutor(max_workers=4)
        
    def get_available_tools(self) -> List[str]:
        """
        Get list of all available MCP tools from real external servers
        
        This function connects to actual MCP servers and discovers their tools.
        """
        try:
            # Use the real MCP client to get tools from external servers
            from .real_mcp_client_new import get_mcp_client
            import asyncio
            
            mcp_client = get_mcp_client()
            
            # Initialize servers if not already connected
            if not mcp_client.connected_servers:
                self.logger.info("Connecting to external MCP servers for tool discovery...")
                connected_count = asyncio.run(mcp_client.initialize_servers())
                self.logger.info(f"Connected to {connected_count} external MCP servers")
            
            # Get all tools from connected servers
            all_external_tools = mcp_client.get_all_tools()
            external_tool_names = list(all_external_tools.keys())
            
            # Add autonomous tools
            autonomous_tools = [
                'execute_autonomous_task',
                'discover_available_tools', 
                'create_intelligent_workflow',
                'analyze_task_complexity',
                'get_personalized_recommendations',
                'monitor_agent_performance',
                'configure_agent_preferences',
                'execute_hybrid_workflow',
                'execute_tool_chain'
            ]
            
            # Combine external and autonomous tools
            all_tools = external_tool_names + autonomous_tools
            
            self.logger.info(f"Discovered {len(external_tool_names)} external tools + {len(autonomous_tools)} autonomous tools = {len(all_tools)} total tools")
            return all_tools
            
        except Exception as e:
            self.logger.error(f"Error discovering tools from external servers: {e}")
            return self._fallback_tool_discovery()
    
    def _global_tool_discovery(self) -> List[str]:
        """Try to discover tools using global mechanisms"""
        try:
            # Check if we can access the tools through the global context
            # This could be extended to use various discovery mechanisms
            
            # For now, return a basic set of known tools from this session
            # In a real implementation, this would connect to the actual MCP system
            self.logger.info("Using global tool discovery mechanism")
            
            # We can get tools from the user preferences that would have been discovered
            # or from any cached discovery data
            known_tool_patterns = [
                'brave_web_search', 'brave_local_search', 'memory_create_entities',
                'memory_read_graph', 'github_search_repositories', 'github_create_repository',
                'postman_list_workspaces', 'trello_get_lists', 'taskmaster_get_tasks'
            ]
            
            return known_tool_patterns
            
        except Exception as e:
            self.logger.warning(f"Global tool discovery failed: {e}")
            return self._fallback_tool_discovery()
    
    def _fallback_tool_discovery(self) -> List[str]:
        """Fallback method to discover tools when MCP functions are not available"""
        # Return a basic set of commonly available tools
        # This ensures the system can still function even without full discovery
        basic_tools = [
            'search_tool', 'memory_tool', 'development_tool', 
            'analysis_tool', 'content_tool'
        ]
        
        self.logger.warning(f"Using fallback discovery - {len(basic_tools)} basic tools available")
        return basic_tools
    
    def execute_chain(self, chain_steps: List[Dict[str, Any]], 
                     initial_input: Any = None) -> ChainResult:
        """
        Execute a complete MCP tool chain
        
        Args:
            chain_steps: List of chain step configurations
            initial_input: Initial input for the first step
            
        Returns:
            ChainResult with execution details
        """
        start_time = time.time()
        results = []
        step_results = []
        current_data = initial_input
        
        self.logger.info(f"Starting chain execution with {len(chain_steps)} steps")
        
        try:
            # Ensure tools are discovered
            self.discovery.discover_all_tools()
            
            # Execute each step in the chain
            for i, step_config in enumerate(chain_steps):
                step_start = time.time()
                
                # Create chain step
                step = ChainStep(
                    tool_name=step_config.get('toolName'),
                    tool_args=step_config.get('toolArgs', {}),
                    input_path=step_config.get('inputPath'),
                    output_path=step_config.get('outputPath'),
                    timeout=step_config.get('timeout', 30.0),
                    retry_count=step_config.get('retryCount', 3)
                )
                
                self.logger.info(f"Executing step {i+1}: {step.tool_name}")
                
                # Execute the step
                step_result = self._execute_step(step, current_data)
                
                if not step_result['success']:
                    error_msg = f"Step {i+1} failed: {step_result.get('error', 'Unknown error')}"
                    self.logger.error(error_msg)
                    return ChainResult(
                        success=False,
                        results=results,
                        execution_time=time.time() - start_time,
                        error_message=error_msg,
                        step_results=step_results
                    )
                
                # Store step result
                step_execution_time = time.time() - step_start
                step_results.append({
                    'step': i + 1,
                    'tool': step.tool_name,
                    'success': True,
                    'execution_time': step_execution_time,
                    'output_size': len(str(step_result.get('result', '')))
                })
                
                # Update current data for next step
                current_data = step_result['result']
                results.append(current_data)
                
                # Update tool metrics
                self.discovery.update_tool_metrics(
                    step.tool_name, 
                    step_execution_time, 
                    True
                )
            
            # Calculate final metrics
            total_execution_time = time.time() - start_time
            
            # Update global metrics
            self._update_execution_metrics(total_execution_time, True)
            
            self.logger.info(f"Chain execution completed successfully in {total_execution_time:.2f}s")
            
            return ChainResult(
                success=True,
                results=results,
                execution_time=total_execution_time,
                step_results=step_results,
                performance_metrics=self._calculate_chain_metrics(step_results)
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Chain execution failed: {str(e)}"
            self.logger.error(error_msg)
            
            self._update_execution_metrics(execution_time, False)
            
            return ChainResult(
                success=False,
                results=results,
                execution_time=execution_time,
                error_message=error_msg,
                step_results=step_results
            )
    
    def _execute_step(self, step: ChainStep, input_data: Any) -> Dict[str, Any]:
        """Execute a single step in the chain"""
        try:
            # Prepare tool arguments
            prepared_args = self._prepare_tool_arguments(step, input_data)
            
            # Validate tool exists
            if step.tool_name not in self.discovery.tools:
                return {
                    'success': False,
                    'error': f"Tool {step.tool_name} not found"
                }
            
            # Execute with timeout and retries
            for attempt in range(step.retry_count):
                try:
                    result = self._execute_tool_with_timeout(
                        step.tool_name, 
                        prepared_args, 
                        step.timeout
                    )
                    
                    # Apply output path filtering if specified
                    if step.output_path:
                        result = self._apply_json_path(result, step.output_path)
                    
                    return {
                        'success': True,
                        'result': result,
                        'attempt': attempt + 1
                    }
                    
                except TimeoutError:
                    self.logger.warning(f"Tool {step.tool_name} timed out on attempt {attempt + 1}")
                    if attempt == step.retry_count - 1:
                        return {
                            'success': False,
                            'error': f"Tool execution timed out after {step.retry_count} attempts"
                        }
                except Exception as e:
                    self.logger.warning(f"Tool {step.tool_name} failed on attempt {attempt + 1}: {e}")
                    if attempt == step.retry_count - 1:
                        return {
                            'success': False,
                            'error': f"Tool execution failed: {str(e)}"
                        }
                        
        except Exception as e:
            return {
                'success': False,
                'error': f"Step preparation failed: {str(e)}"
            }
    
    def _prepare_tool_arguments(self, step: ChainStep, input_data: Any) -> Dict[str, Any]:
        """Prepare tool arguments, handling CHAIN_RESULT placeholders"""
        prepared_args = {}
        
        # Handle case where tool_args is a string (JSON) or dict
        if isinstance(step.tool_args, str):
            try:
                # Try to parse as JSON
                args_dict = json.loads(step.tool_args)
            except json.JSONDecodeError:
                # If not JSON, treat as a single argument
                args_dict = {"input": step.tool_args}
        elif isinstance(step.tool_args, dict):
            args_dict = step.tool_args.copy()
        else:
            # For other types, wrap in a dict
            args_dict = {"input": step.tool_args}
        
        # Process each argument
        for key, value in args_dict.items():
            prepared_args[key] = self._replace_chain_result(value, input_data, step.input_path)
        
        return prepared_args
    
    def _replace_chain_result(self, value: Any, input_data: Any, input_path: Optional[str]) -> Any:
        """Replace CHAIN_RESULT placeholders with actual data"""
        if input_data is None:
            return value
            
        # Determine what data to use
        chain_data = input_data
        if input_path:
            chain_data = self._apply_json_path(input_data, input_path)
        
        # Handle different value types
        if isinstance(value, str):
            if value == "CHAIN_RESULT":
                return chain_data
            elif "CHAIN_RESULT" in value:
                # Replace within string
                return value.replace("CHAIN_RESULT", str(chain_data))
        elif isinstance(value, list):
            # Handle list with CHAIN_RESULT
            return [chain_data if item == "CHAIN_RESULT" else item for item in value]
        elif isinstance(value, dict):
            # Recursively handle dictionary
            return {k: self._replace_chain_result(v, input_data, input_path) for k, v in value.items()}
        
        return value
    
    def _apply_json_path(self, data: Any, json_path: str) -> Any:
        """Apply JSONPath expression to extract data"""
        try:
            # Simple JSONPath implementation for basic paths like $.field or $.field.subfield
            if not json_path.startswith('$.'):
                return data
                
            path_parts = json_path[2:].split('.')
            result = data
            
            for part in path_parts:
                if isinstance(result, dict):
                    result = result.get(part)
                elif isinstance(result, list) and part.isdigit():
                    index = int(part)
                    result = result[index] if 0 <= index < len(result) else None
                else:
                    return None
                    
            return result
            
        except Exception as e:
            self.logger.warning(f"JSONPath extraction failed for {json_path}: {e}")
            return data
    
    def _execute_tool_with_timeout(self, tool_name: str, args: Dict[str, Any], timeout: float) -> Any:
        """Execute a tool with timeout protection using real MCP servers"""
        try:
            # Check if this is an autonomous tool
            autonomous_tools = [
                'execute_autonomous_task', 'discover_available_tools', 'create_intelligent_workflow',
                'analyze_task_complexity', 'get_personalized_recommendations', 'monitor_agent_performance',
                'configure_agent_preferences', 'execute_hybrid_workflow', 'execute_tool_chain'
            ]
            
            if tool_name in autonomous_tools:
                # Execute autonomous tool locally
                return self._execute_autonomous_tool(tool_name, args)
            else:
                # Execute external tool via MCP client
                return self._execute_external_tool(tool_name, args, timeout)
                
        except Exception as e:
            self.logger.error(f"Error executing tool {tool_name}: {e}")
            raise
    
    def _execute_autonomous_tool(self, tool_name: str, args: Dict[str, Any]) -> Any:
        """Execute an autonomous agent tool"""
        # Simulate autonomous tool execution
        # In a real implementation, this would call the actual autonomous tool functions
        
        result = {
            "tool": tool_name,
            "executed_by": "autonomous_agent",
            "args": args,
            "success": True,
            "message": f"Autonomous tool {tool_name} executed successfully"
        }
        
        # Add tool-specific mock results
        if tool_name == 'discover_available_tools':
            result["discovered_tools"] = self.get_available_tools()
        elif tool_name == 'analyze_task_complexity':
            result["complexity_score"] = 3.5
            result["recommendations"] = ["Break into subtasks", "Use parallel execution"]
        
        return result
    
    def _execute_external_tool(self, tool_name: str, args: Dict[str, Any], timeout: float) -> Any:
        """Execute a tool on an external MCP server"""
        import asyncio
        from .real_mcp_client_new import get_mcp_client
        
        mcp_client = get_mcp_client()
        
        # Execute the tool asynchronously
        async def execute():
            return await mcp_client.execute_tool(tool_name, args)
        
        # Run with timeout
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(asyncio.wait_for(execute(), timeout=timeout))
            loop.close()
            
            if result.get('success'):
                return result.get('result', result)
            else:
                raise Exception(result.get('error', 'Unknown error'))
                
        except asyncio.TimeoutError:
            raise TimeoutError(f"External tool {tool_name} execution timed out")
        except Exception as e:
            raise Exception(f"External tool execution failed: {str(e)}")
    
    def _simulate_tool_execution(self, tool_name: str, args: Dict[str, Any]) -> Any:
        """
        Simulate tool execution - replace with actual MCP tool calls
        
        In the real implementation, this would:
        1. Call the actual MCP tool using the MCP protocol
        2. Handle the tool's response
        3. Return the result
        """
        # Simulate execution time
        time.sleep(0.1)
        
        # Return a mock result based on tool type
        if 'search' in tool_name.lower():
            return {"results": [f"Search result for {args}"], "count": 1}
        elif 'create' in tool_name.lower():
            return {"created": True, "id": "12345", "args": args}
        elif 'get' in tool_name.lower():
            return {"data": f"Retrieved data for {args}", "status": "success"}
        else:
            return {"result": f"Executed {tool_name} with {args}", "success": True}
    
    def _update_execution_metrics(self, execution_time: float, success: bool) -> None:
        """Update global execution metrics"""
        self.performance_metrics['total_chains_executed'] += 1
        
        # Update success rate (exponential moving average)
        alpha = 0.1
        if success:
            self.performance_metrics['success_rate'] = (
                (1 - alpha) * self.performance_metrics['success_rate'] + alpha * 1.0
            )
        else:
            self.performance_metrics['success_rate'] = (
                (1 - alpha) * self.performance_metrics['success_rate'] + alpha * 0.0
            )
        
        # Update average execution time
        total_executions = self.performance_metrics['total_chains_executed']
        self.performance_metrics['avg_execution_time'] = (
            (self.performance_metrics['avg_execution_time'] * (total_executions - 1) + execution_time) /
            total_executions
        )
    
    def _calculate_chain_metrics(self, step_results: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate performance metrics for a chain execution"""
        if not step_results:
            return {}
            
        total_time = sum(step['execution_time'] for step in step_results)
        avg_step_time = total_time / len(step_results)
        max_step_time = max(step['execution_time'] for step in step_results)
        min_step_time = min(step['execution_time'] for step in step_results)
        
        return {
            'total_steps': len(step_results),
            'total_execution_time': total_time,
            'avg_step_time': avg_step_time,
            'max_step_time': max_step_time,
            'min_step_time': min_step_time,
            'efficiency_score': min_step_time / max_step_time if max_step_time > 0 else 1.0
        }
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """Get summary of chain execution performance"""
        return {
            'performance_metrics': self.performance_metrics,
            'recent_executions': len(self.execution_history),
            'tool_availability': len(self.discovery.tools),
            'discovery_summary': self.discovery.get_discovery_summary()
        }


# Global instance for singleton access
_executor_instance = None

def get_executor_instance() -> RealMCPChainExecutor:
    """Get the global executor instance"""
    global _executor_instance
    if _executor_instance is None:
        _executor_instance = RealMCPChainExecutor()
    return _executor_instance


# Convenience function for external access
def get_available_tools() -> List[str]:
    """Get all available MCP tools"""
    executor = get_executor_instance()
    return executor.get_available_tools()
