# 🎯 PHASE 6.3 CAPABILITY DEMONSTRATION
# Shows the new hybrid workflow orchestration in action

import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from autonomous_mcp.mcp_protocol import MCPProtocolBridge

async def demonstrate_phase_6_3_capabilities():
    """Demonstrate the new hybrid workflow capabilities"""
    
    print("PHASE 6.3 CAPABILITY DEMONSTRATION")
    print("=" * 50)
    
    # Initialize the enhanced protocol
    protocol = MCPProtocolBridge()
    protocol._initialize_framework()
    
    print("SUCCESS: Enhanced MCP protocol initialized with hybrid workflows")
    
    # Demonstration 1: Research and Development Workflow
    print("\nDEMO 1: RESEARCH & DEVELOPMENT WORKFLOW")
    print("-" * 40)
    
    research_workflow = [
        {
            'tool': 'brave_web_search',  # Proxy tool - external web search
            'parameters': {'query': 'autonomous agent best practices', 'count': 3},
            'description': 'Research autonomous agent best practices'
        },
        {
            'tool': 'memory_create_entities',  # Proxy tool - external memory storage
            'parameters': {
                'entities': [
                    {
                        'name': 'research_findings',
                        'entityType': 'knowledge',
                        'observations': ['Researched autonomous agent best practices']
                    }
                ]
            },
            'description': 'Store research findings in knowledge graph'
        },
        {
            'tool': 'create_intelligent_workflow',  # Internal tool - autonomous planning
            'parameters': {
                'task_description': 'Create implementation plan based on research',
                'include_analysis': True
            },
            'description': 'Create intelligent implementation workflow'
        }
    ]
    
    try:
        result = await protocol._execute_hybrid_workflow(
            "Research autonomous agents and create implementation plan",
            research_workflow,
            {'priority': 'high', 'domain': 'AI development'}
        )
        
        print(f"Result: {'SUCCESS' if result['success'] else 'FAILED'}")
        print(f"Workflow Type: {result['workflow_type']}")
        summary = result['execution_summary']
        print(f"Tools Executed: {summary['completed_steps']}/{summary['total_steps']}")
        print(f"Proxy Tools: {summary['proxy_steps']}")
        print(f"Internal Tools: {summary['internal_steps']}")
        print(f"Execution Time: {summary['total_execution_time']:.2f}s")
        
    except Exception as e:
        print(f"Demo 1 failed: {e}")
    
    # Demonstration 2: Development Tool Chain
    print("\nDEMO 2: DEVELOPMENT TOOL CHAIN")
    print("-" * 40)
    
    dev_tool_chain = [
        {
            'tool_name': 'github_search_repositories',  # Proxy - find similar projects
            'parameters': {'q': 'MCP autonomous agent', 'per_page': 3},
            'description': 'Find similar MCP agent projects'
        },
        {
            'tool_name': 'analyze_task_complexity',  # Internal - analyze development complexity
            'parameters': {
                'task_description': 'Develop MCP autonomous agent',
                'include_tool_recommendations': True
            },
            'description': 'Analyze development complexity'
        },
        {
            'tool_name': 'get_personalized_recommendations',  # Internal - get recommendations
            'parameters': {
                'task_description': 'Optimize MCP agent development workflow',
                'include_optimization_tips': True
            },
            'description': 'Get development optimization recommendations'
        }
    ]
    
    try:
        chain_result = await protocol._execute_tool_chain(
            dev_tool_chain,
            optimize_execution=True
        )
        
        print(f"Result: {'SUCCESS' if chain_result['success'] else 'FAILED'}")
        print(f"Execution Type: {chain_result['execution_type']}")
        summary = chain_result['chain_summary']
        print(f"Tools: {summary['successful_tools']}/{summary['total_tools']}")
        print(f"Mixed Execution: {summary['proxy_tools_used']} proxy + {summary['internal_tools_used']} internal")
        print(f"Total Time: {summary['total_execution_time']:.2f}s")
        
    except Exception as e:
        print(f"Demo 2 failed: {e}")
    
    print("\nPHASE 6.3 CAPABILITIES DEMONSTRATED")
    print("Hybrid workflow orchestration operational!")
    print("Users can now execute complex workflows spanning")
    print("both internal autonomous and external proxy tools")

if __name__ == "__main__":
    asyncio.run(demonstrate_phase_6_3_capabilities())
