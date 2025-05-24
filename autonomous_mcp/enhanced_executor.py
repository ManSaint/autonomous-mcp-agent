"""
Enhanced Chain Executor with Production-Grade Error Handling

This module extends the basic ChainExecutor with sophisticated error handling,
recovery mechanisms, and intelligent tool substitution capabilities.
"""

import asyncio
import time
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass
import logging

from .executor import ChainExecutor, ExecutionResult, ExecutionStatus
from .enhanced_error_handling import (
    EnhancedErrorHandler, ErrorContext, ErrorCategory, ErrorSeverity,
    ToolSubstitutionEngine, ToolHealthMetrics
)
from .discovery import ToolDiscovery
from .planner import ExecutionPlan, ToolCall


class EnhancedChainExecutor(ChainExecutor):
    """Enhanced executor with sophisticated error handling and recovery"""
    
    def __init__(self, discovery_system: ToolDiscovery):
        super().__init__(discovery_system)
        self.error_handler = EnhancedErrorHandler(discovery_system)
        self.logger = logging.getLogger(__name__)
        
        # Enhanced configuration
        self.enable_smart_substitution = True
        self.enable_partial_execution = True
        self.enable_adaptive_retries = True
        self.max_substitution_attempts = 2
        
    async def execute_plan_with_enhanced_handling(self, plan: ExecutionPlan) -> ExecutionResult:
        """Execute plan with enhanced error handling and recovery"""
        start_time = time.time()
        results = {}
        errors = []
        executed_tools = set()
        substituted_tools = {}  # Track tool substitutions
        
        try:
            self.logger.info(f"Starting enhanced execution of plan with {len(plan.tools)} tools")
            
            # Execute tools with enhanced error handling
            for tool_call in plan.tools:
                tool_start_time = time.time()
                success = False
                final_error = None
                
                # Try original tool with retries and substitutions
                for attempt in range(self.max_substitution_attempts + 1):
                    current_tool = tool_call.tool_name
                    
                    # Check circuit breaker before execution
                    if not self.error_handler.tool_metrics[current_tool].circuit_breaker.should_allow_request():
                        error_context = ErrorContext(
                            category=ErrorCategory.TOOL_UNAVAILABLE,
                            severity=ErrorSeverity.HIGH,
                            message=f"Circuit breaker open for tool {current_tool}",
                            tool_name=current_tool,
                            tool_call=tool_call,
                            circuit_breaker_triggered=True
                        )
                        
                        if attempt < self.max_substitution_attempts and self.enable_smart_substitution:
                            # Try substitution
                            substitution_result = await self._try_tool_substitution(
                                tool_call, error_context, results
                            )
                            if substitution_result:
                                current_tool, result = substitution_result
                                substituted_tools[tool_call.tool_name] = current_tool
                                results[tool_call.tool_name] = result
                                executed_tools.add(current_tool)
                                success = True
                                break
                        
                        # No substitution available or disabled
                        final_error = error_context
                        break
                    
                    # Execute tool with enhanced error handling
                    try:
                        result = await self._execute_tool_with_monitoring(
                            current_tool, tool_call, results
                        )
                        
                        # Record successful execution
                        tool_execution_time = time.time() - tool_start_time
                        self.error_handler.record_tool_execution(
                            current_tool, True, tool_execution_time
                        )
                        
                        results[tool_call.tool_name] = result
                        executed_tools.add(current_tool)
                        success = True
                        
                        self.logger.info(f"Successfully executed {current_tool} in {tool_execution_time:.3f}s")
                        break
                        
                    except Exception as e:
                        tool_execution_time = time.time() - tool_start_time
                        
                        # Create enhanced error context
                        error_context = self.error_handler.create_error_context(
                            e, current_tool, tool_call
                        )
                        
                        # Record failed execution
                        self.error_handler.record_tool_execution(
                            current_tool, False, tool_execution_time, e
                        )
                        
                        self.logger.warning(f"Tool {current_tool} failed: {error_context.to_human_readable()}")
                        
                        # Try substitution if enabled and appropriate
                        if (attempt < self.max_substitution_attempts and 
                            self.enable_smart_substitution and
                            error_context.retry_recommended):
                            
                            substitution_result = await self._try_tool_substitution(
                                tool_call, error_context, results
                            )
                            if substitution_result:
                                substitute_tool, result = substitution_result
                                substituted_tools[tool_call.tool_name] = substitute_tool
                                results[tool_call.tool_name] = result
                                executed_tools.add(substitute_tool)
                                success = True
                                
                                self.logger.info(f"Successfully substituted {current_tool} → {substitute_tool}")
                                break
                        
                        final_error = error_context
                        
                        # If not retrying, break
                        if not error_context.retry_recommended:
                            break
                
                # Handle execution failure
                if not success:
                    errors.append(final_error)
                    
                    # Check if we should continue with partial execution
                    if not self.enable_partial_execution:
                        # Fail fast mode
                        execution_time = time.time() - start_time
                        return ExecutionResult(
                            status=ExecutionStatus.FAILED,
                            results=results,
                            errors=[final_error.to_human_readable()],
                            execution_time=execution_time,
                            executed_tools=list(executed_tools),
                            metadata={
                                'substituted_tools': substituted_tools,
                                'partial_execution': True,
                                'failed_tool': tool_call.tool_name,
                                'error_context': final_error.__dict__
                            }
                        )
                    else:
                        # Continue with partial execution
                        self.logger.warning(f"Continuing execution despite {tool_call.tool_name} failure")
            
            # Determine final status
            execution_time = time.time() - start_time
            
            if not errors:
                status = ExecutionStatus.SUCCESS
            elif len(executed_tools) > 0:
                status = ExecutionStatus.PARTIAL_SUCCESS
            else:
                status = ExecutionStatus.FAILED
            
            # Create comprehensive metadata
            metadata = {
                'substituted_tools': substituted_tools,
                'total_tools_planned': len(plan.tools),
                'tools_executed': len(executed_tools),
                'substitutions_made': len(substituted_tools),
                'error_count': len(errors),
                'execution_mode': 'partial' if self.enable_partial_execution else 'fail_fast',
                'tool_health_summary': self._generate_health_summary()
            }
            
            self.logger.info(f"Enhanced execution completed: {status.value} in {execution_time:.3f}s")
            
            return ExecutionResult(
                status=status,
                results=results,
                errors=[error.to_human_readable() for error in errors],
                execution_time=execution_time,
                executed_tools=list(executed_tools),
                metadata=metadata
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_context = self.error_handler.create_error_context(e)
            
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                results=results,
                errors=[error_context.to_human_readable()],
                execution_time=execution_time,
                executed_tools=list(executed_tools),
                metadata={'fatal_error': True, 'substituted_tools': substituted_tools}
            )
    
    async def _try_tool_substitution(self, original_tool_call: ToolCall, 
                                   error_context: ErrorContext, 
                                   current_results: Dict[str, Any]) -> Optional[Tuple[str, Any]]:
        """Attempt to substitute failed tool with alternative"""
        if not self.enable_smart_substitution:
            return None
            
        alternatives = self.error_handler.substitution_engine.find_alternatives(
            original_tool_call.tool_name
        )
        
        if not alternatives:
            self.logger.info(f"No alternatives found for {original_tool_call.tool_name}")
            return None
        
        # Try alternatives in order of preference
        for alt_tool in alternatives:
            # Check if alternative tool is healthy
            alt_metrics = self.error_handler.tool_metrics[alt_tool.name]
            if not alt_metrics.is_healthy:
                continue
                
            try:
                self.logger.info(f"Trying substitution: {original_tool_call.tool_name} → {alt_tool.name}")
                
                # Create modified tool call for alternative
                alt_tool_call = ToolCall(
                    tool_name=alt_tool.name,
                    arguments=original_tool_call.arguments,
                    dependencies=original_tool_call.dependencies
                )
                
                # Execute alternative tool
                result = await self._execute_tool_with_monitoring(
                    alt_tool.name, alt_tool_call, current_results
                )
                
                # Record successful substitution
                sub_time = time.time()
                self.error_handler.record_tool_execution(alt_tool.name, True, 0.1)
                
                return alt_tool.name, result
                
            except Exception as e:
                # Record failed substitution attempt
                self.error_handler.record_tool_execution(alt_tool.name, False, 0.1, e)
                self.logger.warning(f"Substitution {alt_tool.name} also failed: {str(e)}")
                continue
        
        return None
    
    async def _execute_tool_with_monitoring(self, tool_name: str, tool_call: ToolCall, 
                                          current_results: Dict[str, Any]) -> Any:
        """Execute tool with comprehensive monitoring and timeout handling"""
        # Enhanced timeout based on tool health
        metrics = self.error_handler.tool_metrics[tool_name]
        base_timeout = self.default_timeout
        
        # Adjust timeout based on tool performance
        if metrics.average_response_time > 0:
            adjusted_timeout = max(base_timeout, metrics.average_response_time * 3)
        else:
            adjusted_timeout = base_timeout
        
        # Execute with monitoring
        return await asyncio.wait_for(
            self._execute_single_tool(tool_call, current_results),
            timeout=adjusted_timeout
        )
    
    def _generate_health_summary(self) -> Dict[str, Any]:
        """Generate summary of tool health metrics"""
        all_metrics = self.error_handler.tool_metrics
        
        if not all_metrics:
            return {'status': 'no_data'}
        
        healthy_tools = sum(1 for m in all_metrics.values() if m.is_healthy)
        total_tools = len(all_metrics)
        
        avg_success_rate = sum(m.success_rate for m in all_metrics.values()) / total_tools
        
        return {
            'healthy_tools': healthy_tools,
            'total_tools': total_tools,
            'overall_health_percentage': (healthy_tools / total_tools) * 100,
            'average_success_rate': round(avg_success_rate, 2),
            'tools_with_circuit_breaker_open': sum(
                1 for m in all_metrics.values() 
                if m.circuit_breaker.state == 'open'
            )
        }
    
    def get_enhanced_health_report(self) -> Dict[str, Any]:
        """Get comprehensive health and error handling report"""
        return {
            'tool_health': self.error_handler.get_tool_health_report(),
            'error_metrics': self.error_handler.export_error_metrics(),
            'configuration': {
                'smart_substitution': self.enable_smart_substitution,
                'partial_execution': self.enable_partial_execution,
                'adaptive_retries': self.enable_adaptive_retries,
                'max_substitution_attempts': self.max_substitution_attempts
            },
            'system_summary': self._generate_health_summary()
        }
