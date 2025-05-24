"""
Basic Execution Planner for Autonomous MCP Agent
Task 1.2: Creates linear execution plans from discovered tools
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class ToolCall:
    """Represents a single tool call in an execution plan"""
    tool_name: str
    tool_id: str
    parameters: Dict[str, Any]
    order: int
    dependencies: List[int] = field(default_factory=list)
    expected_output_type: Optional[str] = None
    timeout: float = 30.0
    retry_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'tool_name': self.tool_name,
            'tool_id': self.tool_id,
            'parameters': self.parameters,
            'order': self.order,
            'dependencies': self.dependencies,
            'expected_output_type': self.expected_output_type,
            'timeout': self.timeout,
            'retry_count': self.retry_count
        }


@dataclass
class ExecutionPlan:
    """Represents a complete execution plan"""
    plan_id: str
    intent: str
    tools: List[ToolCall]
    created_at: datetime = field(default_factory=datetime.now)
    estimated_duration: float = 0.0
    confidence_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'plan_id': self.plan_id,
            'intent': self.intent,
            'tools': [tool.to_dict() for tool in self.tools],
            'created_at': self.created_at.isoformat(),
            'estimated_duration': self.estimated_duration,
            'confidence_score': self.confidence_score,
            'metadata': self.metadata
        }
    
    def get_execution_order(self) -> List[ToolCall]:
        """Get tools in execution order, respecting dependencies"""
        # Sort by order, ensuring dependencies are met
        sorted_tools = sorted(self.tools, key=lambda t: t.order)
        return sorted_tools
    
    def validate(self) -> Tuple[bool, List[str]]:
        """Validate the execution plan"""
        errors = []
        
        # Check for empty plan
        if not self.tools:
            errors.append("Plan has no tools")
        
        # Check for duplicate orders
        orders = [tool.order for tool in self.tools]
        if len(orders) != len(set(orders)):
            errors.append("Duplicate execution orders found")
        
        # Check dependencies are valid
        valid_orders = set(orders)
        for tool in self.tools:
            for dep in tool.dependencies:
                if dep not in valid_orders:
                    errors.append(f"Tool {tool.tool_name} has invalid dependency: {dep}")
                if dep >= tool.order:
                    errors.append(f"Tool {tool.tool_name} depends on future step: {dep}")
        
        # Check for circular dependencies
        if self._has_circular_dependencies():
            errors.append("Circular dependencies detected")
        
        return len(errors) == 0, errors
    
    def _has_circular_dependencies(self) -> bool:
        """Check for circular dependencies using DFS"""
        # Build adjacency list
        graph = {tool.order: tool.dependencies for tool in self.tools}
        
        # Track visited and recursion stack
        visited = set()
        rec_stack = set()
        
        def has_cycle(node: int) -> bool:
            visited.add(node)
            rec_stack.add(node)
            
            # Check all dependencies
            for dep in graph.get(node, []):
                if dep not in visited:
                    if has_cycle(dep):
                        return True
                elif dep in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        # Check each node
        for order in graph:
            if order not in visited:
                if has_cycle(order):
                    return True
        
        return False


class BasicExecutionPlanner:
    """Creates linear execution plans from discovered tools"""
    
    def __init__(self, discovery_system=None):
        """
        Initialize the planner
        
        Args:
            discovery_system: Instance of ToolDiscoverySystem for tool selection
        """
        self.discovery = discovery_system
        self.plan_counter = 0
        
    def create_plan(self, intent: str, context: Dict[str, Any] = None) -> ExecutionPlan:
        """
        Create an execution plan for the given intent
        
        Args:
            intent: User's intended action
            context: Additional context for planning
            
        Returns:
            ExecutionPlan instance
        """
        if not self.discovery:
            raise ValueError("Discovery system not initialized")
        
        # Get relevant tools from discovery system
        tools_info = self.discovery.get_tools_for_intent(intent)
        
        if not tools_info:
            logger.warning(f"No tools found for intent: {intent}")
            return self._create_empty_plan(intent)
        
        # Create tool calls from discovered tools
        tool_calls = []
        for i, discovered_tool in enumerate(tools_info):
            # discovered_tool is a DiscoveredTool object
            tool_id = discovered_tool.name
            
            # Calculate confidence from the tool's capabilities
            confidence = max(cap.confidence for cap in discovered_tool.capabilities) if discovered_tool.capabilities else 0.5
            
            # Create tool info dict for helper methods
            tool_info_dict = {
                'name': discovered_tool.name,
                'server': discovered_tool.server,
                'description': discovered_tool.description,
                'parameters': discovered_tool.parameters,
                'category': discovered_tool.capabilities[0].category if discovered_tool.capabilities else 'unknown'
            }
            
            # Create basic parameters based on context
            parameters = self._generate_parameters(tool_info_dict, intent, context)
            
            tool_call = ToolCall(
                tool_name=discovered_tool.name,
                tool_id=tool_id,
                parameters=parameters,
                order=i,
                dependencies=self._determine_dependencies(i, tool_calls),
                expected_output_type=self._infer_output_type(tool_info_dict)
            )
            
            tool_calls.append(tool_call)
        
        # Create the plan
        plan_id = f"plan_{self.plan_counter:04d}"
        self.plan_counter += 1
        
        plan = ExecutionPlan(
            plan_id=plan_id,
            intent=intent,
            tools=tool_calls,
            confidence_score=self._calculate_plan_confidence(tools_info),
            estimated_duration=self._estimate_duration(tool_calls),
            metadata={'context': context or {}}
        )
        
        # Validate the plan
        is_valid, errors = plan.validate()
        if not is_valid:
            logger.error(f"Plan validation failed: {errors}")
            plan.metadata['validation_errors'] = errors
        
        return plan
    
    def create_linear_plan(self, tool_sequence: List[str], intent: str, 
                          parameters_list: List[Dict[str, Any]] = None) -> ExecutionPlan:
        """
        Create a linear execution plan from a specific sequence of tools
        
        Args:
            tool_sequence: List of tool IDs in execution order
            intent: User's intended action
            parameters_list: Optional list of parameters for each tool
            
        Returns:
            ExecutionPlan instance
        """
        if not tool_sequence:
            return self._create_empty_plan(intent)
        
        tool_calls = []
        for i, tool_id in enumerate(tool_sequence):
            # Get parameters for this tool
            params = {}
            if parameters_list and i < len(parameters_list):
                params = parameters_list[i]
            
            # Look up tool info if discovery system is available
            tool_info = {}
            if self.discovery and tool_id in self.discovery.tools:
                tool_info = self.discovery.tools[tool_id]
            
            tool_call = ToolCall(
                tool_name=tool_info.get('name', tool_id),
                tool_id=tool_id,
                parameters=params,
                order=i,
                dependencies=[i-1] if i > 0 else [],  # Linear dependency
                expected_output_type=self._infer_output_type(tool_info)
            )
            
            tool_calls.append(tool_call)
        
        # Create the plan
        plan_id = f"plan_{self.plan_counter:04d}"
        self.plan_counter += 1
        
        plan = ExecutionPlan(
            plan_id=plan_id,
            intent=intent,
            tools=tool_calls,
            confidence_score=1.0,  # Explicit plan has high confidence
            estimated_duration=self._estimate_duration(tool_calls)
        )
        
        return plan
    
    def optimize_plan(self, plan: ExecutionPlan) -> ExecutionPlan:
        """
        Optimize an execution plan by reordering independent steps
        
        Args:
            plan: ExecutionPlan to optimize
            
        Returns:
            Optimized ExecutionPlan
        """
        # For now, just validate and return
        # Future: implement parallel execution detection
        is_valid, errors = plan.validate()
        if not is_valid:
            logger.warning(f"Cannot optimize invalid plan: {errors}")
        
        return plan
    
    def merge_plans(self, plans: List[ExecutionPlan], intent: str) -> ExecutionPlan:
        """
        Merge multiple plans into a single execution plan
        
        Args:
            plans: List of ExecutionPlans to merge
            intent: Overall intent for merged plan
            
        Returns:
            Merged ExecutionPlan
        """
        if not plans:
            return self._create_empty_plan(intent)
        
        # Collect all tools and adjust orders
        merged_tools = []
        offset = 0
        
        for plan in plans:
            for tool in plan.tools:
                # Create new tool with adjusted order and dependencies
                new_tool = ToolCall(
                    tool_name=tool.tool_name,
                    tool_id=tool.tool_id,
                    parameters=tool.parameters.copy(),
                    order=tool.order + offset,
                    dependencies=[d + offset for d in tool.dependencies],
                    expected_output_type=tool.expected_output_type,
                    timeout=tool.timeout,
                    retry_count=tool.retry_count
                )
                merged_tools.append(new_tool)
            
            # Update offset for next plan
            if plan.tools:
                offset = max(t.order for t in plan.tools) + offset + 1
        
        # Create merged plan
        plan_id = f"plan_{self.plan_counter:04d}"
        self.plan_counter += 1
        
        merged_plan = ExecutionPlan(
            plan_id=plan_id,
            intent=intent,
            tools=merged_tools,
            confidence_score=min(p.confidence_score for p in plans) if plans else 0.0,
            estimated_duration=sum(p.estimated_duration for p in plans)
        )
        
        return merged_plan
    
    def _create_empty_plan(self, intent: str) -> ExecutionPlan:
        """Create an empty execution plan"""
        plan_id = f"plan_{self.plan_counter:04d}"
        self.plan_counter += 1
        
        return ExecutionPlan(
            plan_id=plan_id,
            intent=intent,
            tools=[],
            confidence_score=0.0
        )
    
    def _generate_parameters(self, tool_info: Dict[str, Any], 
                           intent: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate parameters for a tool based on intent and context"""
        # Basic parameter generation
        # Future: Use NLP to extract parameters from intent
        params = {}
        
        # Use context if available
        if context:
            params.update(context)
        
        return params
    
    def _determine_dependencies(self, current_order: int, 
                              existing_tools: List[ToolCall]) -> List[int]:
        """Determine dependencies for a tool"""
        # For basic linear execution, depend on previous tool
        if current_order > 0:
            return [current_order - 1]
        return []
    
    def _infer_output_type(self, tool_info: Dict[str, Any]) -> Optional[str]:
        """Infer the expected output type of a tool"""
        # Check if tool info has output type
        if 'output_type' in tool_info:
            return tool_info['output_type']
        
        # Infer from category
        category = tool_info.get('category', '')
        if category == 'data_processing':
            return 'data'
        elif category == 'file_system':
            return 'file_path'
        elif category == 'web_interaction':
            return 'web_content'
        
        return None
    
    def _calculate_plan_confidence(self, tools_info: List) -> float:
        """Calculate overall confidence score for a plan"""
        if not tools_info:
            return 0.0
        
        # Calculate confidence from DiscoveredTool objects
        confidences = []
        for tool in tools_info:
            if hasattr(tool, 'capabilities') and tool.capabilities:
                # Get max confidence from capabilities
                tool_confidence = max(cap.confidence for cap in tool.capabilities)
            else:
                # Fallback confidence
                tool_confidence = 0.5
            confidences.append(tool_confidence)
        
        # Average confidence of all tools
        return sum(confidences) / len(confidences)
    
    def _estimate_duration(self, tool_calls: List[ToolCall]) -> float:
        """Estimate total execution duration"""
        # Sum of timeouts as rough estimate
        return sum(tool.timeout for tool in tool_calls)
    
    def export_plan(self, plan: ExecutionPlan, filepath: str):
        """Export a plan to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(plan.to_dict(), f, indent=2)
        logger.info(f"Exported plan to {filepath}")
    
    def import_plan(self, filepath: str) -> ExecutionPlan:
        """Import a plan from JSON file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        # Reconstruct tools
        tools = []
        for tool_data in data.get('tools', []):
            tool = ToolCall(
                tool_name=tool_data['tool_name'],
                tool_id=tool_data['tool_id'],
                parameters=tool_data['parameters'],
                order=tool_data['order'],
                dependencies=tool_data.get('dependencies', []),
                expected_output_type=tool_data.get('expected_output_type'),
                timeout=tool_data.get('timeout', 30.0),
                retry_count=tool_data.get('retry_count', 0)
            )
            tools.append(tool)
        
        # Reconstruct plan
        plan = ExecutionPlan(
            plan_id=data['plan_id'],
            intent=data['intent'],
            tools=tools,
            created_at=datetime.fromisoformat(data['created_at']),
            estimated_duration=data.get('estimated_duration', 0.0),
            confidence_score=data.get('confidence_score', 0.0),
            metadata=data.get('metadata', {})
        )
        
        logger.info(f"Imported plan from {filepath}")
        return plan
