"""
Error Recovery System for Autonomous MCP Agent

This module provides production-grade error handling, recovery mechanisms,
and intelligent fallback strategies for robust autonomous operations.

Key Features:
- Error classification and severity assessment
- Intelligent retry strategies with exponential backoff
- Tool substitution when tools fail
- Circuit breaker patterns for failing services
- Error context and human-readable explanations
- Recovery suggestion engine
"""

import asyncio
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Set, Any, Callable, Union, Tuple
from dataclasses import dataclass, field
from collections import defaultdict, deque
import logging
import json
import traceback

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
    AUTHENTICATION_ERROR = "authentication_error"
    PERMISSION_DENIED = "permission_denied"
    RESOURCE_EXHAUSTED = "resource_exhausted"
    DEPENDENCY_ERROR = "dependency_error"
    
    # Data and validation errors
    INVALID_DATA = "invalid_data"
    VALIDATION_ERROR = "validation_error"
    PARSING_ERROR = "parsing_error"
    
    # Generic fallback
    UNKNOWN_ERROR = "unknown_error"


@dataclass
class ErrorContext:
    """Comprehensive error context for intelligent recovery"""
    error_type: str
    error_message: str
    category: ErrorCategory
    severity: ErrorSeverity
    timestamp: datetime
    tool_name: Optional[str] = None
    tool_args: Optional[Dict[str, Any]] = None
    execution_context: Optional[Dict[str, Any]] = None
    stack_trace: Optional[str] = None
    retry_count: int = 0
    recoverable: bool = True
    suggested_recovery: Optional[str] = None
    human_explanation: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error context to dictionary"""
        return {
            'error_type': self.error_type,
            'error_message': self.error_message,
            'category': self.category.value,
            'severity': self.severity.value,
            'timestamp': self.timestamp.isoformat(),
            'tool_name': self.tool_name,
            'tool_args': self.tool_args,
            'execution_context': self.execution_context,
            'stack_trace': self.stack_trace,
            'retry_count': self.retry_count,
            'recoverable': self.recoverable,
            'suggested_recovery': self.suggested_recovery,
            'human_explanation': self.human_explanation
        }


@dataclass
class RecoveryStrategy:
    """Defines a recovery strategy for error handling"""
    name: str
    description: str
    max_retries: int
    backoff_factor: float
    timeout_seconds: float
    applicable_categories: Set[ErrorCategory]
    recovery_actions: List[str]
    fallback_tools: Optional[List[str]] = None
    
    def is_applicable(self, error_context: ErrorContext) -> bool:
        """Check if this strategy applies to the given error"""
        return error_context.category in self.applicable_categories


class ErrorRecoverySystem:
    """
    Production-grade error recovery system with intelligent strategies
    """
    
    def __init__(self, discovery: Optional[ToolDiscovery] = None):
        self.discovery = discovery
        self.error_history: List[ErrorContext] = []
        self.recovery_strategies: Dict[str, RecoveryStrategy] = {}
        self.tool_failure_counts: Dict[str, int] = defaultdict(int)
        self.circuit_breakers: Dict[str, bool] = defaultdict(bool)
        self.setup_default_strategies()
        
    def setup_default_strategies(self):
        """Setup default recovery strategies"""
        # Network retry strategy
        self.recovery_strategies['network_retry'] = RecoveryStrategy(
            name="network_retry",
            description="Retry network operations with exponential backoff",
            max_retries=3,
            backoff_factor=2.0,
            timeout_seconds=30.0,
            applicable_categories={
                ErrorCategory.NETWORK_ERROR,
                ErrorCategory.CONNECTION_TIMEOUT,
                ErrorCategory.API_UNAVAILABLE
            },
            recovery_actions=["wait", "retry", "check_connectivity"]
        )
        
        # Tool substitution strategy
        self.recovery_strategies['tool_substitution'] = RecoveryStrategy(
            name="tool_substitution",
            description="Find alternative tools when primary tool fails",
            max_retries=1,
            backoff_factor=1.0,
            timeout_seconds=10.0,
            applicable_categories={
                ErrorCategory.TOOL_NOT_FOUND,
                ErrorCategory.TOOL_UNAVAILABLE,
                ErrorCategory.TOOL_EXECUTION_ERROR
            },
            recovery_actions=["find_alternative", "substitute_tool"]
        )
        
        # Rate limit strategy
        self.recovery_strategies['rate_limit_backoff'] = RecoveryStrategy(
            name="rate_limit_backoff",
            description="Wait for rate limits to reset",
            max_retries=2,
            backoff_factor=5.0,
            timeout_seconds=120.0,
            applicable_categories={ErrorCategory.RATE_LIMITED},
            recovery_actions=["wait_exponential", "retry_after_cooldown"]
        )
        
        # Authentication retry strategy
        self.recovery_strategies['auth_retry'] = RecoveryStrategy(
            name="auth_retry",
            description="Retry authentication errors once",
            max_retries=1,
            backoff_factor=1.0,
            timeout_seconds=5.0,
            applicable_categories={
                ErrorCategory.AUTHENTICATION_ERROR,
                ErrorCategory.PERMISSION_DENIED
            },
            recovery_actions=["refresh_credentials", "retry_once"]
        )
    
    def categorize_error(self, error: Exception, tool_name: Optional[str] = None) -> ErrorCategory:
        """Intelligently categorize errors based on type and message"""
        error_msg = str(error).lower()
        error_type = type(error).__name__
        
        # Network-related errors - check timeout first for more specific matching
        if 'timeout' in error_msg or 'timed out' in error_msg:
            return ErrorCategory.CONNECTION_TIMEOUT
            
        if any(keyword in error_msg for keyword in [
            'connection', 'network', 'unreachable', 'dns'
        ]):
            return ErrorCategory.NETWORK_ERROR
        
        # API and service errors
        if any(keyword in error_msg for keyword in [
            'rate limit', 'quota', 'too many requests'
        ]):
            return ErrorCategory.RATE_LIMITED
        
        if any(keyword in error_msg for keyword in [
            'unavailable', 'service down', '503', '502', '504'
        ]):
            return ErrorCategory.API_UNAVAILABLE
        
        # Authentication errors
        if any(keyword in error_msg for keyword in [
            'unauthorized', 'forbidden', 'authentication', 'api key', 'token'
        ]):
            if any(perm in error_msg for perm in ['forbidden', '403']):
                return ErrorCategory.PERMISSION_DENIED
            return ErrorCategory.AUTHENTICATION_ERROR
        
        # Tool-specific errors
        if tool_name and any(keyword in error_msg for keyword in [
            'not found', 'unknown tool', 'invalid tool'
        ]):
            return ErrorCategory.TOOL_NOT_FOUND
        
        if any(keyword in error_msg for keyword in [
            'invalid argument', 'parameter', 'missing required'
        ]):
            return ErrorCategory.INVALID_ARGUMENTS
        
        # Data errors
        if any(keyword in error_msg for keyword in [
            'json', 'parse', 'decode', 'format', 'invalid data'
        ]):
            return ErrorCategory.PARSING_ERROR
        
        if any(keyword in error_msg for keyword in [
            'validation', 'invalid', 'constraint'
        ]):
            return ErrorCategory.VALIDATION_ERROR
        
        # Default fallback
        return ErrorCategory.UNKNOWN_ERROR
    
    def determine_severity(self, error_context: ErrorContext) -> ErrorSeverity:
        """Determine error severity based on category and context"""
        category = error_context.category
        
        # Critical errors that halt execution
        if category in [ErrorCategory.RESOURCE_EXHAUSTED, ErrorCategory.DEPENDENCY_ERROR]:
            return ErrorSeverity.CRITICAL
        
        # High severity errors requiring intervention
        if category in [
            ErrorCategory.AUTHENTICATION_ERROR,
            ErrorCategory.PERMISSION_DENIED,
            ErrorCategory.API_UNAVAILABLE
        ]:
            return ErrorSeverity.HIGH
        
        # Medium severity errors with alternatives
        if category in [
            ErrorCategory.TOOL_NOT_FOUND,
            ErrorCategory.TOOL_UNAVAILABLE,
            ErrorCategory.RATE_LIMITED,
            ErrorCategory.TOOL_EXECUTION_ERROR
        ]:
            return ErrorSeverity.MEDIUM
        
        # Low severity errors that are recoverable
        return ErrorSeverity.LOW
    
    def create_error_context(
        self,
        error: Exception,
        tool_name: Optional[str] = None,
        tool_args: Optional[Dict[str, Any]] = None,
        execution_context: Optional[Dict[str, Any]] = None
    ) -> ErrorContext:
        """Create comprehensive error context"""
        category = self.categorize_error(error, tool_name)
        
        context = ErrorContext(
            error_type=type(error).__name__,
            error_message=str(error),
            category=category,
            severity=self.determine_severity(ErrorContext(
                error_type=type(error).__name__,
                error_message=str(error),
                category=category,
                severity=ErrorSeverity.LOW,  # Temporary for determination
                timestamp=datetime.now()
            )),
            timestamp=datetime.now(),
            tool_name=tool_name,
            tool_args=tool_args,
            execution_context=execution_context,
            stack_trace=traceback.format_exc(),
            retry_count=0,
            recoverable=True
        )
        
        # Generate recovery suggestions and human explanations
        context.suggested_recovery = self.generate_recovery_suggestion(context)
        context.human_explanation = self.generate_human_explanation(context)
        
        return context
    
    def generate_recovery_suggestion(self, error_context: ErrorContext) -> str:
        """Generate intelligent recovery suggestions"""
        category = error_context.category
        
        suggestions = {
            ErrorCategory.NETWORK_ERROR: "Check network connectivity and retry with exponential backoff",
            ErrorCategory.CONNECTION_TIMEOUT: "Increase timeout duration and retry operation",
            ErrorCategory.API_UNAVAILABLE: "Wait for service recovery or use alternative API",
            ErrorCategory.RATE_LIMITED: "Implement rate limiting backoff and retry after cooldown",
            ErrorCategory.TOOL_NOT_FOUND: "Find alternative tools with similar capabilities",
            ErrorCategory.TOOL_UNAVAILABLE: "Check tool availability or use fallback options",
            ErrorCategory.INVALID_ARGUMENTS: "Validate and correct tool arguments",
            ErrorCategory.AUTHENTICATION_ERROR: "Refresh credentials and retry authentication",
            ErrorCategory.PERMISSION_DENIED: "Check permissions or use alternative access method",
            ErrorCategory.PARSING_ERROR: "Validate data format and implement robust parsing",
            ErrorCategory.VALIDATION_ERROR: "Review input data and fix validation issues"
        }
        
        return suggestions.get(category, "Manual intervention may be required")
    
    def generate_human_explanation(self, error_context: ErrorContext) -> str:
        """Generate human-readable error explanations"""
        category = error_context.category
        tool_name = error_context.tool_name or "the tool"
        
        explanations = {
            ErrorCategory.NETWORK_ERROR: f"A network issue prevented {tool_name} from connecting to the service",
            ErrorCategory.CONNECTION_TIMEOUT: f"{tool_name} took too long to respond",
            ErrorCategory.API_UNAVAILABLE: f"The service that {tool_name} relies on is currently unavailable",
            ErrorCategory.RATE_LIMITED: f"{tool_name} has hit rate limits and needs to slow down",
            ErrorCategory.TOOL_NOT_FOUND: f"The requested tool '{tool_name}' could not be found",
            ErrorCategory.TOOL_UNAVAILABLE: f"{tool_name} is currently unavailable or not working",
            ErrorCategory.INVALID_ARGUMENTS: f"{tool_name} received invalid or incorrect arguments",
            ErrorCategory.AUTHENTICATION_ERROR: f"{tool_name} failed to authenticate with the service",
            ErrorCategory.PERMISSION_DENIED: f"{tool_name} doesn't have permission to perform this action",
            ErrorCategory.PARSING_ERROR: f"{tool_name} couldn't understand the data format received",
            ErrorCategory.VALIDATION_ERROR: f"The data provided to {tool_name} didn't pass validation"
        }
        
        return explanations.get(category, f"An unexpected error occurred with {tool_name}")
    
    def should_retry(self, error_context: ErrorContext) -> bool:
        """Determine if an error should be retried"""
        # Check if we're in a circuit breaker state
        if (error_context.tool_name and 
            self.circuit_breakers.get(error_context.tool_name, False)):
            return False
        
        # Check severity - don't retry critical errors
        if error_context.severity == ErrorSeverity.CRITICAL:
            return False
        
        # Find applicable strategy
        strategy = self.find_recovery_strategy(error_context)
        if not strategy:
            return False
        
        # Check retry count
        return error_context.retry_count < strategy.max_retries
    
    def find_recovery_strategy(self, error_context: ErrorContext) -> Optional[RecoveryStrategy]:
        """Find the best recovery strategy for an error"""
        for strategy in self.recovery_strategies.values():
            if strategy.is_applicable(error_context):
                return strategy
        return None
    
    async def attempt_recovery(
        self,
        error_context: ErrorContext,
        original_action: Callable
    ) -> Tuple[bool, Any, Optional[ErrorContext]]:
        """
        Attempt to recover from an error using intelligent strategies
        
        Returns:
            Tuple of (success, result, new_error_context)
        """
        strategy = self.find_recovery_strategy(error_context)
        if not strategy:
            return False, None, error_context
        
        # Calculate backoff delay
        delay = strategy.backoff_factor ** error_context.retry_count
        
        # Wait before retry if not first attempt
        if error_context.retry_count > 0:
            await asyncio.sleep(delay)
        
        try:
            # Attempt the original action
            result = await original_action()
            
            # Record successful recovery
            self.record_recovery_success(error_context, strategy)
            
            return True, result, None
            
        except Exception as new_error:
            # Create new error context with incremented retry count
            new_context = self.create_error_context(
                new_error,
                error_context.tool_name,
                error_context.tool_args,
                error_context.execution_context
            )
            new_context.retry_count = error_context.retry_count + 1
            
            # Record failure and update circuit breaker if needed
            self.record_recovery_failure(error_context, strategy)
            
            return False, None, new_context
    
    def record_recovery_success(self, error_context: ErrorContext, strategy: RecoveryStrategy):
        """Record successful recovery for learning"""
        if error_context.tool_name:
            # Reset failure count on success
            self.tool_failure_counts[error_context.tool_name] = 0
            # Reset circuit breaker
            self.circuit_breakers[error_context.tool_name] = False
    
    def record_recovery_failure(self, error_context: ErrorContext, strategy: RecoveryStrategy):
        """Record failed recovery attempt"""
        if error_context.tool_name:
            self.tool_failure_counts[error_context.tool_name] += 1
            
            # Implement circuit breaker after repeated failures
            if self.tool_failure_counts[error_context.tool_name] >= 5:
                self.circuit_breakers[error_context.tool_name] = True
    
    def record_error(self, error_context: ErrorContext):
        """Record error in history for analysis"""
        self.error_history.append(error_context)
        
        # Keep only recent errors (last 1000)
        if len(self.error_history) > 1000:
            self.error_history = self.error_history[-1000:]
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get comprehensive error statistics"""
        if not self.error_history:
            return {
                'total_errors': 0,
                'by_category': {},
                'by_severity': {},
                'by_tool': {},
                'recovery_rate': 0.0
            }
        
        total_errors = len(self.error_history)
        
        # Count by category
        by_category = defaultdict(int)
        for error in self.error_history:
            by_category[error.category.value] += 1
        
        # Count by severity
        by_severity = defaultdict(int)
        for error in self.error_history:
            by_severity[error.severity.value] += 1
        
        # Count by tool
        by_tool = defaultdict(int)
        for error in self.error_history:
            if error.tool_name:
                by_tool[error.tool_name] += 1
        
        # Calculate recovery rate (errors that were eventually resolved)
        recovered_errors = sum(1 for error in self.error_history 
                              if error.retry_count > 0 and error.recoverable)
        recovery_rate = recovered_errors / total_errors if total_errors > 0 else 0.0
        
        return {
            'total_errors': total_errors,
            'by_category': dict(by_category),
            'by_severity': dict(by_severity),
            'by_tool': dict(by_tool),
            'recovery_rate': recovery_rate,
            'circuit_breakers_active': sum(1 for active in self.circuit_breakers.values() if active)
        }
    
    def export_error_report(self) -> Dict[str, Any]:
        """Export comprehensive error report"""
        return {
            'statistics': self.get_error_statistics(),
            'recent_errors': [error.to_dict() for error in self.error_history[-10:]],
            'recovery_strategies': {
                name: {
                    'name': strategy.name,
                    'description': strategy.description,
                    'max_retries': strategy.max_retries,
                    'applicable_categories': [cat.value for cat in strategy.applicable_categories]
                }
                for name, strategy in self.recovery_strategies.items()
            },
            'tool_health': {
                tool: {
                    'failure_count': count,
                    'circuit_breaker_active': self.circuit_breakers.get(tool, False)
                }
                for tool, count in self.tool_failure_counts.items()
            }
        }
