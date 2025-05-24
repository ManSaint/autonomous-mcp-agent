"""
Real MCP Executor for Autonomous MCP Agent

This module provides execution capabilities that work with actual MCP tools
through the mcp_chain infrastructure.
"""

import json
import logging
import asyncio
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from .executor import ChainExecutor, ExecutionStatus, ExecutionState
from .planner import ExecutionPlan, ToolCall
from .mcp_integration import MCPToolChainBuilder

logger = logging.getLogger(__name__)


@dataclass
class MCPExecutionResult:
    """Result from MCP tool execution"""
    tool_name: str
    success: bool
    data: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class RealMCPExecutor(ChainExecutor):
    """
    Executor that works with real MCP tools through mcp_chain.
    
    This class extends ChainExecutor to execute actual MCP tools
    available in the Claude Desktop environment.
    """
    
    def __init__(self, discovery_system, mcp_chain_function: Optional[Callable] = None):
        super().__init__(discovery_system)
        self.mcp_chain_function = mcp_chain_function
        self.execution_history: List[MCPExecutionResult] = []
        
    async def execute_real_plan(self, plan: ExecutionPlan, 
                               mcp_chain_function: Optional[Callable] = None) -> ExecutionState:
        """
        Execute a plan using real MCP tools.
        
        Args:
            plan: Execution plan to run
            mcp_chain_function: Function to call mcp_chain tool
            
        Returns:
            ExecutionState with real results
        """
        # Use provided function or stored function
        chain_function = mcp_chain_function or self.mcp_chain_function
        
        if not chain_function:
            logger.error("No mcp_chain function available for execution")
            return self._create_error_state("No MCP chain function available")
        
        logger.info(f"Executing real MCP plan with {len(plan.tools)} tools")
        
        # Initialize execution state using the existing ExecutionState from executor
        execution_state = ExecutionState(plan=plan)
        execution_state.status = ExecutionStatus.RUNNING
        execution_state.start_time = self._get_current_time()
        
        try:
            # Execute tools in order
            for i, tool_call in enumerate(plan.tools):
                logger.info(f"Executing tool {i+1}/{len(plan.tools)}: {tool_call.tool_name}")
                
                # Execute single tool
                result = await self._execute_single_mcp_tool(tool_call, chain_function)
                
                # Create ExecutionResult for compatibility
                from .executor import ExecutionResult
                exec_result = ExecutionResult(
                    tool_call=tool_call,
                    status=ExecutionStatus.SUCCESS if result.success else ExecutionStatus.FAILED,
                    output=result.data,
                    error=result.error,
                    execution_time=result.execution_time
                )
                
                # Update execution state
                execution_state.results[tool_call.order] = exec_result
                
                # Store in history
                self.execution_history.append(result)
                
                # Check for failure
                if not result.success:
                    execution_state.status = ExecutionStatus.FAILED
                    logger.error(f"Tool execution failed: {result.error}")
                    break
                
            # Mark as successful if no failures
            if execution_state.status == ExecutionStatus.RUNNING:
                execution_state.status = ExecutionStatus.SUCCESS
                
        except Exception as e:
            logger.error(f"Plan execution failed: {e}")
            execution_state.status = ExecutionStatus.FAILED
            
        finally:
            execution_state.end_time = self._get_current_time()
            execution_state.total_execution_time = (
                execution_state.end_time - execution_state.start_time
            )
            
        logger.info(f"Plan execution completed: {execution_state.status}")
        return execution_state
    
    async def _execute_single_mcp_tool(self, tool_call: ToolCall, 
                                     chain_function: Callable) -> MCPExecutionResult:
        """Execute a single MCP tool using mcp_chain"""
        start_time = self._get_current_time()
        
        try:
            # Build mcp_chain configuration
            chain_config = MCPToolChainBuilder.build_single_tool_chain(
                tool_call.tool_name, 
                tool_call.parameters
            )
            
            logger.debug(f"Calling mcp_chain with config: {chain_config}")
            
            # Execute the tool
            result = await chain_function(mcpPath=chain_config["mcpPath"])
            
            execution_time = self._get_current_time() - start_time
            
            # Parse result
            if isinstance(result, dict) and result.get('error'):
                return MCPExecutionResult(
                    tool_name=tool_call.tool_name,
                    success=False,
                    error=result['error'],
                    execution_time=execution_time,
                    metadata={'chain_config': chain_config}
                )
            else:
                return MCPExecutionResult(
                    tool_name=tool_call.tool_name,
                    success=True,
                    data=result,
                    execution_time=execution_time,
                    metadata={'chain_config': chain_config}
                )
                
        except Exception as e:
            execution_time = self._get_current_time() - start_time
            logger.error(f"MCP tool execution failed: {e}")
            
            return MCPExecutionResult(
                tool_name=tool_call.tool_name,
                success=False,
                error=str(e),
                execution_time=execution_time,
                metadata={'exception_type': type(e).__name__}
            )
    
    async def execute_tool_chain(self, tool_calls: List[ToolCall],
                               chain_function: Optional[Callable] = None) -> MCPExecutionResult:
        """Execute multiple tools as a chain using mcp_chain"""
        chain_function = chain_function or self.mcp_chain_function
        
        if not chain_function:
            return MCPExecutionResult(
                tool_name="chain",
                success=False,
                error="No MCP chain function available"
            )
        
        start_time = self._get_current_time()
        
        try:
            # Convert tool calls to chain format
            tool_chain = [
                (tool_call.tool_name, tool_call.parameters) 
                for tool_call in tool_calls
            ]
            
            # Build chain configuration
            chain_config = MCPToolChainBuilder.build_multi_tool_chain(tool_chain)
            
            # Execute the chain
            result = await chain_function(mcpPath=chain_config["mcpPath"])
            
            execution_time = self._get_current_time() - start_time
            
            return MCPExecutionResult(
                tool_name="chain",
                success=True,
                data=result,
                execution_time=execution_time,
                metadata={
                    'chain_length': len(tool_calls),
                    'tools': [tc.tool_name for tc in tool_calls]
                }
            )
            
        except Exception as e:
            execution_time = self._get_current_time() - start_time
            
            return MCPExecutionResult(
                tool_name="chain",
                success=False,
                error=str(e),
                execution_time=execution_time,
                metadata={'exception_type': type(e).__name__}
            )
    
    def _create_error_state(self, error_message: str) -> ExecutionState:
        """Create an error execution state"""
        from .planner import ExecutionPlan
        current_time = self._get_current_time()
        
        # Create empty plan for error state
        error_plan = ExecutionPlan(tools=[])
        state = ExecutionState(plan=error_plan)
        state.status = ExecutionStatus.FAILED
        state.start_time = current_time
        state.end_time = current_time
        state.total_execution_time = 0.0
        
        return state
    
    def _get_current_time(self) -> float:
        """Get current timestamp"""
        import time
        return time.time()
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get statistics about MCP tool executions"""
        if not self.execution_history:
            return {'total_executions': 0}
        
        successful = [r for r in self.execution_history if r.success]
        failed = [r for r in self.execution_history if not r.success]
        
        return {
            'total_executions': len(self.execution_history),
            'successful': len(successful),
            'failed': len(failed),
            'success_rate': len(successful) / len(self.execution_history),
            'average_execution_time': sum(r.execution_time for r in self.execution_history) / len(self.execution_history),
            'tools_used': list(set(r.tool_name for r in self.execution_history)),
            'recent_executions': [
                {
                    'tool': r.tool_name,
                    'success': r.success,
                    'time': r.execution_time
                }
                for r in self.execution_history[-10:]  # Last 10 executions
            ]
        }
    
    def clear_execution_history(self):
        """Clear execution history"""
        self.execution_history.clear()
        logger.info("Execution history cleared")


class MCPWorkflowBuilder:
    """Helper class to build complex MCP workflows"""
    
    def __init__(self, discovery_system):
        self.discovery = discovery_system
        
    def build_research_workflow(self, query: str) -> List[ToolCall]:
        """Build a research workflow using available MCP tools"""
        workflow = []
        
        # Step 1: Web search
        if self.discovery.find_tool_by_intent("web search"):
            workflow.append(ToolCall(
                tool_name="brave_web_search",
                parameters={"query": query, "count": 5},
                order=1
            ))
        
        # Step 2: Store findings in memory
        if self.discovery.find_tool_by_intent("create entities"):
            workflow.append(ToolCall(
                tool_name="create_entities",
                parameters={
                    "entities": [{
                        "name": f"research_{query.replace(' ', '_')}",
                        "entityType": "research",
                        "observations": ["Research findings from web search"]
                    }]
                },
                order=2,
                dependencies=[1]
            ))
        
        return workflow
    
    def build_file_analysis_workflow(self, file_path: str) -> List[ToolCall]:
        """Build a file analysis workflow"""
        workflow = []
        
        # Step 1: Read file
        workflow.append(ToolCall(
            tool_name="read_file",
            parameters={"path": file_path},
            order=1
        ))
        
        # Step 2: Search for code patterns (if it's a code file)
        if file_path.endswith(('.py', '.js', '.java', '.cpp')):
            workflow.append(ToolCall(
                tool_name="search_code",
                parameters={"path": file_path, "pattern": "function|class|def"},
                order=2
            ))
        
        return workflow
    
    def build_github_workflow(self, repo_query: str) -> List[ToolCall]:
        """Build a GitHub analysis workflow"""
        workflow = []
        
        # Step 1: Search repositories
        workflow.append(ToolCall(
            tool_name="search_repositories",
            parameters={"query": repo_query},
            order=1
        ))
        
        # Step 2: Search code across results
        workflow.append(ToolCall(
            tool_name="search_code",
            parameters={"q": repo_query},
            order=2
        ))
        
        return workflow


# Integration function for easy usage
async def create_real_mcp_system(mcp_chain_function):
    """
    Create a complete real MCP system with discovery and execution.
    
    Args:
        mcp_chain_function: The mcp_chain function for tool execution
        
    Returns:
        Tuple of (discovery_system, executor, workflow_builder)
    """
    from .mcp_integration import RealMCPDiscovery
    
    # Create discovery system
    discovery = RealMCPDiscovery()
    
    # Discover real tools (this would need the actual discover_tools function)
    # await discovery.discover_real_mcp_tools(discover_tools_function)
    
    # Create executor
    executor = RealMCPExecutor(discovery, mcp_chain_function)
    
    # Create workflow builder
    workflow_builder = MCPWorkflowBuilder(discovery)
    
    return discovery, executor, workflow_builder
