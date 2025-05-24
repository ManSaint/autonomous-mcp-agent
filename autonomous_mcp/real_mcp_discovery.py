"""
Real MCP Tool Discovery System

This module discovers and categorizes actual MCP servers and tools available
in the runtime environment, providing dynamic tool management and intelligent
categorization for the autonomous agent framework.
"""

import logging
import time
from typing import Dict, List, Set, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import json
import re


class ToolCategory(Enum):
    """Categories for MCP tools based on functionality"""
    SEARCH = "search"
    MEMORY = "memory" 
    DEVELOPMENT = "development"
    COMMUNICATION = "communication"
    AUTOMATION = "automation"
    ANALYSIS = "analysis"
    CONTENT = "content"
    PRODUCTIVITY = "productivity"
    SYSTEM = "system"
    UNKNOWN = "unknown"


@dataclass
class MCPServer:
    """Represents a discovered MCP server"""
    name: str
    tools: List[str] = field(default_factory=list)
    capabilities: Set[str] = field(default_factory=set)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    last_discovered: float = field(default_factory=time.time)
    status: str = "active"
    
    
@dataclass
class MCPTool:
    """Represents a discovered MCP tool with metadata"""
    name: str
    server: str
    category: ToolCategory
    description: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    usage_count: int = 0
    success_rate: float = 1.0
    avg_execution_time: float = 0.0
    last_used: Optional[float] = None
    complexity_score: float = 1.0
    reliability_score: float = 1.0
    
    @property
    def capabilities(self):
        """Compatibility property for planner - returns list of capability-like objects"""
        from dataclasses import dataclass
        
        @dataclass
        class CapabilityCompat:
            category: str
            subcategory: str
            confidence: float = 0.8
            
        # Create a compatibility capability based on the tool's category
        return [CapabilityCompat(
            category=self.category.value,
            subcategory="general",
            confidence=self.reliability_score
        )]


class RealMCPDiscovery:
    """
    Real-time MCP tool discovery and categorization system
    
    This class discovers actual MCP servers and tools available in the runtime
    environment, categorizes them intelligently, and provides performance tracking.
    """
    
    def __init__(self):
        """Initialize the MCP discovery system"""
        self.logger = logging.getLogger(__name__)
        
        # Tool storage
        self.servers: Dict[str, MCPServer] = {}
        self.tools: Dict[str, MCPTool] = {}
        self.categories: Dict[ToolCategory, List[str]] = {cat: [] for cat in ToolCategory}
        
        # Performance tracking
        self.discovery_metrics = {
            'total_discoveries': 0,
            'discovery_time': 0.0,
            'categorization_accuracy': 0.0,
            'tool_availability_rate': 1.0
        }
        
        # Tool categorization patterns
        self.category_patterns = self._init_categorization_patterns()
        
        # Discovery cache
        self._discovery_cache = {}
        self._cache_timestamp = 0
        self._cache_ttl = 300  # 5 minutes
        
    def _init_categorization_patterns(self) -> Dict[ToolCategory, List[str]]:
        """Initialize patterns for automatic tool categorization"""
        return {
            ToolCategory.SEARCH: [
                r'search', r'find', r'query', r'lookup', r'browse', 
                r'brave', r'web', r'local'
            ],
            ToolCategory.MEMORY: [
                r'memory', r'knowledge', r'graph', r'store', r'recall',
                r'entities', r'relations', r'observations'
            ],
            ToolCategory.DEVELOPMENT: [
                r'github', r'git', r'code', r'repo', r'branch', r'commit',
                r'pull_request', r'issue', r'file', r'create', r'update'
            ],
            ToolCategory.COMMUNICATION: [
                r'post', r'send', r'message', r'email', r'chat', r'notify',
                r'slack', r'discord', r'teams'
            ],
            ToolCategory.AUTOMATION: [
                r'workflow', r'automate', r'trigger', r'schedule', r'run',
                r'execute', r'process', r'batch'
            ],
            ToolCategory.ANALYSIS: [
                r'analyze', r'report', r'metrics', r'stats', r'monitor',
                r'track', r'measure', r'evaluate'
            ],
            ToolCategory.CONTENT: [
                r'content', r'text', r'document', r'write', r'generate',
                r'transcript', r'video', r'audio', r'image'
            ],
            ToolCategory.PRODUCTIVITY: [
                r'task', r'todo', r'project', r'calendar', r'schedule',
                r'trello', r'notion', r'asana', r'board', r'card'
            ],
            ToolCategory.SYSTEM: [
                r'config', r'system', r'admin', r'manage', r'control',
                r'initialize', r'setup', r'install'
            ]
        }
    
    def discover_all_tools(self, force_refresh: bool = False) -> Dict[str, MCPTool]:
        """
        Discover all available MCP tools in the environment
        
        Args:
            force_refresh: Force rediscovery even if cached
            
        Returns:
            Dictionary of discovered tools
        """
        start_time = time.time()
        
        # Check cache first
        if not force_refresh and self._is_cache_valid():
            self.logger.info("Returning cached tool discovery results")
            return self.tools
            
        self.logger.info("Starting real-time MCP tool discovery...")
        
        try:
            # Import the chainable_tools function from the MCP chain system
            # This gives us access to all available MCP tools
            from .mcp_chain_executor import get_available_tools
            
            # Get all available tools
            available_tools = get_available_tools()
            
            # Clear existing data
            self.servers.clear()
            self.tools.clear()
            for cat in self.categories:
                self.categories[cat].clear()
                
            # Process discovered tools
            for tool_name in available_tools:
                self._process_discovered_tool(tool_name)
                
            # Update discovery metrics
            discovery_time = time.time() - start_time
            self.discovery_metrics.update({
                'total_discoveries': len(self.tools),
                'discovery_time': discovery_time,
                'tool_availability_rate': len(self.tools) / max(len(available_tools), 1)
            })
            
            # Update cache
            self._cache_timestamp = time.time()
            
            self.logger.info(f"Discovered {len(self.tools)} tools across {len(self.servers)} servers in {discovery_time:.2f}s")
            
            return self.tools
            
        except Exception as e:
            self.logger.error(f"Error during tool discovery: {e}")
            return {}
    
    def _process_discovered_tool(self, tool_name: str) -> None:
        """Process a single discovered tool"""
        try:
            # Extract server name and tool info
            server_name = self._extract_server_name(tool_name)
            category = self._categorize_tool(tool_name)
            
            # Create or update server
            if server_name not in self.servers:
                self.servers[server_name] = MCPServer(name=server_name)
            
            self.servers[server_name].tools.append(tool_name)
            
            # Create tool entry
            tool = MCPTool(
                name=tool_name,
                server=server_name,
                category=category,
                description=self._generate_tool_description(tool_name),
                complexity_score=self._calculate_complexity_score(tool_name)
            )
            
            self.tools[tool_name] = tool
            self.categories[category].append(tool_name)
            
        except Exception as e:
            self.logger.warning(f"Error processing tool {tool_name}: {e}")
    
    def _extract_server_name(self, tool_name: str) -> str:
        """Extract server name from tool name"""
        # Handle different naming patterns
        if '_' in tool_name:
            # Pattern: server_action or action_server_subaction
            parts = tool_name.split('_')
            
            # Common server names we can identify
            known_servers = [
                'brave', 'github', 'postman', 'memory', 'trello', 'youtube',
                'taskmaster', 'sequential', 'tmdb'
            ]
            
            for server in known_servers:
                if server in tool_name.lower():
                    return server
                    
            # Default: use first part
            return parts[0]
        
        # Single word tools - try to identify by patterns
        if 'search' in tool_name.lower():
            return 'search'
        elif any(word in tool_name.lower() for word in ['create', 'read', 'update', 'delete']):
            return 'crud'
        else:
            return 'core'
    
    def _categorize_tool(self, tool_name: str) -> ToolCategory:
        """Automatically categorize a tool based on its name and patterns"""
        tool_lower = tool_name.lower()
        
        # Check each category's patterns
        for category, patterns in self.category_patterns.items():
            for pattern in patterns:
                if re.search(pattern, tool_lower):
                    return category
        
        return ToolCategory.UNKNOWN
    
    def _generate_tool_description(self, tool_name: str) -> str:
        """Generate a description for a tool based on its name"""
        # Basic description generation based on tool name patterns
        if 'search' in tool_name.lower():
            return f"Search tool: {tool_name}"
        elif 'create' in tool_name.lower():
            return f"Creation tool: {tool_name}"
        elif 'get' in tool_name.lower():
            return f"Retrieval tool: {tool_name}"
        elif 'update' in tool_name.lower():
            return f"Update tool: {tool_name}"
        elif 'delete' in tool_name.lower():
            return f"Deletion tool: {tool_name}"
        else:
            return f"Tool: {tool_name}"
    
    def _calculate_complexity_score(self, tool_name: str) -> float:
        """Calculate complexity score for a tool (1.0 = simple, 5.0 = complex)"""
        # Basic complexity scoring
        complexity = 1.0
        
        # Tools with multiple words tend to be more complex
        word_count = len(tool_name.split('_'))
        complexity += (word_count - 1) * 0.5
        
        # Certain patterns indicate higher complexity
        if any(word in tool_name.lower() for word in ['analyze', 'complex', 'advanced']):
            complexity += 1.0
        if any(word in tool_name.lower() for word in ['workflow', 'chain', 'batch']):
            complexity += 0.5
            
        return min(complexity, 5.0)
    
    def _is_cache_valid(self) -> bool:
        """Check if discovery cache is still valid"""
        return (time.time() - self._cache_timestamp) < self._cache_ttl
    
    def get_tools_by_category(self, category: ToolCategory) -> List[MCPTool]:
        """Get all tools in a specific category"""
        return [self.tools[name] for name in self.categories[category] if name in self.tools]
    
    def get_tools_by_server(self, server_name: str) -> List[MCPTool]:
        """Get all tools from a specific server"""
        if server_name not in self.servers:
            return []
        
        return [self.tools[name] for name in self.servers[server_name].tools if name in self.tools]
    
    def find_tools_by_pattern(self, pattern: str) -> List[MCPTool]:
        """Find tools matching a regex pattern"""
        matching_tools = []
        compiled_pattern = re.compile(pattern, re.IGNORECASE)
        
        for tool_name, tool in self.tools.items():
            if compiled_pattern.search(tool_name) or compiled_pattern.search(tool.description):
                matching_tools.append(tool)
        
        return matching_tools
    
    def get_recommended_tools(self, task_description: str, limit: int = 5) -> List[MCPTool]:
        """
        Get recommended tools for a task based on description
        
        Args:
            task_description: Description of the task
            limit: Maximum number of tools to recommend
            
        Returns:
            List of recommended MCPTool objects
        """
        # Simple keyword-based recommendation
        task_lower = task_description.lower()
        tool_scores = []
        
        for tool_name, tool in self.tools.items():
            score = 0.0
            
            # Score based on name matching
            tool_words = tool_name.lower().split('_')
            for word in task_lower.split():
                if word in tool_words:
                    score += 1.0
                    
            # Score based on category relevance
            if 'search' in task_lower and tool.category == ToolCategory.SEARCH:
                score += 2.0
            elif 'create' in task_lower and tool.category == ToolCategory.DEVELOPMENT:
                score += 2.0
            elif 'analyze' in task_lower and tool.category == ToolCategory.ANALYSIS:
                score += 2.0
                
            # Factor in tool reliability and usage
            score *= tool.success_rate
            score += tool.usage_count * 0.1
            
            tool_scores.append((tool, score))
        
        # Sort by score and return top tools
        tool_scores.sort(key=lambda x: x[1], reverse=True)
        return [tool for tool, score in tool_scores[:limit] if score > 0]
    
    def update_tool_metrics(self, tool_name: str, execution_time: float, 
                          success: bool = True) -> None:
        """Update performance metrics for a tool"""
        if tool_name not in self.tools:
            return
            
        tool = self.tools[tool_name]
        tool.usage_count += 1
        tool.last_used = time.time()
        
        # Update success rate (exponential moving average)
        alpha = 0.1
        if success:
            tool.success_rate = (1 - alpha) * tool.success_rate + alpha * 1.0
        else:
            tool.success_rate = (1 - alpha) * tool.success_rate + alpha * 0.0
            
        # Update average execution time
        tool.avg_execution_time = (
            (tool.avg_execution_time * (tool.usage_count - 1) + execution_time) / 
            tool.usage_count
        )
        
        # Update reliability score
        tool.reliability_score = tool.success_rate * max(0.1, 1.0 - (tool.avg_execution_time / 30.0))
    
    def get_discovery_summary(self) -> Dict[str, Any]:
        """Get a summary of the discovery results"""
        return {
            'total_tools': len(self.tools),
            'total_servers': len(self.servers),
            'categories': {cat.value: len(tools) for cat, tools in self.categories.items()},
            'metrics': self.discovery_metrics,
            'top_servers': sorted(
                [(name, len(server.tools)) for name, server in self.servers.items()],
                key=lambda x: x[1], reverse=True
            )[:5]
        }
    
    def get_tools_for_intent(self, intent: str) -> List[MCPTool]:
        """
        Get tools that match a specific intent (compatibility method for planner)
        
        Args:
            intent: User's intended action
            
        Returns:
            List of MCPTool objects that match the intent
        """
        return self.get_recommended_tools(intent, limit=10)
    
    async def get_all_tools(self) -> List[MCPTool]:
        """
        Get all discovered tools as a list (compatibility method for smart_selector)
        
        Returns:
            List of all MCPTool objects
        """
        return list(self.tools.values())

    def export_tool_catalog(self) -> Dict[str, Any]:
        """Export complete tool catalog for external use"""
        return {
            'servers': {
                name: {
                    'name': server.name,
                    'tools': server.tools,
                    'status': server.status,
                    'last_discovered': server.last_discovered
                }
                for name, server in self.servers.items()
            },
            'tools': {
                name: {
                    'name': tool.name,
                    'server': tool.server,
                    'category': tool.category.value,
                    'description': tool.description,
                    'complexity_score': tool.complexity_score,
                    'reliability_score': tool.reliability_score,
                    'usage_count': tool.usage_count,
                    'success_rate': tool.success_rate
                }
                for name, tool in self.tools.items()
            },
            'summary': self.get_discovery_summary()
        }


# Global instance for singleton access
_discovery_instance = None

def get_discovery_instance() -> RealMCPDiscovery:
    """Get the global discovery instance"""
    global _discovery_instance
    if _discovery_instance is None:
        _discovery_instance = RealMCPDiscovery()
    return _discovery_instance
