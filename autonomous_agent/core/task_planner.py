#!/usr/bin/env python3
"""Task Planner - Phase 4 Implementation - Complete Version"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

try:
    from .tool_chainer import real_tool_chainer, ToolChainResult
    from .workflow_orchestrator import WorkflowOrchestrator
except ImportError:
    import sys, os
    sys.path.append(os.path.dirname(__file__))
    from tool_chainer import real_tool_chainer, ToolChainResult
    from workflow_orchestrator import WorkflowOrchestrator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TaskAnalysis:
    """Analysis results for a task"""
    task_type: str
    complexity: str  # 'simple', 'medium', 'complex'
    required_tools: List[str]
    suggested_workflow: str
    parameters: Dict[str, Any]
    estimated_steps: int
    confidence: float


@dataclass
class PlanningResult:
    """Result of autonomous planning"""
    success: bool
    analysis: Optional[TaskAnalysis]
    workflow_plan: Optional[Dict[str, Any]]
    execution_strategy: Optional[str]
    error_message: Optional[str] = None


class TaskPlanner:
    """Autonomous task planning and workflow generation"""
    
    def __init__(self):
        self.orchestrator = WorkflowOrchestrator()
        self.task_patterns = {}
        self.tool_capabilities = {}
        self._initialize_patterns()
        self._initialize_tool_capabilities()
        logger.info("Task planner initialized")
    
    def _initialize_patterns(self):
        """Initialize task pattern recognition"""
        self.task_patterns = {
            'research': {
                'keywords': ['research', 'find', 'search', 'investigate', 'analyze', 'study'],
                'complexity': 'medium',
                'tools': ['web_search', 'repl', 'artifacts'],
                'workflow_template': 'research'
            },
            'analysis': {
                'keywords': ['analyze', 'calculate', 'compute', 'process', 'evaluate'],
                'complexity': 'medium', 
                'tools': ['repl', 'artifacts'],
                'workflow_template': 'analysis'
            },
            'web_lookup': {
                'keywords': ['what is', 'who is', 'when', 'where', 'current', 'latest'],
                'complexity': 'simple',
                'tools': ['web_search'],
                'workflow_template': 'research'
            }
        }
    
    def _initialize_tool_capabilities(self):
        """Initialize understanding of tool capabilities"""
        self.tool_capabilities = {
            'web_search': {'purpose': 'Search the internet for current information'},
            'repl': {'purpose': 'Execute JavaScript code and perform calculations'},
            'artifacts': {'purpose': 'Create documents, reports, and structured content'}
        }
    
    def analyze_task(self, task_description: str) -> TaskAnalysis:
        """Analyze a task description and determine requirements"""
        task_lower = task_description.lower()
        
        # Pattern matching
        best_pattern = 'research'  # default
        best_confidence = 0.0
        
        for pattern_name, pattern_info in self.task_patterns.items():
            keyword_matches = sum(1 for keyword in pattern_info['keywords'] 
                                if keyword in task_lower)
            if keyword_matches > 0:
                confidence = keyword_matches / len(pattern_info['keywords'])
                if confidence > best_confidence:
                    best_pattern = pattern_name
                    best_confidence = confidence
        
        # Get pattern info
        pattern_info = self.task_patterns[best_pattern]
        
        # Extract parameters
        parameters = {'original_task': task_description, 'query': task_description}
        
        return TaskAnalysis(
            task_type=best_pattern,
            complexity=pattern_info['complexity'],
            required_tools=pattern_info['tools'],
            suggested_workflow=pattern_info['workflow_template'],
            parameters=parameters,
            estimated_steps=len(pattern_info['tools']),
            confidence=best_confidence if best_confidence > 0 else 0.5
        )

    def generate_workflow_plan(self, analysis: TaskAnalysis) -> Dict[str, Any]:
        """Generate a detailed workflow plan from task analysis"""
        
        plan = {
            'workflow_name': analysis.suggested_workflow,
            'task_type': analysis.task_type,
            'complexity': analysis.complexity,
            'estimated_steps': analysis.estimated_steps,
            'confidence': analysis.confidence,
            'tools_required': analysis.required_tools,
            'parameters': analysis.parameters,
            'template': {
                'name': f'{analysis.task_type.title()} Workflow',
                'description': f'Generated workflow for {analysis.task_type} task',
                'steps': self._generate_steps(analysis)
            }
        }
        
        return plan
    
    def _generate_steps(self, analysis: TaskAnalysis) -> List[Dict[str, Any]]:
        """Generate workflow steps based on analysis"""
        steps = []
        
        for tool in analysis.required_tools:
            if tool == 'web_search':
                steps.append({'tool': 'web_search', 'parameters': {'query': '{query}'}})
            elif tool == 'repl':
                steps.append({'tool': 'repl', 'parameters': {'code': 'console.log("Processing...");'}})
            elif tool == 'artifacts':
                steps.append({'tool': 'artifacts', 'parameters': {'command': 'create', 'content': 'Results'}})
        
        return steps
    
    async def plan_task_execution(self, task_description: str) -> PlanningResult:
        """Main entry point: analyze task and generate execution plan"""
        try:
            logger.info(f"Planning task: {task_description}")
            
            # Step 1: Analyze the task
            analysis = self.analyze_task(task_description)
            logger.info(f"Task analysis: {analysis.task_type} ({analysis.complexity})")
            
            # Step 2: Generate workflow plan
            workflow_plan = self.generate_workflow_plan(analysis)
            logger.info(f"Generated workflow: {workflow_plan['workflow_name']}")
            
            # Step 3: Determine execution strategy
            execution_strategy = 'sequential'
            
            return PlanningResult(
                success=True,
                analysis=analysis,
                workflow_plan=workflow_plan,
                execution_strategy=execution_strategy
            )
            
        except Exception as e:
            logger.error(f"Planning failed: {str(e)}")
            return PlanningResult(
                success=False,
                analysis=None,
                workflow_plan=None,
                execution_strategy=None,
                error_message=str(e)
            )


# Convenience function for easy access
async def autonomous_task_planning(task_description: str) -> PlanningResult:
    """Convenience function for autonomous task planning"""
    planner = TaskPlanner()
    return await planner.plan_task_execution(task_description)
