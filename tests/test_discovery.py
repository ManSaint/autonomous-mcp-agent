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
    ToolDiscovery, DiscoveredTool, ToolCapability
)


class TestToolDiscovery:
    """Test the ToolDiscovery system"""
    
    def setup_method(self):
        """Setup test instance"""
        self.discovery = ToolDiscovery(cache_ttl=60)  # Short TTL for testing
    
    def test_basic_tool_discovery(self):
        """Test basic tool discovery functionality"""
        # Mock available tools
        mock_tools = [
            {
                'name': 'brave_web_search',
                'description': 'Search the web using Brave API',
                'parameters': {'properties': {'query': {'type': 'string'}}}
            },
            {
                'name': 'create_entities',
                'description': 'Create entities in knowledge graph',
                'parameters': {'properties': {'entities': {'type': 'array'}}}
            }
        ]
        
        # Test discovery
        discovered_tools = self.discovery.discover_all_tools(mock_tools)
        
        assert len(discovered_tools) == 2
        assert 'brave_web_search' in discovered_tools
        assert 'create_entities' in discovered_tools
        
        # Check tool properties
        search_tool = discovered_tools['brave_web_search']
        assert search_tool.name == 'brave_web_search'
        assert 'search' in search_tool.description.lower() or 'web' in search_tool.description.lower()
        assert len(search_tool.capabilities) > 0
    
    def test_capability_detection(self):
        """Test that capabilities are correctly detected"""
        mock_tool = {
            'name': 'github_create_repository',
            'description': 'Create a new GitHub repository',
            'parameters': {'properties': {'name': {'type': 'string'}}}
        }
        
        discovered_tools = self.discovery.discover_all_tools([mock_tool])
        tool = discovered_tools['github_create_repository']
        
        # Should detect code development capabilities
        capabilities = tool.capabilities
        assert len(capabilities) > 0
        
        # Check if any capability relates to code/development
        has_code_capability = any(
            'code' in cap.category.lower() or 'development' in cap.category.lower() 
            or 'github' in cap.description.lower()
            for cap in capabilities
        )
        assert has_code_capability
    
    def test_intent_matching(self):
        """Test intent matching to tools"""
        mock_tools = [
            {
                'name': 'brave_web_search',
                'description': 'Search the web',
                'parameters': {'properties': {'query': {'type': 'string'}}}
            },
            {
                'name': 'create_entities',
                'description': 'Create knowledge entities',
                'parameters': {'properties': {'entities': {'type': 'array'}}}
            }
        ]
        
        # Discover tools first
        self.discovery.discover_all_tools(mock_tools)
        
        # Test intent matching
        search_intent = "I need to search for information online"
        matching_tools = self.discovery.get_tools_for_intent(search_intent)
        
        assert len(matching_tools) > 0
        # Should match web search tool better
        tool_names = [tool.name for tool in matching_tools]
        assert 'brave_web_search' in tool_names
    
    def test_caching_functionality(self):
        """Test caching reduces discovery overhead"""
        mock_tools = [
            {
                'name': 'test_tool',
                'description': 'Test tool',
                'parameters': {}
            }
        ]
        
        # First discovery
        import time
        start_time = time.time()
        tools1 = self.discovery.discover_all_tools(mock_tools)
        first_duration = time.time() - start_time
        
        # Second discovery - should use cache
        start_time = time.time()
        tools2 = self.discovery.discover_all_tools(mock_tools)
        second_duration = time.time() - start_time
        
        # Results should be the same
        assert len(tools1) == len(tools2)
        assert list(tools1.keys()) == list(tools2.keys())
        
        # Second call should be faster (cached)
        assert second_duration < first_duration or second_duration < 0.001  # Very fast cache hit
    
    def test_tool_performance_update(self):
        """Test performance metrics update"""
        mock_tools = [
            {
                'name': 'test_tool',
                'description': 'Test tool',
                'parameters': {}
            }
        ]
        
        # Discover tools first
        discovered_tools = self.discovery.discover_all_tools(mock_tools)
        
        # Update performance
        self.discovery.update_tool_performance('test_tool', success=True, execution_time=1.5)
        
        # Check tool was updated
        tool = self.discovery.tools['test_tool']
        assert tool.usage_count == 1
        assert tool.success_rate == 1.0
        assert tool.average_execution_time == 1.5
        assert tool.last_used is not None
        
        # Update again with failure
        self.discovery.update_tool_performance('test_tool', success=False, execution_time=2.0)
        
        # Check updated metrics (uses exponential moving average with alpha=0.1)
        tool = self.discovery.tools['test_tool']
        assert tool.usage_count == 2
        # Success rate: 0.1 * 0 + 0.9 * 1.0 = 0.9 (exponential moving average)
        assert abs(tool.success_rate - 0.9) < 0.01  # Allow for floating point precision
        assert tool.average_execution_time > 1.5  # Should be updated average
    
    def test_export_import_functionality(self):
        """Test export/import of discovered tools"""
        mock_tools = [
            {
                'name': 'test_tool',
                'description': 'Test tool for export/import',
                'parameters': {'properties': {'param': {'type': 'string'}}}
            }
        ]
        
        # Discover tools
        self.discovery.discover_all_tools(mock_tools)
        
        # Export discoveries
        export_data = self.discovery.export_discoveries()
        
        assert 'discovered_tools' in export_data  # Actual key name
        assert 'last_discovery_time' in export_data
        assert 'test_tool' in export_data['discovered_tools']
        
        # Create new discovery instance and import
        new_discovery = ToolDiscovery()
        new_discovery.import_discoveries(export_data)
        
        # Check imported data
        assert 'test_tool' in new_discovery.tools
        imported_tool = new_discovery.tools['test_tool']
        assert imported_tool.name == 'test_tool'
        assert imported_tool.description == 'Test tool for export/import'
    
    def test_find_best_tool(self):
        """Test finding best tool for category"""
        mock_tools = [
            {
                'name': 'web_search_tool',
                'description': 'Search the web for information',
                'parameters': {}
            },
            {
                'name': 'file_reader',
                'description': 'Read file contents',
                'parameters': {}
            }
        ]
        
        # Discover tools
        self.discovery.discover_all_tools(mock_tools)
        
        # Find best tool for web interaction
        best_web_tool = self.discovery.find_best_tool('web_interaction')
        if best_web_tool:
            assert 'web' in best_web_tool.name.lower() or 'search' in best_web_tool.name.lower()
        
        # Find best tool for file operations
        best_file_tool = self.discovery.find_best_tool('file_operations')
        if best_file_tool:
            assert 'file' in best_file_tool.name.lower() or 'read' in best_file_tool.name.lower()
    
    def test_get_tool_stats(self):
        """Test getting tool statistics"""
        mock_tools = [
            {
                'name': 'tool1',
                'description': 'First tool',
                'parameters': {}
            },
            {
                'name': 'tool2',
                'description': 'Second tool',
                'parameters': {}
            }
        ]
        
        # Discover tools
        self.discovery.discover_all_tools(mock_tools)
        
        # Get stats
        stats = self.discovery.get_tool_stats()
        
        assert 'total_tools' in stats
        assert 'categories' in stats
        # Check actual keys that exist in the stats
        assert 'tools_by_category' in stats
        assert stats['total_tools'] == 2
    
    def test_categorize_by_capability(self):
        """Test categorizing tools by capability"""
        mock_tools = [
            {
                'name': 'web_tool',
                'description': 'Web search functionality',
                'parameters': {}
            },
            {
                'name': 'file_tool',
                'description': 'File operations',
                'parameters': {}
            }
        ]
        
        # Discover tools
        self.discovery.discover_all_tools(mock_tools)
        
        # Categorize by capability
        categories = self.discovery.categorize_by_capability()
        
        assert isinstance(categories, dict)
        assert len(categories) > 0
        
        # Check that tools are properly categorized
        all_categorized_tools = []
        for category_tools in categories.values():
            all_categorized_tools.extend(category_tools)
        
        assert 'web_tool' in all_categorized_tools
        assert 'file_tool' in all_categorized_tools


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
