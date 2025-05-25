"""
MCP Protocol Validator

This module ensures MCP protocol standard compliance and validates server
responses according to the MCP specification.
"""

import json
import logging
from typing import Dict, List, Optional, Any, Set, Union
from dataclasses import dataclass
from datetime import datetime
import re


@dataclass
class ValidationResult:
    """Result of a validation check"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    details: Optional[Dict[str, Any]] = None


# Alias for compatibility with __init__.py imports
ProtocolValidationResult = ValidationResult


class MCPProtocolValidator:
    """
    Ensure MCP protocol standard compliance
    
    Validates MCP messages, server responses, and tool definitions
    according to the Model Context Protocol specification.
    """
    
    # Supported MCP protocol versions
    SUPPORTED_VERSIONS = ["2024-11-05", "2024-10-07"]
    
    # Required fields for different message types
    REQUIRED_FIELDS = {
        "request": {"jsonrpc", "id", "method"},
        "response": {"jsonrpc", "id"},
        "notification": {"jsonrpc", "method"},
        "error_response": {"jsonrpc", "id", "error"}
    }
    
    # Valid MCP methods
    VALID_METHODS = {
        "initialize", "initialized", "tools/list", "tools/call",
        "resources/list", "resources/read", "resources/subscribe",
        "resources/unsubscribe", "prompts/list", "prompts/get",
        "notifications/cancelled", "notifications/progress"
    }
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
    
    async def validate_server_handshake(self, server_response: Dict[str, Any]) -> ValidationResult:
        """
        Validate proper MCP initialize response
        
        Args:
            server_response: Server's response to initialize request
            
        Returns:
            ValidationResult with validation details
        """
        errors = []
        warnings = []
        
        try:
            # Check basic JSON-RPC structure
            basic_validation = self._validate_json_rpc_structure(server_response)
            if not basic_validation.is_valid:
                errors.extend(basic_validation.errors)
                return ValidationResult(False, errors, warnings)
            
            # Check for result field in initialize response
            if "result" not in server_response:
                errors.append("Initialize response missing 'result' field")
                return ValidationResult(False, errors, warnings)
            
            result = server_response["result"]
            
            # Validate protocol version
            protocol_version = result.get("protocolVersion")
            if not protocol_version:
                errors.append("Initialize response missing 'protocolVersion'")
            elif protocol_version not in self.SUPPORTED_VERSIONS:
                warnings.append(f"Unsupported protocol version: {protocol_version}")
            
            # Validate capabilities
            capabilities = result.get("capabilities", {})
            if not isinstance(capabilities, dict):
                errors.append("Capabilities must be an object")
            else:
                # Validate individual capability sections
                for cap_name in ["tools", "resources", "prompts"]:
                    if cap_name in capabilities:
                        if not isinstance(capabilities[cap_name], dict):
                            errors.append(f"Capability '{cap_name}' must be an object")
            
            # Validate server info
            server_info = result.get("serverInfo")
            if server_info:
                if not isinstance(server_info, dict):
                    errors.append("serverInfo must be an object")
                else:
                    if "name" not in server_info:
                        warnings.append("serverInfo missing recommended 'name' field")
                    if "version" not in server_info:
                        warnings.append("serverInfo missing recommended 'version' field")
            
            self.logger.debug(f"Handshake validation: {len(errors)} errors, {len(warnings)} warnings")
            
        except Exception as e:
            errors.append(f"Validation error: {e}")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            details={"protocol_version": protocol_version, "capabilities": capabilities}
        )
    
    async def validate_tool_schema(self, tool_definition: Dict[str, Any]) -> ValidationResult:
        """
        Validate tool follows MCP schema
        
        Args:
            tool_definition: Tool definition to validate
            
        Returns:
            ValidationResult with validation details
        """
        errors = []
        warnings = []
        
        try:
            # Check required fields
            required_fields = {"name", "description"}
            for field in required_fields:
                if field not in tool_definition:
                    errors.append(f"Tool definition missing required field: {field}")
            
            # Validate name
            name = tool_definition.get("name")
            if name:
                if not isinstance(name, str):
                    errors.append("Tool name must be a string")
                elif not re.match(r"^[a-zA-Z_][a-zA-Z0-9_-]*$", name):
                    errors.append("Tool name contains invalid characters")
            
            # Validate description
            description = tool_definition.get("description")
            if description and not isinstance(description, str):
                errors.append("Tool description must be a string")
            
            # Validate input schema
            input_schema = tool_definition.get("inputSchema")
            if input_schema:
                schema_validation = self._validate_json_schema(input_schema)
                if not schema_validation.is_valid:
                    errors.extend([f"Input schema: {err}" for err in schema_validation.errors])
            
            self.logger.debug(f"Tool schema validation for '{name}': {len(errors)} errors, {len(warnings)} warnings")
            
        except Exception as e:
            errors.append(f"Tool validation error: {e}")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            details={"tool_name": tool_definition.get("name")}
        )
    
    async def handle_protocol_versions(self, server_version: str) -> ValidationResult:
        """
        Handle different MCP protocol versions
        
        Args:
            server_version: Protocol version reported by server
            
        Returns:
            ValidationResult with compatibility details
        """
        errors = []
        warnings = []
        details = {"server_version": server_version, "supported": False}
        
        try:
            if server_version in self.SUPPORTED_VERSIONS:
                details["supported"] = True
                self.logger.info(f"✅ Protocol version {server_version} is fully supported")
            else:
                # Check if it's a newer version we might partially support
                if self._is_newer_version(server_version, max(self.SUPPORTED_VERSIONS)):
                    warnings.append(f"Server uses newer protocol version {server_version}")
                    warnings.append("Some features may not be available")
                    details["compatibility"] = "partial"
                else:
                    errors.append(f"Unsupported protocol version: {server_version}")
                    details["compatibility"] = "none"
            
        except Exception as e:
            errors.append(f"Version handling error: {e}")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            details=details
        )
    
    def _validate_json_rpc_structure(self, message: Dict[str, Any]) -> ValidationResult:
        """Validate basic JSON-RPC 2.0 structure"""
        errors = []
        warnings = []
        
        # Check jsonrpc field
        if "jsonrpc" not in message:
            errors.append("Missing 'jsonrpc' field")
        elif message["jsonrpc"] != "2.0":
            errors.append(f"Invalid jsonrpc version: {message['jsonrpc']}")
        
        # Determine message type and validate accordingly
        has_id = "id" in message
        has_method = "method" in message
        has_result = "result" in message
        has_error = "error" in message
        
        if has_method and not has_result and not has_error:
            # Request or notification
            if has_id:
                # Request
                required = self.REQUIRED_FIELDS["request"]
            else:
                # Notification
                required = self.REQUIRED_FIELDS["notification"]
        elif has_id and (has_result or has_error):
            # Response
            if has_error:
                required = self.REQUIRED_FIELDS["error_response"]
            else:
                required = self.REQUIRED_FIELDS["response"]
        else:
            errors.append("Invalid message structure")
            return ValidationResult(False, errors, warnings)
        
        # Check required fields
        for field in required:
            if field not in message:
                errors.append(f"Missing required field: {field}")
        
        return ValidationResult(len(errors) == 0, errors, warnings)
    
    def _validate_json_schema(self, schema: Dict[str, Any]) -> ValidationResult:
        """Validate JSON Schema structure"""
        errors = []
        warnings = []
        
        # Basic schema validation
        if not isinstance(schema, dict):
            errors.append("Schema must be an object")
            return ValidationResult(False, errors, warnings)
        
        # Check for type field
        if "type" not in schema:
            warnings.append("Schema missing 'type' field")
        
        # Validate properties if object type
        if schema.get("type") == "object":
            properties = schema.get("properties")
            if properties and not isinstance(properties, dict):
                errors.append("Properties must be an object")
        
        return ValidationResult(len(errors) == 0, errors, warnings)
    
    def _is_newer_version(self, version1: str, version2: str) -> bool:
        """Check if version1 is newer than version2"""
        try:
            # Simple date-based version comparison
            return version1 > version2
        except:
            return False
    
    async def validate_tool_call_request(self, request: Dict[str, Any]) -> ValidationResult:
        """Validate a tools/call request"""
        errors = []
        warnings = []
        
        try:
            # Validate basic structure
            basic_validation = self._validate_json_rpc_structure(request)
            if not basic_validation.is_valid:
                return basic_validation
            
            # Check method
            if request.get("method") != "tools/call":
                errors.append("Invalid method for tool call request")
            
            # Check params
            params = request.get("params", {})
            if not isinstance(params, dict):
                errors.append("Params must be an object")
            else:
                # Check required params
                if "name" not in params:
                    errors.append("Tool call missing 'name' parameter")
                if "arguments" not in params:
                    errors.append("Tool call missing 'arguments' parameter")
                elif not isinstance(params["arguments"], dict):
                    errors.append("Tool arguments must be an object")
        
        except Exception as e:
            errors.append(f"Tool call validation error: {e}")
        
        return ValidationResult(len(errors) == 0, errors, warnings)
    
    async def validate_tool_call_response(self, response: Dict[str, Any]) -> ValidationResult:
        """Validate a tools/call response"""
        errors = []
        warnings = []
        
        try:
            # Validate basic structure
            basic_validation = self._validate_json_rpc_structure(response)
            if not basic_validation.is_valid:
                return basic_validation
            
            # Check for result or error
            if "result" in response:
                result = response["result"]
                if not isinstance(result, dict):
                    errors.append("Tool call result must be an object")
                else:
                    # Check for content array
                    if "content" not in result:
                        warnings.append("Tool result missing 'content' field")
                    elif not isinstance(result["content"], list):
                        errors.append("Tool result content must be an array")
            elif "error" in response:
                error = response["error"]
                if not isinstance(error, dict):
                    errors.append("Error must be an object")
                else:
                    if "code" not in error:
                        errors.append("Error missing 'code' field")
                    if "message" not in error:
                        errors.append("Error missing 'message' field")
        
        except Exception as e:
            errors.append(f"Tool response validation error: {e}")
        
        return ValidationResult(len(errors) == 0, errors, warnings)
    
    def get_validation_summary(self, results: List[ValidationResult]) -> Dict[str, Any]:
        """Get summary of multiple validation results"""
        total_errors = sum(len(result.errors) for result in results)
        total_warnings = sum(len(result.warnings) for result in results)
        valid_count = sum(1 for result in results if result.is_valid)
        
        return {
            "total_validations": len(results),
            "valid_count": valid_count,
            "invalid_count": len(results) - valid_count,
            "total_errors": total_errors,
            "total_warnings": total_warnings,
            "success_rate": valid_count / len(results) if results else 0.0
        }
