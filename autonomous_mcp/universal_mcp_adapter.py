"""
Universal MCP Adapter

This module adapts to any MCP server implementation, handling variations
and quirks in different server implementations while maintaining compatibility.
"""

import logging
import re
from typing import Dict, List, Optional, Any, Set, Callable
from dataclasses import dataclass, field
import json


@dataclass
class ServerQuirks:
    """Known quirks and adaptations for specific servers"""
    name: str
    response_normalizations: Dict[str, Callable] = field(default_factory=dict)
    error_mappings: Dict[str, str] = field(default_factory=dict)
    capability_overrides: Dict[str, Any] = field(default_factory=dict)
    command_variations: List[str] = field(default_factory=list)


class UniversalMCPAdapter:
    """
    Adapt to any MCP server implementation
    
    Provides compatibility layer for different MCP server implementations,
    handling variations in responses, error codes, and capabilities.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.known_quirks: Dict[str, ServerQuirks] = {}
        self._setup_known_quirks()
    
    def _setup_known_quirks(self):
        """Setup known quirks for common MCP servers"""
        
        # GitHub MCP Server quirks
        self.known_quirks["github"] = ServerQuirks(
            name="github",
            command_variations=["@modelcontextprotocol/server-github", "mcp-server-github"],
            error_mappings={
                "API_ERROR": "GITHUB_API_ERROR",
                "RATE_LIMITED": "GITHUB_RATE_LIMIT"
            }
        )
        
        # Filesystem MCP Server quirks
        self.known_quirks["filesystem"] = ServerQuirks(
            name="filesystem",
            command_variations=["@modelcontextprotocol/server-filesystem", "mcp-server-filesystem"],
            error_mappings={
                "ENOENT": "FILE_NOT_FOUND",
                "EACCES": "PERMISSION_DENIED"
            }
        )
        
        # SQLite MCP Server quirks
        self.known_quirks["sqlite"] = ServerQuirks(
            name="sqlite",
            command_variations=["@modelcontextprotocol/server-sqlite", "mcp-server-sqlite"],
            error_mappings={
                "SQLITE_ERROR": "DATABASE_ERROR"
            }
        )
        
        # Brave Search MCP Server quirks
        self.known_quirks["brave-search"] = ServerQuirks(
            name="brave-search",
            command_variations=["@modelcontextprotocol/server-brave-search", "mcp-server-brave-search"],
            capability_overrides={
                "search_timeout": 30
            }
        )
    
    async def detect_server_capabilities(self, server_name: str) -> Dict[str, Any]:
        """
        Auto-detect server capabilities
        
        Args:
            server_name: Name of the server
            
        Returns:
            Dictionary of detected capabilities
        """
        capabilities = {
            "detected_type": "unknown",
            "supports_tools": False,
            "supports_resources": False,
            "supports_prompts": False,
            "estimated_tool_count": 0,
            "command_variations": [],
            "quirks_applied": False
        }
        
        try:
            # Check if we have known quirks for this server
            server_type = self._identify_server_type(server_name)
            if server_type in self.known_quirks:
                quirks = self.known_quirks[server_type]
                capabilities["detected_type"] = server_type
                capabilities["command_variations"] = quirks.command_variations
                capabilities["quirks_applied"] = True
                
                # Apply capability overrides
                capabilities.update(quirks.capability_overrides)
            
            # Detect capabilities based on server name patterns
            name_lower = server_name.lower()
            
            if any(keyword in name_lower for keyword in ["github", "git"]):
                capabilities["supports_tools"] = True
                capabilities["estimated_tool_count"] = 15
                capabilities["detected_type"] = "github"
            elif any(keyword in name_lower for keyword in ["filesystem", "file", "fs"]):
                capabilities["supports_tools"] = True
                capabilities["supports_resources"] = True
                capabilities["estimated_tool_count"] = 10
                capabilities["detected_type"] = "filesystem"
            elif any(keyword in name_lower for keyword in ["sqlite", "database", "db"]):
                capabilities["supports_tools"] = True
                capabilities["estimated_tool_count"] = 8
                capabilities["detected_type"] = "database"
            elif any(keyword in name_lower for keyword in ["search", "brave", "web"]):
                capabilities["supports_tools"] = True
                capabilities["estimated_tool_count"] = 5
                capabilities["detected_type"] = "search"
            elif any(keyword in name_lower for keyword in ["memory", "knowledge"]):
                capabilities["supports_tools"] = True
                capabilities["supports_resources"] = True
                capabilities["estimated_tool_count"] = 12
                capabilities["detected_type"] = "memory"
            else:
                # Generic server - assume basic tool support
                capabilities["supports_tools"] = True
                capabilities["estimated_tool_count"] = 5
            
            self.logger.info(f"✅ Detected capabilities for {server_name}: {capabilities['detected_type']}")
            
        except Exception as e:
            self.logger.error(f"Failed to detect capabilities for {server_name}: {e}")
        
        return capabilities
    
    async def adapt_to_server_quirks(self, server_name: str, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle server-specific variations
        
        Args:
            server_name: Name of the server
            response: Raw response from server
            
        Returns:
            Adapted response
        """
        try:
            server_type = self._identify_server_type(server_name)
            
            if server_type in self.known_quirks:
                quirks = self.known_quirks[server_type]
                
                # Apply error mappings
                if "error" in response:
                    error = response["error"]
                    if isinstance(error, dict) and "code" in error:
                        original_code = error["code"]
                        if original_code in quirks.error_mappings:
                            error["code"] = quirks.error_mappings[original_code]
                            error["original_code"] = original_code
                
                # Apply response normalizations
                for field, normalizer in quirks.response_normalizations.items():
                    if field in response:
                        response[field] = normalizer(response[field])
            
            return response
            
        except Exception as e:
            self.logger.error(f"Failed to adapt response for {server_name}: {e}")
            return response
    
    async def normalize_responses(self, server_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize different response formats
        
        Args:
            server_response: Raw server response
            
        Returns:
            Normalized response
        """
        normalized = server_response.copy()
        
        try:
            # Normalize tool list responses
            if "result" in normalized and "tools" in normalized["result"]:
                tools = normalized["result"]["tools"]
                normalized_tools = []
                
                for tool in tools:
                    normalized_tool = self._normalize_tool_definition(tool)
                    normalized_tools.append(normalized_tool)
                
                normalized["result"]["tools"] = normalized_tools
            
            # Normalize tool call responses
            elif "result" in normalized and isinstance(normalized["result"], dict):
                result = normalized["result"]
                
                # Ensure content is always an array
                if "content" in result and not isinstance(result["content"], list):
                    result["content"] = [result["content"]]
                
                # Normalize content items
                if "content" in result and isinstance(result["content"], list):
                    normalized_content = []
                    for item in result["content"]:
                        normalized_item = self._normalize_content_item(item)
                        normalized_content.append(normalized_item)
                    result["content"] = normalized_content
            
            # Normalize error responses
            elif "error" in normalized:
                error = normalized["error"]
                if isinstance(error, dict):
                    # Ensure error has required fields
                    if "code" not in error:
                        error["code"] = -32603  # Internal error
                    if "message" not in error:
                        error["message"] = "Unknown error"
            
        except Exception as e:
            self.logger.error(f"Failed to normalize response: {e}")
        
        return normalized
    
    def _identify_server_type(self, server_name: str) -> str:
        """Identify server type from name"""
        name_lower = server_name.lower()
        
        for server_type, quirks in self.known_quirks.items():
            if server_type in name_lower:
                return server_type
            
            # Check command variations
            for variation in quirks.command_variations:
                if variation.lower() in name_lower:
                    return server_type
        
        # Try pattern matching for common types
        if re.search(r'github|git', name_lower):
            return "github"
        elif re.search(r'file|fs', name_lower):
            return "filesystem"
        elif re.search(r'sql|db', name_lower):
            return "sqlite"
        elif re.search(r'search|brave', name_lower):
            return "brave-search"
        
        return "unknown"
    
    def _normalize_tool_definition(self, tool: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize a tool definition"""
        normalized = tool.copy()
        
        # Ensure required fields
        if "name" not in normalized:
            normalized["name"] = "unknown_tool"
        
        if "description" not in normalized:
            normalized["description"] = "No description available"
        
        # Normalize input schema
        if "inputSchema" in normalized:
            schema = normalized["inputSchema"]
            if not isinstance(schema, dict):
                normalized["inputSchema"] = {"type": "object", "properties": {}}
            elif "type" not in schema:
                schema["type"] = "object"
        else:
            normalized["inputSchema"] = {"type": "object", "properties": {}}
        
        return normalized
    
    def _normalize_content_item(self, item: Any) -> Dict[str, Any]:
        """Normalize a content item"""
        if isinstance(item, str):
            return {"type": "text", "text": item}
        elif isinstance(item, dict):
            # Ensure type field
            if "type" not in item:
                if "text" in item:
                    item["type"] = "text"
                elif "data" in item:
                    item["type"] = "blob"
                else:
                    item["type"] = "text"
                    item["text"] = str(item)
            return item
        else:
            return {"type": "text", "text": str(item)}
    
    def add_custom_quirks(self, server_name: str, quirks: ServerQuirks):
        """Add custom quirks for a server"""
        self.known_quirks[server_name] = quirks
        self.logger.info(f"Added custom quirks for {server_name}")
    
    def get_server_recommendations(self, server_name: str) -> Dict[str, Any]:
        """Get recommendations for configuring a server"""
        server_type = self._identify_server_type(server_name)
        
        recommendations = {
            "server_type": server_type,
            "recommended_timeout": 30,
            "retry_strategy": "exponential_backoff",
            "health_check_interval": 60,
            "error_handling": "graceful_degradation"
        }
        
        # Type-specific recommendations
        if server_type == "github":
            recommendations.update({
                "recommended_timeout": 45,
                "rate_limit_aware": True,
                "requires_auth": True
            })
        elif server_type == "filesystem":
            recommendations.update({
                "recommended_timeout": 15,
                "path_validation": True,
                "permission_checks": True
            })
        elif server_type == "sqlite":
            recommendations.update({
                "recommended_timeout": 20,
                "transaction_support": True,
                "schema_validation": True
            })
        elif server_type == "brave-search":
            recommendations.update({
                "recommended_timeout": 30,
                "requires_api_key": True,
                "rate_limit_aware": True
            })
        
        return recommendations
    
    async def validate_server_compatibility(self, server_response: Dict[str, Any]) -> Dict[str, Any]:
        """Validate server compatibility and suggest adaptations"""
        compatibility = {
            "is_compatible": True,
            "issues": [],
            "suggestions": [],
            "confidence": 1.0
        }
        
        try:
            # Check basic MCP compliance
            if "jsonrpc" not in server_response:
                compatibility["issues"].append("Missing JSON-RPC version")
                compatibility["is_compatible"] = False
            
            if "result" not in server_response and "error" not in server_response:
                compatibility["issues"].append("Response missing result or error")
                compatibility["is_compatible"] = False
            
            # Check for common compatibility issues
            if "result" in server_response:
                result = server_response["result"]
                
                # Check protocol version
                if "protocolVersion" in result:
                    version = result["protocolVersion"]
                    if version not in ["2024-11-05", "2024-10-07"]:
                        compatibility["suggestions"].append(f"Consider updating protocol version from {version}")
                        compatibility["confidence"] *= 0.9
                
                # Check capabilities structure
                if "capabilities" in result:
                    caps = result["capabilities"]
                    if not isinstance(caps, dict):
                        compatibility["issues"].append("Capabilities should be an object")
                        compatibility["confidence"] *= 0.7
            
        except Exception as e:
            compatibility["issues"].append(f"Compatibility check error: {e}")
            compatibility["is_compatible"] = False
        
        return compatibility
