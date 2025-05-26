"""
MCP Configuration Reader

This module reads and manages MCP server configurations, providing
connection details for external MCP servers that the autonomous agent
can connect to directly.
"""

import json
import logging
import os
import platform
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path


@dataclass
class MCPServerConfig:
    """Configuration for an MCP server"""
    name: str
    command: str
    args: List[str] = None
    env: Dict[str, str] = None
    transport: str = "stdio"
    enabled: bool = True
    
    def __post_init__(self):
        if self.args is None:
            self.args = []
        if self.env is None:
            self.env = {}


class MCPConfigReader:
    """
    Reads MCP server configurations from various sources
    
    This class can read from Claude's configuration files, custom configs,
    or provide default server configurations for common MCP servers.
    """
    
    def __init__(self):
        """Initialize the MCP config reader"""
        self.logger = logging.getLogger(__name__)
        self.config_cache = {}
        
        # Known MCP server configurations
        self.default_servers = self._init_default_servers()
    
    def _init_default_servers(self) -> Dict[str, MCPServerConfig]:
        """Initialize default MCP server configurations"""
        servers = {}
        
        # Postman MCP Server
        servers['postman'] = MCPServerConfig(
            name='postman',
            command='npx',
            args=['-y', '@postman/mcp-server'],
            env={'POSTMAN_API_KEY': ''}  # User needs to set this
        )
        
        # GitHub MCP Server  
        servers['github'] = MCPServerConfig(
            name='github',
            command='npx',
            args=['-y', '@modelcontextprotocol/server-github'],
            env={'GITHUB_PERSONAL_ACCESS_TOKEN': ''}  # User needs to set this
        )
        
        # Trello MCP Server
        servers['trello'] = MCPServerConfig(
            name='trello',
            command='npx',
            args=['-y', 'trello-mcp-server'],
            env={
                'TRELLO_API_KEY': '',  # User needs to set this
                'TRELLO_TOKEN': ''     # User needs to set this
            }
        )
        
        # Memory/Knowledge Graph MCP Server
        servers['memory'] = MCPServerConfig(
            name='memory',
            command='npx',
            args=['-y', '@modelcontextprotocol/server-memory']
        )
        
        # Desktop Commander MCP Server (if available)
        servers['commander'] = MCPServerConfig(
            name='commander',
            command='desktop-commander-mcp',
            args=[]
        )
        
        # YouTube MCP Server
        servers['youtube'] = MCPServerConfig(
            name='youtube',
            command='npx',
            args=['-y', 'youtube-transcript-mcp-server']
        )
        
        # Task Master MCP Server
        servers['taskmaster'] = MCPServerConfig(
            name='taskmaster',
            command='npx',
            args=['-y', 'task-master-mcp']
        )
        
        # Movie Database MCP Server
        servers['tmdb'] = MCPServerConfig(
            name='tmdb',
            command='npx',
            args=['-y', 'tmdb-mcp-server'],
            env={'TMDB_API_KEY': ''}  # User needs to set this
        )
        
        # Search MCP Servers
        servers['brave_search'] = MCPServerConfig(
            name='brave_search',
            command='npx',
            args=['-y', '@modelcontextprotocol/server-brave-search'],
            env={'BRAVE_API_KEY': ''}  # User needs to set this
        )
        
        # Additional common servers
        servers['puppeteer'] = MCPServerConfig(
            name='puppeteer',
            command='npx',
            args=['-y', '@modelcontextprotocol/server-puppeteer']
        )
        
        servers['magic_ui'] = MCPServerConfig(
            name='magic_ui',
            command='npx',
            args=['-y', 'magic-ui-mcp-server']
        )
        
        return servers
    
    def find_claude_config(self) -> Optional[Path]:
        """Find Claude's desktop configuration file"""
        try:
            # Common Claude configuration locations
            system = platform.system()
            
            if system == "Windows":
                # Windows locations
                locations = [
                    Path.home() / "AppData" / "Roaming" / "Claude" / "claude_desktop_config.json",
                    Path.home() / "AppData" / "Local" / "Claude" / "claude_desktop_config.json",
                    Path("C:/ProgramData/Claude/claude_desktop_config.json"),
                ]
            elif system == "Darwin":  # macOS
                locations = [
                    Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json",
                    Path("/Applications/Claude.app/Contents/Resources/claude_desktop_config.json"),
                ]
            else:  # Linux
                locations = [
                    Path.home() / ".config" / "claude" / "claude_desktop_config.json",
                    Path("/etc/claude/claude_desktop_config.json"),
                ]
            
            # Check each location
            for location in locations:
                if location.exists():
                    self.logger.info(f"Found Claude config at: {location}")
                    return location
            
            self.logger.warning("Claude configuration file not found")
            return None
            
        except Exception as e:
            self.logger.error(f"Error finding Claude config: {e}")
            return None
    
    def read_claude_config(self) -> Dict[str, MCPServerConfig]:
        """Read MCP server configurations from Claude's config file"""
        config_path = self.find_claude_config()
        if not config_path:
            self.logger.info("Using default MCP server configurations")
            return self.default_servers.copy()
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            servers = {}
            mcp_servers = config_data.get('mcpServers', {})
            
            for server_name, server_config in mcp_servers.items():
                try:
                    servers[server_name] = MCPServerConfig(
                        name=server_name,
                        command=server_config.get('command', ''),
                        args=server_config.get('args', []),
                        env=server_config.get('env', {}),
                        transport=server_config.get('transport', 'stdio'),
                        enabled=server_config.get('enabled', True)
                    )
                except Exception as e:
                    self.logger.warning(f"Error parsing server config for {server_name}: {e}")
            
            self.logger.info(f"Loaded {len(servers)} MCP servers from Claude config")
            return servers
            
        except Exception as e:
            self.logger.error(f"Error reading Claude config: {e}")
            self.logger.info("Falling back to default configurations")
            return self.default_servers.copy()
    
    def read_custom_config(self, config_path: str) -> Dict[str, MCPServerConfig]:
        """Read MCP server configurations from a custom file"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            servers = {}
            
            # Handle different config formats
            if 'mcpServers' in config_data:
                server_configs = config_data['mcpServers']
            elif 'servers' in config_data:
                server_configs = config_data['servers']
            else:
                server_configs = config_data
            
            for server_name, server_config in server_configs.items():
                servers[server_name] = MCPServerConfig(
                    name=server_name,
                    command=server_config.get('command', ''),
                    args=server_config.get('args', []),
                    env=server_config.get('env', {}),
                    transport=server_config.get('transport', 'stdio'),
                    enabled=server_config.get('enabled', True)
                )
            
            self.logger.info(f"Loaded {len(servers)} servers from custom config: {config_path}")
            return servers
            
        except Exception as e:
            self.logger.error(f"Error reading custom config {config_path}: {e}")
            return {}
    
    def get_server_configs(self, config_source: Optional[str] = None) -> Dict[str, MCPServerConfig]:
        """
        Get MCP server configurations
        
        Args:
            config_source: Optional custom config file path
            
        Returns:
            Dictionary of server configurations
        """
        if config_source and os.path.exists(config_source):
            return self.read_custom_config(config_source)
        else:
            # Try to read from Claude config, fall back to defaults
            servers = self.read_claude_config()
            
            # Merge with defaults for any missing common servers
            for name, default_server in self.default_servers.items():
                if name not in servers:
                    servers[name] = default_server
            
            return servers
    
    def validate_server_config(self, config: MCPServerConfig) -> List[str]:
        """
        Validate a server configuration
        
        Args:
            config: Server configuration to validate
            
        Returns:
            List of validation issues (empty if valid)
        """
        issues = []
        
        if not config.name:
            issues.append("Server name is required")
        
        if not config.command:
            issues.append("Server command is required")
        
        # Check for required environment variables
        if config.name == 'postman' and not config.env.get('POSTMAN_API_KEY'):
            issues.append("POSTMAN_API_KEY environment variable is required for Postman server")
        
        if config.name == 'github' and not config.env.get('GITHUB_PERSONAL_ACCESS_TOKEN'):
            issues.append("GITHUB_PERSONAL_ACCESS_TOKEN environment variable is required for GitHub server")
        
        if config.name == 'trello':
            if not config.env.get('TRELLO_API_KEY'):
                issues.append("TRELLO_API_KEY environment variable is required for Trello server")
            if not config.env.get('TRELLO_TOKEN'):
                issues.append("TRELLO_TOKEN environment variable is required for Trello server")
        
        return issues
    
    def create_config_template(self, output_path: str) -> None:
        """Create a configuration template file"""
        template = {
            "mcpServers": {
                "postman": {
                    "command": "npx",
                    "args": ["-y", "@postman/mcp-server"],
                    "env": {
                        "POSTMAN_API_KEY": "your_postman_api_key_here"
                    }
                },
                "github": {
                    "command": "npx", 
                    "args": ["-y", "@modelcontextprotocol/server-github"],
                    "env": {
                        "GITHUB_PERSONAL_ACCESS_TOKEN": "your_github_token_here"
                    }
                },
                "memory": {
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-memory"]
                },
                "brave_search": {
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-brave-search"],
                    "env": {
                        "BRAVE_API_KEY": "your_brave_api_key_here"
                    }
                }
            }
        }
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(template, f, indent=2)
            
            self.logger.info(f"Created configuration template at: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Error creating config template: {e}")
    
    def get_enabled_servers(self, config_source: Optional[str] = None) -> Dict[str, MCPServerConfig]:
        """Get only enabled server configurations"""
        all_servers = self.get_server_configs(config_source)
        return {name: config for name, config in all_servers.items() if config.enabled}
    
    def get_config_summary(self, config_source: Optional[str] = None) -> Dict[str, Any]:
        """Get a summary of the current configuration"""
        servers = self.get_server_configs(config_source)
        enabled_servers = self.get_enabled_servers(config_source)
        
        validation_issues = {}
        for name, config in servers.items():
            issues = self.validate_server_config(config)
            if issues:
                validation_issues[name] = issues
        
        return {
            'total_servers': len(servers),
            'enabled_servers': len(enabled_servers),
            'server_names': list(servers.keys()),
            'enabled_server_names': list(enabled_servers.keys()),
            'validation_issues': validation_issues,
            'has_claude_config': self.find_claude_config() is not None
        }


# Global instance for singleton access
_config_reader_instance = None

def get_config_reader() -> MCPConfigReader:
    """Get the global config reader instance"""
    global _config_reader_instance
    if _config_reader_instance is None:
        _config_reader_instance = MCPConfigReader()
    return _config_reader_instance
