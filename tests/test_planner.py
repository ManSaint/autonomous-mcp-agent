"""
Unit tests for Basic Execution Planner
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
import json
import tempfile
import os
from datetime import datetime

from autonomous_mcp.planner import (
    ToolCall, ExecutionPlan, BasicExecutionPlanner
)


class TestToolCall(unittest.TestCase):
    """Test ToolCall dataclass"""
    
    def test_tool_call_creation(self):
        """Test creating a ToolCall"""
        tool = ToolCall(
            tool_name="web_search",
            tool_id="brave_web_search",
            parameters={"query": "test"},
            order=0
        )
        
        self.assertEqual(tool.tool_name, "web_search")
        self.assertEqual(tool.tool_id, "brave_web_search")
        self.assertEqual(tool.parameters, {"query": "test"})
        self.assertEqual(tool.order, 0)
        self.assertEqual(tool.dependencies, [])
        self.assertEqual(tool.timeout, 30.0)
        
    def test_tool_call_to_dict(self):
        """Test converting ToolCall to dictionary"""
        tool = ToolCall(
            tool_name="web_search",
            tool_id="brave_web_search",
            parameters={"query": "test"},
            order=0,
            dependencies=[1, 2],
            expected_output_type="web_content"
        )
        
        result = tool.to_dict()
        self.assertEqual(result['tool_name'], "web_search")
        self.assertEqual(result['dependencies'], [1, 2])
        self.assertEqual(result['expected_output_type'], "web_content")

class TestExecutionPlan(unittest.TestCase):
    """Test ExecutionPlan dataclass"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.tools = [
            ToolCall("tool1", "id1", {}, 0),
            ToolCall("tool2", "id2", {}, 1, dependencies=[0]),
            ToolCall("tool3", "id3", {}, 2, dependencies=[1])
        ]
        
    def test_execution_plan_creation(self):
        """Test creating an ExecutionPlan"""
        plan = ExecutionPlan(
            plan_id="test_001",
            intent="search and analyze",
            tools=self.tools
        )
        
        self.assertEqual(plan.plan_id, "test_001")
        self.assertEqual(plan.intent, "search and analyze")
        self.assertEqual(len(plan.tools), 3)
        self.assertIsInstance(plan.created_at, datetime)
        
    def test_get_execution_order(self):
        """Test getting tools in execution order"""
        # Create tools in wrong order
        tools = [
            ToolCall("tool3", "id3", {}, 2),
            ToolCall("tool1", "id1", {}, 0),
            ToolCall("tool2", "id2", {}, 1)
        ]
        
        plan = ExecutionPlan("test", "intent", tools)
        ordered = plan.get_execution_order()
        
        self.assertEqual(ordered[0].order, 0)
        self.assertEqual(ordered[1].order, 1)
        self.assertEqual(ordered[2].order, 2)
    def test_validate_valid_plan(self):
        """Test validating a valid plan"""
        plan = ExecutionPlan("test", "intent", self.tools)
        is_valid, errors = plan.validate()
        
        self.assertTrue(is_valid)
        self.assertEqual(errors, [])
        
    def test_validate_empty_plan(self):
        """Test validating an empty plan"""
        plan = ExecutionPlan("test", "intent", [])
        is_valid, errors = plan.validate()
        
        self.assertFalse(is_valid)
        self.assertIn("Plan has no tools", errors)
        
    def test_validate_duplicate_orders(self):
        """Test validating plan with duplicate orders"""
        tools = [
            ToolCall("tool1", "id1", {}, 0),
            ToolCall("tool2", "id2", {}, 0)  # Duplicate order
        ]
        
        plan = ExecutionPlan("test", "intent", tools)
        is_valid, errors = plan.validate()
        
        self.assertFalse(is_valid)
        self.assertIn("Duplicate execution orders found", errors)
        
    def test_validate_invalid_dependencies(self):
        """Test validating plan with invalid dependencies"""
        tools = [
            ToolCall("tool1", "id1", {}, 0, dependencies=[5])  # Invalid dep
        ]
        
        plan = ExecutionPlan("test", "intent", tools)
        is_valid, errors = plan.validate()
        
        self.assertFalse(is_valid)
        self.assertTrue(any("invalid dependency" in e for e in errors))
    def test_validate_future_dependencies(self):
        """Test validating plan with future dependencies"""
        tools = [
            ToolCall("tool1", "id1", {}, 0, dependencies=[1]),  # Future dep
            ToolCall("tool2", "id2", {}, 1)
        ]
        
        plan = ExecutionPlan("test", "intent", tools)
        is_valid, errors = plan.validate()
        
        self.assertFalse(is_valid)
        self.assertTrue(any("future step" in e for e in errors))
        
    def test_circular_dependencies(self):
        """Test detecting circular dependencies"""
        tools = [
            ToolCall("tool1", "id1", {}, 0, dependencies=[2]),
            ToolCall("tool2", "id2", {}, 1, dependencies=[0]),
            ToolCall("tool3", "id3", {}, 2, dependencies=[1])
        ]
        
        plan = ExecutionPlan("test", "intent", tools)
        is_valid, errors = plan.validate()
        
        self.assertFalse(is_valid)
        self.assertIn("Circular dependencies detected", errors)
        
    def test_plan_to_dict(self):
        """Test converting plan to dictionary"""
        plan = ExecutionPlan(
            plan_id="test_001",
            intent="search",
            tools=self.tools,
            confidence_score=0.9
        )
        
        result = plan.to_dict()
        self.assertEqual(result['plan_id'], "test_001")
        self.assertEqual(result['confidence_score'], 0.9)
        self.assertEqual(len(result['tools']), 3)
        self.assertIn('created_at', result)

class TestBasicExecutionPlanner(unittest.TestCase):
    """Test BasicExecutionPlanner class"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Mock discovery system
        self.mock_discovery = Mock()
        self.mock_discovery.tools = {
            'brave_web_search': {
                'name': 'web_search',
                'category': 'web_interaction'
            },
            'search_code': {
                'name': 'code_search',
                'category': 'code_development'
            }
        }
        
        self.planner = BasicExecutionPlanner(self.mock_discovery)
        
    def test_planner_initialization(self):
        """Test planner initialization"""
        planner = BasicExecutionPlanner()
        self.assertIsNone(planner.discovery)
        self.assertEqual(planner.plan_counter, 0)
        
    def test_create_plan_no_discovery(self):
        """Test creating plan without discovery system"""
        planner = BasicExecutionPlanner()
        
        with self.assertRaises(ValueError) as context:
            planner.create_plan("search for something")
        
        self.assertIn("Discovery system not initialized", str(context.exception))
    def test_create_plan_no_tools_found(self):
        """Test creating plan when no tools are found"""
        self.mock_discovery.get_tools_for_intent.return_value = []
        
        plan = self.planner.create_plan("unknown intent")
        
        self.assertEqual(plan.intent, "unknown intent")
        self.assertEqual(len(plan.tools), 0)
        self.assertEqual(plan.confidence_score, 0.0)
        
    def test_create_plan_with_tools(self):
        """Test creating plan with discovered tools"""
        self.mock_discovery.get_tools_for_intent.return_value = [
            ('brave_web_search', 0.9),
            ('search_code', 0.7)
        ]
        
        plan = self.planner.create_plan("search for code examples")
        
        self.assertEqual(plan.intent, "search for code examples")
        self.assertEqual(len(plan.tools), 2)
        self.assertEqual(plan.tools[0].tool_id, 'brave_web_search')
        self.assertEqual(plan.tools[1].tool_id, 'search_code')
        self.assertEqual(plan.tools[1].dependencies, [0])
        self.assertAlmostEqual(plan.confidence_score, 0.8, places=2)
        
    def test_create_linear_plan(self):
        """Test creating a linear plan from tool sequence"""
        tool_sequence = ['brave_web_search', 'search_code']
        parameters = [
            {'query': 'python examples'},
            {'pattern': 'def.*example'}
        ]
        
        plan = self.planner.create_linear_plan(
            tool_sequence, 
            "find examples",
            parameters
        )
        
        self.assertEqual(len(plan.tools), 2)
        self.assertEqual(plan.tools[0].parameters, {'query': 'python examples'})
        self.assertEqual(plan.tools[1].dependencies, [0])
        self.assertEqual(plan.confidence_score, 1.0)
    def test_create_linear_plan_empty(self):
        """Test creating linear plan with empty sequence"""
        plan = self.planner.create_linear_plan([], "empty intent")
        
        self.assertEqual(plan.intent, "empty intent")
        self.assertEqual(len(plan.tools), 0)
        
    def test_optimize_plan(self):
        """Test plan optimization"""
        tools = [
            ToolCall("tool1", "id1", {}, 0),
            ToolCall("tool2", "id2", {}, 1)
        ]
        plan = ExecutionPlan("test", "intent", tools)
        
        optimized = self.planner.optimize_plan(plan)
        
        # Currently just returns the same plan
        self.assertEqual(optimized.plan_id, plan.plan_id)
        
    def test_merge_plans(self):
        """Test merging multiple plans"""
        plan1 = ExecutionPlan("plan1", "intent1", [
            ToolCall("tool1", "id1", {}, 0),
            ToolCall("tool2", "id2", {}, 1, dependencies=[0])
        ])
        
        plan2 = ExecutionPlan("plan2", "intent2", [
            ToolCall("tool3", "id3", {}, 0),
            ToolCall("tool4", "id4", {}, 1, dependencies=[0])
        ])
        
        merged = self.planner.merge_plans([plan1, plan2], "merged intent")
        
        self.assertEqual(merged.intent, "merged intent")
        self.assertEqual(len(merged.tools), 4)
        # Check order adjustment
        self.assertEqual(merged.tools[0].order, 0)
        self.assertEqual(merged.tools[1].order, 1)
        self.assertEqual(merged.tools[2].order, 2)
        self.assertEqual(merged.tools[3].order, 3)
        # Check dependency adjustment
        self.assertEqual(merged.tools[3].dependencies, [2])
    def test_merge_empty_plans(self):
        """Test merging empty list of plans"""
        merged = self.planner.merge_plans([], "empty merge")
        
        self.assertEqual(merged.intent, "empty merge")
        self.assertEqual(len(merged.tools), 0)
        
    def test_export_import_plan(self):
        """Test exporting and importing plans"""
        tools = [
            ToolCall("web_search", "brave_web_search", {"query": "test"}, 0),
            ToolCall("analyze", "analyzer", {"data": "result"}, 1, dependencies=[0])
        ]
        
        original_plan = ExecutionPlan(
            plan_id="export_test",
            intent="test export",
            tools=tools,
            confidence_score=0.95
        )
        
        # Export to temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name
            
        try:
            # Export
            self.planner.export_plan(original_plan, temp_path)
            
            # Import
            imported_plan = self.planner.import_plan(temp_path)
            
            # Verify
            self.assertEqual(imported_plan.plan_id, original_plan.plan_id)
            self.assertEqual(imported_plan.intent, original_plan.intent)
            self.assertEqual(len(imported_plan.tools), len(original_plan.tools))
            self.assertEqual(imported_plan.confidence_score, original_plan.confidence_score)
            
            # Check tool details
            self.assertEqual(imported_plan.tools[0].tool_name, "web_search")
            self.assertEqual(imported_plan.tools[0].parameters, {"query": "test"})
            self.assertEqual(imported_plan.tools[1].dependencies, [0])
            
        finally:
            # Cleanup
            if os.path.exists(temp_path):
                os.unlink(temp_path)


if __name__ == '__main__':
    unittest.main()