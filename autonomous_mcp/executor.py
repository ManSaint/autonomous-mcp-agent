"""
Chain Executor for Autonomous MCP Agent
Task 1.3: Executes plans using mcp_chain with retry logic and state tracking
"""

import json
import time
import asyncio
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

from .planner import ExecutionPlan, ToolCall
from .discovery import ToolDiscovery, DiscoveredTool

logger = logging.getLogger(__name__)


class ExecutionStatus(Enum):
    """Status of a tool execution"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    TIMEOUT = "timeout"
    RETRYING = "retrying"


@dataclass
class ExecutionResult:
    """Result of a tool execution"""
    tool_call: ToolCall
    status: ExecutionStatus
    output: Any = None
    error: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    execution_time: float = 0.0
    retry_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'tool_call': self.tool_call.to_dict(),
            'status': self.status.value,
            'output': self.output,
            'error': self.error,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'execution_time': self.execution_time,
            'retry_count': self.retry_count
        }


@dataclass
class ExecutionState:
    """Tracks the state of an execution plan"""
    plan: ExecutionPlan
    results: Dict[int, ExecutionResult] = field(default_factory=dict)
    current_step: int = 0
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    total_execution_time: float = 0.0
    status: ExecutionStatus = ExecutionStatus.PENDING
    
    def is_complete(self) -> bool:
        """Check if all tools have been executed"""
        return all(
            result.status in [ExecutionStatus.SUCCESS, ExecutionStatus.FAILED, ExecutionStatus.SKIPPED]
            for result in self.results.values()
        )
    
    def get_successful_outputs(self) -> Dict[int, Any]:
        """Get outputs from successful executions"""
        return {
            order: result.output 
            for order, result in self.results.items()
            if result.status == ExecutionStatus.SUCCESS and result.output is not None
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'plan': self.plan.to_dict(),
            'results': {order: result.to_dict() for order, result in self.results.items()},
            'current_step': self.current_step,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'total_execution_time': self.total_execution_time,
            'status': self.status.value
        }


class ChainExecutor:
    """
    Executes tool chains using mcp_chain.
    
    This class handles:
    - Sequential and dependency-based execution
    - Output passing between tools
    - Retry logic on failures
    - Timeout handling
    - State tracking and persistence
    """
    
    def __init__(self, 
                 discovery: Optional[ToolDiscovery] = None,
                 max_retries: int = 3,
                 default_timeout: float = 30.0):
        """
        Initialize the Chain Executor.
        
        Args:
            discovery: Tool discovery instance for updating performance metrics
            max_retries: Maximum number of retries per tool
            default_timeout: Default timeout for tool execution in seconds
        """
        self.discovery = discovery
        self.max_retries = max_retries
        self.default_timeout = default_timeout
        self.execution_states: Dict[str, ExecutionState] = {}
    
    async def execute_plan(self, 
                          plan: ExecutionPlan,
                          mcp_chain_func: Any,
                          parallel: bool = False) -> ExecutionState:
        """
        Execute a complete plan using mcp_chain.
        
        Args:
            plan: The execution plan to run
            mcp_chain_func: The mcp_chain function to use for execution
            parallel: Whether to execute independent tools in parallel
            
        Returns:
            ExecutionState with results
        """
        # Initialize execution state
        state = ExecutionState(plan=plan)
        self.execution_states[plan.plan_id] = state
        
        logger.info(f"Starting execution of plan {plan.plan_id} with {len(plan.tools)} tools")
        
        try:
            if parallel and self._can_parallelize(plan):
                await self._execute_parallel(state, mcp_chain_func)
            else:
                await self._execute_sequential(state, mcp_chain_func)
                
        except Exception as e:
            logger.error(f"Error executing plan {plan.plan_id}: {e}")
            state.status = ExecutionStatus.FAILED
            
        finally:
            state.end_time = datetime.now()
            state.total_execution_time = (state.end_time - state.start_time).total_seconds()
            
            if state.is_complete() and not any(
                r.status == ExecutionStatus.FAILED for r in state.results.values()
            ):
                state.status = ExecutionStatus.SUCCESS
            
        logger.info(f"Completed execution of plan {plan.plan_id} with status {state.status}")
        return state
    
    async def _execute_sequential(self, state: ExecutionState, mcp_chain_func: Any) -> None:
        """Execute tools sequentially based on order and dependencies"""
        # Sort tools by order
        sorted_tools = sorted(state.plan.tools, key=lambda t: t.order)
        
        for tool_call in sorted_tools:
            # Check dependencies
            if not self._dependencies_satisfied(tool_call, state):
                logger.warning(f"Skipping {tool_call.tool_name} due to failed dependencies")
                state.results[tool_call.order] = ExecutionResult(
                    tool_call=tool_call,
                    status=ExecutionStatus.SKIPPED,
                    error="Dependencies not satisfied"
                )
                continue
            
            # Execute the tool
            result = await self._execute_tool(tool_call, state, mcp_chain_func)
            state.results[tool_call.order] = result
            state.current_step = tool_call.order
            
            # Update discovery metrics if available
            if self.discovery and result.status in [ExecutionStatus.SUCCESS, ExecutionStatus.FAILED]:
                self.discovery.update_tool_performance(
                    tool_call.tool_name,
                    result.status == ExecutionStatus.SUCCESS,
                    result.execution_time
                )
    
    async def _execute_parallel(self, state: ExecutionState, mcp_chain_func: Any) -> None:
        """Execute independent tools in parallel"""
        # Group tools by dependency levels
        levels = self._get_dependency_levels(state.plan)
        
        for level, tools in sorted(levels.items()):
            # Execute all tools at this level in parallel
            tasks = []
            for tool_call in tools:
                if self._dependencies_satisfied(tool_call, state):
                    task = self._execute_tool(tool_call, state, mcp_chain_func)
                    tasks.append(task)
                else:
                    state.results[tool_call.order] = ExecutionResult(
                        tool_call=tool_call,
                        status=ExecutionStatus.SKIPPED,
                        error="Dependencies not satisfied"
                    )
            
            # Wait for all tasks at this level to complete
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        logger.error(f"Error in parallel execution: {result}")
    
    async def _execute_tool(self, 
                           tool_call: ToolCall, 
                           state: ExecutionState,
                           mcp_chain_func: Any) -> ExecutionResult:
        """Execute a single tool with retry logic"""
        result = ExecutionResult(
            tool_call=tool_call,
            status=ExecutionStatus.PENDING,
            start_time=datetime.now()
        )
        
        for attempt in range(self.max_retries + 1):
            try:
                result.retry_count = attempt
                if attempt > 0:
                    result.status = ExecutionStatus.RETRYING
                    logger.info(f"Retrying {tool_call.tool_name} (attempt {attempt + 1}/{self.max_retries + 1})")
                else:
                    result.status = ExecutionStatus.RUNNING
                
                # Prepare parameters with output substitution
                params = self._prepare_parameters(tool_call, state)
                
                # Build mcp_chain call
                if len(state.results) == 0:
                    # First tool - no chaining needed
                    output = await self._execute_single_tool(
                        tool_call, params, mcp_chain_func, tool_call.timeout or self.default_timeout
                    )
                else:
                    # Chain with previous results
                    output = await self._execute_chained_tool(
                        tool_call, params, state, mcp_chain_func, tool_call.timeout or self.default_timeout
                    )
                
                result.output = output
                result.status = ExecutionStatus.SUCCESS
                result.end_time = datetime.now()
                result.execution_time = (result.end_time - result.start_time).total_seconds()
                
                logger.info(f"Successfully executed {tool_call.tool_name} in {result.execution_time:.2f}s")
                return result
                
            except asyncio.TimeoutError:
                result.status = ExecutionStatus.TIMEOUT
                result.error = f"Timeout after {tool_call.timeout or self.default_timeout}s"
                logger.error(f"Timeout executing {tool_call.tool_name}")
                
            except Exception as e:
                result.error = str(e)
                logger.error(f"Error executing {tool_call.tool_name}: {e}")
                
                if attempt < self.max_retries:
                    # Exponential backoff
                    await asyncio.sleep(2 ** attempt)
                else:
                    result.status = ExecutionStatus.FAILED
        
        result.end_time = datetime.now()
        result.execution_time = (result.end_time - result.start_time).total_seconds()
        return result
    
    async def _execute_single_tool(self, 
                                  tool_call: ToolCall,
                                  params: Dict[str, Any],
                                  mcp_chain_func: Any,
                                  timeout: float) -> Any:
        """Execute a single tool without chaining"""
        # Simulate async execution with timeout
        # In real implementation, this would call the actual mcp_chain function
        
        # For now, we'll create a mock response
        logger.debug(f"Executing single tool: {tool_call.tool_name} with params: {params}")
        
        # Simulate execution time
        await asyncio.sleep(0.1)
        
        # Mock successful execution
        return {
            "tool": tool_call.tool_name,
            "params": params,
            "result": f"Mock result from {tool_call.tool_name}",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _execute_chained_tool(self,
                                   tool_call: ToolCall,
                                   params: Dict[str, Any],
                                   state: ExecutionState,
                                   mcp_chain_func: Any,
                                   timeout: float) -> Any:
        """Execute a tool chained with previous results"""
        # Build the chain based on dependencies
        chain_path = self._build_chain_path(tool_call, state)
        
        logger.debug(f"Executing chained tool: {tool_call.tool_name} with chain: {[t['toolName'] for t in chain_path]}")
        
        # Simulate chained execution
        await asyncio.sleep(0.1)
        
        # Mock chained result
        return {
            "tool": tool_call.tool_name,
            "params": params,
            "chain": [t['toolName'] for t in chain_path],
            "result": f"Mock chained result from {tool_call.tool_name}",
            "timestamp": datetime.now().isoformat()
        }
    
    def _prepare_parameters(self, tool_call: ToolCall, state: ExecutionState) -> Dict[str, Any]:
        """Prepare parameters by substituting CHAIN_RESULT placeholders"""
        params = tool_call.parameters.copy()
        
        # Look for CHAIN_RESULT placeholders
        for key, value in params.items():
            if isinstance(value, str) and "CHAIN_RESULT" in value:
                # Find the most recent successful output
                if tool_call.dependencies:
                    for dep_order in reversed(tool_call.dependencies):
                        if dep_order in state.results and state.results[dep_order].status == ExecutionStatus.SUCCESS:
                            params[key] = value.replace("CHAIN_RESULT", json.dumps(state.results[dep_order].output))
                            break
            elif isinstance(value, list) and "CHAIN_RESULT" in value:
                # Handle array parameters
                if tool_call.dependencies:
                    for dep_order in reversed(tool_call.dependencies):
                        if dep_order in state.results and state.results[dep_order].status == ExecutionStatus.SUCCESS:
                            params[key] = [state.results[dep_order].output if item == "CHAIN_RESULT" else item for item in value]
                            break
        
        return params
    
    def _build_chain_path(self, tool_call: ToolCall, state: ExecutionState) -> List[Dict[str, Any]]:
        """Build the mcp_chain path for a tool based on its dependencies"""
        chain_path = []
        
        # Add dependent tools in order
        if tool_call.dependencies:
            for dep_order in tool_call.dependencies:
                if dep_order in state.results and state.results[dep_order].status == ExecutionStatus.SUCCESS:
                    dep_tool = state.results[dep_order].tool_call
                    chain_path.append({
                        "toolName": dep_tool.tool_name,
                        "toolArgs": json.dumps(dep_tool.parameters)
                    })
        
        # Add current tool
        chain_path.append({
            "toolName": tool_call.tool_name,
            "toolArgs": json.dumps(tool_call.parameters)
        })
        
        return chain_path
    
    def _dependencies_satisfied(self, tool_call: ToolCall, state: ExecutionState) -> bool:
        """Check if all dependencies for a tool have been successfully executed"""
        if not tool_call.dependencies:
            return True
            
        for dep_order in tool_call.dependencies:
            if dep_order not in state.results:
                return False
            if state.results[dep_order].status != ExecutionStatus.SUCCESS:
                return False
                
        return True
    
    def _can_parallelize(self, plan: ExecutionPlan) -> bool:
        """Check if the plan can be parallelized"""
        # A plan can be parallelized if there are tools without dependencies
        # or tools that share the same dependencies
        return any(not tool.dependencies for tool in plan.tools)
    
    def _get_dependency_levels(self, plan: ExecutionPlan) -> Dict[int, List[ToolCall]]:
        """Group tools by dependency levels for parallel execution"""
        levels = {}
        visited = set()
        
        def get_level(tool: ToolCall) -> int:
            if tool.order in visited:
                return levels.get(tool.order, 0)
                
            visited.add(tool.order)
            
            if not tool.dependencies:
                level = 0
            else:
                # Level is 1 + max level of dependencies
                dep_levels = []
                for dep_order in tool.dependencies:
                    dep_tool = next((t for t in plan.tools if t.order == dep_order), None)
                    if dep_tool:
                        dep_levels.append(get_level(dep_tool))
                level = 1 + max(dep_levels) if dep_levels else 0
            
            if level not in levels:
                levels[level] = []
            levels[level].append(tool)
            
            return level
        
        # Calculate levels for all tools
        for tool in plan.tools:
            get_level(tool)
            
        return levels
    
    def get_execution_state(self, plan_id: str) -> Optional[ExecutionState]:
        """Get the execution state for a plan"""
        return self.execution_states.get(plan_id)
    
    def export_state(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """Export execution state for persistence"""
        state = self.execution_states.get(plan_id)
        return state.to_dict() if state else None
    
    def import_state(self, state_data: Dict[str, Any]) -> ExecutionState:
        """Import execution state from persisted data"""
        # Recreate the execution plan
        plan_data = state_data['plan']
        tools = [
            ToolCall(
                tool_name=t['tool_name'],
                tool_id=t['tool_id'],
                parameters=t['parameters'],
                order=t['order'],
                dependencies=t['dependencies'],
                expected_output_type=t.get('expected_output_type'),
                timeout=t.get('timeout', 30.0),
                retry_count=t.get('retry_count', 0)
            )
            for t in plan_data['tools']
        ]
        
        plan = ExecutionPlan(
            plan_id=plan_data['plan_id'],
            intent=plan_data['intent'],
            tools=tools,
            created_at=datetime.fromisoformat(plan_data['created_at']),
            estimated_duration=plan_data.get('estimated_duration', 0.0),
            confidence_score=plan_data.get('confidence_score', 0.0),
            metadata=plan_data.get('metadata', {})
        )
        
        # Recreate the state
        state = ExecutionState(
            plan=plan,
            current_step=state_data['current_step'],
            start_time=datetime.fromisoformat(state_data['start_time']),
            end_time=datetime.fromisoformat(state_data['end_time']) if state_data['end_time'] else None,
            total_execution_time=state_data['total_execution_time'],
            status=ExecutionStatus(state_data['status'])
        )
        
        # Recreate results
        for order_str, result_data in state_data['results'].items():
            tool_call_data = result_data['tool_call']
            tool_call = ToolCall(
                tool_name=tool_call_data['tool_name'],
                tool_id=tool_call_data['tool_id'],
                parameters=tool_call_data['parameters'],
                order=tool_call_data['order'],
                dependencies=tool_call_data['dependencies'],
                expected_output_type=tool_call_data.get('expected_output_type'),
                timeout=tool_call_data.get('timeout', 30.0),
                retry_count=tool_call_data.get('retry_count', 0)
            )
            
            result = ExecutionResult(
                tool_call=tool_call,
                status=ExecutionStatus(result_data['status']),
                output=result_data['output'],
                error=result_data['error'],
                start_time=datetime.fromisoformat(result_data['start_time']) if result_data['start_time'] else None,
                end_time=datetime.fromisoformat(result_data['end_time']) if result_data['end_time'] else None,
                execution_time=result_data['execution_time'],
                retry_count=result_data['retry_count']
            )
            
            state.results[int(order_str)] = result
        
        self.execution_states[plan.plan_id] = state
        return state


# Example usage for testing
if __name__ == "__main__":
    import asyncio
    
    async def test_executor():
        # Create a sample plan
        from .planner import ExecutionPlan, ToolCall
        
        tools = [
            ToolCall(
                tool_name="web_search",
                tool_id="search_1",
                parameters={"query": "Python tutorials", "count": 5},
                order=1,
                dependencies=[]
            ),
            ToolCall(
                tool_name="summarize",
                tool_id="summarize_1",
                parameters={"text": "CHAIN_RESULT"},
                order=2,
                dependencies=[1]
            )
        ]
        
        plan = ExecutionPlan(
            plan_id="test_plan_1",
            intent="Find and summarize Python tutorials",
            tools=tools
        )
        
        # Create executor
        executor = ChainExecutor()
        
        # Mock mcp_chain function
        async def mock_mcp_chain(chain_path):
            return {"success": True, "data": "Mock execution"}
        
        # Execute plan
        state = await executor.execute_plan(plan, mock_mcp_chain)
        
        print(f"Execution completed with status: {state.status}")
        print(f"Total execution time: {state.total_execution_time:.2f}s")
        
        for order, result in state.results.items():
            print(f"\nTool {order} ({result.tool_call.tool_name}):")
            print(f"  Status: {result.status}")
            print(f"  Output: {result.output}")
            print(f"  Execution time: {result.execution_time:.2f}s")
    
    # Run the test
    asyncio.run(test_executor())
