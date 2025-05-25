"""
Phase 7.3: Advanced Cross-Server Workflow Orchestration

This module implements sophisticated workflow orchestration spanning multiple MCP servers,
including intelligent server selection, load balancing, and complex dependency management.
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Set, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict

try:
    from .multi_server_discovery import get_client_manager, get_tool_registry, ServerConnection
    from .multi_server_executor import get_multi_server_executor, WorkflowStep, ToolExecutionResult
    from .workflow_builder import WorkflowBuilder, AdvancedWorkflowStep
except ImportError:
    # Fallback for standalone testing
    pass


class SimpleDiGraph:
    """Simple directed graph implementation to replace NetworkX dependency"""
    
    def __init__(self):
        self.nodes_data = {}
        self.edges_data = defaultdict(set)
        self.predecessors_data = defaultdict(set)
    
    def add_node(self, node, **attrs):
        self.nodes_data[node] = attrs
    
    def add_edge(self, from_node, to_node):
        self.edges_data[from_node].add(to_node)
        self.predecessors_data[to_node].add(from_node)
    
    @property
    def nodes(self):
        return self.nodes_data
    
    @property
    def edges(self):
        edges = []
        for from_node, to_nodes in self.edges_data.items():
            for to_node in to_nodes:
                edges.append((from_node, to_node))
        return edges
    
    def predecessors(self, node):
        return list(self.predecessors_data[node])
    
    def topological_sort(self):
        """Simple topological sort implementation"""
        in_degree = defaultdict(int)
        for node in self.nodes_data:
            in_degree[node] = len(self.predecessors_data[node])
        
        queue = [node for node in self.nodes_data if in_degree[node] == 0]
        result = []
        
        while queue:
            node = queue.pop(0)
            result.append(node)
            
            for successor in self.edges_data[node]:
                in_degree[successor] -= 1
                if in_degree[successor] == 0:
                    queue.append(successor)
        
        return result


class ServerLoadStatus(Enum):
    """Server load status levels"""
    IDLE = "idle"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    OVERLOADED = "overloaded"


@dataclass
class ServerLoadMetrics:
    """Metrics for server load and performance"""
    server_name: str
    current_load: ServerLoadStatus = ServerLoadStatus.IDLE
    active_tasks: int = 0
    queue_length: int = 0
    avg_response_time: float = 0.0
    success_rate: float = 1.0
    last_updated: float = field(default_factory=time.time)
    capacity_score: float = 1.0  # 0.0 to 1.0, higher is better


@dataclass
class WorkflowExecutionPlan:
    """Execution plan for cross-server workflows"""
    workflow_id: str
    total_steps: int
    execution_stages: List[List[str]]  # Steps grouped by execution stage
    server_assignments: Dict[str, str]  # step_id -> server_name
    dependency_graph: SimpleDiGraph
    estimated_total_time: float
    resource_requirements: Dict[str, Any]
    optimization_score: float


@dataclass
class CrossServerTask:
    """Task that spans multiple servers"""
    task_id: str
    description: str
    required_servers: List[str]
    workflow_steps: List[WorkflowStep]
    priority: int = 1  # 1-10, higher is more urgent
    deadline: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    estimated_duration: float = 0.0


class CrossServerWorkflowBuilder:
    """Build workflows spanning multiple MCP servers"""
    
    def __init__(self):
        """Initialize cross-server workflow builder"""
        self.logger = logging.getLogger(__name__)
        self.client_manager = get_client_manager()
        self.tool_registry = get_tool_registry()
        self.executor = get_multi_server_executor()
        self.workflow_builder = WorkflowBuilder()
        
        # Server capability mapping
        self.server_capabilities = {}
        self.server_load_metrics = {}
        
        # Workflow optimization
        self.execution_plans = {}
        self.optimization_cache = {}
        
        self.logger.info("Cross-server workflow builder initialized")
    
    async def analyze_workflow_requirements(self, task_description: str) -> Dict[str, Any]:
        """
        Determine which servers needed for task
        
        Args:
            task_description: Description of the task to analyze
            
        Returns:
            Analysis of workflow requirements including needed servers and tools
        """
        self.logger.info(f"Analyzing workflow requirements for: {task_description}")
        
        analysis = {
            'task_description': task_description,
            'required_servers': [],
            'required_tools': [],
            'tool_mapping': {},
            'complexity_score': 0.0,
            'estimated_duration': 0.0,
            'resource_requirements': {},
            'suggested_optimizations': []
        }
        
        try:
            # Get available tools and their servers
            await self.tool_registry.update_registry_real_time()
            available_tools = self.tool_registry.tools
            
            # Analyze task for required capabilities
            required_capabilities = await self._extract_capabilities_from_description(task_description)
            
            # Map capabilities to tools and servers
            for capability in required_capabilities:
                matching_tools = await self._find_tools_for_capability(capability, available_tools)
                
                for tool_name, tool_info in matching_tools.items():
                    if tool_name not in analysis['required_tools']:
                        analysis['required_tools'].append(tool_name)
                        analysis['tool_mapping'][tool_name] = tool_info.server
                        
                        if tool_info.server not in analysis['required_servers']:
                            analysis['required_servers'].append(tool_info.server)
            
            # Calculate complexity score
            analysis['complexity_score'] = self._calculate_task_complexity(
                len(analysis['required_servers']),
                len(analysis['required_tools']),
                task_description
            )
            
            # Estimate duration
            analysis['estimated_duration'] = await self._estimate_task_duration(
                analysis['required_tools'],
                analysis['complexity_score']
            )
            
            # Analyze resource requirements
            analysis['resource_requirements'] = await self._analyze_resource_requirements(
                analysis['required_servers'],
                analysis['required_tools']
            )
            
            # Generate optimization suggestions
            analysis['suggested_optimizations'] = await self._generate_optimization_suggestions(
                analysis['required_servers'],
                analysis['complexity_score']
            )
            
            self.logger.info(f"Analysis complete: {len(analysis['required_servers'])} servers, {len(analysis['required_tools'])} tools")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Workflow analysis failed: {e}")
            analysis['error'] = str(e)
            return analysis
    
    async def optimize_server_usage(self, workflow_plan: Dict[str, Any]) -> WorkflowExecutionPlan:
        """
        Optimize workflow for performance across servers
        
        Args:
            workflow_plan: Basic workflow plan to optimize
            
        Returns:
            Optimized execution plan
        """
        self.logger.info("Optimizing server usage for workflow")
        
        try:
            # Create execution plan
            plan = WorkflowExecutionPlan(
                workflow_id=f"optimized_{int(time.time())}",
                total_steps=len(workflow_plan.get('required_tools', [])),
                execution_stages=[],
                server_assignments={},
                dependency_graph=SimpleDiGraph(),
                estimated_total_time=workflow_plan.get('estimated_duration', 0.0),
                resource_requirements=workflow_plan.get('resource_requirements', {}),
                optimization_score=0.0
            )
            
            # Update server load metrics
            await self._update_server_load_metrics()
            
            # Build dependency graph
            dependency_graph = await self._build_task_dependency_graph(workflow_plan['required_tools'])
            plan.dependency_graph = dependency_graph
            
            # Optimize server assignments
            optimized_assignments = await self._optimize_server_assignments(
                workflow_plan['required_tools'],
                workflow_plan['tool_mapping'],
                dependency_graph
            )
            plan.server_assignments = optimized_assignments
            
            # Create execution stages based on dependencies
            execution_stages = self._create_execution_stages(dependency_graph)
            plan.execution_stages = execution_stages
            
            # Calculate optimization score
            plan.optimization_score = await self._calculate_optimization_score(plan)
            
            # Store plan for future reference
            self.execution_plans[plan.workflow_id] = plan
            
            self.logger.info(f"Optimization complete: score {plan.optimization_score:.2f}")
            return plan
            
        except Exception as e:
            self.logger.error(f"Server usage optimization failed: {e}")
            raise
    
    async def build_dependency_graph(self, multi_server_workflow: List[WorkflowStep]) -> SimpleDiGraph:
        """
        Build execution graph considering server capabilities
        
        Args:
            multi_server_workflow: List of workflow steps spanning multiple servers
            
        Returns:
            Directed graph representing workflow dependencies
        """
        self.logger.info(f"Building dependency graph for {len(multi_server_workflow)} steps")
        
        graph = SimpleDiGraph()
        
        try:
            # Add nodes for each workflow step
            for step in multi_server_workflow:
                graph.add_node(step.tool_name, 
                             server=step.server,
                             parameters=step.parameters,
                             timeout=step.timeout,
                             retry_count=step.retry_count)
            
            # Add edges based on dependencies
            for step in multi_server_workflow:
                if step.depends_on:
                    for dependency in step.depends_on:
                        if dependency in [s.tool_name for s in multi_server_workflow]:
                            graph.add_edge(dependency, step.tool_name)
            
            # Add implicit server-based dependencies
            await self._add_server_dependencies(graph, multi_server_workflow)
            
            # Validate graph (check for cycles, etc.)
            # Note: For simplicity, we skip cycle detection in this implementation
            
            self.logger.info(f"Dependency graph built: {len(graph.nodes)} nodes, {len(graph.edges)} edges")
            return graph
            
        except Exception as e:
            self.logger.error(f"Dependency graph building failed: {e}")
            raise
    
    # Helper methods for workflow analysis
    
    async def _extract_capabilities_from_description(self, description: str) -> List[str]:
        """Extract required capabilities from task description"""
        description_lower = description.lower()
        
        capabilities = []
        
        # Map keywords to capabilities
        capability_keywords = {
            'search': ['search', 'find', 'query', 'lookup'],
            'web_scraping': ['scrape', 'crawl', 'fetch', 'extract web'],
            'file_management': ['file', 'directory', 'folder', 'read', 'write'],
            'github': ['github', 'repository', 'repo', 'code', 'commit'],
            'api_testing': ['api', 'postman', 'test', 'endpoint'],
            'project_management': ['task', 'project', 'trello', 'board'],
            'memory': ['memory', 'knowledge', 'store', 'remember'],
            'browser_automation': ['browser', 'website', 'click', 'navigate'],
            'documentation': ['document', 'docs', 'library', 'reference']
        }
        
        for capability, keywords in capability_keywords.items():
            if any(keyword in description_lower for keyword in keywords):
                capabilities.append(capability)
        
        if not capabilities:
            capabilities.append('general')
        
        return capabilities
    
    async def _find_tools_for_capability(self, capability: str, available_tools: Dict) -> Dict:
        """Find tools that provide a specific capability"""
        matching_tools = {}
        
        # Capability to tool mapping
        capability_tools = {
            'search': ['brave_web_search', 'duckduckgo_web_search', 'search_repositories', 'search_nodes'],
            'web_scraping': ['firecrawl_scrape', 'firecrawl_crawl', 'firecrawl_search'],
            'file_management': ['read_file', 'write_file', 'list_directory', 'search_files'],
            'github': ['search_repositories', 'create_repository', 'get_file_contents'],
            'api_testing': ['list_workspaces', 'create_collection', 'get_workspace'],
            'project_management': ['get_lists', 'add_card_to_list', 'get_cards_by_list_id'],
            'memory': ['create_entities', 'search_nodes', 'read_graph'],
            'browser_automation': ['puppeteer_navigate', 'puppeteer_click', 'puppeteer_screenshot'],
            'documentation': ['resolve-library-id', 'get-library-docs']
        }
        
        tool_names = capability_tools.get(capability, [])
        
        for tool_name in tool_names:
            if tool_name in available_tools:
                matching_tools[tool_name] = available_tools[tool_name]
        
        return matching_tools
    
    def _calculate_task_complexity(self, server_count: int, tool_count: int, description: str) -> float:
        """Calculate complexity score for a task"""
        # Base complexity from server and tool count
        base_complexity = (server_count * 0.3) + (tool_count * 0.2)
        
        # Adjust based on description keywords
        complexity_keywords = {
            'complex': 0.5, 'advanced': 0.4, 'comprehensive': 0.6,
            'multiple': 0.3, 'parallel': 0.4, 'concurrent': 0.4,
            'analysis': 0.3, 'processing': 0.3, 'workflow': 0.2
        }
        
        description_lower = description.lower()
        keyword_complexity = sum(
            weight for keyword, weight in complexity_keywords.items()
            if keyword in description_lower
        )
        
        return min(base_complexity + keyword_complexity, 10.0)
    
    async def _estimate_task_duration(self, required_tools: List[str], complexity_score: float) -> float:
        """Estimate task duration based on tools and complexity"""
        # Base duration per tool
        base_duration_per_tool = 15.0  # seconds
        
        # Tool-specific duration modifiers
        tool_durations = {
            'firecrawl_crawl': 60.0,
            'firecrawl_deep_research': 120.0,
            'search_repositories': 10.0,
            'create_entities': 5.0,
            'puppeteer_navigate': 8.0
        }
        
        total_duration = 0.0
        for tool in required_tools:
            tool_duration = tool_durations.get(tool, base_duration_per_tool)
            total_duration += tool_duration
        
        # Apply complexity multiplier
        complexity_multiplier = 1.0 + (complexity_score / 10.0)
        
        return total_duration * complexity_multiplier
    
    async def _analyze_resource_requirements(self, required_servers: List[str], required_tools: List[str]) -> Dict[str, Any]:
        """Analyze resource requirements for the workflow"""
        return {
            'server_count': len(required_servers),
            'tool_count': len(required_tools),
            'estimated_memory_mb': len(required_tools) * 50,  # Rough estimate
            'network_intensive': any('crawl' in tool or 'search' in tool for tool in required_tools),
            'cpu_intensive': any('analysis' in tool or 'processing' in tool for tool in required_tools),
            'concurrent_servers': min(len(required_servers), 3)  # Practical limit
        }
    
    async def _generate_optimization_suggestions(self, required_servers: List[str], complexity_score: float) -> List[str]:
        """Generate suggestions for workflow optimization"""
        suggestions = []
        
        if len(required_servers) > 3:
            suggestions.append("Consider breaking into smaller workflows to reduce server dependencies")
        
        if complexity_score > 7.0:
            suggestions.append("High complexity detected - consider adding checkpoints and error handling")
        
        suggestions.append("Use parallel execution where possible to improve performance")
        suggestions.append("Implement caching for repeated operations")
        
        return suggestions
    
    # Helper methods for server optimization
    
    async def _update_server_load_metrics(self):
        """Update load metrics for all servers"""
        for server_name in self.client_manager.servers:
            if server_name not in self.server_load_metrics:
                self.server_load_metrics[server_name] = ServerLoadMetrics(server_name=server_name)
            
            # Update metrics based on server performance
            metrics = self.server_load_metrics[server_name]
            server_performance = self.executor.server_performance.get(server_name, {})
            
            metrics.avg_response_time = server_performance.get('avg_response_time', 0.0)
            metrics.success_rate = server_performance.get('success_rate', 1.0)
            metrics.last_updated = time.time()
            
            # Calculate capacity score
            metrics.capacity_score = self._calculate_capacity_score(metrics)
    
    def _calculate_capacity_score(self, metrics: ServerLoadMetrics) -> float:
        """Calculate capacity score for a server"""
        # Base score from success rate
        score = metrics.success_rate
        
        # Adjust for response time (penalize slow responses)
        if metrics.avg_response_time > 1.0:
            score *= max(0.1, 1.0 - (metrics.avg_response_time - 1.0) / 10.0)
        
        # Adjust for current load
        load_penalties = {
            ServerLoadStatus.IDLE: 0.0,
            ServerLoadStatus.LOW: 0.05,
            ServerLoadStatus.MEDIUM: 0.15,
            ServerLoadStatus.HIGH: 0.3,
            ServerLoadStatus.OVERLOADED: 0.6
        }
        
        score *= (1.0 - load_penalties.get(metrics.current_load, 0.0))
        
        return max(0.0, min(1.0, score))
    
    async def _build_task_dependency_graph(self, required_tools: List[str]) -> SimpleDiGraph:
        """Build dependency graph for required tools"""
        graph = SimpleDiGraph()
        
        # Add all tools as nodes
        for tool in required_tools:
            graph.add_node(tool)
        
        # Add logical dependencies between tools
        tool_dependencies = {
            'search_repositories': [],
            'get_file_contents': ['search_repositories'],
            'create_entities': ['search_repositories'],
            'create_collection': ['list_workspaces'],
            'add_card_to_list': ['get_lists']
        }
        
        for tool, deps in tool_dependencies.items():
            if tool in required_tools:
                for dep in deps:
                    if dep in required_tools:
                        graph.add_edge(dep, tool)
        
        return graph
    
    async def _optimize_server_assignments(self, tools: List[str], tool_mapping: Dict[str, str], 
                                         dependency_graph: SimpleDiGraph) -> Dict[str, str]:
        """Optimize server assignments for tools"""
        assignments = {}
        
        # Start with default mapping
        for tool in tools:
            assignments[tool] = tool_mapping.get(tool, 'unknown')
        
        # Optimize based on server capacity and dependencies
        for tool in dependency_graph.topological_sort():
            if tool in tools:
                best_server = await self._select_best_server_for_tool(tool, assignments)
                if best_server:
                    assignments[tool] = best_server
        
        return assignments
    
    async def _select_best_server_for_tool(self, tool: str, current_assignments: Dict[str, str]) -> Optional[str]:
        """Select the best server for a specific tool"""
        # Find servers that can execute this tool
        available_servers = []
        for server_name, server_info in self.client_manager.servers.items():
            if tool in server_info.tools and server_info.status == "connected":
                available_servers.append(server_name)
        
        if not available_servers:
            return None
        
        # Score servers based on capacity and current load
        server_scores = {}
        for server_name in available_servers:
            metrics = self.server_load_metrics.get(server_name)
            if metrics:
                server_scores[server_name] = metrics.capacity_score
            else:
                server_scores[server_name] = 0.5  # Default score
        
        # Return server with highest score
        return max(server_scores.items(), key=lambda x: x[1])[0]
    
    def _create_execution_stages(self, dependency_graph: SimpleDiGraph) -> List[List[str]]:
        """Create execution stages based on dependency graph"""
        stages = []
        remaining_nodes = set(dependency_graph.nodes.keys())
        
        while remaining_nodes:
            # Find nodes with no unresolved dependencies
            ready_nodes = []
            for node in remaining_nodes:
                dependencies = set(dependency_graph.predecessors(node))
                if dependencies.issubset(set().union(*stages)):
                    ready_nodes.append(node)
            
            if not ready_nodes:
                # If no nodes are ready, take nodes with fewest dependencies
                ready_nodes = [min(remaining_nodes, 
                                 key=lambda n: len(list(dependency_graph.predecessors(n))))]
            
            stages.append(ready_nodes)
            remaining_nodes -= set(ready_nodes)
        
        return stages
    
    async def _calculate_optimization_score(self, plan: WorkflowExecutionPlan) -> float:
        """Calculate optimization score for execution plan"""
        # Base score from server distribution
        server_count = len(set(plan.server_assignments.values()))
        distribution_score = min(1.0, server_count / len(plan.server_assignments))
        
        # Score from execution stage efficiency
        avg_stage_size = sum(len(stage) for stage in plan.execution_stages) / max(len(plan.execution_stages), 1)
        stage_score = min(1.0, avg_stage_size / 3.0)  # Target 3 tools per stage
        
        # Score from server capacity
        capacity_scores = []
        for tool, server in plan.server_assignments.items():
            metrics = self.server_load_metrics.get(server)
            if metrics:
                capacity_scores.append(metrics.capacity_score)
        
        capacity_score = sum(capacity_scores) / max(len(capacity_scores), 1)
        
        # Combined score
        return (distribution_score * 0.3 + stage_score * 0.3 + capacity_score * 0.4)
    
    async def _add_server_dependencies(self, graph: SimpleDiGraph, workflow_steps: List[WorkflowStep]):
        """Add implicit dependencies based on server capabilities"""
        # Group steps by server
        server_steps = defaultdict(list)
        for step in workflow_steps:
            server_steps[step.server].append(step.tool_name)
        
        # Add dependencies for tools that must run sequentially on same server
        sequential_tools = ['firecrawl_crawl', 'firecrawl_check_crawl_status']
        
        for server, tools in server_steps.items():
            server_sequential = [tool for tool in tools if any(seq in tool for seq in sequential_tools)]
            for i in range(len(server_sequential) - 1):
                graph.add_edge(server_sequential[i], server_sequential[i + 1])
    
    async def _resolve_circular_dependencies(self, graph: SimpleDiGraph) -> SimpleDiGraph:
        """Resolve circular dependencies in graph"""
        # Simple resolution: remove problematic edges
        # For this implementation, we'll just return the graph as-is
        # since cycle detection is complex without NetworkX
        return graph


class ServerCoordinationEngine:
    """Coordinate execution across multiple servers"""
    
    def __init__(self):
        """Initialize server coordination engine"""
        self.logger = logging.getLogger(__name__)
        self.client_manager = get_client_manager()
        self.executor = get_multi_server_executor()
        self.workflow_builder = CrossServerWorkflowBuilder()
        
        # Coordination state
        self.active_workflows = {}
        self.server_queues = defaultdict(list)
        self.coordination_metrics = {
            'workflows_executed': 0,
            'parallel_executions': 0,
            'coordination_failures': 0,
            'avg_coordination_time': 0.0
        }
        
        self.logger.info("Server coordination engine initialized")
    
    async def parallel_server_execution(self, parallel_steps: List[WorkflowStep]) -> List[ToolExecutionResult]:
        """
        Execute steps in parallel across different servers
        
        Args:
            parallel_steps: List of workflow steps to execute in parallel
            
        Returns:
            List of execution results
        """
        self.logger.info(f"Executing {len(parallel_steps)} steps in parallel across servers")
        start_time = time.time()
        
        try:
            # Create execution tasks
            execution_tasks = []
            for step in parallel_steps:
                task = self.executor.route_tool_call(step.tool_name, step.parameters)
                execution_tasks.append(task)
            
            # Execute all tasks concurrently
            results = await asyncio.gather(*execution_tasks, return_exceptions=True)
            
            # Process results
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    error_result = ToolExecutionResult(
                        success=False,
                        tool_name=parallel_steps[i].tool_name,
                        server=parallel_steps[i].server,
                        error_message=str(result),
                        execution_time=time.time() - start_time
                    )
                    processed_results.append(error_result)
                else:
                    processed_results.append(result)
            
            # Update metrics
            execution_time = time.time() - start_time
            self.coordination_metrics['parallel_executions'] += 1
            self._update_coordination_metrics('parallel_execution', execution_time)
            
            successful_count = sum(1 for r in processed_results if r.success)
            self.logger.info(f"Parallel execution completed: {successful_count}/{len(parallel_steps)} successful")
            
            return processed_results
            
        except Exception as e:
            self.logger.error(f"Parallel server execution failed: {e}")
            self.coordination_metrics['coordination_failures'] += 1
            raise
    
    async def handle_server_dependencies(self, workflow_graph: SimpleDiGraph) -> Dict[str, Any]:
        """
        Manage dependencies between different servers
        
        Args:
            workflow_graph: Directed graph representing workflow dependencies
            
        Returns:
            Coordination results and metrics
        """
        self.logger.info(f"Handling server dependencies for workflow with {len(workflow_graph.nodes)} steps")
        
        try:
            coordination_result = {
                'workflow_id': f"coord_{int(time.time())}",
                'total_steps': len(workflow_graph.nodes),
                'execution_order': [],
                'server_coordination': {},
                'dependency_resolution': {},
                'execution_results': []
            }
            
            # Analyze server distribution
            server_steps = defaultdict(list)
            for node in workflow_graph.nodes:
                node_data = workflow_graph.nodes[node]
                server = node_data.get('server', 'unknown')
                server_steps[server].append(node)
            
            coordination_result['server_coordination'] = dict(server_steps)
            
            # Create execution order respecting dependencies
            execution_order = workflow_graph.topological_sort()
            coordination_result['execution_order'] = execution_order
            
            # Execute workflow with dependency management
            executed_steps = set()
            step_results = {}
            
            for step_name in execution_order:
                # Check if dependencies are satisfied
                dependencies = list(workflow_graph.predecessors(step_name))
                unresolved_deps = [dep for dep in dependencies if dep not in executed_steps]
                
                if unresolved_deps:
                    self.logger.warning(f"Step {step_name} has unresolved dependencies: {unresolved_deps}")
                    coordination_result['dependency_resolution'][step_name] = {
                        'status': 'delayed',
                        'unresolved_dependencies': unresolved_deps
                    }
                    continue
                
                # Execute step
                node_data = workflow_graph.nodes[step_name]
                server = node_data.get('server', 'unknown')
                parameters = node_data.get('parameters', {})
                
                # Resolve parameter dependencies
                resolved_parameters = await self._resolve_parameter_dependencies(
                    parameters, step_results
                )
                
                # Execute tool
                result = await self.executor.route_tool_call(step_name, resolved_parameters)
                step_results[step_name] = result
                coordination_result['execution_results'].append(result)
                
                executed_steps.add(step_name)
                coordination_result['dependency_resolution'][step_name] = {
                    'status': 'completed',
                    'success': result.success,
                    'server': result.server
                }
                
                self.logger.info(f"Executed step {step_name} on {result.server}: {'SUCCESS' if result.success else 'FAILED'}")
            
            # Update workflow metrics
            self.coordination_metrics['workflows_executed'] += 1
            successful_steps = sum(1 for r in coordination_result['execution_results'] if r.success)
            
            self.logger.info(f"Workflow coordination completed: {successful_steps}/{len(execution_order)} steps successful")
            
            return coordination_result
            
        except Exception as e:
            self.logger.error(f"Server dependency handling failed: {e}")
            self.coordination_metrics['coordination_failures'] += 1
            raise
    
    async def coordinate_complex_workflow(self, task: CrossServerTask) -> Dict[str, Any]:
        """
        Coordinate execution of a complex multi-server task
        
        Args:
            task: Complex task spanning multiple servers
            
        Returns:
            Comprehensive coordination results
        """
        self.logger.info(f"Coordinating complex workflow: {task.description}")
        
        try:
            workflow_id = task.task_id
            self.active_workflows[workflow_id] = {
                'task': task,
                'start_time': time.time(),
                'status': 'executing',
                'current_step': 0
            }
            
            # Build workflow execution plan
            workflow_analysis = await self.workflow_builder.analyze_workflow_requirements(task.description)
            execution_plan = await self.workflow_builder.optimize_server_usage(workflow_analysis)
            
            # Build dependency graph
            dependency_graph = await self.workflow_builder.build_dependency_graph(task.workflow_steps)
            
            # Execute workflow with coordination
            coordination_results = await self.handle_server_dependencies(dependency_graph)
            
            # Execute parallel steps where possible
            parallel_groups = self._identify_parallel_groups(execution_plan.execution_stages, task.workflow_steps)
            
            for group in parallel_groups:
                if len(group) > 1:
                    parallel_results = await self.parallel_server_execution(group)
                    coordination_results['execution_results'].extend(parallel_results)
            
            # Finalize workflow
            total_time = time.time() - self.active_workflows[workflow_id]['start_time']
            self.active_workflows[workflow_id]['status'] = 'completed'
            
            final_result = {
                'workflow_id': workflow_id,
                'task_description': task.description,
                'total_execution_time': total_time,
                'execution_plan': execution_plan,
                'coordination_results': coordination_results,
                'success_rate': self._calculate_workflow_success_rate(coordination_results),
                'server_utilization': self._calculate_server_utilization(coordination_results),
                'optimization_achieved': execution_plan.optimization_score
            }
            
            self.logger.info(f"Complex workflow completed in {total_time:.2f}s with {final_result['success_rate']:.1%} success rate")
            
            return final_result
            
        except Exception as e:
            self.logger.error(f"Complex workflow coordination failed: {e}")
            if workflow_id in self.active_workflows:
                self.active_workflows[workflow_id]['status'] = 'failed'
            raise
    
    # Helper methods
    
    async def _resolve_parameter_dependencies(self, parameters: Dict[str, Any], 
                                            step_results: Dict[str, ToolExecutionResult]) -> Dict[str, Any]:
        """Resolve parameter dependencies from previous step results"""
        resolved = parameters.copy()
        
        for key, value in parameters.items():
            if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                dependency_ref = value[2:-1]
                
                if "." in dependency_ref:
                    step_name, field = dependency_ref.split(".", 1)
                    if step_name in step_results and step_results[step_name].success:
                        result_data = step_results[step_name].result
                        if isinstance(result_data, dict) and field in result_data:
                            resolved[key] = result_data[field]
                        else:
                            resolved[key] = result_data
                else:
                    if dependency_ref in step_results and step_results[dependency_ref].success:
                        resolved[key] = step_results[dependency_ref].result
        
        return resolved
    
    def _identify_parallel_groups(self, execution_stages: List[List[str]], 
                                workflow_steps: List[WorkflowStep]) -> List[List[WorkflowStep]]:
        """Identify groups of steps that can be executed in parallel"""
        parallel_groups = []
        
        # Create step lookup
        step_lookup = {step.tool_name: step for step in workflow_steps}
        
        for stage in execution_stages:
            if len(stage) > 1:
                # Multiple steps in stage can be executed in parallel
                parallel_group = [step_lookup[step_name] for step_name in stage if step_name in step_lookup]
                if len(parallel_group) > 1:
                    parallel_groups.append(parallel_group)
        
        return parallel_groups
    
    def _calculate_workflow_success_rate(self, coordination_results: Dict[str, Any]) -> float:
        """Calculate success rate for workflow execution"""
        results = coordination_results.get('execution_results', [])
        if not results:
            return 0.0
        
        successful = sum(1 for r in results if r.success)
        return successful / len(results)
    
    def _calculate_server_utilization(self, coordination_results: Dict[str, Any]) -> Dict[str, float]:
        """Calculate utilization metrics for servers"""
        server_usage = defaultdict(int)
        results = coordination_results.get('execution_results', [])
        
        for result in results:
            if result.server:
                server_usage[result.server] += 1
        
        total_calls = sum(server_usage.values())
        if total_calls == 0:
            return {}
        
        return {server: count / total_calls for server, count in server_usage.items()}
    
    def _update_coordination_metrics(self, operation_type: str, execution_time: float):
        """Update coordination metrics"""
        current_avg = self.coordination_metrics['avg_coordination_time']
        executions = self.coordination_metrics['workflows_executed'] + self.coordination_metrics['parallel_executions']
        
        if executions > 0:
            self.coordination_metrics['avg_coordination_time'] = (
                (current_avg * (executions - 1) + execution_time) / executions
            )
        else:
            self.coordination_metrics['avg_coordination_time'] = execution_time
    
    def get_coordination_summary(self) -> Dict[str, Any]:
        """Get comprehensive coordination summary"""
        return {
            'coordination_metrics': self.coordination_metrics,
            'active_workflows': len(self.active_workflows),
            'server_queue_lengths': {server: len(queue) for server, queue in self.server_queues.items()},
            'workflow_statuses': {
                workflow_id: info['status'] 
                for workflow_id, info in self.active_workflows.items()
            }
        }


# Global instances
_cross_server_workflow_builder = None
_server_coordination_engine = None

def get_cross_server_workflow_builder() -> CrossServerWorkflowBuilder:
    """Get global cross-server workflow builder instance"""
    global _cross_server_workflow_builder
    if _cross_server_workflow_builder is None:
        _cross_server_workflow_builder = CrossServerWorkflowBuilder()
    return _cross_server_workflow_builder

def get_server_coordination_engine() -> ServerCoordinationEngine:
    """Get global server coordination engine instance"""
    global _server_coordination_engine
    if _server_coordination_engine is None:
        _server_coordination_engine = ServerCoordinationEngine()
    return _server_coordination_engine
