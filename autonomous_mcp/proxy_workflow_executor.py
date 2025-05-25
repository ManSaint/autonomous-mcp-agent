# 🚀 PHASE 6.3: PROXY WORKFLOW EXECUTOR
# Enhanced workflow execution supporting both internal and proxy tools

import asyncio
import logging
import time
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime

from .workflow_builder import WorkflowBuilder, AdvancedWorkflowStep, WorkflowStepType
from .proxy_executor import ProxyExecutor, ProxyExecutionResult
from .mcp_chain_executor import RealMCPChainExecutor
from .external_tool_registry import EXTERNAL_TOOL_REGISTRY
from .autonomous_tools import IntelligentWorkflow, WorkflowStep

logger = logging.getLogger(__name__)


@dataclass
class ProxyWorkflowResult:
    """Result of proxy workflow execution"""
    success: bool
    workflow_id: str
    total_steps: int
    completed_steps: int
    failed_steps: int
    proxy_steps: int
    internal_steps: int
    total_execution_time: float
    results: List[Dict[str, Any]]
    errors: List[str]
    performance_metrics: Dict[str, Any]


class ProxyWorkflowExecutor:
    """Enhanced workflow executor supporting both internal and proxy tools"""
    
    def __init__(self):
        self.workflow_builder = WorkflowBuilder()
        self.proxy_executor = ProxyExecutor()
        self.internal_executor = RealMCPChainExecutor()
        self.performance_metrics = {}
        
        logger.info("Proxy workflow executor initialized")
    
    async def execute_hybrid_workflow(self, workflow: IntelligentWorkflow) -> ProxyWorkflowResult:
        """Execute workflow supporting both internal and proxy tools"""
        start_time = time.time()
        
        logger.info(f"Starting hybrid workflow execution: {workflow.workflow_id}")
        
        results = []
        errors = []
        completed_steps = 0
        failed_steps = 0
        proxy_steps = 0
        internal_steps = 0
        
        try:
            for step in workflow.steps:
                step_start = time.time()
                
                # Determine if this is a proxy tool
                is_proxy = self._is_proxy_tool(step.tool_name)
                
                try:
                    if is_proxy:
                        # Execute via proxy system
                        result = await self._execute_proxy_step(step)
                        proxy_steps += 1
                    else:
                        # Execute via internal system
                        result = await self._execute_internal_step(step)
                        internal_steps += 1
                    
                    # Record successful execution
                    step_time = time.time() - step_start
                    results.append({
                        'step_id': step.step_id,
                        'tool_name': step.tool_name,
                        'is_proxy': is_proxy,
                        'success': True,
                        'execution_time': step_time,
                        'result': result
                    })
                    completed_steps += 1
                    
                    logger.info(f"Step {step.step_id} completed successfully in {step_time:.2f}s")
                    
                except Exception as e:
                    # Record failed execution
                    step_time = time.time() - step_start
                    error_msg = f"Step {step.step_id} failed: {str(e)}"
                    errors.append(error_msg)
                    
                    results.append({
                        'step_id': step.step_id,
                        'tool_name': step.tool_name,
                        'is_proxy': is_proxy,
                        'success': False,
                        'execution_time': step_time,
                        'error': str(e)
                    })
                    failed_steps += 1
                    
                    logger.error(error_msg)
                    
                    # Decide whether to continue or stop
                    if not self._should_continue_on_failure(step, workflow):
                        logger.warning(f"Stopping workflow due to critical step failure: {step.step_id}")
                        break
            
            total_time = time.time() - start_time
            
            # Calculate performance metrics
            performance_metrics = self._calculate_performance_metrics(
                results, total_time, proxy_steps, internal_steps
            )
            
            success = failed_steps == 0 or (completed_steps > failed_steps)
            
            logger.info(f"Workflow {workflow.workflow_id} completed: {completed_steps}/{len(workflow.steps)} steps successful")
            
            return ProxyWorkflowResult(
                success=success,
                workflow_id=workflow.workflow_id,
                total_steps=len(workflow.steps),
                completed_steps=completed_steps,
                failed_steps=failed_steps,
                proxy_steps=proxy_steps,
                internal_steps=internal_steps,
                total_execution_time=total_time,
                results=results,
                errors=errors,
                performance_metrics=performance_metrics
            )
            
        except Exception as e:
            total_time = time.time() - start_time
            logger.error(f"Workflow execution failed: {e}")
            
            return ProxyWorkflowResult(
                success=False,
                workflow_id=workflow.workflow_id,
                total_steps=len(workflow.steps),
                completed_steps=completed_steps,
                failed_steps=failed_steps + 1,
                proxy_steps=proxy_steps,
                internal_steps=internal_steps,
                total_execution_time=total_time,
                results=results,
                errors=errors + [f"Workflow execution failed: {str(e)}"],
                performance_metrics={}
            )
    
    async def _execute_proxy_step(self, step: WorkflowStep) -> Dict[str, Any]:
        """Execute a proxy tool step"""
        logger.debug(f"Executing proxy step: {step.tool_name}")
        
        proxy_result = await self.proxy_executor.execute_proxy_tool(
            step.tool_name, 
            step.parameters
        )
        
        if proxy_result.success:
            return {
                'proxy_execution': True,
                'tool_name': step.tool_name,
                'result': proxy_result.result,
                'execution_time': proxy_result.execution_time,
                'fallback_used': proxy_result.fallback_used
            }
        else:
            # Create helpful error with guidance
            error_response = {
                'proxy_execution': True,
                'tool_name': step.tool_name,
                'success': False,
                'error': proxy_result.error,
                'helpful_message': proxy_result.helpful_message,
                'manual_alternative': self._get_manual_alternative(step)
            }
            
            if proxy_result.fallback_used:
                # Don't throw exception for fallback - return helpful guidance
                return error_response
            else:
                raise Exception(f"Proxy tool {step.tool_name} failed: {proxy_result.error}")
    
    async def _execute_internal_step(self, step: WorkflowStep) -> Dict[str, Any]:
        """Execute an internal autonomous tool step"""
        logger.debug(f"Executing internal step: {step.tool_name}")
        
        # Use the existing internal MCP chain executor
        try:
            # Convert to chain step format
            chain_steps = [{
                'toolName': step.tool_name,
                'toolArgs': step.parameters
            }]
            
            result = self.internal_executor.execute_chain(chain_steps, {})
            
            return {
                'internal_execution': True,
                'tool_name': step.tool_name,
                'result': result.results,
                'success': result.success,
                'execution_time': result.execution_time
            }
            
        except Exception as e:
            logger.error(f"Internal tool execution failed: {e}")
            raise
    
    def _is_proxy_tool(self, tool_name: str) -> bool:
        """Determine if a tool is a proxy tool"""
        return tool_name in EXTERNAL_TOOL_REGISTRY
    
    def _should_continue_on_failure(self, failed_step: WorkflowStep, workflow: IntelligentWorkflow) -> bool:
        """Determine if workflow should continue after step failure"""
        # Check if step has error handling configuration
        if hasattr(failed_step, 'error_handling') and failed_step.error_handling:
            return failed_step.error_handling.get('continue_on_failure', False)
        
        # Check if step is marked as critical
        if hasattr(failed_step, 'is_critical') and failed_step.is_critical:
            return False
        
        # Default: continue for proxy tools (graceful degradation), stop for internal tools
        return self._is_proxy_tool(failed_step.tool_name)
    
    def _get_manual_alternative(self, step: WorkflowStep) -> Dict[str, Any]:
        """Get manual alternative for failed proxy tool"""
        return {
            'tool_name': step.tool_name,
            'description': f"Manual alternative for {step.tool_name}",
            'parameters': step.parameters,
            'suggestion': f"You can manually execute {step.tool_name} with the provided parameters"
        }
    
    def _calculate_performance_metrics(self, results: List[Dict], total_time: float, 
                                     proxy_steps: int, internal_steps: int) -> Dict[str, Any]:
        """Calculate comprehensive performance metrics"""
        
        successful_results = [r for r in results if r.get('success', False)]
        failed_results = [r for r in results if not r.get('success', True)]
        
        proxy_results = [r for r in results if r.get('is_proxy', False)]
        internal_results = [r for r in results if not r.get('is_proxy', True)]
        
        return {
            'execution_summary': {
                'total_execution_time': total_time,
                'total_steps': len(results),
                'successful_steps': len(successful_results),
                'failed_steps': len(failed_results),
                'success_rate': len(successful_results) / len(results) if results else 0
            },
            'tool_breakdown': {
                'proxy_tools': {
                    'count': proxy_steps,
                    'avg_execution_time': sum(r.get('execution_time', 0) for r in proxy_results) / len(proxy_results) if proxy_results else 0,
                    'success_rate': len([r for r in proxy_results if r.get('success', False)]) / len(proxy_results) if proxy_results else 0
                },
                'internal_tools': {
                    'count': internal_steps,
                    'avg_execution_time': sum(r.get('execution_time', 0) for r in internal_results) / len(internal_results) if internal_results else 0,
                    'success_rate': len([r for r in internal_results if r.get('success', False)]) / len(internal_results) if internal_results else 0
                }
            },
            'performance_insights': {
                'avg_step_time': total_time / len(results) if results else 0,
                'fastest_step': min(results, key=lambda r: r.get('execution_time', float('inf'))).get('execution_time', 0) if results else 0,
                'slowest_step': max(results, key=lambda r: r.get('execution_time', 0)).get('execution_time', 0) if results else 0
            }
        }
    
    async def create_and_execute_hybrid_workflow(self, description: str, 
                                               steps: List[Dict[str, Any]], 
                                               context: Optional[Dict[str, Any]] = None) -> ProxyWorkflowResult:
        """Create and execute a hybrid workflow in one operation"""
        
        # Create workflow using enhanced builder
        workflow = await self.workflow_builder.create_custom_workflow(description, steps, context)
        
        # Execute the workflow
        return await self.execute_hybrid_workflow(workflow)
    
    async def execute_multi_tool_chain(self, tool_chain: List[Dict[str, Any]]) -> ProxyWorkflowResult:
        """Execute a simple chain of tools (convenience method)"""
        
        description = f"Multi-tool chain with {len(tool_chain)} tools"
        
        # Convert tool chain to workflow steps
        steps = []
        for i, tool_call in enumerate(tool_chain):
            steps.append({
                'type': 'tool_execution',
                'tool': tool_call.get('tool_name', tool_call.get('tool')),
                'description': tool_call.get('description', f"Execute {tool_call.get('tool_name', 'tool')}"),
                'parameters': tool_call.get('parameters', {}),
                'dependencies': [f"step_{i-1}"] if i > 0 else []
            })
        
        return await self.create_and_execute_hybrid_workflow(description, steps)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get overall performance summary"""
        return {
            'proxy_executor_status': 'operational',
            'internal_executor_status': 'operational',
            'supported_tool_types': ['internal_autonomous', 'external_proxy'],
            'workflow_capabilities': [
                'sequential_execution',
                'error_recovery',
                'graceful_degradation',
                'performance_monitoring'
            ]
        }


# Export the main class
__all__ = ['ProxyWorkflowExecutor', 'ProxyWorkflowResult']
