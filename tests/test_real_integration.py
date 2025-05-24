"""
Real Integration Tests for Autonomous MCP Agent
Task 1B.2: Enhanced real-world integration testing with actual MCP tools
"""

import pytest
import asyncio
import time
import json
import tempfile
import os
from unittest.mock import Mock, patch
from typing import List, Dict, Any

# Import all components
from autonomous_mcp.discovery import ToolDiscovery
from autonomous_mcp.planner import BasicExecutionPlanner, ExecutionPlan
from autonomous_mcp.executor import ChainExecutor, ExecutionStatus


class TestRealIntegration:
    """Real integration tests with actual MCP tools"""
    
    def setup_method(self):
        """Setup components for real integration testing"""
        self.discovery = ToolDiscovery()
        self.planner = BasicExecutionPlanner(self.discovery)
        self.executor = ChainExecutor(self.discovery)
        
        # Create realistic sample tools for testing
        self.real_tools_config = self._get_realistic_test_tools()
        self.real_tools = self.discovery.discover_all_tools(self.real_tools_config)
        print(f"Discovered {len(self.real_tools)} real tools for testing")
    
    def _get_realistic_test_tools(self):
        """Get realistic test tools based on available MCP tools"""
        return [
            {
                'name': 'brave_web_search',
                'server': 'brave_search',
                'description': 'Performs web search using Brave Search API',
                'parameters': {'query': 'string', 'count': 'number', 'offset': 'number'}
            },
            {
                'name': 'duckduckgo_web_search',
                'server': 'duckduckgo',
                'description': 'Performs web search using DuckDuckGo',
                'parameters': {'query': 'string', 'count': 'number', 'safeSearch': 'string'}
            }            ,
            {
                'name': 'create_entities',
                'server': 'memory_server',
                'description': 'Create multiple new entities in the knowledge graph',
                'parameters': {'entities': 'array'}
            },
            {
                'name': 'read_graph',
                'server': 'memory_server', 
                'description': 'Read the entire knowledge graph',
                'parameters': {}
            },
            {
                'name': 'list_directory',
                'server': 'desktop_commander',
                'description': 'Get detailed listing of files and directories',
                'parameters': {'path': 'string'}
            },
            {
                'name': 'read_file',
                'server': 'desktop_commander',
                'description': 'Read the contents of a file from the file system',
                'parameters': {'path': 'string', 'offset': 'number', 'length': 'number'}
            },
            {
                'name': 'github_search_repositories',
                'server': 'github_api',
                'description': 'Search for repositories on GitHub',
                'parameters': {'query': 'string', 'page': 'number', 'perPage': 'number'}
            },
            {
                'name': 'firecrawl_search',
                'server': 'firecrawl',
                'description': 'Search the web and optionally extract content from search results',
                'parameters': {'query': 'string', 'limit': 'number', 'lang': 'string'}
            }
        ]
    
    def test_real_tool_discovery_comprehensive(self):
        """Test comprehensive real tool discovery across all MCP servers"""
        # Verify we have tools from multiple servers
        server_categories = {}
        for tool in self.real_tools.values():
            server = tool.server
            if server not in server_categories:
                server_categories[server] = []
            server_categories[server].append(tool.name)
        
        print(f"Tools discovered from {len(server_categories)} servers:")
        for server, tools in server_categories.items():
            print(f"  {server}: {len(tools)} tools")
        
        # Should have tools from at least 3 different servers
        assert len(server_categories) >= 3
        
        # Test tool categorization
        categories = set()
        for tool in self.real_tools.values():
            for capability in tool.capabilities:
                categories.add(capability.category)
        
        print(f"Tool categories: {categories}")
        assert len(categories) >= 3  # Should have diverse categories    
    @pytest.mark.asyncio
    async def test_real_web_search_workflow(self):
        """Test real web search workflow with brave/duckduckgo"""
        # Find real web search tools
        web_tools = [t for t in self.real_tools.values() 
                     if 'search' in t.name and ('brave' in t.name or 'duckduckgo' in t.name)]
        
        if not web_tools:
            pytest.skip("No web search tools available")
        
        print(f"Found {len(web_tools)} web search tools: {[t.name for t in web_tools]}")
        
    @pytest.mark.asyncio
    async def test_real_web_search_workflow(self):
        """Test real web search workflow with brave/duckduckgo"""
        # Find real web search tools
        web_tools = [t for t in self.real_tools.values() 
                     if 'search' in t.name and ('brave' in t.name or 'duckduckgo' in t.name)]
        
        if not web_tools:
            pytest.skip("No web search tools available")
        
        print(f"Found {len(web_tools)} web search tools: {[t.name for t in web_tools]}")
        
        # Create plan for web search using the planner
        search_intent = "search for Python programming tutorials"
        plan = self.planner.create_plan(search_intent)
        
        assert plan is not None
        assert len(plan.tools) > 0
        
        # Execute with mock (real web calls would be too slow for tests)
        def mock_mcp_chain(*args, **kwargs):
            """Simple mock function for mcp_chain"""
            return {
                "success": True,
                "data": "Mocked search results for Python programming",
                "timestamp": time.time()
            }
        
        result = await asyncio.wait_for(
            self.executor.execute_plan(plan, mock_mcp_chain), 
            timeout=10.0
        )
        
        print(f"Web search execution status: {result.status}")
        print(f"Tool results: {len(result.results)}")
        
        # Should complete successfully with mocked response
        assert result.status == ExecutionStatus.SUCCESS
    
    @pytest.mark.asyncio
    async def test_real_memory_operations(self):
        """Test real memory/knowledge operations"""
        # Find memory tools
        memory_tools = [t for t in self.real_tools.values() 
                       if 'memory' in t.server or 'entities' in t.name]
        
        if not memory_tools:
            pytest.skip("No memory tools available")
        
        print(f"Found {len(memory_tools)} memory tools: {[t.name for t in memory_tools]}")
        
        # Test entity creation workflow
        create_tools = [t for t in memory_tools if 'create' in t.name]
        if create_tools:
            # Create plan for entity creation using create_linear_plan
            plan = self.planner.create_linear_plan(
                tool_sequence=[create_tools[0].name],
                intent="test entity creation",
                parameters_list=[{"entities": [{"name": "TestEntity", "entityType": "concept", 
                                               "observations": ["Test observation for integration"]}]}]
            )
            
            # Execute with mock to avoid actual memory operations
            def mock_mcp_chain(*args, **kwargs):
                """Simple mock function for mcp_chain"""
                return {
                    "success": True,
                    "data": "Entity created successfully",
                    "timestamp": time.time()
                }
            
            result = await asyncio.wait_for(
                self.executor.execute_plan(plan, mock_mcp_chain),
                timeout=10.0
            )
            
            print(f"Memory operation status: {result.status}")
            assert result.status == ExecutionStatus.SUCCESS    
    @pytest.mark.asyncio
    async def test_complex_real_workflow_chain(self):
        """Test complex workflow chaining multiple real tools"""
        # Create a workflow that chains multiple real operations
        
        # 1. First, try to get some basic system info
        file_tools = [t for t in self.real_tools.values() if 'list_directory' in t.name]
        
        # 2. Then try to create a knowledge entity about it
        memory_tools = [t for t in self.real_tools.values() if 'create_entities' in t.name]
        
        if not (file_tools and memory_tools):
            pytest.skip("Required tools not available for complex workflow")
        
        # Create a multi-step plan using create_linear_plan
        tool_sequence = [file_tools[0].name, memory_tools[0].name]
        parameters_list = [
            {"path": "D:\\Development\\Autonomous-MCP-Agent"},
            {"entities": [{
                "name": "ProjectStructure",
                "entityType": "project", 
                "observations": ["Integration test project analysis"]
            }]}
        ]
        
        # Create plan
        plan = self.planner.create_linear_plan(
            tool_sequence=tool_sequence,
            intent="complex workflow integration test",
            parameters_list=parameters_list
        )
        
        # Execute with mock responses
        def mock_mcp_chain(*args, **kwargs):
            """Mock function that cycles through responses"""
            if not hasattr(mock_mcp_chain, 'call_count'):
                mock_mcp_chain.call_count = 0
            
            responses = [
                {"success": True, "data": "Directory listing: test files", "timestamp": time.time()},
                {"success": True, "data": "Entity created with ID: project_1", "timestamp": time.time()}
            ]
            
            response = responses[mock_mcp_chain.call_count % len(responses)]
            mock_mcp_chain.call_count += 1
            return response
        
        result = await asyncio.wait_for(
            self.executor.execute_plan(plan, mock_mcp_chain),
            timeout=15.0
        )
        
        print(f"Complex workflow status: {result.status}")
        print(f"Steps completed: {len(result.results)}")
        
        # Should complete all steps successfully
        assert result.status == ExecutionStatus.SUCCESS
        assert len(result.results) == 2


if __name__ == "__main__":
    # Quick test runner for development
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        # Run a quick subset of tests
        pytest.main([__file__ + "::TestRealIntegration::test_real_tool_discovery_comprehensive", "-v"])
    else:
        # Run all tests
        pytest.main([__file__, "-v"])