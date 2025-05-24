"""
Tool Discovery System for Autonomous MCP Agent.

This module handles automatic discovery, categorization, and caching of available MCP tools.
It provides intelligent tool selection based on capabilities and user intent.
"""

import json
import time
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
from collections import defaultdict
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)


@dataclass
class ToolCapability:
    """Represents a specific capability that a tool provides."""
    category: str  # e.g., 'file_system', 'web_search', 'data_processing'
    subcategory: str  # e.g., 'read', 'write', 'search'
    description: str
    confidence: float = 1.0  # How well this tool performs this capability


@dataclass
class DiscoveredTool:
    """Represents a discovered MCP tool with its metadata and capabilities."""
    name: str
    server: str
    description: str
    parameters: Dict[str, Any]
    capabilities: List[ToolCapability] = field(default_factory=list)
    usage_count: int = 0
    success_rate: float = 1.0
    average_execution_time: float = 0.0
    last_used: Optional[float] = None
    aliases: List[str] = field(default_factory=list)  # Alternative names for the tool


class ToolDiscovery:
    """
    Discovers and categorizes available MCP tools.
    
    This class handles:
    - Automatic discovery of MCP servers and their tools
    - Tool categorization based on capabilities
    - Intelligent tool selection for specific intents
    - Performance tracking and optimization
    """
    
    # Tool category definitions
    TOOL_CATEGORIES = {
        'file_system': {
            'keywords': ['file', 'directory', 'read', 'write', 'create', 'delete', 'move', 'search'],
            'subcategories': ['read', 'write', 'manipulate', 'search']
        },
        'web_interaction': {
            'keywords': ['web', 'search', 'scrape', 'browse', 'fetch', 'crawl', 'http'],
            'subcategories': ['search', 'scrape', 'api', 'browser']
        },
        'data_processing': {
            'keywords': ['parse', 'analyze', 'transform', 'convert', 'process', 'extract'],
            'subcategories': ['parse', 'transform', 'analyze', 'extract']
        },
        'memory_knowledge': {
            'keywords': ['memory', 'store', 'retrieve', 'knowledge', 'graph', 'entity', 'relation'],
            'subcategories': ['store', 'retrieve', 'query', 'update']
        },
        'code_development': {
            'keywords': ['github', 'code', 'repository', 'commit', 'branch', 'pull', 'issue'],
            'subcategories': ['vcs', 'review', 'build', 'deploy']
        },
        'communication': {
            'keywords': ['email', 'message', 'notify', 'alert', 'webhook'],
            'subcategories': ['send', 'receive', 'notify']
        },
        'api_integration': {
            'keywords': ['api', 'rest', 'graphql', 'postman', 'collection', 'endpoint'],
            'subcategories': ['test', 'document', 'monitor']
        },
        'media_processing': {
            'keywords': ['image', 'video', 'audio', 'transcript', 'screenshot'],
            'subcategories': ['capture', 'convert', 'analyze']
        },
        'task_management': {
            'keywords': ['task', 'project', 'workflow', 'plan', 'schedule', 'track'],
            'subcategories': ['create', 'update', 'track', 'automate']
        },
        'browser_automation': {
            'keywords': ['puppeteer', 'selenium', 'browser', 'click', 'navigate', 'automate'],
            'subcategories': ['navigate', 'interact', 'extract']
        }
    }
    
    def __init__(self, cache_ttl: int = 3600):
        """
        Initialize the Tool Discovery system.
        
        Args:
            cache_ttl: Time to live for cached discoveries in seconds
        """
        self.discovered_tools: Dict[str, DiscoveredTool] = {}
        self.category_index: Dict[str, Set[str]] = defaultdict(set)
        self.capability_index: Dict[Tuple[str, str], Set[str]] = defaultdict(set)
        self.cache_ttl = cache_ttl
        self.last_discovery_time = 0
        self._discovery_cache = {}
        
    def discover_all_tools(self, available_tools: List[Dict[str, Any]], force_refresh: bool = False) -> Dict[str, DiscoveredTool]:
        """
        Discover all available MCP tools from the provided list.
        
        Args:
            available_tools: List of available tool configurations
            force_refresh: Force refresh even if cache is valid
            
        Returns:
            Dictionary of tool name to DiscoveredTool objects
        """
        # Check cache validity
        if not force_refresh and self._is_cache_valid():
            return self.discovered_tools
            
        logger.info(f"Discovering {len(available_tools)} tools...")
        
        # Clear existing data
        self.discovered_tools.clear()
        self.category_index.clear()
        self.capability_index.clear()
        
        # Process each tool
        for tool_info in available_tools:
            tool = self._process_tool(tool_info)
            if tool:
                self.discovered_tools[tool.name] = tool
                
                # Update indices
                for capability in tool.capabilities:
                    self.category_index[capability.category].add(tool.name)
                    self.capability_index[(capability.category, capability.subcategory)].add(tool.name)
        
        self.last_discovery_time = time.time()
        logger.info(f"Discovered {len(self.discovered_tools)} tools across {len(self.category_index)} categories")
        
        return self.discovered_tools
    
    def _process_tool(self, tool_info: Dict[str, Any]) -> Optional[DiscoveredTool]:
        """Process a single tool configuration and extract its capabilities."""
        try:
            name = tool_info.get('name', '')
            if not name:
                return None
                
            # Extract basic info
            tool = DiscoveredTool(
                name=name,
                server=tool_info.get('server', 'unknown'),
                description=tool_info.get('description', ''),
                parameters=tool_info.get('parameters', {})
            )
            
            # Detect capabilities
            tool.capabilities = self._detect_capabilities(tool)
            
            # Extract aliases if present
            if 'aliases' in tool_info:
                tool.aliases = tool_info['aliases']
            
            return tool
            
        except Exception as e:
            logger.error(f"Error processing tool {tool_info}: {e}")
            return None
    
    def _detect_capabilities(self, tool: DiscoveredTool) -> List[ToolCapability]:
        """Detect capabilities based on tool name, description, and parameters."""
        capabilities = []
        
        # Combine all text for analysis
        text_to_analyze = f"{tool.name} {tool.description}".lower()
        param_names = ' '.join(tool.parameters.keys()).lower()
        
        # Check each category
        for category, config in self.TOOL_CATEGORIES.items():
            # Calculate keyword matches
            keyword_matches = sum(1 for keyword in config['keywords'] 
                                if keyword in text_to_analyze or keyword in param_names)
            
            if keyword_matches > 0:
                # Determine confidence based on number of matches
                confidence = min(1.0, keyword_matches / len(config['keywords']))
                
                # Try to determine subcategory
                for subcategory in config['subcategories']:
                    if subcategory in text_to_analyze or subcategory in param_names:
                        capabilities.append(ToolCapability(
                            category=category,
                            subcategory=subcategory,
                            description=f"{tool.name} can {subcategory} {category}",
                            confidence=confidence
                        ))
                        break
                else:
                    # No specific subcategory found, use general
                    capabilities.append(ToolCapability(
                        category=category,
                        subcategory='general',
                        description=f"{tool.name} provides {category} functionality",
                        confidence=confidence * 0.8  # Lower confidence for general
                    ))
        
        return capabilities
    
    def categorize_by_capability(self) -> Dict[str, List[str]]:
        """
        Get tools organized by their primary categories.
        
        Returns:
            Dictionary mapping category names to lists of tool names
        """
        return {category: list(tools) for category, tools in self.category_index.items()}
    
    def get_tools_for_intent(self, intent: str, required_capabilities: Optional[List[Tuple[str, str]]] = None) -> List[DiscoveredTool]:
        """
        Get tools that match a specific intent or required capabilities.
        
        Args:
            intent: Natural language description of what the user wants to do
            required_capabilities: Optional list of (category, subcategory) tuples
            
        Returns:
            List of tools sorted by relevance
        """
        matching_tools = []
        intent_lower = intent.lower()
        
        if required_capabilities:
            # Get tools that have all required capabilities
            tool_sets = [self.capability_index.get(cap, set()) for cap in required_capabilities]
            if tool_sets:
                # Find intersection of all capability sets
                common_tools = set.intersection(*tool_sets)
                matching_tools = [self.discovered_tools[name] for name in common_tools]
        else:
            # Score tools based on intent matching
            for tool_name, tool in self.discovered_tools.items():
                score = self._calculate_intent_score(tool, intent_lower)
                if score > 0:
                    matching_tools.append((score, tool))
            
            # Sort by score and extract tools
            matching_tools = [tool for score, tool in sorted(matching_tools, key=lambda x: x[0], reverse=True)]
        
        return matching_tools
    
    def _calculate_intent_score(self, tool: DiscoveredTool, intent: str) -> float:
        """Calculate how well a tool matches an intent."""
        score = 0.0
        
        # Check tool name and description
        if tool.name.lower() in intent:
            score += 2.0
        if any(alias.lower() in intent for alias in tool.aliases):
            score += 1.5
            
        # Check description words
        description_words = tool.description.lower().split()
        intent_words = intent.split()
        matching_words = sum(1 for word in description_words if word in intent_words)
        score += matching_words * 0.5
        
        # Check capabilities
        for capability in tool.capabilities:
            if capability.category in intent or capability.subcategory in intent:
                score += capability.confidence
        
        # Boost score based on tool performance
        score *= tool.success_rate
        
        return score
    
    @lru_cache(maxsize=128)
    def find_best_tool(self, category: str, subcategory: str = 'general') -> Optional[DiscoveredTool]:
        """
        Find the best tool for a specific capability.
        
        Args:
            category: Tool category
            subcategory: Specific subcategory
            
        Returns:
            Best matching tool or None
        """
        tool_names = self.capability_index.get((category, subcategory), set())
        
        if not tool_names:
            # Try general subcategory
            tool_names = self.capability_index.get((category, 'general'), set())
        
        if not tool_names:
            return None
        
        # Find tool with highest success rate and capability confidence
        best_tool = None
        best_score = 0
        
        for tool_name in tool_names:
            tool = self.discovered_tools.get(tool_name)
            if tool:
                # Find relevant capability
                for cap in tool.capabilities:
                    if cap.category == category and (cap.subcategory == subcategory or subcategory == 'general'):
                        score = tool.success_rate * cap.confidence
                        if score > best_score:
                            best_score = score
                            best_tool = tool
                        break
        
        return best_tool
    
    def refresh_tool_cache(self, available_tools: List[Dict[str, Any]]) -> None:
        """Force refresh the tool cache with new data."""
        self.discover_all_tools(available_tools, force_refresh=True)
    
    def update_tool_performance(self, tool_name: str, success: bool, execution_time: float) -> None:
        """
        Update performance metrics for a tool.
        
        Args:
            tool_name: Name of the tool
            success: Whether the execution was successful
            execution_time: Time taken to execute in seconds
        """
        if tool_name not in self.discovered_tools:
            return
            
        tool = self.discovered_tools[tool_name]
        tool.usage_count += 1
        tool.last_used = time.time()
        
        # Update success rate (exponential moving average)
        alpha = 0.1  # Smoothing factor
        tool.success_rate = alpha * (1.0 if success else 0.0) + (1 - alpha) * tool.success_rate
        
        # Update average execution time
        if tool.average_execution_time == 0:
            tool.average_execution_time = execution_time
        else:
            tool.average_execution_time = alpha * execution_time + (1 - alpha) * tool.average_execution_time
    
    def get_tool_stats(self) -> Dict[str, Any]:
        """Get statistics about discovered tools."""
        return {
            'total_tools': len(self.discovered_tools),
            'categories': len(self.category_index),
            'tools_by_category': {cat: len(tools) for cat, tools in self.category_index.items()},
            'most_used_tools': sorted(
                [(tool.name, tool.usage_count) for tool in self.discovered_tools.values()],
                key=lambda x: x[1],
                reverse=True
            )[:10],
            'highest_success_rate': sorted(
                [(tool.name, tool.success_rate) for tool in self.discovered_tools.values()],
                key=lambda x: x[1],
                reverse=True
            )[:10]
        }
    
    def _is_cache_valid(self) -> bool:
        """Check if the discovery cache is still valid."""
        return (time.time() - self.last_discovery_time) < self.cache_ttl
    
    def export_discoveries(self) -> Dict[str, Any]:
        """Export discovered tools for persistence."""
        return {
            'discovered_tools': {
                name: {
                    'name': tool.name,
                    'server': tool.server,
                    'description': tool.description,
                    'parameters': tool.parameters,
                    'capabilities': [
                        {
                            'category': cap.category,
                            'subcategory': cap.subcategory,
                            'description': cap.description,
                            'confidence': cap.confidence
                        }
                        for cap in tool.capabilities
                    ],
                    'usage_count': tool.usage_count,
                    'success_rate': tool.success_rate,
                    'average_execution_time': tool.average_execution_time,
                    'last_used': tool.last_used,
                    'aliases': tool.aliases
                }
                for name, tool in self.discovered_tools.items()
            },
            'last_discovery_time': self.last_discovery_time
        }
    
    def import_discoveries(self, data: Dict[str, Any]) -> None:
        """Import previously discovered tools."""
        self.discovered_tools.clear()
        self.category_index.clear()
        self.capability_index.clear()
        
        for name, tool_data in data.get('discovered_tools', {}).items():
            capabilities = [
                ToolCapability(**cap_data)
                for cap_data in tool_data.get('capabilities', [])
            ]
            
            tool = DiscoveredTool(
                name=tool_data['name'],
                server=tool_data['server'],
                description=tool_data['description'],
                parameters=tool_data['parameters'],
                capabilities=capabilities,
                usage_count=tool_data.get('usage_count', 0),
                success_rate=tool_data.get('success_rate', 1.0),
                average_execution_time=tool_data.get('average_execution_time', 0.0),
                last_used=tool_data.get('last_used'),
                aliases=tool_data.get('aliases', [])
            )
            
            self.discovered_tools[name] = tool
            
            # Rebuild indices
            for capability in tool.capabilities:
                self.category_index[capability.category].add(tool.name)
                self.capability_index[(capability.category, capability.subcategory)].add(tool.name)
        
        self.last_discovery_time = data.get('last_discovery_time', 0)


# Example usage and testing
if __name__ == "__main__":
    # Example tool list (would come from mcp_chain or similar)
    example_tools = [
        {
            'name': 'read_file',
            'server': 'desktop_commander',
            'description': 'Read the contents of a file from the file system',
            'parameters': {'path': 'string', 'offset': 'number', 'length': 'number'}
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
        }
    ]
    
    # Test discovery
    discovery = ToolDiscovery()
    tools = discovery.discover_all_tools(example_tools)
    
    print("Discovered Tools:")
    for name, tool in tools.items():
        print(f"\n{name}:")
        print(f"  Server: {tool.server}")
        print(f"  Capabilities:")
        for cap in tool.capabilities:
            print(f"    - {cap.category}/{cap.subcategory} (confidence: {cap.confidence})")
    
    print("\n\nTools by Category:")
    categories = discovery.categorize_by_capability()
    for category, tool_names in categories.items():
        print(f"  {category}: {', '.join(tool_names)}")
    
    print("\n\nTools for 'search for files':")
    matching_tools = discovery.get_tools_for_intent("search for files")
    for tool in matching_tools:
        print(f"  - {tool.name}: {tool.description}")
