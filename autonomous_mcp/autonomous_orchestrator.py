"""Phase 10 Autonomous Orchestrator"""
from execution_engine import *
from typing import Dict, Any
from datetime import datetime

class TaskPlanner:
    def __init__(self):
        self.templates = {
            'research': ['web_search', 'repl', 'artifacts'],
            'market': ['web_search', 'repl', 'artifacts']
        }
    
    async def plan_workflow(self, task: str) -> WorkflowPlan:
        task_type = 'market' if 'market' in task.lower() else 'research'
        tools = self.templates[task_type]
        
        steps = []
        for i, tool_name in enumerate(tools):
            step = self._make_step(i, tool_name, task)
            steps.append(step)
        
        return WorkflowPlan(
            id=f"workflow_{datetime.now().strftime('%H%M%S')}",
            description=task,
            steps=steps,
            created_at=datetime.now()
        )
    
    def _make_step(self, i: int, tool: str, task: str) -> WorkflowStep:
        if tool == 'web_search':
            return WorkflowStep(
                id=f"step_{i+1}",
                tool_spec=ToolSpec('web_search', ToolType.SEARCH, {'query': task}),
                context_inputs=[],
                context_outputs=['search_results']
            )
        elif tool == 'repl':
            return WorkflowStep(
                id=f"step_{i+1}",
                tool_spec=ToolSpec('repl', ToolType.ANALYSIS, {}),
                context_inputs=['search_results'], 
                context_outputs=['analysis']
            )
        else:
            return WorkflowStep(
                id=f"step_{i+1}",
                tool_spec=ToolSpec('artifacts', ToolType.CREATION, {}),
                context_inputs=['analysis'],
                context_outputs=['report']
            )

class AutonomousOrchestrator:
    def __init__(self):
        self.engine = AutonomousExecutionEngine()
        self.planner = TaskPlanner()
    
    async def execute_autonomous_task(self, task: str) -> Dict[str, Any]:
        workflow = await self.planner.plan_workflow(task)
        result = await self.engine.execute_workflow(workflow)
        
        return {
            'status': result.status.value,
            'autonomous_execution': result.autonomous_execution,
            'tool_chain_length': result.tool_chain_length,
            'results': result.results,
            'total_time': result.total_time,
            'manual_interventions': result.manual_interventions
        }
