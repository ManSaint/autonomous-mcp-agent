"""
Example usage of the Basic Execution Planner
"""

from autonomous_mcp.planner import BasicExecutionPlanner, ToolCall, ExecutionPlan


def main():
    # Initialize planner (without discovery system for this demo)
    planner = BasicExecutionPlanner()
    
    # Example 1: Create a linear plan manually
    print("=== Example 1: Linear Plan ===")
    
    tool_sequence = [
        'brave_web_search',
        'web_fetch',
        'search_code',
        'create_entities'
    ]
    
    parameters = [
        {'query': 'python async programming best practices'},
        {'url': 'https://example.com/article'},
        {'pattern': 'async def', 'path': '/home/user/code'},
        {'entities': [{'name': 'AsyncConcept', 'type': 'Knowledge'}]}
    ]
    
    plan = planner.create_linear_plan(
        tool_sequence,
        "Research async programming and store knowledge",
        parameters
    )
    
    # Validate the plan
    is_valid, errors = plan.validate()
    print(f"Plan ID: {plan.plan_id}")
    print(f"Intent: {plan.intent}")
    print(f"Valid: {is_valid}")
    if errors:
        print(f"Errors: {errors}")
    
    # Display execution order
    print("\nExecution Order:")
    for tool in plan.get_execution_order():
        deps = f" (depends on: {tool.dependencies})" if tool.dependencies else ""
        print(f"  {tool.order}: {tool.tool_name}{deps}")
    
    # Example 2: Merge multiple plans
    print("\n=== Example 2: Merged Plan ===")
    
    # Create sub-plans
    search_plan = planner.create_linear_plan(
        ['brave_web_search', 'web_fetch'],
        "Search and fetch content",
        [{'query': 'MCP tools'}, {'url': 'https://example.com'}]
    )
    
    process_plan = planner.create_linear_plan(
        ['search_code', 'create_entities'],
        "Process and store",
        [{'pattern': 'class'}, {'entities': []}]
    )
    
    # Merge plans
    merged_plan = planner.merge_plans(
        [search_plan, process_plan],
        "Complete research workflow"
    )
    
    print(f"Merged Plan ID: {merged_plan.plan_id}")
    print(f"Total tools: {len(merged_plan.tools)}")
    print(f"Estimated duration: {merged_plan.estimated_duration}s")
    
    # Example 3: Export plan
    print("\n=== Example 3: Export/Import ===")
    
    export_path = "example_plan.json"
    planner.export_plan(merged_plan, export_path)
    print(f"Exported plan to: {export_path}")
    
    # Import it back
    imported_plan = planner.import_plan(export_path)
    print(f"Imported plan: {imported_plan.plan_id}")
    print(f"Tools count: {len(imported_plan.tools)}")
    
    # Clean up
    import os
    os.unlink(export_path)


if __name__ == "__main__":
    main()
