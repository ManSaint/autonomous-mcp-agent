"""
Autonomous MCP Agent - Production Ready
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
__status__ = "Production Ready"

# Main entry point
def create_orchestrator():
    """Create an autonomous orchestrator instance"""
    return AutonomousOrchestrator()

# Quick execution function
async def execute_task(task_description: str):
    """Quick autonomous task execution"""
    orchestrator = AutonomousOrchestrator()
    return await orchestrator.execute_autonomous_task(task_description)

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
    'ToolType',
    'create_orchestrator',
    'execute_task'
]
