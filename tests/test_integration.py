"""
Integration Tests for Autonomous MCP Agent
Task 1.4: End-to-end testing of Discovery + Planner + Executor components

This module tests the complete autonomous workflow:
1. Tool discovery from available MCP servers
2. Execution plan creation from user intent  
3. Chain execution with real MCP tool calls
4. Performance benchmarking and error handling
"""

import pytest
import asyncio
import time
import json
from unittest.mock import Mock, patch

# Import all components
from autonomous_mcp.discovery import ToolDiscovery
from autonomous_mcp.planner import BasicExecutionPlanner
from autonomous_mcp.executor import ChainExecutor, ExecutionStatus


class TestIntegration:
    """Integration tests for the complete autonomous agent pipeline"""
    
    def setup_method(self):
        """Setup components for integration testing"""
        self.discovery = ToolDiscovery()
        self.planner = BasicExecutionPlanner()
        self.executor = ChainExecutor()
        
        # Initialize with real tools for testing
        self.real_tools = self.discovery.discover_from_chainable_tools()
    
    def test_component_integration(self):
        """Test basic integration between components"""
        # Verify components can work together
        assert len(self.real_tools) > 0
        
        # Test planner can use discovered tools
        intent = "search for Python tutorials"
        relevant_tools = self.discovery.get_tools_for_intent(intent)
        assert len(relevant_tools) > 0
        
        # Test planner can create plans
        plan = self.planner.create_plan_from_intent(intent, relevant_tools)
        assert plan is not None
        assert len(plan.tool_calls) > 0    
    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow with real MCP tools"""
        # Define a realistic user intent
        user_intent = "search for information about Python programming"
        
        # Step 1: Discover relevant tools
        start_time = time.time()
        relevant_tools = self.discovery.get_tools_for_intent(user_intent)
        discovery_time = time.time() - start_time
        
        assert len(relevant_tools) > 0
        print(f"Discovery took {discovery_time:.3f}s, found {len(relevant_tools)} tools")
        
        # Step 2: Create execution plan
        start_time = time.time()
        plan = self.planner.create_plan_from_intent(user_intent, relevant_tools)
        planning_time = time.time() - start_time
        
        assert plan is not None
        assert len(plan.tool_calls) > 0
        print(f"Planning took {planning_time:.3f}s, created {len(plan.tool_calls)} steps")
        
        # Step 3: Execute the plan (with mocked responses to avoid external dependencies)
        with patch('autonomous_mcp.executor.mcp_chain') as mock_mcp:
            mock_mcp.return_value = {
                "success": True,
                "data": "Mocked search results for Python programming"
            }
            
            start_time = time.time()
            result = await self.executor.execute_plan(plan)
            execution_time = time.time() - start_time
            
            assert result.overall_status == ExecutionStatus.SUCCESS
            print(f"Execution took {execution_time:.3f}s, status: {result.overall_status}")
    
    def test_performance_benchmarks(self):
        """Test performance benchmarks vs manual tool selection"""
        test_intents = [
            "search the web for news",
            "create a knowledge entity",
            "search GitHub repositories",
            "get movie recommendations",
            "create a file"
        ]
        
        # Benchmark autonomous discovery vs manual selection
        autonomous_times = []
        manual_times = []
        
        for intent in test_intents:
            # Autonomous approach
            start_time = time.time()
            auto_tools = self.discovery.get_tools_for_intent(intent)
            auto_time = time.time() - start_time
            autonomous_times.append(auto_time)
            
            # Manual approach (simulated)
            start_time = time.time()
            manual_tools = [t for t in self.real_tools.values() if intent.split()[0] in t.name]
            manual_time = time.time() - start_time
            manual_times.append(manual_time)
        
        avg_auto = sum(autonomous_times) / len(autonomous_times)
        avg_manual = sum(manual_times) / len(manual_times)
        
        print(f"Average autonomous selection: {avg_auto:.4f}s")
        print(f"Average manual selection: {avg_manual:.4f}s")
        
        # Autonomous should be reasonably fast (under 100ms typically)
        assert avg_auto < 0.1    
    @pytest.mark.asyncio
    async def test_error_handling_scenarios(self):
        """Test error handling in integration scenarios"""
        # Test with invalid intent
        invalid_tools = self.discovery.get_tools_for_intent("xyz_nonexistent_capability")
        plan = self.planner.create_plan_from_intent("invalid", invalid_tools)
        
        # Should handle gracefully
        assert plan.tool_calls == [] or len(plan.tool_calls) == 0
        
        # Test execution with tool failures
        failing_plan = self.planner.create_basic_plan(
            "test_plan",
            ["nonexistent_tool"],
            [{"param": "value"}]
        )
        
        with patch('autonomous_mcp.executor.mcp_chain') as mock_mcp:
            mock_mcp.side_effect = Exception("Tool not found")
            
            result = await self.executor.execute_plan(failing_plan)
            
            # Should handle failure gracefully
            assert result.overall_status in [ExecutionStatus.FAILED, ExecutionStatus.TIMEOUT]
    
    @pytest.mark.asyncio
    async def test_complex_workflow_simulation(self):
        """Test complex workflow with multiple steps and dependencies"""
        # Simulate a complex user request
        complex_intent = "search for Python tutorials, save results, and create a summary"
        
        # Get tools that could handle this
        search_tools = [t for t in self.real_tools.values() 
                       if "search" in t.name or "web" in t.name]
        memory_tools = [t for t in self.real_tools.values()
                       if "entities" in t.name or "memory" in t.name]
        
        all_tools = search_tools + memory_tools
        
        if len(all_tools) > 0:
            # Create a multi-step plan
            plan = self.planner.create_plan_from_intent(complex_intent, all_tools[:3])
            
            assert plan is not None
            
            # Test execution with chained results
            with patch('autonomous_mcp.executor.mcp_chain') as mock_mcp:
                mock_responses = [
                    {"success": True, "data": "Search results: Python tutorial links"},
                    {"success": True, "data": "Entity created with ID: tutorial_1"},
                    {"success": True, "data": "Summary: Python tutorials overview"}
                ]
                mock_mcp.side_effect = mock_responses
                
                result = await self.executor.execute_plan(plan)
                
                # Should complete successfully
                if len(plan.tool_calls) > 0:
                    assert result.overall_status == ExecutionStatus.SUCCESS
                    assert len(result.tool_results) == len(plan.tool_calls)    
    def test_tool_discovery_coverage(self):
        """Test discovery system covers major tool categories"""
        discovered_categories = set()
        for tool in self.real_tools.values():
            discovered_categories.add(tool.category)
        
        # Should discover tools from multiple categories
        expected_categories = [
            "web_interaction", "memory_knowledge", "code_development", 
            "file_system", "data_processing"
        ]
        
        found_categories = [cat for cat in expected_categories 
                           if cat in discovered_categories]
        
        assert len(found_categories) >= 3, f"Only found {found_categories}"
        print(f"Discovered {len(discovered_categories)} categories: {discovered_categories}")
    
    def test_plan_validation_integration(self):
        """Test plan validation works across components"""
        # Create a plan with circular dependencies (should be invalid)
        invalid_plan = self.planner.create_basic_plan(
            "invalid_plan",
            ["tool_a", "tool_b", "tool_c"],
            [{"dep": None}, {"dep": None}, {"dep": None}]
        )
        
        # Add circular dependencies manually
        if len(invalid_plan.tool_calls) >= 3:
            invalid_plan.tool_calls[0].dependencies = [2]  # tool_a depends on tool_c
            invalid_plan.tool_calls[1].dependencies = [0]  # tool_b depends on tool_a
            invalid_plan.tool_calls[2].dependencies = [1]  # tool_c depends on tool_b
            
            # Validation should catch this
            is_valid, errors = invalid_plan.validate()
            assert not is_valid
            assert "circular" in str(errors).lower()
    
    def test_state_persistence_integration(self):
        """Test state persistence across components"""
        # Test discovery export/import
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            self.discovery.export_tools(f.name)
            temp_discovery = f.name
        
        try:
            new_discovery = ToolDiscovery()
            new_discovery.import_tools(temp_discovery)
            
            # Should have same tools
            assert len(new_discovery.tools) == len(self.discovery.tools)
        finally:
            os.unlink(temp_discovery)
        
        # Test plan export/import
        sample_plan = self.planner.create_basic_plan(
            "sample", ["brave_web_search"], [{"query": "test"}]
        )
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            sample_plan.export_to_file(f.name)
            temp_plan = f.name
        
        try:
            imported_plan = ExecutionPlan.import_from_file(temp_plan)
            assert imported_plan.id == sample_plan.id
            assert len(imported_plan.tool_calls) == len(sample_plan.tool_calls)
        finally:
            os.unlink(temp_plan)


import tempfile
import os
from autonomous_mcp.planner import ExecutionPlan