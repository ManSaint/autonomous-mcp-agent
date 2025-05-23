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
    'GracefulDegradationStrategy'
]
