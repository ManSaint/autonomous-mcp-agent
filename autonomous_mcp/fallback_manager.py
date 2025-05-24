"""
Fallback Management System for Autonomous MCP Agent

This module provides intelligent fallback mechanisms that work in conjunction
with the error recovery system to ensure robust execution paths when primary
methods fail.

Key Features:
- Multi-level fallback strategies (tool, plan, execution)
- Dynamic alternative discovery and ranking
- Context-aware fallback selection
- Performance-based fallback prioritization
- Graceful degradation patterns
- Fallback chain orchestration
"""

import asyncio
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Set, Any, Callable, Union, Tuple, Protocol
from dataclasses import dataclass, field
from collections import defaultdict, deque
import logging
import json
from abc import ABC, abstractmethod

from .discovery import ToolDiscovery, DiscoveredTool
from .planner import ToolCall, ExecutionPlan, BasicExecutionPlanner
from .executor import ChainExecutor, ExecutionStatus, ExecutionResult, ExecutionState
from .error_recovery import ErrorRecoverySystem, ErrorContext, ErrorCategory, ErrorSeverity


# Create a simplified result type for fallback operations
@dataclass
class FallbackExecutionResult:
    """Simplified execution result for fallback operations"""
    status: ExecutionStatus
    outputs: List[Any] = field(default_factory=list)
    total_execution_time: float = 0.0
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_execution_state(cls, state: ExecutionState) -> 'FallbackExecutionResult':
        """Create result from ExecutionState"""
        outputs = []
        error_messages = []
        
        for result in state.results.values():
            if result.status == ExecutionStatus.SUCCESS and result.output:
                outputs.append(result.output)
            elif result.error:
                error_messages.append(result.error)
        
        error_msg = "; ".join(error_messages) if error_messages else None
        
        return cls(
            status=state.status,
            outputs=outputs,
            total_execution_time=state.total_execution_time,
            error_message=error_msg,
            metadata={'execution_state_id': state.plan.plan_id}
        )


class FallbackLevel(Enum):
    """Levels of fallback mechanisms"""
    TOOL = "tool"           # Individual tool alternatives
    PLAN = "plan"           # Alternative execution plans
    STRATEGY = "strategy"   # Different approach strategies
    GRACEFUL = "graceful"   # Graceful degradation


class FallbackReason(Enum):
    """Reasons for triggering fallback mechanisms"""
    TOOL_FAILURE = "tool_failure"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    RESOURCE_UNAVAILABLE = "resource_unavailable"
    TIMEOUT_EXCEEDED = "timeout_exceeded"
    QUALITY_THRESHOLD = "quality_threshold"
    USER_PREFERENCE = "user_preference"
    CIRCUIT_BREAKER = "circuit_breaker"
    DEPENDENCY_FAILURE = "dependency_failure"
    STRATEGY = "strategy"


@dataclass
class FallbackOption:
    """Represents a single fallback option"""
    level: FallbackLevel
    reason: FallbackReason
    alternative: Union[str, ToolCall, ExecutionPlan]
    confidence: float  # 0.0 to 1.0
    estimated_cost: float  # Relative cost (time/resources)
    description: str
    prerequisites: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    success_rate: float = 0.0  # Historical success rate
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'level': self.level.value,
            'reason': self.reason.value,
            'alternative': str(self.alternative),
            'confidence': self.confidence,
            'estimated_cost': self.estimated_cost,
            'description': self.description,
            'prerequisites': self.prerequisites,
            'metadata': self.metadata,
            'success_rate': self.success_rate
        }


@dataclass
class FallbackChain:
    """Represents a chain of fallback options"""
    primary_target: str
    fallback_options: List[FallbackOption]
    total_confidence: float
    execution_order: List[int]  # Indices into fallback_options
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    usage_count: int = 0
    success_count: int = 0
    
    def get_success_rate(self) -> float:
        """Calculate overall success rate of this chain"""
        if self.usage_count == 0:
            return 0.0
        return self.success_count / self.usage_count
    
    def update_performance(self, success: bool):
        """Update performance metrics"""
        self.usage_count += 1
        if success:
            self.success_count += 1
        self.last_updated = datetime.now()


class FallbackStrategy(ABC):
    """Abstract base class for fallback strategies"""
    
    @abstractmethod
    async def find_alternatives(
        self, 
        target: Union[str, ToolCall, ExecutionPlan],
        context: Dict[str, Any],
        discovery: ToolDiscovery
    ) -> List[FallbackOption]:
        """Find alternative options for the given target"""
        pass
    
    @abstractmethod
    def get_strategy_name(self) -> str:
        """Get the name of this strategy"""
        pass


class ToolFallbackStrategy(FallbackStrategy):
    """Strategy for finding tool alternatives"""
    
    def get_strategy_name(self) -> str:
        return "tool_fallback"
    
    async def find_alternatives(
        self, 
        target: Union[str, ToolCall, ExecutionPlan],
        context: Dict[str, Any],
        discovery: ToolDiscovery
    ) -> List[FallbackOption]:
        """Find alternative tools with similar capabilities"""
        alternatives = []
        
        if isinstance(target, str):
            tool_name = target
        elif isinstance(target, ToolCall):
            tool_name = target.tool_name
        else:
            return alternatives
        
        # Get the primary tool info
        primary_tool = discovery.available_tools.get(tool_name)
        if not primary_tool:
            return alternatives
        
        # Find tools with similar capabilities
        for name, tool in discovery.available_tools.items():
            if name == tool_name:
                continue
                
            # Calculate capability overlap
            primary_caps = getattr(primary_tool, 'capabilities', [])
            tool_caps = getattr(tool, 'capabilities', [])
            
            if primary_caps and tool_caps:
                # Convert to sets for overlap calculation
                primary_caps_set = set(primary_caps) if isinstance(primary_caps, list) else set()
                tool_caps_set = set(tool_caps) if isinstance(tool_caps, list) else set()
                
                overlap = len(primary_caps_set.intersection(tool_caps_set))
                total_caps = len(primary_caps_set.union(tool_caps_set))
                
                if total_caps > 0:
                    similarity = overlap / total_caps
                    if similarity > 0.3:  # At least 30% capability overlap
                        # Get performance data if available
                        performance = discovery.performance_data.get(name, {})
                        success_rate = performance.get('success_rate', 0.5)
                        avg_time = performance.get('avg_execution_time', 1.0)
                        
                        alternatives.append(FallbackOption(
                            level=FallbackLevel.TOOL,
                            reason=FallbackReason.TOOL_FAILURE,
                            alternative=name,
                            confidence=similarity * success_rate,
                            estimated_cost=avg_time,
                            description=f"Alternative tool: {tool.description}",
                            success_rate=success_rate,
                            metadata={
                                'similarity': similarity,
                                'capabilities_overlap': list(primary_caps_set.intersection(tool_caps_set)),
                                'tool_server': getattr(tool, 'server', 'unknown')
                            }
                        ))
        
        # Sort by confidence score
        alternatives.sort(key=lambda x: x.confidence, reverse=True)
        return alternatives[:5]  # Return top 5 alternatives


class PlanFallbackStrategy(FallbackStrategy):
    """Strategy for finding plan alternatives"""
    
    def get_strategy_name(self) -> str:
        return "plan_fallback"
    
    async def find_alternatives(
        self, 
        target: Union[str, ToolCall, ExecutionPlan],
        context: Dict[str, Any],
        discovery: ToolDiscovery
    ) -> List[FallbackOption]:
        """Find alternative execution plans"""
        alternatives = []
        
        if not isinstance(target, ExecutionPlan):
            return alternatives
        
        # Analyze the plan structure
        plan = target
        failed_tools = context.get('failed_tools', set())
        
        # Strategy 1: Replace failed tools in the plan
        if failed_tools:
            tool_fallback = ToolFallbackStrategy()
            for i, step in enumerate(plan.tools):
                if step.tool_name in failed_tools:
                    tool_alternatives = await tool_fallback.find_alternatives(
                        step.tool_name, context, discovery
                    )
                    
                    for alt in tool_alternatives[:2]:  # Top 2 alternatives per failed tool
                        # Create a modified plan
                        new_tools = plan.tools.copy()
                        new_tool = ToolCall(
                            tool_name=alt.alternative,
                            tool_id=f"{alt.alternative}_{i}",
                            parameters=step.parameters,
                            order=step.order,
                            dependencies=step.dependencies
                        )
                        new_tools[i] = new_tool
                        
                        # Calculate confidence based on tool alternative confidence
                        # and plan complexity
                        plan_confidence = alt.confidence * (0.9 ** len(failed_tools))
                        
                        alternatives.append(FallbackOption(
                            level=FallbackLevel.PLAN,
                            reason=FallbackReason.TOOL_FAILURE,
                            alternative=ExecutionPlan(
                                plan_id=f"fallback_{plan.plan_id}_{i}",
                                intent=f"fallback for {plan.intent}",
                                tools=new_tools
                            ),
                            confidence=plan_confidence,
                            estimated_cost=alt.estimated_cost * 1.2,  # Slight overhead
                            description=f"Modified plan using {alt.alternative} instead of {step.tool_name}",
                            metadata={
                                'original_tool': step.tool_name,
                                'replacement_tool': alt.alternative,
                                'step_index': i
                            }
                        ))
        
        # Strategy 2: Simplify the plan by removing non-essential steps
        if len(plan.tools) > 1:
            # Identify potentially optional steps (those with no dependents)
            dependent_steps = set()
            for step in plan.tools:
                dependent_steps.update(step.dependencies)
            
            essential_steps = []
            optional_steps = []
            
            for i, step in enumerate(plan.tools):
                step_id = step.order
                if step_id in dependent_steps or i == len(plan.tools) - 1:  # Last step is usually essential
                    essential_steps.append(step)
                else:
                    optional_steps.append((i, step))
            
            if optional_steps and len(essential_steps) > 0:
                alternatives.append(FallbackOption(
                    level=FallbackLevel.PLAN,
                    reason=FallbackReason.PERFORMANCE_DEGRADATION,
                    alternative=ExecutionPlan(
                        plan_id=f"simplified_{plan.plan_id}",
                        intent=f"simplified {plan.intent}",
                        tools=essential_steps
                    ),
                    confidence=0.7,  # Lower confidence due to reduced functionality
                    estimated_cost=sum(discovery.performance_data.get(s.tool_name, {}).get('avg_execution_time', 1.0) for s in essential_steps),
                    description=f"Simplified plan removing {len(optional_steps)} optional steps",
                    metadata={
                        'removed_steps': [step.tool_name for _, step in optional_steps],
                        'essential_steps': [step.tool_name for step in essential_steps]
                    }
                ))
        
        # Sort by confidence
        alternatives.sort(key=lambda x: x.confidence, reverse=True)
        return alternatives[:3]  # Return top 3 plan alternatives


class GracefulDegradationStrategy(FallbackStrategy):
    """Strategy for graceful degradation when all else fails"""
    
    def get_strategy_name(self) -> str:
        return "graceful_degradation"
    
    async def find_alternatives(
        self, 
        target: Union[str, ToolCall, ExecutionPlan],
        context: Dict[str, Any],
        discovery: ToolDiscovery
    ) -> List[FallbackOption]:
        """Provide graceful degradation options"""
        alternatives = []
        
        # Option 1: Partial execution with manual intervention
        alternatives.append(FallbackOption(
            level=FallbackLevel.GRACEFUL,
            reason=FallbackReason.DEPENDENCY_FAILURE,
            alternative="manual_intervention_required",
            confidence=0.9,  # High confidence that this will "work" (by requesting help)
            estimated_cost=float('inf'),  # Infinite cost due to manual intervention
            description="Request manual intervention to complete the task",
            metadata={
                'intervention_type': 'manual_completion',
                'user_guidance': 'Requires user to manually complete remaining steps'
            }
        ))
        
        # Option 2: Return partial results
        if context.get('partial_results'):
            alternatives.append(FallbackOption(
                level=FallbackLevel.GRACEFUL,
                reason=FallbackReason.QUALITY_THRESHOLD,
                alternative="return_partial_results",
                confidence=0.6,
                estimated_cost=0.0,  # No additional cost
                description="Return available partial results",
                metadata={
                    'partial_data': context.get('partial_results', {}),
                    'completion_percentage': context.get('completion_percentage', 0)
                }
            ))
        
        # Option 3: Suggest alternative approach
        alternatives.append(FallbackOption(
            level=FallbackLevel.GRACEFUL,
            reason=FallbackReason.STRATEGY,
            alternative="suggest_alternative_approach",
            confidence=0.4,
            estimated_cost=0.0,
            description="Suggest alternative approach to achieve the goal",
            metadata={
                'suggestions': [
                    "Break down the task into smaller, manageable steps",
                    "Use different tools or services",
                    "Modify the requirements to match available capabilities"
                ]
            }
        ))
        
        return alternatives


class FallbackManager:
    """
    Central manager for intelligent fallback mechanisms
    """
    
    def __init__(
        self, 
        discovery: ToolDiscovery,
        error_recovery: Optional[ErrorRecoverySystem] = None,
        planner: Optional[BasicExecutionPlanner] = None
    ):
        self.discovery = discovery
        self.error_recovery = error_recovery or ErrorRecoverySystem(discovery)
        self.planner = planner or BasicExecutionPlanner()
        
        # Fallback strategies
        self.strategies: Dict[str, FallbackStrategy] = {
            'tool': ToolFallbackStrategy(),
            'plan': PlanFallbackStrategy(),
            'graceful': GracefulDegradationStrategy()
        }
        
        # Fallback chains cache
        self.fallback_chains: Dict[str, FallbackChain] = {}
        
        # Performance tracking
        self.fallback_usage: Dict[str, int] = defaultdict(int)
        self.fallback_success: Dict[str, int] = defaultdict(int)
        
        # Configuration
        self.max_fallback_depth = 3
        self.confidence_threshold = 0.3
        self.performance_weight = 0.7
        self.cost_weight = 0.3
    
    async def create_fallback_chain(
        self,
        target: Union[str, ToolCall, ExecutionPlan],
        context: Dict[str, Any],
        max_depth: Optional[int] = None
    ) -> FallbackChain:
        """Create a comprehensive fallback chain"""
        max_depth = max_depth or self.max_fallback_depth
        all_options = []
        
        # Generate fallback options from all strategies
        for strategy_name, strategy in self.strategies.items():
            try:
                options = await strategy.find_alternatives(target, context, self.discovery)
                for option in options:
                    option.metadata['strategy'] = strategy_name
                all_options.extend(options)
            except Exception as e:
                logging.warning(f"Strategy {strategy_name} failed: {e}")
                continue
        
        # Filter by confidence threshold
        viable_options = [
            opt for opt in all_options 
            if opt.confidence >= self.confidence_threshold
        ]
        
        # Sort by composite score (confidence + performance - cost)
        def calculate_score(option: FallbackOption) -> float:
            performance_score = option.confidence * self.performance_weight
            cost_score = (1.0 / (1.0 + option.estimated_cost)) * self.cost_weight
            return performance_score + cost_score
        
        viable_options.sort(key=calculate_score, reverse=True)
        
        # Limit to max_depth
        selected_options = viable_options[:max_depth]
        
        # Calculate total confidence
        if selected_options:
            # Use weighted average of top options
            weights = [opt.confidence for opt in selected_options]
            total_weight = sum(weights)
            total_confidence = sum(opt.confidence * weight for opt, weight in zip(selected_options, weights)) / total_weight if total_weight > 0 else 0.0
        else:
            total_confidence = 0.0
        
        # Create execution order (highest confidence first)
        execution_order = list(range(len(selected_options)))
        
        chain = FallbackChain(
            primary_target=str(target),
            fallback_options=selected_options,
            total_confidence=total_confidence,
            execution_order=execution_order
        )
        
        # Cache the chain
        chain_key = self._generate_chain_key(target, context)
        self.fallback_chains[chain_key] = chain
        
        return chain
    
    async def execute_with_fallback(
        self,
        target: Union[str, ToolCall, ExecutionPlan],
        context: Dict[str, Any],
        executor: ChainExecutor,
        mcp_chain_func: Any
    ) -> FallbackExecutionResult:
        """Execute with automatic fallback on failure"""
        chain_key = self._generate_chain_key(target, context)
        
        # Try to get cached chain or create new one
        if chain_key not in self.fallback_chains:
            await self.create_fallback_chain(target, context)
        
        chain = self.fallback_chains[chain_key]
        chain.usage_count += 1
        
        # First try the primary target
        try:
            if isinstance(target, ExecutionPlan):
                state = await executor.execute_plan(target, mcp_chain_func)
                result = FallbackExecutionResult.from_execution_state(state)
            elif isinstance(target, ToolCall):
                plan = ExecutionPlan(
                    plan_id=f"fallback_{int(time.time())}",
                    intent="fallback execution",
                    tools=[target]
                )
                state = await executor.execute_plan(plan, mcp_chain_func)
                result = FallbackExecutionResult.from_execution_state(state)
            else:
                # Assume it's a tool name
                tool_call = ToolCall(
                    tool_name=target,
                    tool_id=f"{target}_fallback",
                    parameters={},
                    order=1
                )
                plan = ExecutionPlan(
                    plan_id=f"fallback_{target}_{int(time.time())}",
                    intent=f"execute {target}",
                    tools=[tool_call]
                )
                state = await executor.execute_plan(plan, mcp_chain_func)
                result = FallbackExecutionResult.from_execution_state(state)
            
            if result.status == ExecutionStatus.SUCCESS:
                chain.success_count += 1
                return result
        except Exception as e:
            logging.warning(f"Primary execution failed: {e}")
            context['primary_error'] = str(e)
        
        # Try fallback options in order
        for i, option_index in enumerate(chain.execution_order):
            option = chain.fallback_options[option_index]
            self.fallback_usage[option.level.value] += 1
            
            try:
                logging.info(f"Trying fallback option {i+1}: {option.description}")
                
                if isinstance(option.alternative, ExecutionPlan):
                    state = await executor.execute_plan(option.alternative, mcp_chain_func)
                    result = FallbackExecutionResult.from_execution_state(state)
                elif isinstance(option.alternative, ToolCall):
                    plan = ExecutionPlan(
                        plan_id=f"fallback_option_{i}_{int(time.time())}",
                        intent="fallback alternative",
                        tools=[option.alternative]
                    )
                    state = await executor.execute_plan(plan, mcp_chain_func)
                    result = FallbackExecutionResult.from_execution_state(state)
                elif isinstance(option.alternative, str) and option.alternative.startswith('manual_'):
                    # Handle manual intervention
                    result = FallbackExecutionResult(
                        status=ExecutionStatus.FAILED,  # Use FAILED since REQUIRES_INTERVENTION doesn't exist
                        outputs=[],
                        total_execution_time=0.0,
                        metadata={'intervention_required': option.description}
                    )
                elif isinstance(option.alternative, str) and option.alternative.startswith('return_partial'):
                    # Handle partial results
                    result = FallbackExecutionResult(
                        status=ExecutionStatus.SUCCESS,  # Partial success is still success
                        outputs=[context.get('partial_results', {})],
                        total_execution_time=0.0,
                        metadata={'partial_completion': True}
                    )
                else:
                    # Try to execute as tool name
                    tool_call = ToolCall(
                        tool_name=str(option.alternative),
                        tool_id=f"{option.alternative}_fallback",
                        parameters={},
                        order=1
                    )
                    plan = ExecutionPlan(
                        plan_id=f"fallback_tool_{option.alternative}_{int(time.time())}",
                        intent=f"execute fallback {option.alternative}",
                        tools=[tool_call]
                    )
                    state = await executor.execute_plan(plan, mcp_chain_func)
                    result = FallbackExecutionResult.from_execution_state(state)
                
                if result.status == ExecutionStatus.SUCCESS:
                    self.fallback_success[option.level.value] += 1
                    chain.success_count += 1
                    result.metadata = result.metadata or {}
                    result.metadata['fallback_used'] = option.to_dict()
                    return result
                    
            except Exception as e:
                logging.warning(f"Fallback option {i+1} failed: {e}")
                continue
        
        # All fallbacks failed
        return FallbackExecutionResult(
            status=ExecutionStatus.FAILED,
            outputs=[],
            total_execution_time=0.0,
            error_message="All fallback options exhausted",
            metadata={'fallback_chain': chain.primary_target}
        )
    
    def _generate_chain_key(self, target: Union[str, ToolCall, ExecutionPlan], context: Dict[str, Any]) -> str:
        """Generate a unique key for caching fallback chains"""
        target_str = str(target)
        context_hash = hash(json.dumps(sorted(context.items()), default=str))
        return f"{target_str}:{context_hash}"
    
    def get_fallback_statistics(self) -> Dict[str, Any]:
        """Get comprehensive fallback usage statistics"""
        total_usage = sum(self.fallback_usage.values())
        total_success = sum(self.fallback_success.values())
        
        stats = {
            'total_fallback_usage': total_usage,
            'total_fallback_success': total_success,
            'overall_fallback_success_rate': total_success / total_usage if total_usage > 0 else 0.0,
            'usage_by_level': dict(self.fallback_usage),
            'success_by_level': dict(self.fallback_success),
            'success_rates_by_level': {
                level: self.fallback_success[level] / self.fallback_usage[level] 
                if self.fallback_usage[level] > 0 else 0.0
                for level in self.fallback_usage.keys()
            },
            'cached_chains': len(self.fallback_chains),
            'chain_performance': {
                key: {
                    'usage_count': chain.usage_count,
                    'success_count': chain.success_count,
                    'success_rate': chain.get_success_rate(),
                    'total_confidence': chain.total_confidence,
                    'options_count': len(chain.fallback_options)
                }
                for key, chain in self.fallback_chains.items()
            }
        }
        
        return stats
    
    def clear_cache(self):
        """Clear fallback chain cache"""
        self.fallback_chains.clear()
    
    def add_custom_strategy(self, name: str, strategy: FallbackStrategy):
        """Add a custom fallback strategy"""
        self.strategies[name] = strategy
    
    def remove_strategy(self, name: str):
        """Remove a fallback strategy"""
        if name in self.strategies:
            del self.strategies[name]
