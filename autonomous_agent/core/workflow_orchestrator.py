#!/usr/bin/env python3
"""Workflow Orchestrator - Phase 3 Implementation"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
try:
    from .tool_chainer import real_tool_chainer, ToolChainResult
except ImportError:
    import sys, os
    sys.path.append(os.path.dirname(__file__))
    from tool_chainer import real_tool_chainer, ToolChainResult

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WorkflowOrchestrator:
    """Orchestrates complex multi-tool workflows"""
    
    def __init__(self):
        self.workflow_templates = {}
        self.active_workflows = {}
        self.completed_workflows = []
        self._initialize_templates()
        logger.info("Workflow orchestrator initialized")
    
    def _initialize_templates(self):
        """Initialize pre-defined workflow templates"""
        
        # Research workflow: search -> analyze -> document
        self.workflow_templates['research'] = {
            'name': 'Research Workflow',
            'description': 'Search, analyze, and document',
            'steps': [
                {'tool': 'web_search', 'parameters': {'query': '{query}'}},
                {'tool': 'repl', 'parameters': {'code': 'console.log("Analysis")', 'use_previous_output': True}},
                {'tool': 'artifacts', 'parameters': {'command': 'create', 'content': 'Report', 'use_previous_output': True}}
            ]
        }
        
        # Analysis workflow: code -> document
        self.workflow_templates['analysis'] = {
            'name': 'Analysis Workflow',
            'description': 'Execute code and document results',
            'steps': [
                {'tool': 'repl', 'parameters': {'code': '{analysis_code}'}},
                {'tool': 'artifacts', 'parameters': {'command': 'create', 'content': 'Results', 'use_previous_output': True}}
            ]
        }

    async def execute_workflow(self, template_name: str, parameters: Dict[str, Any]) -> ToolChainResult:
        """Execute a workflow from template"""
        if template_name not in self.workflow_templates:
            raise ValueError(f"Unknown workflow template: {template_name}")
        
        template = self.workflow_templates[template_name]
        
        # Substitute parameters in template
        steps = []
        for step in template['steps']:
            new_step = {'tool': step['tool'], 'parameters': {}}
            for key, value in step['parameters'].items():
                if isinstance(value, str) and '{' in value:
                    new_step['parameters'][key] = value.format(**parameters)
                else:
                    new_step['parameters'][key] = value
            steps.append(new_step)
        
        # Create and execute chain
        chain_id = real_tool_chainer.create_tool_chain(steps, template['name'])
        result = await real_tool_chainer.execute_chain(chain_id)
        
        logger.info(f"Workflow {template_name} completed")
        return result
    
    async def execute_custom_workflow(self, template: Dict[str, Any], parameters: Dict[str, Any]) -> ToolChainResult:
        """Execute a custom workflow template"""
        
        # Substitute parameters in template steps
        steps = []
        for step in template['steps']:
            new_step = {'tool': step['tool'], 'parameters': {}}
            for key, value in step['parameters'].items():
                if isinstance(value, str) and '{' in value:
                    new_step['parameters'][key] = value.format(**parameters)
                else:
                    new_step['parameters'][key] = value
            steps.append(new_step)
        
        # Create and execute chain
        workflow_name = template.get('name', 'Custom Workflow')
        chain_id = real_tool_chainer.create_tool_chain(steps, workflow_name)
        result = await real_tool_chainer.execute_chain(chain_id)
        
        logger.info(f"Custom workflow {workflow_name} completed")
        return result
    
    def add_workflow_template(self, name: str, template: Dict[str, Any]):
        """Add a new workflow template"""
        self.workflow_templates[name] = template
        logger.info(f"Added workflow template: {name}")
    
    def get_available_workflows(self) -> List[str]:
        """Get list of available workflow templates"""
        return list(self.workflow_templates.keys())


# Create singleton instance
workflow_orchestrator = WorkflowOrchestrator()
