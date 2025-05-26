#!/usr/bin/env python3
"""Enhanced Autonomous Executor - Phase 5 - Clean Implementation"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

import sys, os
sys.path.append(os.path.dirname(__file__))
from task_planner import TaskPlanner, PlanningResult
from tool_chainer import real_tool_chainer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed" 
    FAILED = "failed"


@dataclass
class ExecutionContext:
    execution_id: str
    task_description: str
    previous_results: List[Dict[str, Any]]
    context_data: Dict[str, Any]
    timestamp: datetime


@dataclass
class ExecutionResult:
    execution_id: str
    status: TaskStatus
    success: bool
    result_data: Optional[Dict[str, Any]]
    error_info: Optional[str]
    execution_time: float
    lessons_learned: List[str]


class ContextAwareExecutor:
    """Context-aware execution engine with error recovery"""
    
    def __init__(self):
        self.planner = TaskPlanner()
        self.execution_history = []
        self.global_context = {'learned_patterns': {}, 'successful_workflows': {}}
        self.max_retries = 3
        logger.info("Enhanced autonomous executor initialized")
    
    def build_execution_context(self, task_description: str) -> ExecutionContext:
        """Build execution context with history awareness"""
        execution_id = f"enhanced_exec_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        previous_results = self._get_relevant_previous_results(task_description)
        
        context_data = {
            'domain': self._identify_domain(task_description),
            'complexity': self._estimate_complexity(task_description),
            'related_count': len(previous_results)
        }
        
        return ExecutionContext(
            execution_id=execution_id,
            task_description=task_description,
            previous_results=previous_results,
            context_data=context_data,
            timestamp=datetime.now()
        )
    
    def _get_relevant_previous_results(self, task_description: str) -> List[Dict[str, Any]]:
        """Get results from related previous executions"""
        results = []
        task_words = set(task_description.lower().split())
        
        for execution in self.execution_history[-20:]:
            if 'task_description' in execution:
                existing_words = set(execution['task_description'].lower().split())
                overlap = len(task_words & existing_words) / len(task_words | existing_words)
                if overlap > 0.3:
                    results.append({
                        'task': execution['task_description'],
                        'result': execution.get('result_data'),
                        'success': execution.get('success', False)
                    })
        
        return results[-3:]
    
    def _identify_domain(self, task_description: str) -> str:
        """Identify the domain/category of the task"""
        domains = {
            'technical': ['code', 'programming', 'software', 'api', 'technical'],
            'business': ['business', 'market', 'finance', 'strategy'],
            'science': ['research', 'study', 'analysis', 'data'],
            'general': ['information', 'find', 'what', 'how']
        }
        
        task_lower = task_description.lower()
        for domain, keywords in domains.items():
            if any(keyword in task_lower for keyword in keywords):
                return domain
        return 'general'
    
    def _estimate_complexity(self, task_description: str) -> str:
        """Estimate task complexity"""
        complex_indicators = ['analyze', 'compare', 'evaluate', 'comprehensive', 'detailed']
        simple_indicators = ['find', 'what', 'when', 'where', 'simple']
        
        task_lower = task_description.lower()
        
        if any(indicator in task_lower for indicator in complex_indicators):
            return 'complex'
        elif any(indicator in task_lower for indicator in simple_indicators):
            return 'simple'
        else:
            return 'medium'
    
    async def execute_with_context(self, context: ExecutionContext) -> ExecutionResult:
        """Execute task with context awareness and error recovery"""
        start_time = datetime.now()
        
        try:
            logger.info(f"Starting enhanced execution: {context.execution_id}")
            logger.info(f"Task: {context.task_description}")
            logger.info(f"Domain: {context.context_data.get('domain')}")
            logger.info(f"Previous results available: {context.context_data.get('related_count', 0)}")
            
            # Step 1: Enhanced planning with context
            planning_result = await self._context_aware_planning(context)
            if not planning_result.success:
                return self._create_failure_result(context, planning_result.error_message)
            
            # Step 2: Execute with retry logic
            execution_result = await self._execute_with_recovery(context, planning_result)
            
            # Step 3: Learn from execution
            self._update_global_context(context, execution_result)
            
            return execution_result
            
        except Exception as e:
            logger.error(f"Critical execution error: {str(e)}")
            execution_time = (datetime.now() - start_time).total_seconds()
            return ExecutionResult(
                execution_id=context.execution_id,
                status=TaskStatus.FAILED,
                success=False,
                result_data=None,
                error_info=f"Critical error: {str(e)}",
                execution_time=execution_time,
                lessons_learned=[f"Critical error in execution: {str(e)}"]
            )

    async def _context_aware_planning(self, context: ExecutionContext) -> PlanningResult:
        """Enhanced planning that uses context information"""
        try:
            enhanced_task_description = context.task_description
            
            if context.previous_results:
                logger.info(f"Using context from {len(context.previous_results)} previous results")
                recent_result = context.previous_results[-1]
                context_info = f"Related previous task: {recent_result['task']}"
                enhanced_task_description += f"\n\nContext: {context_info}"
            
            planning_result = await self.planner.plan_task_execution(enhanced_task_description)
            
            if planning_result.success and planning_result.workflow_plan:
                planning_result.workflow_plan['context'] = {
                    'domain': context.context_data.get('domain'),
                    'complexity': context.context_data.get('complexity'),
                    'has_previous_results': len(context.previous_results) > 0
                }
            
            return planning_result
            
        except Exception as e:
            logger.error(f"Context-aware planning failed: {str(e)}")
            return PlanningResult(
                success=False,
                analysis=None,
                workflow_plan=None,
                execution_strategy=None,
                error_message=f"Planning error: {str(e)}"
            )
    
    async def _execute_with_recovery(self, context: ExecutionContext, 
                                   planning_result: PlanningResult) -> ExecutionResult:
        """Execute with error recovery"""
        start_time = datetime.now()
        retry_count = 0
        
        while retry_count <= self.max_retries:
            try:
                logger.info(f"Execution attempt {retry_count + 1}/{self.max_retries + 1}")
                
                workflow_plan = planning_result.workflow_plan
                steps = []
                
                for step in workflow_plan.get('template', {}).get('steps', []):
                    steps.append({
                        'tool': step['tool'],
                        'parameters': step['parameters']
                    })
                
                # Create and execute tool chain
                chain_id = real_tool_chainer.create_tool_chain(steps, workflow_plan['workflow_name'])
                chain_result = await real_tool_chainer.execute_chain(chain_id)
                
                if chain_result.status == "completed":
                    execution_time = (datetime.now() - start_time).total_seconds()
                    
                    result = ExecutionResult(
                        execution_id=context.execution_id,
                        status=TaskStatus.COMPLETED,
                        success=True,
                        result_data={
                            'chain_result': chain_result.final_result,
                            'workflow_used': workflow_plan['workflow_name'],
                            'tools_executed': [step['tool'] for step in workflow_plan.get('template', {}).get('steps', [])],
                            'retry_count': retry_count,
                            'steps_executed': len(chain_result.steps_executed)
                        },
                        error_info=None,
                        execution_time=execution_time,
                        lessons_learned=[
                            f"Successfully executed {workflow_plan['workflow_name']} workflow",
                            f"Used domain: {context.context_data.get('domain')}",
                            f"Completed in {retry_count + 1} attempts"
                        ]
                    )
                    
                    self._record_execution(context, result)
                    return result
                    
                else:
                    # Tool chain failed - prepare for retry
                    error_info = f"Chain status: {chain_result.status}"
                    logger.warning(f"Tool chain failed: {error_info}")
                    
                    if retry_count < self.max_retries:
                        logger.info(f"Retrying with simplified approach...")
                        await asyncio.sleep(retry_count + 1)
                    
                    retry_count += 1
                    
            except Exception as e:
                logger.error(f"Execution attempt {retry_count + 1} failed: {str(e)}")
                retry_count += 1
                
                if retry_count <= self.max_retries:
                    await asyncio.sleep(retry_count)
        
        execution_time = (datetime.now() - start_time).total_seconds()
        result = ExecutionResult(
            execution_id=context.execution_id,
            status=TaskStatus.FAILED,
            success=False,
            result_data=None,
            error_info=f"All {self.max_retries + 1} attempts failed",
            execution_time=execution_time,
            lessons_learned=[f"Failed after {retry_count} attempts", "Consider task simplification"]
        )
        
        self._record_execution(context, result)
        return result

    def _update_global_context(self, context: ExecutionContext, result: ExecutionResult):
        """Update global context with execution learnings"""
        try:
            domain = context.context_data.get('domain', 'general')
            if domain not in self.global_context['learned_patterns']:
                self.global_context['learned_patterns'][domain] = []
            
            pattern_info = {
                'task_description': context.task_description,
                'success': result.success,
                'execution_time': result.execution_time,
                'timestamp': datetime.now().isoformat()
            }
            
            self.global_context['learned_patterns'][domain].append(pattern_info)
            
            if len(self.global_context['learned_patterns'][domain]) > 20:
                self.global_context['learned_patterns'][domain] = \
                    self.global_context['learned_patterns'][domain][-20:]
            
            if result.success and result.result_data:
                workflow_name = result.result_data.get('workflow_used')
                if workflow_name:
                    if workflow_name not in self.global_context['successful_workflows']:
                        self.global_context['successful_workflows'][workflow_name] = 0
                    self.global_context['successful_workflows'][workflow_name] += 1
            
            logger.info(f"Updated global context for domain: {domain}")
            
        except Exception as e:
            logger.error(f"Failed to update global context: {str(e)}")
    
    def _record_execution(self, context: ExecutionContext, result: ExecutionResult):
        """Record execution in history for future context"""
        execution_record = {
            'execution_id': context.execution_id,
            'task_description': context.task_description,
            'domain': context.context_data.get('domain'),
            'success': result.success,
            'execution_time': result.execution_time,
            'result_data': result.result_data,
            'timestamp': datetime.now().isoformat()
        }
        
        self.execution_history.append(execution_record)
        
        if len(self.execution_history) > 50:
            self.execution_history = self.execution_history[-50:]
    
    def _create_failure_result(self, context: ExecutionContext, error_message: str) -> ExecutionResult:
        """Create a failure result"""
        return ExecutionResult(
            execution_id=context.execution_id,
            status=TaskStatus.FAILED,
            success=False,
            result_data=None,
            error_info=error_message,
            execution_time=0.0,
            lessons_learned=[f"Failed during planning: {error_message}"]
        )
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get current execution statistics"""
        total = len(self.execution_history)
        if total > 0:
            successful = sum(1 for exec in self.execution_history if exec.get('success', False))
            success_rate = successful / total * 100
            avg_time = sum(exec.get('execution_time', 0) for exec in self.execution_history) / total
        else:
            success_rate = 0.0
            avg_time = 0.0
        
        return {
            'total_executions': total,
            'success_rate': success_rate,
            'average_execution_time': avg_time,
            'context_domains': list(self.global_context['learned_patterns'].keys()),
            'successful_workflows': self.global_context['successful_workflows'],
            'execution_history_size': len(self.execution_history)
        }
    
    def get_context_summary(self) -> Dict[str, Any]:
        """Get summary of learned context"""
        return {
            'domains_learned': list(self.global_context['learned_patterns'].keys()),
            'successful_workflows': self.global_context['successful_workflows'],
            'total_patterns': sum(len(patterns) for patterns in 
                                self.global_context['learned_patterns'].values()),
            'recent_executions': len(self.execution_history)
        }


# Convenience functions
async def execute_task_with_context(task_description: str) -> ExecutionResult:
    """Convenience function for context-aware task execution"""
    executor = ContextAwareExecutor()
    context = executor.build_execution_context(task_description)
    return await executor.execute_with_context(context)


async def enhanced_autonomous_execution(task_description: str) -> Dict[str, Any]:
    """Enhanced autonomous execution with full context and error recovery"""
    executor = ContextAwareExecutor()
    context = executor.build_execution_context(task_description)
    result = await executor.execute_with_context(context)
    
    return {
        'execution_id': result.execution_id,
        'success': result.success,
        'status': result.status.value,
        'result_data': result.result_data,
        'execution_time': result.execution_time,
        'error_info': result.error_info,
        'lessons_learned': result.lessons_learned
    }
