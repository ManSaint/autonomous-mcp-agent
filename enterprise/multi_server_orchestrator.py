"""
🚀 PHASE 9: Advanced Multi-Server Orchestrator
Enterprise-grade orchestration across 15 validated servers with 202 tools

This module provides sophisticated workflow orchestration capabilities across
the validated 15-server ecosystem from Phase 8.9, enabling complex enterprise
automation scenarios with real GitHub, Postman, and Trello integrations.
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid
from concurrent.futures import ThreadPoolExecutor
import threading

# Phase 8.9 Foundation Imports
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from autonomous_mcp.real_mcp_client_new import RealMCPClient
from autonomous_mcp.real_mcp_discovery import RealMCPDiscovery
from autonomous_mcp.mcp_config_reader import MCPConfigReader

class WorkflowStatus(Enum):
    """Workflow execution status states"""
    PENDING = "pending"
    RUNNING = "running" 
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"

class ServerRole(Enum):
    """Server roles in enterprise workflows"""
    PRIMARY = "primary"
    SECONDARY = "secondary" 
    FALLBACK = "fallback"
    PARALLEL = "parallel"

@dataclass
class WorkflowStep:
    """Individual step in a multi-server workflow"""
    id: str
    server_name: str
    tool_name: str
    parameters: Dict[str, Any]
    dependencies: List[str] = field(default_factory=list)
    timeout: int = 30
    retry_count: int = 3
    role: ServerRole = ServerRole.PRIMARY
    condition: Optional[str] = None
    output_mapping: Dict[str, str] = field(default_factory=dict)

@dataclass  
class WorkflowDefinition:
    """Complete workflow definition for multi-server orchestration"""
    id: str
    name: str
    description: str
    steps: List[WorkflowStep]
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    version: str = "1.0"

@dataclass
class WorkflowExecution:
    """Runtime execution context for workflows"""
    workflow_id: str
    execution_id: str
    status: WorkflowStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    current_step: Optional[str] = None
    results: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)

class MultiServerOrchestrator:
    """
    🚀 Enterprise Multi-Server Orchestrator
    
    Orchestrates complex workflows across the validated 15-server ecosystem
    with 202 tools, providing enterprise-grade automation capabilities.
    """
    
    def __init__(self, config_path: str = None):
        """Initialize the orchestrator with Phase 8.9 foundation"""
        self.logger = logging.getLogger(__name__)
        self.config_reader = MCPConfigReader(config_path)
        self.discovery = RealMCPDiscovery(self.config_reader)
        self.mcp_client = RealMCPClient(self.discovery, self.config_reader)
        
        # Enterprise orchestration state
        self.workflows: Dict[str, WorkflowDefinition] = {}
        self.executions: Dict[str, WorkflowExecution] = {}
        self.servers: Dict[str, Dict[str, Any]] = {}
        self.tools: Dict[str, List[str]] = {}
        
        # Performance tracking
        self.metrics = {
            'total_workflows': 0,
            'successful_executions': 0,
            'failed_executions': 0,
            'average_execution_time': 0,
            'server_utilization': {},
            'tool_usage_stats': {}
        }
        
        # Thread pool for parallel execution
        self.executor = ThreadPoolExecutor(max_workers=15)  # One per server
        self.lock = threading.Lock()
        
        self.logger.info("🚀 Multi-Server Orchestrator initialized for Phase 9")
    
    async def initialize(self) -> bool:
        """Initialize orchestrator with validated server ecosystem"""
        try:
            self.logger.info("🔄 Initializing Multi-Server Orchestrator...")
            
            # Discover and validate all servers from Phase 8.9
            discovery_result = await self.discovery.discover_all_servers()
            if not discovery_result['success']:
                self.logger.error("❌ Failed to discover servers")
                return False
            
            # Load server information
            self.servers = discovery_result['servers']
            self.tools = discovery_result['tools_by_server']
            
            # Initialize MCP client
            await self.mcp_client.initialize()
            
            # Load pre-built enterprise workflow templates
            await self._load_enterprise_workflows()
            
            self.logger.info(f"✅ Orchestrator initialized with {len(self.servers)} servers and {sum(len(tools) for tools in self.tools.values())} tools")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Orchestrator initialization failed: {str(e)}")
            return False
    
    async def _load_enterprise_workflows(self):
        """Load pre-built enterprise workflow templates"""
        
        # GitHub → Postman → Trello DevOps Pipeline
        devops_workflow = WorkflowDefinition(
            id="devops_pipeline_v1",
            name="DevOps Pipeline Automation",
            description="Automated GitHub commit → Postman API testing → Trello task update",
            steps=[
                WorkflowStep(
                    id="check_commits",
                    server_name="github",
                    tool_name="list_commits", 
                    parameters={"owner": "{{repo_owner}}", "repo": "{{repo_name}}"},
                    role=ServerRole.PRIMARY
                ),
                WorkflowStep(
                    id="run_api_tests",
                    server_name="postman",
                    tool_name="run_monitor",
                    parameters={"monitorId": "{{monitor_id}}"},
                    dependencies=["check_commits"],
                    role=ServerRole.PRIMARY
                ),
                WorkflowStep(
                    id="update_project_status",
                    server_name="trello", 
                    tool_name="update_card_details",
                    parameters={
                        "cardId": "{{card_id}}",
                        "description": "API tests completed: {{api_test_results}}"
                    },
                    dependencies=["run_api_tests"],
                    role=ServerRole.PRIMARY
                )
            ],
            metadata={"category": "devops", "complexity": "medium"}
        )
        
        # Multi-Server Content Generation Pipeline
        content_workflow = WorkflowDefinition(
            id="content_generation_v1", 
            name="Multi-Server Content Generation",
            description="Generate documentation across GitHub, manage in Trello, validate with Postman",
            steps=[
                WorkflowStep(
                    id="create_documentation",
                    server_name="github",
                    tool_name="create_or_update_file",
                    parameters={
                        "owner": "{{repo_owner}}",
                        "repo": "{{repo_name}}", 
                        "path": "docs/{{doc_name}}.md",
                        "content": "{{doc_content}}",
                        "message": "Auto-generated documentation"
                    },
                    role=ServerRole.PRIMARY
                ),
                WorkflowStep(
                    id="create_tracking_card",
                    server_name="trello",
                    tool_name="add_card_to_list", 
                    parameters={
                        "listId": "{{todo_list_id}}",
                        "name": "Documentation: {{doc_name}}",
                        "description": "Auto-generated documentation tracking"
                    },
                    dependencies=["create_documentation"],
                    role=ServerRole.PARALLEL
                ),
                WorkflowStep(
                    id="validate_endpoints",
                    server_name="postman",
                    tool_name="list_collections",
                    parameters={},
                    dependencies=["create_documentation"],
                    role=ServerRole.SECONDARY
                )
            ],
            metadata={"category": "content", "complexity": "low"}
        )
        
        # Store workflows
        self.workflows[devops_workflow.id] = devops_workflow
        self.workflows[content_workflow.id] = content_workflow
        
        self.logger.info(f"📚 Loaded {len(self.workflows)} enterprise workflow templates")
    
    async def execute_workflow(self, workflow_id: str, parameters: Dict[str, Any]) -> str:
        """Execute a workflow across multiple servers"""
        try:
            if workflow_id not in self.workflows:
                raise ValueError(f"Workflow {workflow_id} not found")
            
            workflow = self.workflows[workflow_id]
            execution_id = str(uuid.uuid4())
            
            # Create execution context
            execution = WorkflowExecution(
                workflow_id=workflow_id,
                execution_id=execution_id,
                status=WorkflowStatus.RUNNING,
                start_time=datetime.now()
            )
            
            self.executions[execution_id] = execution
            self.logger.info(f"🚀 Starting workflow execution: {workflow.name} ({execution_id})")
            
            # Execute workflow steps
            await self._execute_workflow_steps(workflow, execution, parameters)
            
            # Update metrics
            with self.lock:
                self.metrics['total_workflows'] += 1
                if execution.status == WorkflowStatus.COMPLETED:
                    self.metrics['successful_executions'] += 1
                else:
                    self.metrics['failed_executions'] += 1
            
            return execution_id
            
        except Exception as e:
            self.logger.error(f"❌ Workflow execution failed: {str(e)}")
            if execution_id in self.executions:
                self.executions[execution_id].status = WorkflowStatus.FAILED
                self.executions[execution_id].errors.append(str(e))
            raise
    
    async def _execute_workflow_steps(self, workflow: WorkflowDefinition, 
                                     execution: WorkflowExecution, 
                                     parameters: Dict[str, Any]):
        """Execute individual workflow steps with dependency management"""
        
        completed_steps = set()
        pending_steps = {step.id: step for step in workflow.steps}
        
        while pending_steps:
            # Find steps ready to execute (dependencies satisfied)
            ready_steps = []
            for step_id, step in pending_steps.items():
                if all(dep in completed_steps for dep in step.dependencies):
                    ready_steps.append(step)
            
            if not ready_steps:
                raise RuntimeError("Circular dependency detected in workflow")
            
            # Execute ready steps (parallel where possible)
            step_tasks = []
            for step in ready_steps:
                if step.role == ServerRole.PARALLEL:
                    task = asyncio.create_task(
                        self._execute_single_step(step, execution, parameters)
                    )
                    step_tasks.append((step.id, task))
                else:
                    # Execute sequentially for primary/secondary steps
                    result = await self._execute_single_step(step, execution, parameters)
                    execution.results[step.id] = result
                    completed_steps.add(step.id)
                    del pending_steps[step.id]
                    
                    # Update parameters with step results for next steps
                    parameters.update(self._extract_output_mapping(step, result))
            
            # Wait for parallel tasks
            for step_id, task in step_tasks:
                try:
                    result = await task
                    execution.results[step_id] = result
                    completed_steps.add(step_id)
                    del pending_steps[step_id]
                    
                    # Update parameters with step results
                    step = next(s for s in workflow.steps if s.id == step_id)
                    parameters.update(self._extract_output_mapping(step, result))
                    
                except Exception as e:
                    self.logger.error(f"❌ Parallel step {step_id} failed: {str(e)}")
                    execution.errors.append(f"Step {step_id}: {str(e)}")
        
        # Mark execution as completed
        execution.status = WorkflowStatus.COMPLETED
        execution.end_time = datetime.now()
        execution.metrics['duration'] = (execution.end_time - execution.start_time).total_seconds()
        
        self.logger.info(f"✅ Workflow execution completed: {execution.execution_id}")
    
    async def _execute_single_step(self, step: WorkflowStep, 
                                  execution: WorkflowExecution,
                                  parameters: Dict[str, Any]) -> Any:
        """Execute a single workflow step"""
        
        execution.current_step = step.id
        self.logger.info(f"🔄 Executing step: {step.id} on {step.server_name}")
        
        # Substitute parameters in step parameters
        step_params = self._substitute_parameters(step.parameters, parameters)
        
        retry_count = 0
        while retry_count < step.retry_count:
            try:
                # Execute tool on specified server
                result = await self.mcp_client.execute_tool(
                    server_name=step.server_name,
                    tool_name=step.tool_name,
                    parameters=step_params
                )
                
                # Update server utilization metrics
                with self.lock:
                    if step.server_name not in self.metrics['server_utilization']:
                        self.metrics['server_utilization'][step.server_name] = 0
                    self.metrics['server_utilization'][step.server_name] += 1
                
                self.logger.info(f"✅ Step completed: {step.id}")
                return result
                
            except Exception as e:
                retry_count += 1
                if retry_count >= step.retry_count:
                    self.logger.error(f"❌ Step failed after {step.retry_count} retries: {step.id}")
                    raise
                else:
                    self.logger.warning(f"⚠️ Step retry {retry_count}/{step.retry_count}: {step.id}")
                    await asyncio.sleep(1)  # Brief delay before retry
    
    def _substitute_parameters(self, step_params: Dict[str, Any], 
                              workflow_params: Dict[str, Any]) -> Dict[str, Any]:
        """Substitute workflow parameters in step parameters"""
        result = {}
        for key, value in step_params.items():
            if isinstance(value, str) and value.startswith('{{') and value.endswith('}}'):
                param_name = value[2:-2]
                result[key] = workflow_params.get(param_name, value)
            else:
                result[key] = value
        return result
    
    def _extract_output_mapping(self, step: WorkflowStep, result: Any) -> Dict[str, Any]:
        """Extract values from step results based on output mapping"""
        if not step.output_mapping or not isinstance(result, dict):
            return {}
        
        extracted = {}
        for output_key, result_path in step.output_mapping.items():
            try:
                # Simple dot notation support
                value = result
                for path_part in result_path.split('.'):
                    value = value[path_part]
                extracted[output_key] = value
            except (KeyError, TypeError):
                self.logger.warning(f"⚠️ Could not extract {output_key} from step result")
        
        return extracted
    
    def get_workflow_status(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Get the status of a workflow execution"""
        return self.executions.get(execution_id)
    
    def list_workflows(self) -> List[Dict[str, Any]]:
        """List all available workflows"""
        return [
            {
                'id': wf.id,
                'name': wf.name,
                'description': wf.description,
                'steps': len(wf.steps),
                'metadata': wf.metadata
            }
            for wf in self.workflows.values()
        ]
    
    def get_orchestration_metrics(self) -> Dict[str, Any]:
        """Get comprehensive orchestration metrics"""
        return {
            'workflow_metrics': self.metrics.copy(),
            'active_executions': len([e for e in self.executions.values() 
                                    if e.status == WorkflowStatus.RUNNING]),
            'total_executions': len(self.executions),
            'server_count': len(self.servers),
            'tool_count': sum(len(tools) for tools in self.tools.values()),
            'success_rate': (self.metrics['successful_executions'] / 
                           max(1, self.metrics['total_workflows'])) * 100
        }
    
    async def create_custom_workflow(self, workflow_def: Dict[str, Any]) -> str:
        """Create a custom workflow from definition"""
        try:
            # Validate workflow definition
            workflow = WorkflowDefinition(
                id=workflow_def.get('id', str(uuid.uuid4())),
                name=workflow_def['name'],
                description=workflow_def['description'],
                steps=[
                    WorkflowStep(**step_def) 
                    for step_def in workflow_def['steps']
                ],
                metadata=workflow_def.get('metadata', {})
            )
            
            self.workflows[workflow.id] = workflow
            self.logger.info(f"📝 Created custom workflow: {workflow.name}")
            return workflow.id
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create custom workflow: {str(e)}")
            raise

    async def parallel_server_processing(self, server_tasks: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Execute tasks across multiple servers in parallel"""
        try:
            self.logger.info(f"🚀 Starting parallel processing across {len(server_tasks)} servers")
            
            # Create tasks for parallel execution
            tasks = []
            for server_name, task_info in server_tasks.items():
                task = asyncio.create_task(
                    self.mcp_client.execute_tool(
                        server_name=server_name,
                        tool_name=task_info['tool'],
                        parameters=task_info['parameters']
                    )
                )
                tasks.append((server_name, task))
            
            # Wait for all tasks to complete
            results = {}
            for server_name, task in tasks:
                try:
                    result = await task
                    results[server_name] = {'success': True, 'result': result}
                except Exception as e:
                    results[server_name] = {'success': False, 'error': str(e)}
            
            self.logger.info(f"✅ Parallel processing completed for {len(results)} servers")
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Parallel processing failed: {str(e)}")
            raise

# Enterprise workflow templates for immediate use
ENTERPRISE_WORKFLOW_TEMPLATES = {
    "github_postman_trello_devops": {
        "name": "GitHub→Postman→Trello DevOps Pipeline",
        "description": "Complete DevOps workflow with GitHub commits, Postman testing, and Trello tracking",
        "servers": ["github", "postman", "trello"],
        "complexity": "high"
    },
    "api_documentation_pipeline": {
        "name": "API Documentation Generation Pipeline", 
        "description": "Generate and validate API documentation across multiple servers",
        "servers": ["github", "postman"],
        "complexity": "medium"
    },
    "project_automation_workflow": {
        "name": "Project Management Automation",
        "description": "Automated project tracking and status updates",
        "servers": ["trello", "github"],
        "complexity": "low"
    }
}
