"""
Workflow Builder for Advanced MCP Agent

This module provides sophisticated workflow creation capabilities,
enabling the construction of complex, multi-step workflows with
intelligent chaining, conditional logic, and error handling.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

# Internal framework imports
from .autonomous_tools import IntelligentWorkflow, WorkflowStep, TaskAnalysisResult
from .discovery import ToolDiscovery
from .real_mcp_discovery import RealMCPDiscovery
from .mcp_chain_executor import RealMCPChainExecutor

# Configure logging
logger = logging.getLogger(__name__)


class WorkflowStepType(Enum):
    """Types of workflow steps"""
    TOOL_EXECUTION = "tool_execution"
    CONDITIONAL = "conditional"
    LOOP = "loop"
    PARALLEL = "parallel"
    CHECKPOINT = "checkpoint"
    ERROR_HANDLER = "error_handler"


@dataclass
class ConditionalStep:
    """Conditional workflow step"""
    condition: str
    true_steps: List[str]
    false_steps: List[str]
    evaluation_method: str = "expression"  # expression, tool_result, user_input


@dataclass
class LoopStep:
    """Loop workflow step"""
    condition: str
    steps: List[str]
    max_iterations: int = 10
    loop_type: str = "while"  # while, for, foreach


@dataclass
class ParallelStep:
    """Parallel execution step"""
    parallel_steps: List[str]
    wait_for_all: bool = True
    timeout: Optional[float] = None


@dataclass
class AdvancedWorkflowStep(WorkflowStep):
    """Extended workflow step with advanced features"""
    step_type: WorkflowStepType = WorkflowStepType.TOOL_EXECUTION
    conditional: Optional[ConditionalStep] = None
    loop: Optional[LoopStep] = None
    parallel: Optional[ParallelStep] = None
    error_handling: Optional[Dict[str, Any]] = None
    checkpoint_data: Optional[Dict[str, Any]] = None
    retry_config: Optional[Dict[str, Any]] = None



class WorkflowBuilder:
    """
    Advanced workflow builder for creating sophisticated task execution flows
    """
    
    def __init__(self):
        """Initialize workflow builder"""
        self.discovery = ToolDiscovery()
        self.real_discovery = RealMCPDiscovery()
        self.mcp_executor = RealMCPChainExecutor()
        
        # Workflow templates
        self.templates: Dict[str, Dict[str, Any]] = {}
        self._load_default_templates()
        
        logger.info("Workflow builder initialized")
    
    def _load_default_templates(self):
        """Load default workflow templates"""
        self.templates = {
            "research_and_analyze": {
                "description": "Research a topic and analyze findings",
                "steps": [
                    {"type": "search", "description": "Search for information"},
                    {"type": "fetch", "description": "Fetch detailed content"},
                    {"type": "analyze", "description": "Analyze findings"},
                    {"type": "summarize", "description": "Create summary"}
                ]
            },
            "data_pipeline": {
                "description": "Process and transform data",
                "steps": [
                    {"type": "extract", "description": "Extract data"},
                    {"type": "transform", "description": "Transform data"},
                    {"type": "validate", "description": "Validate results"},
                    {"type": "load", "description": "Load to destination"}
                ]
            },
            "monitoring_workflow": {
                "description": "Monitor and alert on conditions",
                "steps": [
                    {"type": "check", "description": "Check conditions"},
                    {"type": "conditional", "description": "Evaluate results"},
                    {"type": "alert", "description": "Send alerts if needed"},
                    {"type": "log", "description": "Log results"}
                ]
            }
        }
    
    async def create_workflow_from_template(self, template_name: str, parameters: Dict[str, Any]) -> IntelligentWorkflow:
        """Create workflow from predefined template"""
        if template_name not in self.templates:
            raise ValueError(f"Template '{template_name}' not found")
        
        template = self.templates[template_name]
        return await self._build_workflow_from_template(template, parameters)
    
    async def create_custom_workflow(self, description: str, steps: List[Dict[str, Any]], context: Optional[Dict[str, Any]] = None) -> IntelligentWorkflow:
        """Create custom workflow from step definitions"""
        try:
            logger.info(f"Creating custom workflow: {description}")
            
            # Convert step definitions to workflow steps
            workflow_steps = []
            for i, step_def in enumerate(steps):
                step = await self._create_workflow_step(step_def, i)
                workflow_steps.append(step)
            
            # Calculate metrics
            total_duration = sum(step.estimated_duration for step in workflow_steps)
            overall_probability = min([step.success_probability for step in workflow_steps] or [0.8])
            
            # Create workflow
            workflow = IntelligentWorkflow(
                workflow_id=f"custom_{int(datetime.now().timestamp())}",
                title=f"Custom: {description[:50]}...",
                description=description,
                steps=workflow_steps,
                total_estimated_duration=total_duration,
                overall_success_probability=overall_probability,
                created_at=datetime.now(),
                metadata={
                    "type": "custom",
                    "step_count": len(workflow_steps),
                    "context": context or {}
                }
            )
            
            logger.info(f"Created custom workflow {workflow.workflow_id}")
            return workflow
            
        except Exception as e:
            logger.error(f"Custom workflow creation failed: {e}")
            raise
    
    async def create_conditional_workflow(self, description: str, condition: str, true_steps: List[Dict], false_steps: List[Dict]) -> IntelligentWorkflow:
        """Create workflow with conditional logic"""
        try:
            logger.info(f"Creating conditional workflow: {description}")
            
            # Create conditional step
            conditional_step = ConditionalStep(
                condition=condition,
                true_steps=[f"true_step_{i}" for i in range(len(true_steps))],
                false_steps=[f"false_step_{i}" for i in range(len(false_steps))]
            )
            
            # Create workflow steps
            workflow_steps = []
            
            # Add main conditional step
            main_step = AdvancedWorkflowStep(
                step_id="conditional_main",
                description=f"Evaluate condition: {condition}",
                tool_name="conditional_evaluator",
                parameters={"condition": condition},
                dependencies=[],
                estimated_duration=10.0,
                success_probability=0.9,
                step_type=WorkflowStepType.CONDITIONAL,
                conditional=conditional_step
            )
            workflow_steps.append(main_step)
            
            # Add true branch steps
            for i, step_def in enumerate(true_steps):
                step = await self._create_workflow_step(step_def, len(workflow_steps))
                step.step_id = f"true_step_{i}"
                step.dependencies = ["conditional_main"]
                workflow_steps.append(step)
            
            # Add false branch steps
            for i, step_def in enumerate(false_steps):
                step = await self._create_workflow_step(step_def, len(workflow_steps))
                step.step_id = f"false_step_{i}"
                step.dependencies = ["conditional_main"]
                workflow_steps.append(step)
            
            return await self._finalize_workflow(description, workflow_steps, "conditional")
            
        except Exception as e:
            logger.error(f"Conditional workflow creation failed: {e}")
            raise
    
    async def create_parallel_workflow(self, description: str, parallel_groups: List[List[Dict]], wait_for_all: bool = True) -> IntelligentWorkflow:
        """Create workflow with parallel execution"""
        try:
            logger.info(f"Creating parallel workflow: {description}")
            
            workflow_steps = []
            
            # Create parallel groups
            for group_idx, group_steps in enumerate(parallel_groups):
                # Create parallel step coordinator
                parallel_step_ids = [f"parallel_{group_idx}_{i}" for i in range(len(group_steps))]
                
                parallel_step = ParallelStep(
                    parallel_steps=parallel_step_ids,
                    wait_for_all=wait_for_all,
                    timeout=300.0  # 5 minute timeout
                )
                
                coordinator_step = AdvancedWorkflowStep(
                    step_id=f"parallel_coordinator_{group_idx}",
                    description=f"Coordinate parallel execution group {group_idx}",
                    tool_name="parallel_coordinator",
                    parameters={"group_id": group_idx},
                    dependencies=[],
                    estimated_duration=5.0,
                    success_probability=0.95,
                    step_type=WorkflowStepType.PARALLEL,
                    parallel=parallel_step
                )
                workflow_steps.append(coordinator_step)
                
                # Add individual parallel steps
                for i, step_def in enumerate(group_steps):
                    step = await self._create_workflow_step(step_def, len(workflow_steps))
                    step.step_id = f"parallel_{group_idx}_{i}"
                    step.dependencies = [f"parallel_coordinator_{group_idx}"]
                    workflow_steps.append(step)
            
            return await self._finalize_workflow(description, workflow_steps, "parallel")
            
        except Exception as e:
            logger.error(f"Parallel workflow creation failed: {e}")
            raise
    
    # Helper methods
    
    async def _create_workflow_step(self, step_def: Dict[str, Any], index: int) -> AdvancedWorkflowStep:
        """Create workflow step from definition"""
        step_type = step_def.get("type", "tool_execution")
        tool_name = step_def.get("tool", step_def.get("tool_name", "unknown_tool"))
        
        return AdvancedWorkflowStep(
            step_id=f"step_{index}",
            description=step_def.get("description", f"Execute {tool_name}"),
            tool_name=tool_name,
            parameters=step_def.get("parameters", {}),
            dependencies=step_def.get("dependencies", []),
            estimated_duration=step_def.get("estimated_duration", 30.0),
            success_probability=step_def.get("success_probability", 0.8),
            step_type=WorkflowStepType(step_type) if step_type in [e.value for e in WorkflowStepType] else WorkflowStepType.TOOL_EXECUTION,
            retry_config=step_def.get("retry_config", {"max_retries": 3, "delay": 1.0})
        )
    
    async def _finalize_workflow(self, description: str, steps: List[AdvancedWorkflowStep], workflow_type: str) -> IntelligentWorkflow:
        """Finalize workflow creation"""
        total_duration = sum(step.estimated_duration for step in steps)
        overall_probability = min([step.success_probability for step in steps] or [0.8])
        
        return IntelligentWorkflow(
            workflow_id=f"{workflow_type}_{int(datetime.now().timestamp())}",
            title=f"{workflow_type.title()}: {description[:50]}...",
            description=description,
            steps=steps,
            total_estimated_duration=total_duration,
            overall_success_probability=overall_probability,
            created_at=datetime.now(),
            metadata={
                "type": workflow_type,
                "step_count": len(steps),
                "has_advanced_features": any(step.step_type != WorkflowStepType.TOOL_EXECUTION for step in steps)
            }
        )
    
    async def _build_workflow_from_template(self, template: Dict[str, Any], parameters: Dict[str, Any]) -> IntelligentWorkflow:
        """Build workflow from template"""
        steps = []
        for i, step_template in enumerate(template["steps"]):
            # Merge template with parameters
            step_def = {**step_template, **parameters.get(f"step_{i}", {})}
            step = await self._create_workflow_step(step_def, i)
            steps.append(step)
        
        return await self._finalize_workflow(
            template["description"], 
            steps, 
            "template"
        )
    
    def get_available_templates(self) -> Dict[str, str]:
        """Get list of available workflow templates"""
        return {name: template["description"] for name, template in self.templates.items()}
    
    def add_template(self, name: str, template: Dict[str, Any]):
        """Add new workflow template"""
        self.templates[name] = template
        logger.info(f"Added workflow template: {name}")
    
    async def optimize_workflow(self, workflow: IntelligentWorkflow) -> IntelligentWorkflow:
        """Optimize workflow for better performance"""
        # Simple optimization: remove redundant steps, optimize dependencies
        optimized_steps = []
        seen_tools = set()
        
        for step in workflow.steps:
            # Skip duplicate tool calls with same parameters
            step_signature = f"{step.tool_name}_{hash(str(step.parameters))}"
            if step_signature not in seen_tools:
                optimized_steps.append(step)
                seen_tools.add(step_signature)
        
        # Create optimized workflow
        workflow.steps = optimized_steps
        workflow.metadata["optimized"] = True
        workflow.metadata["optimization_timestamp"] = datetime.now().isoformat()
        
        return workflow


# Export classes
__all__ = ['WorkflowBuilder', 'AdvancedWorkflowStep', 'WorkflowStepType', 'ConditionalStep', 'LoopStep', 'ParallelStep']
