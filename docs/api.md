# API Reference

## Overview

The Autonomous MCP Agent provides 7 core tools for intelligent task automation, workflow generation, and system monitoring. All tools are accessible through natural language commands in Claude Desktop or programmatically via the MCP protocol.

## Core Tools

### 1. execute_autonomous_task

**Purpose**: Master orchestrator for complex, multi-step task execution

**Usage**:
```python
result = await execute_autonomous_task(
    task_description="Build and deploy a web application",
    context={"framework": "React", "deployment": "AWS"},
    preferences={"speed": "fast", "detailed_feedback": True}
)
```

**Parameters**:
- `task_description` (string): Natural language description of the task
- `context` (object, optional): Additional context and constraints
- `preferences` (object, optional): User preferences for execution

**Returns**:
```json
{
  "success": true,
  "execution_id": "exec_1234567890",
  "execution_time": 45.2,
  "workflow": {...},
  "analysis": {...},
  "recommendations": {...},
  "result": {...}
}
```

### 2. discover_available_tools

**Purpose**: Real-time discovery and categorization of MCP tools

**Usage**:
```python
tools = await discover_available_tools(
    capability_filter=["web", "file", "analysis"],
    category_filter=["productivity", "development"]
)
```

**Parameters**:
- `capability_filter` (array, optional): Filter by tool capabilities
- `category_filter` (array, optional): Filter by tool categories
- `include_performance` (boolean, optional): Include performance metrics

**Returns**:
```json
{
  "success": true,
  "total_tools": 12,
  "tools": {
    "web_search": {"category": "web", "server": "brave", "capabilities": [...]},
    "file_operations": {"category": "file", "server": "desktop", "capabilities": [...]}
  },
  "discovery_timestamp": "2025-05-25T19:30:00Z"
}
```

### 3. create_intelligent_workflow

**Purpose**: AI-powered workflow generation with optimization

**Usage**:
```python
workflow = await create_intelligent_workflow(
    task_description="Implement CI/CD pipeline",
    include_analysis=True,
    include_recommendations=True
)
```

**Parameters**:
- `task_description` (string): Description of the workflow to create
- `context` (object, optional): Additional context for workflow generation
- `include_analysis` (boolean, optional): Include complexity analysis
- `include_recommendations` (boolean, optional): Include personalized recommendations

**Returns**:
```json
{
  "success": true,
  "workflow": {
    "workflow_id": "workflow_1234567890",
    "title": "CI/CD Pipeline Implementation",
    "steps": [...],
    "estimated_duration": 120,
    "success_probability": 0.92
  },
  "analysis": {...},
  "recommendations": {...}
}
```

### 4. analyze_task_complexity

**Purpose**: Sophisticated task assessment and risk analysis

**Usage**:
```python
analysis = await analyze_task_complexity(
    task_description="Migrate legacy system to microservices",
    include_tool_recommendations=True
)
```

**Parameters**:
- `task_description` (string): Task to analyze
- `context` (object, optional): Additional context for analysis
- `include_tool_recommendations` (boolean, optional): Include tool suggestions

**Returns**:
```json
{
  "success": true,
  "complexity_score": 8.5,
  "estimated_duration": 240.0,
  "recommended_approach": "Phased migration with parallel systems",
  "success_probability": 0.75,
  "risk_factors": ["Legacy system dependencies", "Data consistency"],
  "required_tools": ["database_tools", "monitoring_tools"]
}
```

### 5. get_personalized_recommendations

**Purpose**: ML-driven personalized suggestions and optimization

**Usage**:
```python
recommendations = await get_personalized_recommendations(
    task_description="Optimize development workflow",
    include_optimization_tips=True
)
```

**Parameters**:
- `task_description` (string): Task to get recommendations for
- `preferences` (object, optional): User preferences to consider
- `context` (object, optional): Additional context
- `include_optimization_tips` (boolean, optional): Include optimization suggestions

**Returns**:
```json
{
  "success": true,
  "personalization_score": 0.92,
  "recommended_tools": ["vscode", "git", "docker"],
  "workflow_suggestions": ["Use automated testing", "Implement code review"],
  "optimization_tips": ["Parallel execution", "Caching strategies"],
  "applied_preferences": {...}
}
```

### 6. monitor_agent_performance

**Purpose**: Comprehensive system monitoring and metrics

**Usage**:
```python
metrics = await monitor_agent_performance(
    time_range="24h",
    include_details=True,
    include_trends=True
)
```

**Parameters**:
- `time_range` (string, optional): Time range for metrics ("1h", "24h", "7d", "30d")
- `include_details` (boolean, optional): Include detailed breakdown
- `include_trends` (boolean, optional): Include trend analysis

**Returns**:
```json
{
  "success": true,
  "metrics": {
    "total_executions": 156,
    "successful_executions": 152,
    "success_rate": 0.974,
    "average_response_time": 2.3,
    "performance_trends": {"trend": "improving", "improvement": 0.15},
    "system_health": "healthy"
  }
}
```

### 7. configure_agent_preferences

**Purpose**: Dynamic preference management and system configuration

**Usage**:
```python
config_result = await configure_agent_preferences(
    operation="update",
    preferences={
        "preferred_tools": {"web_search": ["brave"], "file_ops": ["desktop"]},
        "execution_preferences": {"prefer_speed": True, "detailed_feedback": True}
    },
    validate_preferences=True
)
```

**Parameters**:
- `preferences` (object): Preference settings to apply
- `operation` (string, optional): "update", "replace", or "reset"
- `validate_preferences` (boolean, optional): Validate before applying

**Returns**:
```json
{
  "success": true,
  "operation": "update",
  "previous_preferences": {...},
  "new_preferences": {...},
  "validation_result": {"valid": true, "warnings": []},
  "impact_analysis": {"impact_level": "moderate", "affected_systems": [...]}
}
```

## Error Handling

All tools return consistent error responses:

```json
{
  "success": false,
  "error": "Error description",
  "error_code": "TOOL_ERROR_001",
  "recovery_suggestions": ["Try again", "Check parameters"],
  "support_info": "Contact support with error code"
}
```

## Best Practices

### Tool Chaining

Tools can be chained for complex workflows:

```python
# 1. Analyze complexity
analysis = await analyze_task_complexity("Complex task description")

# 2. Get recommendations based on analysis
recommendations = await get_personalized_recommendations(
    "Complex task description", 
    context={"complexity": analysis["complexity_score"]}
)

# 3. Create workflow incorporating both
workflow = await create_intelligent_workflow(
    "Complex task description",
    context={"analysis": analysis, "recommendations": recommendations}
)

# 4. Execute with monitoring
result = await execute_autonomous_task(
    "Complex task description",
    context={"workflow": workflow}
)
```

### Error Recovery

```python
try:
    result = await execute_autonomous_task("Complex task")
except Exception as e:
    # Automatic error recovery is built-in
    # Check result.recovery_attempted for recovery status
    pass
```

### Performance Optimization

```python
# Configure for speed
await configure_agent_preferences(preferences={
    "execution_preferences": {"prefer_speed": True, "parallel_execution": True}
})

# Monitor performance
metrics = await monitor_agent_performance(include_trends=True)
```

## Integration Examples

### Claude Desktop Integration

Natural language commands automatically map to tool calls:

```
User: "Create a development workflow for a Python web API"
→ Triggers: create_intelligent_workflow + analyze_task_complexity

User: "Execute this task autonomously with monitoring"
→ Triggers: execute_autonomous_task + monitor_agent_performance

User: "Find tools for data analysis and configure preferences"
→ Triggers: discover_available_tools + configure_agent_preferences
```

### Programmatic Integration

```python
from autonomous_mcp.mcp_protocol import MCPProtocolBridge

# Initialize the bridge
bridge = MCPProtocolBridge()

# Call tools programmatically
result = await bridge.call_tool("execute_autonomous_task", {
    "task_description": "Process data pipeline",
    "context": {"data_source": "database", "format": "json"}
})
```

## Support

For detailed examples and advanced usage patterns, see:
- [Usage Examples](examples.md)
- [Architecture Guide](architecture.md)
- [GitHub Issues](https://github.com/ManSaint/autonomous-mcp-agent/issues)
