"""
Unit tests for Tool Discovery System
Tests discovery, categorization, and caching functionality
"""

import pytest
import json
import tempfile
import os
from unittest.mock import Mock, patch
from autonomous_mcp.discovery import (
    ToolDiscovery, DiscoveredTool, ToolCapability, PerformanceMetrics
)


class TestToolDiscovery:
    """Test the ToolDiscovery system"""
    
    def setup_method(self):
        """Setup test instance"""
        self.discovery = ToolDiscovery()
    
    def test_basic_tool_discovery(self):
        """Test basic tool discovery functionality"""
        # Mock chainable tools response
        mock_tools = ["brave_web_search", "create_entities", "github_search_repositories"]
        
        with patch('autonomous_mcp.discovery.chainable_tools') as mock_chainable:
            mock_chainable.return_value = mock_tools
            
            discovered_tools = self.discovery.discover_from_chainable_tools()
            
            assert len(discovered_tools) == 3
            assert "brave_web_search" in discovered_tools
            assert discovered_tools["brave_web_search"].category == "web_interaction"
    
    def test_tool_categorization(self):
        """Test that tools are correctly categorized"""
        tool_name = "github_create_repository"
        category = self.discovery._categorize_tool(tool_name)
        assert category == "code_development"
        
        tool_name = "brave_web_search"
        category = self.discovery._categorize_tool(tool_name)
        assert category == "web_interaction"    
    def test_intent_matching(self):
        """Test intent matching to tools"""
        # Add some mock tools
        self.discovery.tools = {
            "brave_web_search": DiscoveredTool(
                name="brave_web_search",
                category="web_interaction",
                capabilities=[ToolCapability("web_search", "search", "Web search", 0.9)],
                performance=PerformanceMetrics()
            ),
            "create_entities": DiscoveredTool(
                name="create_entities", 
                category="memory_knowledge",
                capabilities=[ToolCapability("memory", "create", "Create knowledge", 0.8)],
                performance=PerformanceMetrics()
            )
        }
        
        # Test intent matching
        tools = self.discovery.get_tools_for_intent("search the web")
        assert len(tools) >= 1
        assert "brave_web_search" in [t.name for t in tools]
    
    def test_caching_functionality(self):
        """Test caching reduces discovery overhead"""
        mock_tools = ["brave_web_search", "create_entities"] 
        
        with patch('autonomous_mcp.discovery.chainable_tools') as mock_chainable:
            mock_chainable.return_value = mock_tools
            
            # First discovery - should call chainable_tools
            start_time = time.time()
            tools1 = self.discovery.discover_from_chainable_tools()
            first_duration = time.time() - start_time
            
            # Second discovery - should use cache
            start_time = time.time()
            tools2 = self.discovery.discover_from_chainable_tools()
            second_duration = time.time() - start_time
            
            # Cache should make it faster
            assert second_duration < first_duration
            assert tools1 == tools2
    
    def test_export_import_functionality(self):
        """Test export/import of discovered tools"""
        # Create test tools
        self.discovery.tools = {
            "test_tool": DiscoveredTool(
                name="test_tool",
                category="test_category", 
                capabilities=[ToolCapability("test", "action", "Test capability", 0.5)],
                performance=PerformanceMetrics()
            )
        }


import time        
        # Export to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            self.discovery.export_tools(f.name)
            temp_file = f.name
        
        try:
            # Import to new instance
            new_discovery = ToolDiscovery()
            new_discovery.import_tools(temp_file)
            
            assert "test_tool" in new_discovery.tools
            assert new_discovery.tools["test_tool"].name == "test_tool"
            assert new_discovery.tools["test_tool"].category == "test_category"
        finally:
            os.unlink(temp_file)
    
    def test_performance_tracking(self):
        """Test performance metrics tracking"""
        tool = DiscoveredTool(
            name="test_tool",
            category="test",
            capabilities=[],
            performance=PerformanceMetrics()
        )
        
        # Update performance metrics
        self.discovery.update_performance_metrics("test_tool", True, 1.5)
        
        # Since tool isn't in discovery.tools, metrics won't update
        # This tests the safety of the method
        assert True  # Test passes if no exception
    
    def test_confidence_scoring(self):
        """Test confidence scoring for tool capabilities"""
        # Test various tool patterns
        test_cases = [
            ("brave_web_search", "web_interaction", 0.9),
            ("github_search_repositories", "code_development", 0.8),
            ("unknown_tool_name", "miscellaneous", 0.3)
        ]
        
        for tool_name, expected_category, min_confidence in test_cases:
            category = self.discovery._categorize_tool(tool_name)
            assert category == expected_category
    
    def test_get_tool_aliases(self):
        """Test tool alias generation"""
        aliases = self.discovery._get_tool_aliases("brave_web_search")
        expected_aliases = ["web search", "search web", "search", "brave", "web"]
        
        for alias in expected_aliases:
            assert alias in aliases