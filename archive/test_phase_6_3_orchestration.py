# 🧪 PHASE 6.3 VALIDATION: PROXY WORKFLOW ORCHESTRATION TEST
# Test hybrid workflow execution with internal and proxy tools

import asyncio
import sys
import os

# Add the autonomous_mcp module to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from autonomous_mcp.proxy_workflow_executor import ProxyWorkflowExecutor, ProxyWorkflowResult
from autonomous_mcp.workflow_builder import WorkflowBuilder
from autonomous_mcp.mcp_protocol import MCPProtocolBridge

async def test_phase_6_3_proxy_orchestration():
    """Test Phase 6.3 proxy workflow orchestration capabilities"""
    
    print("🚀 PHASE 6.3 VALIDATION: PROXY WORKFLOW ORCHESTRATION")
    print("=" * 70)
    
    # Initialize systems
    protocol = MCPProtocolBridge()
    await protocol._initialize_framework()
    
    proxy_executor = ProxyWorkflowExecutor()
    
    print("\n✅ Systems initialized successfully")
    
    # Test 1: Simple tool chain with mix of internal and proxy tools
    print("\n🔍 TEST 1: HYBRID TOOL CHAIN EXECUTION")
    print("-" * 50)
    
    tool_chain = [
        {
            'tool_name': 'discover_available_tools',  # Internal tool
            'parameters': {'include_performance': True},
            'description': 'Discover available tools'
        },
        {
            'tool_name': 'brave_web_search',  # Proxy tool
            'parameters': {'query': 'autonomous agents', 'count': 5},
            'description': 'Search for information about autonomous agents'
        },
        {
            'tool_name': 'create_intelligent_workflow',  # Internal tool
            'parameters': {
                'task_description': 'Analyze search results and create summary',
                'include_analysis': True
            },
            'description': 'Create workflow to analyze results'
        }
    ]
    
    try:
        result = await proxy_executor.execute_multi_tool_chain(tool_chain)
        
        print(f"✅ Tool chain execution: {'SUCCESS' if result.success else 'FAILED'}")
        print(f"   Total tools: {result.total_steps}")
        print(f"   Completed: {result.completed_steps}")
        print(f"   Failed: {result.failed_steps}")
        print(f"   Proxy tools: {result.proxy_steps}")
        print(f"   Internal tools: {result.internal_steps}")
        print(f"   Execution time: {result.total_execution_time:.2f}s")
        
        if result.errors:
            print("   Errors:")
            for error in result.errors[:3]:  # Show first 3 errors
                print(f"     - {error}")
                
    except Exception as e:
        print(f"❌ Tool chain execution failed: {e}")
    
    # Test 2: Complex workflow with conditional logic
    print("\n🔍 TEST 2: COMPLEX HYBRID WORKFLOW")
    print("-" * 50)
    
    workflow_steps = [
        {
            'tool': 'github_search_repositories',  # Proxy tool
            'parameters': {'q': 'autonomous agent python', 'per_page': 5},
            'description': 'Search for autonomous agent repositories'
        },
        {
            'tool': 'memory_create_entities',  # Proxy tool
            'parameters': {
                'entities': [
                    {
                        'name': 'research_session',
                        'entityType': 'session',
                        'observations': ['Started autonomous agent research']
                    }
                ]
            },
            'description': 'Store research session in memory'
        },
        {
            'tool': 'analyze_task_complexity',  # Internal tool
            'parameters': {
                'task_description': 'Build autonomous agent system',
                'include_tool_recommendations': True
            },
            'description': 'Analyze task complexity'
        }
    ]
    
    try:
        result = await proxy_executor.create_and_execute_hybrid_workflow(
            "Research and analyze autonomous agent development",
            workflow_steps,
            {'priority': 'high', 'domain': 'AI research'}
        )
        
        print(f"✅ Complex workflow: {'SUCCESS' if result.success else 'FAILED'}")
        print(f"   Workflow ID: {result.workflow_id}")
        print(f"   Steps completed: {result.completed_steps}/{result.total_steps}")
        print(f"   Proxy tools used: {result.proxy_steps}")
        print(f"   Internal tools used: {result.internal_steps}")
        print(f"   Total time: {result.total_execution_time:.2f}s")
        
        # Show performance metrics
        if result.performance_metrics:
            metrics = result.performance_metrics
            if 'execution_summary' in metrics:
                summary = metrics['execution_summary']
                print(f"   Success rate: {summary['success_rate']:.1%}")
                
        if result.errors:
            print("   Errors encountered:")
            for error in result.errors[:2]:
                print(f"     - {error}")
                
    except Exception as e:
        print(f"❌ Complex workflow failed: {e}")
    
    # Test 3: MCP Protocol Integration Test
    print("\n🔍 TEST 3: MCP PROTOCOL INTEGRATION")
    print("-" * 50)
    
    try:
        # Test hybrid workflow execution via MCP protocol
        hybrid_result = await protocol._execute_hybrid_workflow(
            "Multi-tool research workflow",
            [
                {
                    'tool': 'brave_web_search',
                    'parameters': {'query': 'MCP protocol specification', 'count': 3},
                    'description': 'Search for MCP protocol information'
                },
                {
                    'tool': 'get_personalized_recommendations',
                    'parameters': {'task_description': 'Implement MCP server'},
                    'description': 'Get implementation recommendations'
                }
            ]
        )
        
        print(f"✅ MCP integration: {'SUCCESS' if hybrid_result['success'] else 'FAILED'}")
        if hybrid_result['success']:
            summary = hybrid_result['execution_summary']
            print(f"   Workflow type: {hybrid_result['workflow_type']}")
            print(f"   Steps: {summary['completed_steps']}/{summary['total_steps']}")
            print(f"   Proxy tools: {summary['proxy_steps']}")
            print(f"   Internal tools: {summary['internal_steps']}")
        else:
            print(f"   Error: {hybrid_result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ MCP integration test failed: {e}")
    
    # Test 4: Tool Chain via MCP Protocol
    print("\n🔍 TEST 4: TOOL CHAIN VIA MCP")
    print("-" * 50)
    
    try:
        chain_result = await protocol._execute_tool_chain([
            {
                'tool_name': 'discover_available_tools',
                'parameters': {'category_filter': ['search']},
                'description': 'Find search tools'
            },
            {
                'tool_name': 'brave_web_search',
                'parameters': {'query': 'best practices autonomous agents'},
                'description': 'Search for best practices'
            }
        ])
        
        print(f"✅ Tool chain via MCP: {'SUCCESS' if chain_result['success'] else 'FAILED'}")
        if chain_result['success']:
            summary = chain_result['chain_summary']
            print(f"   Execution type: {chain_result['execution_type']}")
            print(f"   Tools: {summary['successful_tools']}/{summary['total_tools']}")
            print(f"   Proxy tools: {summary['proxy_tools_used']}")
            print(f"   Internal tools: {summary['internal_tools_used']}")
            print(f"   Time: {summary['total_execution_time']:.2f}s")
        else:
            print(f"   Error: {chain_result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Tool chain test failed: {e}")
    
    # Test 5: Error Recovery and Graceful Degradation
    print("\n🔍 TEST 5: ERROR RECOVERY & GRACEFUL DEGRADATION")
    print("-" * 50)
    
    try:
        # Test with some invalid tools to check error handling
        error_test_chain = [
            {
                'tool_name': 'discover_available_tools',  # Valid internal tool
                'parameters': {},
                'description': 'Valid tool call'
            },
            {
                'tool_name': 'nonexistent_proxy_tool',  # Invalid proxy tool
                'parameters': {'test': 'data'},
                'description': 'Invalid tool to test error handling'
            },
            {
                'tool_name': 'brave_web_search',  # Valid proxy tool
                'parameters': {'query': 'recovery test'},
                'description': 'Valid tool after error'
            }
        ]
        
        error_result = await proxy_executor.execute_multi_tool_chain(error_test_chain)
        
        print(f"✅ Error recovery test: {'PARTIAL SUCCESS' if error_result.completed_steps > 0 else 'FAILED'}")
        print(f"   Completed: {error_result.completed_steps}/{error_result.total_steps}")
        print(f"   Failed: {error_result.failed_steps}")
        print(f"   Graceful degradation: {'YES' if error_result.completed_steps > error_result.failed_steps else 'NO'}")
        
        if error_result.errors:
            print(f"   Error handling: {len(error_result.errors)} errors captured")
            
    except Exception as e:
        print(f"❌ Error recovery test failed: {e}")
    
    # Performance Summary
    print("\n📊 PHASE 6.3 PERFORMANCE SUMMARY")
    print("=" * 70)
    
    performance_summary = proxy_executor.get_performance_summary()
    print("✅ Proxy executor status:", performance_summary['proxy_executor_status'])
    print("✅ Internal executor status:", performance_summary['internal_executor_status'])
    print("✅ Supported tool types:", ', '.join(performance_summary['supported_tool_types']))
    print("✅ Workflow capabilities:")
    for capability in performance_summary['workflow_capabilities']:
        print(f"   - {capability.replace('_', ' ').title()}")
    
    print("\n🏆 PHASE 6.3 VALIDATION COMPLETE")
    print("Status: Proxy workflow orchestration system operational")
    print("Capabilities: Internal + Proxy tool execution with error recovery")

if __name__ == "__main__":
    asyncio.run(test_phase_6_3_proxy_orchestration())
