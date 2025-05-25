"""
Autonomous MCP Agent - Core Components
"""

from .discovery import (
    ToolCapability,
    DiscoveredTool,
    ToolDiscovery
)

from .planner import (
    ToolCall,
    ExecutionPlan,
    BasicExecutionPlanner
)

from .advanced_planner import (
    AdvancedExecutionPlanner,
    EnhancedExecutionPlan,
    ReasoningStep
)

from .executor import (
    ChainExecutor,
    ExecutionStatus,
    ExecutionResult,
    ExecutionState
)

from .smart_selector import (
    SmartToolSelector,
    SelectionStrategy,
    ToolScore
)

from .user_preferences import (
    UserPreferenceEngine,
    UserProfile,
    PreferenceType,
    FeedbackType,
    PreferenceItem
)

from .error_recovery import (
    ErrorRecoverySystem,
    ErrorContext,
    ErrorCategory,
    ErrorSeverity,
    RecoveryStrategy
)

from .fallback_manager import (
    FallbackManager,
    FallbackOption,
    FallbackChain,
    FallbackLevel,
    FallbackReason,
    FallbackExecutionResult,
    ToolFallbackStrategy,
    PlanFallbackStrategy,
    GracefulDegradationStrategy
)

# Phase 8: Real MCP Protocol Implementation
from .real_mcp_client import (
    RealMCPClient,
    MCPMessage,
    MCPInitializeParams,
    MCPServerCapabilities
)

from .mcp_client_manager import (
    RealMCPClientManager,
    ServerConnectionInfo,
    ConnectionStatus
)

from .mcp_protocol_validator import (
    MCPProtocolValidator,
    ProtocolValidationResult
)

from .universal_mcp_adapter import (
    UniversalMCPAdapter,
    ServerAdaptation
)

from .real_mcp_validator import (
    RealMCPValidator,
    ValidationReport,
    ConnectionTest
)

__all__ = [
    # Discovery
    'ToolCapability',
    'DiscoveredTool',
    'ToolDiscovery',
    
    # Planner
    'ToolCall',
    'ExecutionPlan',
    'BasicExecutionPlanner',
    
    # Advanced Planner
    'AdvancedExecutionPlanner',
    'EnhancedExecutionPlan',
    'ReasoningStep',
    
    # Executor
    'ChainExecutor',
    'ExecutionStatus',
    'ExecutionResult',
    'ExecutionState',
    
    # Smart Selector
    'SmartToolSelector',
    'SelectionStrategy',
    'ToolScore',
    
    # User Preferences
    'UserPreferenceEngine',
    'UserProfile',
    'PreferenceType',
    'FeedbackType',
    'PreferenceItem',
    
    # Error Recovery
    'ErrorRecoverySystem',
    'ErrorContext',
    'ErrorCategory',
    'ErrorSeverity',
    'RecoveryStrategy',
    
    # Fallback Management
    'FallbackManager',
    'FallbackOption',
    'FallbackChain',
    'FallbackLevel',
    'FallbackReason',
    'FallbackExecutionResult',
    'ToolFallbackStrategy',
    'PlanFallbackStrategy',
    'GracefulDegradationStrategy',
    
    # Phase 8: Real MCP Protocol Implementation
    'RealMCPClient',
    'MCPMessage',
    'MCPInitializeParams',
    'MCPServerCapabilities',
    'RealMCPClientManager',
    'ServerConnectionInfo',
    'ConnectionStatus',
    'MCPProtocolValidator',
    'ProtocolValidationResult',
    'UniversalMCPAdapter',
    'ServerAdaptation',
    'RealMCPValidator',
    'ValidationReport',
    'ConnectionTest'
]
