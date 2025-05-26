"""
Autonomous MCP Agent - Phase 10
True autonomous execution without manual intervention
"""

from .execution_engine import (
    AutonomousExecutionEngine,
    ContextManager,
    WorkflowPlan,
    WorkflowStep,
    ToolSpec,
    ExecutionResult,
    ExecutionStatus,
    ToolType
)

from .autonomous_orchestrator import (
    AutonomousOrchestrator,
    TaskPlanner
)

__version__ = "10.0.0"
__phase__ = "Phase 10: Autonomous Integration and Execution"

__all__ = [
    'AutonomousOrchestrator',
    'AutonomousExecutionEngine', 
    'TaskPlanner',
    'ContextManager',
    'WorkflowPlan',
    'WorkflowStep',
    'ToolSpec',
    'ExecutionResult',
    'ExecutionStatus',
    'ToolType'
]
