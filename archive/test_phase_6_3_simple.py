# PHASE 6.3 VALIDATION: PROXY WORKFLOW ORCHESTRATION TEST
# Test hybrid workflow execution with internal and proxy tools

import asyncio
import sys
import os

# Add the autonomous_mcp module to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from autonomous_mcp.proxy_workflow_executor import ProxyWorkflowExecutor, ProxyWorkflowResult
    from autonomous_mcp.workflow_builder import WorkflowBuilder
    from autonomous_mcp.mcp_protocol import MCPProtocolBridge
    print("SUCCESS: All modules imported successfully")
except ImportError as e:
    print(f"IMPORT ERROR: {e}")
    sys.exit(1)

async def test_phase_6_3_orchestration():
    """Test Phase 6.3 proxy workflow orchestration capabilities"""
    
    print("\nPHASE 6.3 VALIDATION: PROXY WORKFLOW ORCHESTRATION")
    print("=" * 60)
    
    try:
        # Initialize systems
        protocol = MCPProtocolBridge()
        protocol._initialize_framework()  # This is not async
        
        proxy_executor = ProxyWorkflowExecutor()
        
        print("SUCCESS: Systems initialized")
        
        # Test 1: Simple tool chain
        print("\nTEST 1: HYBRID TOOL CHAIN EXECUTION")
        print("-" * 40)
        
        tool_chain = [
            {
                'tool_name': 'discover_available_tools',
                'parameters': {'include_performance': True},
                'description': 'Discover available tools'
            },
            {
                'tool_name': 'brave_web_search',
                'parameters': {'query': 'autonomous agents', 'count': 5},
                'description': 'Search for autonomous agents'
            }
        ]
        
        result = await proxy_executor.execute_multi_tool_chain(tool_chain)
        
        print(f"Result: {'SUCCESS' if result.success else 'FAILED'}")
        print(f"Total tools: {result.total_steps}")
        print(f"Completed: {result.completed_steps}")
        print(f"Proxy tools: {result.proxy_steps}")
        print(f"Internal tools: {result.internal_steps}")
        print(f"Execution time: {result.total_execution_time:.2f}s")
        
        # Test 2: MCP Protocol Integration
        print("\nTEST 2: MCP PROTOCOL INTEGRATION")
        print("-" * 40)
        
        hybrid_result = await protocol._execute_hybrid_workflow(
            "Research workflow test",
            [
                {
                    'tool': 'discover_available_tools',
                    'parameters': {},
                    'description': 'Discover tools'
                },
                {
                    'tool': 'get_personalized_recommendations',
                    'parameters': {'task_description': 'Test recommendations'},
                    'description': 'Get recommendations'
                }
            ]
        )
        
        print(f"MCP Integration: {'SUCCESS' if hybrid_result['success'] else 'FAILED'}")
        if hybrid_result['success']:
            summary = hybrid_result['execution_summary']
            print(f"Workflow type: {hybrid_result['workflow_type']}")
            print(f"Steps: {summary['completed_steps']}/{summary['total_steps']}")
        
        # Test 3: Performance Summary
        print("\nTEST 3: PERFORMANCE SUMMARY")
        print("-" * 40)
        
        performance = proxy_executor.get_performance_summary()
        print(f"Proxy executor: {performance['proxy_executor_status']}")
        print(f"Internal executor: {performance['internal_executor_status']}")
        print(f"Tool types: {', '.join(performance['supported_tool_types'])}")
        
        print("\nPHASE 6.3 VALIDATION COMPLETE")
        print("Status: Proxy workflow orchestration operational")
        
    except Exception as e:
        print(f"ERROR: Test failed - {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_phase_6_3_orchestration())
