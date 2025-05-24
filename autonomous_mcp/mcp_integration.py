"""
Real MCP Integration for Autonomous MCP Agent

This module provides integration with actual MCP servers and tools,
connecting the autonomous agent to real Claude Desktop MCP infrastructure.
"""

import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from .discovery import ToolDiscovery, DiscoveredTool, ToolCapability

logger = logging.getLogger(__name__)


@dataclass 
class MCPServerInfo:
    """Information about a connected MCP server"""
    name: str
    tools: List[str]
    status: str = "connected"
    tool_count: int = 0


class RealMCPDiscovery(ToolDiscovery):
    """
    Discovery system that connects to actual MCP servers through Claude Desktop.
    
    This class extends the base ToolDiscovery to work with real MCP tools
    available in the current Claude session.
    """
    
    def __init__(self, cache_ttl: int = 3600):
        super().__init__(cache_ttl)
        self.mcp_servers: Dict[str, MCPServerInfo] = {}
        self.raw_tool_list: List[str] = []
        
    async def discover_real_mcp_tools(self, discover_tools_function=None) -> Dict[str, DiscoveredTool]:
        """
        Discover actual MCP tools from connected servers.
        
        Args:
            discover_tools_function: Function to call discover_tools (for testing)
            
        Returns:
            Dictionary of discovered tools
        """
        logger.info("Discovering real MCP tools from Claude Desktop...")
        
        try:
            # Get the raw tool list from MCP infrastructure
            if discover_tools_function:
                tools_result = await discover_tools_function()
            else:
                # In real usage, this would call the actual discover_tools
                tools_result = "No discover_tools function provided"
                
            if isinstance(tools_result, str):
                self.raw_tool_list = [tool.strip() for tool in tools_result.split(',')]
            else:
                self.raw_tool_list = tools_result
                
            # Convert to our internal format
            discovered_tools = self._convert_mcp_tools_to_discovered()
            
            # Update our internal state
            self.discovered_tools.update(discovered_tools)
            self._update_indices()
            
            logger.info(f"Successfully discovered {len(discovered_tools)} real MCP tools")
            logger.info(f"Organized into {len(self.category_index)} categories")
            
            return discovered_tools
            
        except Exception as e:
            logger.error(f"Failed to discover MCP tools: {e}")
            return {}
    
    def _convert_mcp_tools_to_discovered(self) -> Dict[str, DiscoveredTool]:
        """Convert raw MCP tool list to DiscoveredTool objects"""
        discovered = {}
        
        for tool_name in self.raw_tool_list:
            if not tool_name:
                continue
                
            # Parse server info from tool name
            server_name, clean_name = self._parse_tool_name(tool_name)
            
            # Create discovered tool
            tool = DiscoveredTool(
                name=clean_name,
                server=server_name,
                description=self._generate_description(clean_name, server_name),
                parameters=self._infer_parameters(clean_name),
                capabilities=self._detect_capabilities(clean_name, server_name)
            )
            
            discovered[clean_name] = tool
            
            # Track server info
            if server_name not in self.mcp_servers:
                self.mcp_servers[server_name] = MCPServerInfo(
                    name=server_name,
                    tools=[],
                    tool_count=0
                )
            self.mcp_servers[server_name].tools.append(clean_name)
            self.mcp_servers[server_name].tool_count += 1
            
        return discovered
    
    def _parse_tool_name(self, full_tool_name: str) -> Tuple[str, str]:
        """Parse server name and clean tool name from full MCP tool name"""
        # Handle different naming patterns in MCP tools
        
        # Pattern 1: server_name_tool_name
        if '_' in full_tool_name:
            parts = full_tool_name.split('_')
            
            # Look for known server patterns
            known_servers = [
                'brave', 'memory', 'github', 'postman', 'firecrawl', 
                'duckduckgo', 'context7', 'desktop', 'commander',
                'puppeteer', 'magicui', 'trello', 'taskmaster', 'youtube'
            ]
            
            for server in known_servers:
                if server in parts[0].lower():
                    # Extract server name and remaining tool name
                    if len(parts) >= 2:
                        return parts[0], '_'.join(parts[1:])
            
            # Default: first part is server, rest is tool
            if len(parts) >= 2:
                return parts[0], '_'.join(parts[1:])
        
        # Pattern 2: no clear server separation
        return "unknown", full_tool_name
    
    def _generate_description(self, tool_name: str, server_name: str) -> str:
        """Generate description based on tool and server name"""
        descriptions = {
            # Web search tools
            'web_search': 'Perform web searches using search engines',
            'brave_web_search': 'Search the web using Brave Search API',
            'duckduckgo_web_search': 'Search the web using DuckDuckGo',
            
            # Memory/Knowledge tools
            'create_entities': 'Create new entities in the knowledge graph',
            'search_nodes': 'Search for nodes in the knowledge graph',
            'read_graph': 'Read the entire knowledge graph',
            'add_observations': 'Add observations to entities',
            
            # File system tools
            'read_file': 'Read contents of a file from the file system',
            'write_file': 'Write content to a file in the file system',
            'list_directory': 'List contents of a directory',
            'search_files': 'Search for files by name pattern',
            'search_code': 'Search for text patterns in code files',
            
            # GitHub tools
            'search_repositories': 'Search for repositories on GitHub',
            'create_repository': 'Create a new GitHub repository',
            'search_code': 'Search code across GitHub repositories',
            'create_pull_request': 'Create a new pull request',
            
            # Browser automation
            'puppeteer_navigate': 'Navigate to a URL in browser',
            'puppeteer_click': 'Click an element on the page',
            'puppeteer_screenshot': 'Take a screenshot of the page',
            
            # Task management
            'add_task': 'Add a new task to the project',
            'get_tasks': 'Get all tasks from the project',
            'update_task': 'Update an existing task',
            
            # API tools
            'list_collections': 'List all collections in workspace',
            'create_api': 'Create a new API definition',
            'run_monitor': 'Execute a monitor test'
        }
        
        # Try exact match first
        if tool_name in descriptions:
            return descriptions[tool_name]
        
        # Try partial matches
        for key, desc in descriptions.items():
            if key in tool_name or tool_name in key:
                return desc
        
        # Generate based on name patterns
        if 'search' in tool_name:
            return f'Search functionality for {server_name}'
        elif 'create' in tool_name:
            return f'Create new items in {server_name}'
        elif 'list' in tool_name:
            return f'List items from {server_name}'
        elif 'get' in tool_name:
            return f'Retrieve information from {server_name}'
        elif 'update' in tool_name:
            return f'Update existing items in {server_name}'
        elif 'delete' in tool_name:
            return f'Delete items from {server_name}'
        else:
            return f'{tool_name} functionality for {server_name} server'
    
    def _infer_parameters(self, tool_name: str) -> Dict[str, Any]:
        """Infer likely parameters based on tool name"""
        common_parameters = {
            # Search tools typically need queries
            'search': {'query': 'string', 'limit': 'number'},
            'web_search': {'query': 'string', 'count': 'number'},
            
            # File tools need paths
            'read_file': {'path': 'string'},
            'write_file': {'path': 'string', 'content': 'string'},
            'list_directory': {'path': 'string'},
            
            # Entity tools need data
            'create_entities': {'entities': 'array'},
            'add_observations': {'observations': 'array'},
            
            # Generic patterns
            'create': {'name': 'string', 'description': 'string'},
            'get': {'id': 'string'},
            'list': {'limit': 'number', 'offset': 'number'},
            'update': {'id': 'string', 'data': 'object'},
            'delete': {'id': 'string'}
        }
        
        # Try exact match
        if tool_name in common_parameters:
            return common_parameters[tool_name]
        
        # Try pattern matching
        for pattern, params in common_parameters.items():
            if pattern in tool_name:
                return params
        
        # Default minimal parameters
        return {'data': 'object'}
    
    def _detect_capabilities(self, tool_name: str, server_name: str) -> List[ToolCapability]:
        """Detect tool capabilities based on name and server"""
        capabilities = []
        
        # Define capability mappings
        capability_patterns = {
            'file_system': {
                'patterns': ['read_file', 'write_file', 'list_directory', 'search_files', 'search_code'],
                'subcategories': ['read', 'write', 'list', 'search']
            },
            'web_interaction': {
                'patterns': ['web_search', 'brave_web_search', 'duckduckgo_web_search', 'firecrawl'],
                'subcategories': ['search', 'scrape', 'crawl']
            },
            'memory_knowledge': {
                'patterns': ['create_entities', 'search_nodes', 'read_graph', 'add_observations'],
                'subcategories': ['create', 'search', 'read', 'update']
            },
            'code_development': {
                'patterns': ['github', 'repository', 'pull_request', 'search_code', 'create_branch'],
                'subcategories': ['vcs', 'review', 'search']
            },
            'api_integration': {
                'patterns': ['postman', 'collection', 'api', 'monitor', 'workspace'],
                'subcategories': ['test', 'document', 'monitor']
            },
            'browser_automation': {
                'patterns': ['puppeteer', 'navigate', 'click', 'screenshot'],
                'subcategories': ['navigate', 'interact', 'capture']
            },
            'task_management': {
                'patterns': ['task', 'add_task', 'get_tasks', 'update_task', 'project'],
                'subcategories': ['create', 'read', 'update', 'track']
            },
            'media_processing': {
                'patterns': ['transcript', 'youtube', 'movie', 'tmdb'],
                'subcategories': ['extract', 'search', 'analyze']
            }
        }
        
        # Detect capabilities
        for category, info in capability_patterns.items():
            for pattern in info['patterns']:
                if pattern in tool_name.lower() or pattern in server_name.lower():
                    # Determine subcategory
                    subcategory = 'general'
                    for subcat in info['subcategories']:
                        if subcat in tool_name.lower():
                            subcategory = subcat
                            break
                    
                    capability = ToolCapability(
                        category=category,
                        subcategory=subcategory,
                        description=f'{category} capability via {tool_name}',
                        confidence=0.8
                    )
                    capabilities.append(capability)
                    break
        
        # Default capability if none detected
        if not capabilities:
            capabilities.append(ToolCapability(
                category='general',
                subcategory='utility',
                description=f'General utility via {tool_name}',
                confidence=0.5
            ))
        
        return capabilities
    
    def _update_indices(self):
        """Update category and capability indices"""
        self.category_index.clear()
        self.capability_index.clear()
        
        for tool_name, tool in self.discovered_tools.items():
            for capability in tool.capabilities:
                self.category_index[capability.category].add(tool_name)
                self.capability_index[(capability.category, capability.subcategory)].add(tool_name)
    
    def get_mcp_server_stats(self) -> Dict[str, Any]:
        """Get statistics about connected MCP servers"""
        return {
            'total_servers': len(self.mcp_servers),
            'total_tools': len(self.discovered_tools),
            'servers': {
                name: {
                    'tool_count': info.tool_count,
                    'status': info.status,
                    'tools': info.tools[:5]  # First 5 tools as sample
                }
                for name, info in self.mcp_servers.items()
            },
            'categories': {
                category: len(tools) 
                for category, tools in self.category_index.items()
            }
        }
    
    def find_tools_by_server(self, server_name: str) -> List[DiscoveredTool]:
        """Find all tools from a specific MCP server"""
        return [
            tool for tool in self.discovered_tools.values() 
            if tool.server == server_name
        ]
    
    def get_available_servers(self) -> List[str]:
        """Get list of all available MCP servers"""
        return list(self.mcp_servers.keys())


class MCPToolChainBuilder:
    """Helper class to build mcp_chain configurations"""
    
    @staticmethod
    def build_single_tool_chain(tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Build mcp_chain config for a single tool"""
        return {
            "mcpPath": [{
                "toolName": tool_name,
                "toolArgs": json.dumps(parameters)
            }]
        }
    
    @staticmethod 
    def build_multi_tool_chain(tool_calls: List[Tuple[str, Dict[str, Any]]]) -> Dict[str, Any]:
        """Build mcp_chain config for multiple tools"""
        mcp_path = []
        
        for i, (tool_name, parameters) in enumerate(tool_calls):
            tool_config = {
                "toolName": tool_name,
                "toolArgs": json.dumps(parameters)
            }
            
            # Add input/output path for chaining if not first tool
            if i > 0:
                tool_config["inputPath"] = "CHAIN_RESULT"
            
            mcp_path.append(tool_config)
        
        return {"mcpPath": mcp_path}
    
    @staticmethod
    def build_conditional_chain(primary_tool: str, fallback_tool: str, 
                              primary_params: Dict[str, Any], 
                              fallback_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build multiple chain configs for fallback scenarios"""
        return [
            MCPToolChainBuilder.build_single_tool_chain(primary_tool, primary_params),
            MCPToolChainBuilder.build_single_tool_chain(fallback_tool, fallback_params)
        ]
