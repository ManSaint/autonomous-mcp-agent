"""
Unit tests for the Tool Discovery System.
"""

import unittest
from unittest.mock import Mock, patch
import time
from typing import List, Dict, Any

from autonomous_mcp.discovery import (
    ToolDiscovery,
    DiscoveredTool,
    ToolCapability
)


class TestToolDiscovery(unittest.TestCase):
    """Test cases for the ToolDiscovery class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.discovery = ToolDiscovery(cache_ttl=60)
        
        # Sample tools for testing
        self.sample_tools = [
            {
                'name': 'read_file',
                'server': 'desktop_commander',
                'description': 'Read the contents of a file from the file system',
                'parameters': {'path': 'string', 'offset': 'number', 'length': 'number'}
            },
            {
                'name': 'write_file',
                'server': 'desktop_commander',
                'description': 'Write content to a file on the file system',
                'parameters': {'path': 'string', 'content': 'string'}
            },
            {
                'name': 'web_search',
                'server': 'brave_search',
                'description': 'Search the web using Brave search engine',
                'parameters': {'query': 'string', 'count': 'number'}
            },
            {
                'name': 'create_entities',
                'server': 'memory_server',
                'description': 'Create entities in the knowledge graph',
                'parameters': {'entities': 'array'}
            },
            {
                'name': 'github_create_repository',
                'server': 'github',
                'description': 'Create a new GitHub repository',
                'parameters': {'name': 'string', 'description': 'string', 'private': 'boolean'},
                'aliases': ['create_repo', 'new_repository']
            }
        ]
    
    def test_discover_all_tools(self):
        """Test discovering all tools."""
        tools = self.discovery.discover_all_tools(self.sample_tools)
        
        # Check all tools were discovered
        self.assertEqual(len(tools), 5)
        self.assertIn('read_file', tools)
        self.assertIn('web_search', tools)
        
        # Check tool properties
        read_file = tools['read_file']
        self.assertEqual(read_file.name, 'read_file')
        self.assertEqual(read_file.server, 'desktop_commander')
        self.assertIsInstance(read_file.capabilities, list)
        self.assertGreater(len(read_file.capabilities), 0)
    
    def test_capability_detection(self):
        """Test capability detection for tools."""
        self.discovery.discover_all_tools(self.sample_tools)
        
        # Check file system capabilities
        read_file = self.discovery.discovered_tools['read_file']
        file_caps = [cap for cap in read_file.capabilities if cap.category == 'file_system']
        self.assertGreater(len(file_caps), 0)
        self.assertTrue(any(cap.subcategory == 'read' for cap in file_caps))
        
        # Check web capabilities
        web_search = self.discovery.discovered_tools['web_search']
        web_caps = [cap for cap in web_search.capabilities if cap.category == 'web_interaction']
        self.assertGreater(len(web_caps), 0)
        self.assertTrue(any(cap.subcategory == 'search' for cap in web_caps))
        
        # Check memory/knowledge capabilities
        create_entities = self.discovery.discovered_tools['create_entities']
        memory_caps = [cap for cap in create_entities.capabilities if cap.category == 'memory_knowledge']
        self.assertGreater(len(memory_caps), 0)
    
    def test_categorize_by_capability(self):
        """Test categorization of tools by capability."""
        self.discovery.discover_all_tools(self.sample_tools)
        categories = self.discovery.categorize_by_capability()
        
        # Check categories exist
        self.assertIn('file_system', categories)
        self.assertIn('web_interaction', categories)
        self.assertIn('memory_knowledge', categories)
        
        # Check tools in categories
        self.assertIn('read_file', categories['file_system'])
        self.assertIn('write_file', categories['file_system'])
        self.assertIn('web_search', categories['web_interaction'])
    
    def test_get_tools_for_intent(self):
        """Test getting tools based on intent."""
        self.discovery.discover_all_tools(self.sample_tools)
        
        # Test file reading intent
        file_tools = self.discovery.get_tools_for_intent("I need to read a file")
        self.assertGreater(len(file_tools), 0)
        self.assertEqual(file_tools[0].name, 'read_file')
        
        # Test web search intent
        search_tools = self.discovery.get_tools_for_intent("search the web for information")
        self.assertGreater(len(search_tools), 0)
        self.assertEqual(search_tools[0].name, 'web_search')
        
        # Test with required capabilities
        tools_with_caps = self.discovery.get_tools_for_intent(
            "any intent",
            required_capabilities=[('file_system', 'read')]
        )
        self.assertGreater(len(tools_with_caps), 0)
        self.assertIn('read_file', [t.name for t in tools_with_caps])
    
    def test_find_best_tool(self):
        """Test finding the best tool for a capability."""
        self.discovery.discover_all_tools(self.sample_tools)
        
        # Find best file reading tool
        best_tool = self.discovery.find_best_tool('file_system', 'read')
        self.assertIsNotNone(best_tool)
        self.assertEqual(best_tool.name, 'read_file')
        
        # Find best web search tool
        best_tool = self.discovery.find_best_tool('web_interaction', 'search')
        self.assertIsNotNone(best_tool)
        self.assertEqual(best_tool.name, 'web_search')
        
        # Test non-existent capability
        best_tool = self.discovery.find_best_tool('non_existent', 'capability')
        self.assertIsNone(best_tool)
    
    def test_update_tool_performance(self):
        """Test updating tool performance metrics."""
        self.discovery.discover_all_tools(self.sample_tools)
        
        # Initial state
        tool = self.discovery.discovered_tools['read_file']
        self.assertEqual(tool.usage_count, 0)
        self.assertEqual(tool.success_rate, 1.0)
        self.assertEqual(tool.average_execution_time, 0.0)
        
        # Update with successful execution
        self.discovery.update_tool_performance('read_file', True, 0.5)
        self.assertEqual(tool.usage_count, 1)
        self.assertGreater(tool.success_rate, 0.9)  # Should still be high
        self.assertGreater(tool.average_execution_time, 0)
        self.assertIsNotNone(tool.last_used)
        
        # Update with failed execution
        self.discovery.update_tool_performance('read_file', False, 1.0)
        self.assertEqual(tool.usage_count, 2)
        self.assertLess(tool.success_rate, 0.95)  # Should decrease
    
    def test_cache_behavior(self):
        """Test caching behavior."""
        # First discovery
        tools1 = self.discovery.discover_all_tools(self.sample_tools)
        discovery_time1 = self.discovery.last_discovery_time
        
        # Second discovery without force refresh (should use cache)
        time.sleep(0.1)
        tools2 = self.discovery.discover_all_tools(self.sample_tools)
        discovery_time2 = self.discovery.last_discovery_time
        
        self.assertEqual(discovery_time1, discovery_time2)
        self.assertEqual(len(tools1), len(tools2))
        
        # Force refresh
        tools3 = self.discovery.discover_all_tools(self.sample_tools, force_refresh=True)
        discovery_time3 = self.discovery.last_discovery_time
        
        self.assertGreater(discovery_time3, discovery_time1)
    
    def test_aliases(self):
        """Test tool aliases handling."""
        self.discovery.discover_all_tools(self.sample_tools)
        
        # Check aliases were loaded
        github_tool = self.discovery.discovered_tools['github_create_repository']
        self.assertEqual(len(github_tool.aliases), 2)
        self.assertIn('create_repo', github_tool.aliases)
        
        # Test intent matching with aliases
        tools = self.discovery.get_tools_for_intent("create_repo on github")
        self.assertGreater(len(tools), 0)
        self.assertIn('github_create_repository', [t.name for t in tools])
    
    def test_export_import_discoveries(self):
        """Test exporting and importing discoveries."""
        # Discover tools and update some metrics
        self.discovery.discover_all_tools(self.sample_tools)
        self.discovery.update_tool_performance('read_file', True, 0.5)
        self.discovery.update_tool_performance('web_search', True, 1.2)
        
        # Export discoveries
        exported_data = self.discovery.export_discoveries()
        
        # Create new discovery instance and import
        new_discovery = ToolDiscovery()
        new_discovery.import_discoveries(exported_data)
        
        # Verify imported data
        self.assertEqual(len(new_discovery.discovered_tools), len(self.discovery.discovered_tools))
        
        # Check specific tool was imported correctly
        imported_tool = new_discovery.discovered_tools.get('read_file')
        original_tool = self.discovery.discovered_tools.get('read_file')
        
        self.assertIsNotNone(imported_tool)
        self.assertEqual(imported_tool.usage_count, original_tool.usage_count)
        self.assertEqual(imported_tool.success_rate, original_tool.success_rate)
        self.assertEqual(imported_tool.average_execution_time, original_tool.average_execution_time)
        
        # Check categories were rebuilt
        categories = new_discovery.categorize_by_capability()
        self.assertIn('file_system', categories)
        self.assertIn('read_file', categories['file_system'])
    
    def test_get_tool_stats(self):
        """Test getting tool statistics."""
        self.discovery.discover_all_tools(self.sample_tools)
        
        # Update some metrics
        self.discovery.update_tool_performance('read_file', True, 0.5)
        self.discovery.update_tool_performance('read_file', True, 0.4)
        self.discovery.update_tool_performance('web_search', True, 1.0)
        self.discovery.update_tool_performance('web_search', False, 2.0)
        
        stats = self.discovery.get_tool_stats()
        
        self.assertEqual(stats['total_tools'], 5)
        self.assertGreater(stats['categories'], 0)
        self.assertIn('tools_by_category', stats)
        self.assertIn('most_used_tools', stats)
        self.assertIn('highest_success_rate', stats)
        
        # Check most used tools
        most_used = dict(stats['most_used_tools'])
        self.assertEqual(most_used.get('read_file', 0), 2)
        self.assertEqual(most_used.get('web_search', 0), 2)
    
    def test_empty_tool_list(self):
        """Test behavior with empty tool list."""
        tools = self.discovery.discover_all_tools([])
        self.assertEqual(len(tools), 0)
        
        categories = self.discovery.categorize_by_capability()
        self.assertEqual(len(categories), 0)
        
        intent_tools = self.discovery.get_tools_for_intent("do something")
        self.assertEqual(len(intent_tools), 0)
    
    def test_invalid_tool_handling(self):
        """Test handling of invalid tool configurations."""
        invalid_tools = [
            {},  # Empty tool
            {'description': 'No name tool'},  # Missing name
            {'name': 'valid_tool', 'description': 'Valid tool'},  # Valid
        ]
        
        tools = self.discovery.discover_all_tools(invalid_tools)
        
        # Should only discover the valid tool
        self.assertEqual(len(tools), 1)
        self.assertIn('valid_tool', tools)


if __name__ == '__main__':
    unittest.main()
