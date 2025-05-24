"""
Enhanced Error Handling System for Autonomous MCP Agent

This module provides production-grade error handling, recovery mechanisms,
and intelligent fallback strategies for robust autonomous operations.

Key Features:
- Smart tool substitution when tools fail
- Enhanced error context and human-readable messages  
- Advanced retry strategies with circuit breaker patterns
- Production monitoring and health checks
- Network and API resilience handling
"""

import asyncio
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Set, Any, Callable, Union
from dataclasses import dataclass, field
from collections import defaultdict, deque
import logging
import json

from .discovery import ToolDiscovery, DiscoveredTool
from .planner import ToolCall, ExecutionPlan
from .executor import ChainExecutor, ExecutionStatus, ExecutionResult


class ErrorSeverity(Enum):
    """Error severity levels for prioritization and handling"""
    LOW = "low"           # Minor issues, continue execution
    MEDIUM = "medium"     # Moderate issues, try alternatives  
    HIGH = "high"         # Major issues, require intervention
    CRITICAL = "critical" # System-level issues, halt execution


class ErrorCategory(Enum):
    """Enhanced error categorization for intelligent handling"""
    # Network and connectivity
    NETWORK_ERROR = "network_error"
    CONNECTION_TIMEOUT = "connection_timeout"
    API_UNAVAILABLE = "api_unavailable"
    RATE_LIMITED = "rate_limited"
    
    # Tool-specific errors
    TOOL_NOT_FOUND = "tool_not_found"
    TOOL_UNAVAILABLE = "tool_unavailable"
    INVALID_ARGUMENTS = "invalid_arguments"
    TOOL_EXECUTION_ERROR = "tool_execution_error"
    
    # System errors
    PERMISSION_DENIED = "permission_denied"
    RESOURCE_EXHAUSTED = "resource_exhausted"
    CONFIGURATION_ERROR = "configuration_error"
    
    # Logic and planning errors
    PLANNING_ERROR = "planning_error"
    DEPENDENCY_ERROR = "dependency_error"
    VALIDATION_ERROR = "validation_error"
    
    # Unknown/unexpected
    UNKNOWN_ERROR = "unknown_error"


@dataclass
class ErrorContext:
    """Rich error context with recovery suggestions"""
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    tool_name: Optional[str] = None
    tool_call: Optional[ToolCall] = None
    original_exception: Optional[Exception] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    recovery_suggestions: List[str] = field(default_factory=list)
    alternative_tools: List[str] = field(default_factory=list)
    retry_recommended: bool = True
    circuit_breaker_triggered: bool = False
    
    def to_human_readable(self) -> str:
        """Convert error to human-readable format"""
        base_msg = f"[{self.severity.value.upper()}] {self.message}"
        
        if self.tool_name:
            base_msg += f" (Tool: {self.tool_name})"
            
        if self.recovery_suggestions:
            base_msg += "\n\nSuggested actions:"
            for i, suggestion in enumerate(self.recovery_suggestions, 1):
                base_msg += f"\n  {i}. {suggestion}"
                
        if self.alternative_tools:
            base_msg += f"\n\nAlternative tools available: {', '.join(self.alternative_tools)}"
            
        return base_msg


@dataclass 
class CircuitBreakerState:
    """Circuit breaker state for preventing cascade failures"""
    failure_count: int = 0
    last_failure_time: Optional[datetime] = None
    state: str = "closed"  # closed, open, half_open
    failure_threshold: int = 5
    recovery_timeout: timedelta = field(default_factory=lambda: timedelta(minutes=5))
    
    def should_allow_request(self) -> bool:
        """Check if requests should be allowed through circuit breaker"""
        if self.state == "closed":
            return True
        elif self.state == "open":
            if (self.last_failure_time and self.recovery_timeout and
               datetime.utcnow() - self.last_failure_time > self.recovery_timeout):
                self.state = "half_open"
                return True
            return False
        else:  # half_open
            return True
    
    def record_success(self):
        """Record successful execution"""
        self.failure_count = 0
        self.state = "closed"
        
    def record_failure(self):
        """Record failed execution"""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "open"


@dataclass
class ToolHealthMetrics:
    """Health and performance metrics for tools"""
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    average_response_time: float = 0.0
    last_success_time: Optional[datetime] = None
    last_failure_time: Optional[datetime] = None
    recent_errors: deque = field(default_factory=lambda: deque(maxlen=10))
    circuit_breaker: CircuitBreakerState = field(default_factory=CircuitBreakerState)
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage"""
        if self.total_calls == 0:
            return 0.0
        return (self.successful_calls / self.total_calls) * 100
    
    @property 
    def is_healthy(self) -> bool:
        """Check if tool is considered healthy"""
        return (self.success_rate >= 80.0 and 
                self.circuit_breaker.state != "open")


class ToolSubstitutionEngine:
    """Smart tool substitution system for handling tool failures"""
    
    def __init__(self, discovery_system: ToolDiscovery):
        self.discovery_system = discovery_system
        self.substitution_rules = self._build_substitution_rules()
        
    def _build_substitution_rules(self) -> Dict[str, List[str]]:
        """Build intelligent tool substitution rules"""
        return {
            # Web search alternatives
            "brave_web_search": ["duckduckgo_web_search", "web_search"],
            "duckduckgo_web_search": ["brave_web_search", "web_search"],
            "web_search": ["brave_web_search", "duckduckgo_web_search"],
            
            # File operations
            "read_file": ["read_multiple_files"],
            "write_file": ["edit_block"],
            
            # Search operations  
            "firecrawl_search": ["brave_web_search", "duckduckgo_web_search"],
            "github_search_repositories": ["search_repositories"],
            
            # Memory operations
            "create_entities": ["add_observations"],
            
            # Add more substitution rules as needed
        }
    
    def find_alternatives(self, failed_tool: str, required_capabilities: List[str] = None) -> List[DiscoveredTool]:
        """Find alternative tools for a failed tool"""
        alternatives = []
        
        # Check predefined substitution rules
        if failed_tool in self.substitution_rules:
            rule_alternatives = self.substitution_rules[failed_tool]
            for alt_name in rule_alternatives:
                alt_tool = self.discovery_system.get_tool_by_name(alt_name)
                if alt_tool:
                    alternatives.append(alt_tool)
        
        # Find tools with similar capabilities
        if required_capabilities:
            similar_tools = self.discovery_system.find_tools_by_capabilities(required_capabilities)
            for tool in similar_tools:
                if tool.name != failed_tool and tool not in alternatives:
                    alternatives.append(tool)
        
        # Find tools in same category
        failed_tool_obj = self.discovery_system.get_tool_by_name(failed_tool)
        if failed_tool_obj:
            category_tools = self.discovery_system.get_tools_by_category(failed_tool_obj.category)
            for tool in category_tools:
                if tool.name != failed_tool and tool not in alternatives:
                    alternatives.append(tool)
        
        return alternatives


class EnhancedErrorHandler:
    """Production-grade error handling system"""
    
    def __init__(self, discovery_system: ToolDiscovery):
        self.discovery_system = discovery_system
        self.substitution_engine = ToolSubstitutionEngine(discovery_system)
        self.tool_metrics: Dict[str, ToolHealthMetrics] = defaultdict(ToolHealthMetrics)
        self.error_history: deque = deque(maxlen=1000)
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.max_retries = 3
        self.base_retry_delay = 1.0
        self.max_retry_delay = 30.0
        self.enable_substitution = True
        self.enable_circuit_breaker = True
        
    def categorize_error(self, error: Exception, tool_name: str = None) -> ErrorCategory:
        """Intelligently categorize errors for appropriate handling"""
        error_msg = str(error).lower()
        error_type = type(error).__name__
        
        # Tool-specific errors (check these before general patterns)
        if "tool not found" in error_msg or "unknown tool" in error_msg:
            return ErrorCategory.TOOL_NOT_FOUND
        if "invalid argument" in error_msg or "parameter" in error_msg:
            return ErrorCategory.INVALID_ARGUMENTS
        if "permission denied" in error_msg or "unauthorized" in error_msg:
            return ErrorCategory.PERMISSION_DENIED
            
        # Network and connectivity errors (after tool-specific checks)
        if any(keyword in error_msg for keyword in ["timeout", "connection", "network"]):
            return ErrorCategory.CONNECTION_TIMEOUT
        if any(keyword in error_msg for keyword in ["unavailable", "not found", "404"]):
            return ErrorCategory.API_UNAVAILABLE
        if any(keyword in error_msg for keyword in ["rate limit", "too many requests", "429"]):
            return ErrorCategory.RATE_LIMITED
            
        # System errors
        if "resource" in error_msg and "exhausted" in error_msg:
            return ErrorCategory.RESOURCE_EXHAUSTED
        if "configuration" in error_msg or "config" in error_msg:
            return ErrorCategory.CONFIGURATION_ERROR
            
        # Default to tool execution error
        return ErrorCategory.TOOL_EXECUTION_ERROR
    
    def determine_severity(self, category: ErrorCategory, tool_name: str = None) -> ErrorSeverity:
        """Determine error severity based on category and context"""
        critical_categories = {ErrorCategory.RESOURCE_EXHAUSTED, ErrorCategory.CONFIGURATION_ERROR}
        high_categories = {ErrorCategory.PERMISSION_DENIED, ErrorCategory.PLANNING_ERROR}
        medium_categories = {ErrorCategory.API_UNAVAILABLE, ErrorCategory.TOOL_UNAVAILABLE, 
                           ErrorCategory.CONNECTION_TIMEOUT}
        
        if category in critical_categories:
            return ErrorSeverity.CRITICAL
        elif category in high_categories:
            return ErrorSeverity.HIGH
        elif category in medium_categories:
            return ErrorSeverity.MEDIUM
        else:
            return ErrorSeverity.LOW
    
    def generate_recovery_suggestions(self, context: ErrorContext) -> List[str]:
        """Generate intelligent recovery suggestions based on error context"""
        suggestions = []
        
        if context.category == ErrorCategory.CONNECTION_TIMEOUT:
            suggestions.extend([
                "Check network connectivity",
                "Retry with increased timeout",
                "Try alternative service endpoint"
            ])
        elif context.category == ErrorCategory.RATE_LIMITED:
            suggestions.extend([
                "Wait before retrying",
                "Reduce request frequency", 
                "Use alternative API if available"
            ])
        elif context.category == ErrorCategory.TOOL_NOT_FOUND:
            suggestions.extend([
                "Verify tool name spelling",
                "Check if tool is properly installed",
                "Use alternative tool with similar functionality"
            ])
        elif context.category == ErrorCategory.INVALID_ARGUMENTS:
            suggestions.extend([
                "Verify argument format and types",
                "Check tool documentation for required parameters",
                "Validate input data before tool execution"
            ])
        elif context.category == ErrorCategory.API_UNAVAILABLE:
            suggestions.extend([
                "Check service status page",
                "Try again later",
                "Use backup service if available"
            ])
        
        # Add tool substitution suggestions
        if context.tool_name and self.enable_substitution:
            alternatives = self.substitution_engine.find_alternatives(context.tool_name)
            if alternatives:
                alt_names = [tool.name for tool in alternatives[:3]]  # Limit to top 3
                suggestions.append(f"Consider using alternative tools: {', '.join(alt_names)}")
        
        return suggestions
    
    def create_error_context(self, error: Exception, tool_name: str = None, 
                           tool_call: ToolCall = None) -> ErrorContext:
        """Create comprehensive error context with recovery information"""
        category = self.categorize_error(error, tool_name)
        severity = self.determine_severity(category, tool_name)
        
        context = ErrorContext(
            category=category,
            severity=severity,
            message=str(error),
            tool_name=tool_name,
            tool_call=tool_call,
            original_exception=error,
            retry_recommended=self._should_retry(category, tool_name)
        )
        
        # Generate recovery suggestions
        context.recovery_suggestions = self.generate_recovery_suggestions(context)
        
        # Find alternative tools
        if tool_name and self.enable_substitution:
            alternatives = self.substitution_engine.find_alternatives(tool_name)
            context.alternative_tools = [tool.name for tool in alternatives]
        
        # Check circuit breaker
        if tool_name and self.enable_circuit_breaker:
            metrics = self.tool_metrics[tool_name]
            context.circuit_breaker_triggered = not metrics.circuit_breaker.should_allow_request()
        
        return context
    
    def _should_retry(self, category: ErrorCategory, tool_name: str = None) -> bool:
        """Determine if error should trigger a retry"""
        non_retryable = {
            ErrorCategory.PERMISSION_DENIED,
            ErrorCategory.INVALID_ARGUMENTS,
            ErrorCategory.CONFIGURATION_ERROR,
            ErrorCategory.TOOL_NOT_FOUND
        }
        
        if category in non_retryable:
            return False
            
        # Check circuit breaker
        if tool_name and self.enable_circuit_breaker:
            metrics = self.tool_metrics[tool_name]
            return metrics.circuit_breaker.should_allow_request()
            
        return True
    
    def record_tool_execution(self, tool_name: str, success: bool, 
                            response_time: float, error: Exception = None):
        """Record tool execution metrics for health monitoring"""
        metrics = self.tool_metrics[tool_name]
        metrics.total_calls += 1
        
        if success:
            metrics.successful_calls += 1
            metrics.last_success_time = datetime.utcnow()
            metrics.circuit_breaker.record_success()
        else:
            metrics.failed_calls += 1
            metrics.last_failure_time = datetime.utcnow()
            metrics.circuit_breaker.record_failure()
            
            if error:
                metrics.recent_errors.append({
                    'timestamp': datetime.utcnow(),
                    'error': str(error),
                    'category': self.categorize_error(error, tool_name).value
                })
        
        # Update average response time
        if metrics.total_calls == 1:
            metrics.average_response_time = response_time
        else:
            metrics.average_response_time = (
                (metrics.average_response_time * (metrics.total_calls - 1) + response_time) 
                / metrics.total_calls
            )
    
    def get_tool_health_report(self) -> Dict[str, Dict[str, Any]]:
        """Generate comprehensive tool health report"""
        report = {}
        
        for tool_name, metrics in self.tool_metrics.items():
            report[tool_name] = {
                'health_status': 'healthy' if metrics.is_healthy else 'unhealthy',
                'success_rate': round(metrics.success_rate, 2),
                'total_calls': metrics.total_calls,
                'average_response_time': round(metrics.average_response_time, 3),
                'circuit_breaker_state': metrics.circuit_breaker.state,
                'recent_errors': list(metrics.recent_errors)[-3:],  # Last 3 errors
                'last_success': metrics.last_success_time.isoformat() if metrics.last_success_time else None,
                'last_failure': metrics.last_failure_time.isoformat() if metrics.last_failure_time else None
            }
        
        return report
    
    def export_error_metrics(self) -> Dict[str, Any]:
        """Export error handling metrics for analysis"""
        return {
            'tool_metrics': {
                tool: {
                    'total_calls': metrics.total_calls,
                    'success_rate': metrics.success_rate,
                    'average_response_time': metrics.average_response_time,
                    'circuit_breaker_state': metrics.circuit_breaker.state,
                    'failure_count': metrics.circuit_breaker.failure_count
                }
                for tool, metrics in self.tool_metrics.items()
            },
            'error_history_count': len(self.error_history),
            'substitution_rules': len(self.substitution_engine.substitution_rules)
        }
