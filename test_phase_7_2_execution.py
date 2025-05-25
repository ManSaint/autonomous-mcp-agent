"""
Phase 7.2 Real Tool Execution Engine Test

Tests the multi-server tool execution capabilities including:
1. Tool routing to appropriate servers
2. Cross-server workflow execution
3. Parameter normalization and response translation
4. Error handling and server failure recovery

Expected outcome: Successful execution of tools across multiple servers
"""

import asyncio
import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_real_tool_execution():
    """Test the real tool execution engine"""
    logger.info("Starting Phase 7.2 Real Tool Execution Test")
    
    try:
        # Import the execution components
        from autonomous_mcp.multi_server_executor import (
            get_multi_server_executor, 
            get_tool_call_translator,
            WorkflowStep
        )
        
        executor = get_multi_server_executor()
        translator = get_tool_call_translator()
        
        # Test 1: Single tool execution routing
        logger.info("\n=== Test 1: Single Tool Execution Routing ===")
        
        # Test GitHub tool
        github_result = await executor.route_tool_call(
            "search_repositories", 
            {"query": "autonomous mcp", "limit": 5}
        )
        
        logger.info(f"GitHub Tool Result: {github_result.success}")
        if github_result.success:
            logger.info(f"  Server: {github_result.server}")
            logger.info(f"  Execution Time: {github_result.execution_time:.3f}s")
            logger.info(f"  Result Type: {type(github_result.result)}")
        
        # Test Memory tool
        memory_result = await executor.route_tool_call(
            "create_entities",
            {"entities": [{"name": "Test Entity", "entityType": "test", "observations": ["Test observation"]}]}
        )
        
        logger.info(f"Memory Tool Result: {memory_result.success}")
        if memory_result.success:
            logger.info(f"  Server: {memory_result.server}")
            logger.info(f"  Result: {memory_result.result}")
        
        # Test 2: Parameter normalization
        logger.info("\n=== Test 2: Parameter Normalization ===")
        
        original_params = {"q": "test query", "sort": "stars"}
        normalized_params = await translator.normalize_parameters(
            "search_repositories", original_params, "github"
        )
        
        logger.info(f"Original: {original_params}")
        logger.info(f"Normalized: {normalized_params}")
        
        # Test 3: Response translation
        logger.info("\n=== Test 3: Response Translation ===")
        
        sample_github_response = {
            "repositories": [
                {"name": "repo1", "stars": 100, "description": "Test repo"},
                {"name": "repo2", "stars": 50, "description": "Another repo"}
            ]
        }
        
        translated_response = await translator.translate_responses(
            sample_github_response, "github"
        )
        
        logger.info(f"Translated response has {len(translated_response.get('items', []))} items")
        
        # Test 4: Cross-server workflow execution
        logger.info("\n=== Test 4: Cross-Server Workflow Execution ===")
        
        workflow_steps = [
            WorkflowStep(
                tool_name="search_repositories",
                server="github", 
                parameters={"query": "mcp framework", "limit": 3}
            ),
            WorkflowStep(
                tool_name="create_entities",
                server="memory",
                parameters={
                    "entities": [{
                        "name": "GitHub Search Results",
                        "entityType": "search_result",
                        "observations": ["${search_repositories.repositories}"]
                    }]
                },
                depends_on=["search_repositories"]
            ),
            WorkflowStep(
                tool_name="get_lists",
                server="trello",
                parameters={}
            )
        ]
        
        workflow_results = await executor.execute_cross_server_workflow(workflow_steps)
        
        logger.info(f"Workflow executed {len(workflow_results)} steps")
        for i, result in enumerate(workflow_results):
            logger.info(f"  Step {i+1}: {result.tool_name} on {result.server} - {'SUCCESS' if result.success else 'FAILED'}")
        
        # Test 5: Error handling and server failure simulation
        logger.info("\n=== Test 5: Error Handling ===")
        
        # Test with non-existent tool
        error_result = await executor.route_tool_call(
            "nonexistent_tool",
            {"param": "value"}
        )
        
        logger.info(f"Non-existent tool result: {error_result.success} - {error_result.error_message}")
        
        # Test server failure handling
        failure_result = await executor.handle_server_failures(
            "unavailable_server",
            {"tool_name": "test_tool", "parameters": {}}
        )
        
        logger.info(f"Server failure handling: {failure_result.success} - {failure_result.error_message}")
        
        # Generate execution summary
        execution_summary = executor.get_execution_summary()
        
        logger.info("\n=== Execution Summary ===")
        logger.info(f"Total executions: {execution_summary['global_metrics']['total_executions']}")
        logger.info(f"Success rate: {execution_summary['global_metrics']['successful_executions'] / max(execution_summary['global_metrics']['total_executions'], 1) * 100:.1f}%")
        logger.info(f"Average execution time: {execution_summary['global_metrics']['avg_execution_time']:.3f}s")
        
        for server, stats in execution_summary['server_performance'].items():
            logger.info(f"  {server}: {stats['total_calls']} calls, {stats['success_rate']*100:.1f}% success, {stats['avg_response_time']:.3f}s avg")
        
        return execution_summary
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        raise


async def test_advanced_workflow_scenarios():
    """Test advanced cross-server workflow scenarios"""
    logger.info("\n=== Advanced Workflow Scenarios ===")
    
    from autonomous_mcp.multi_server_executor import get_multi_server_executor, WorkflowStep
    executor = get_multi_server_executor()
    
    # Scenario 1: Data pipeline across multiple servers
    logger.info("\nScenario 1: Multi-Server Data Pipeline")
    
    pipeline_steps = [
        # Step 1: Search for repositories
        WorkflowStep(
            tool_name="search_repositories",
            server="github",
            parameters={"query": "machine learning", "limit": 2}
        ),
        # Step 2: Store results in memory
        WorkflowStep(
            tool_name="create_entities", 
            server="memory",
            parameters={
                "entities": [{
                    "name": "ML Repositories",
                    "entityType": "repository_collection", 
                    "observations": ["${search_repositories}"]
                }]
            },
            depends_on=["search_repositories"]
        ),
        # Step 3: Create Trello card for tracking
        WorkflowStep(
            tool_name="add_card_to_list",
            server="trello",
            parameters={
                "listId": "default_list",
                "name": "Review ML Repositories",
                "description": "Found repositories: ${search_repositories.repositories}"
            },
            depends_on=["search_repositories"]
        )
    ]
    
    pipeline_results = await executor.execute_cross_server_workflow(pipeline_steps)
    
    success_count = sum(1 for r in pipeline_results if r.success)
    logger.info(f"Pipeline completed: {success_count}/{len(pipeline_steps)} steps successful")
    
    # Scenario 2: Parallel execution test
    logger.info("\nScenario 2: Parallel Tool Execution")
    
    parallel_tasks = [
        executor.route_tool_call("get_lists", {}),
        executor.route_tool_call("list_workspaces", {}),
        executor.route_tool_call("read_graph", {}),
        executor.route_tool_call("search_repositories", {"query": "test", "limit": 1})
    ]
    
    parallel_results = await asyncio.gather(*parallel_tasks, return_exceptions=True)
    
    successful_parallel = sum(1 for r in parallel_results if hasattr(r, 'success') and r.success)
    logger.info(f"Parallel execution: {successful_parallel}/{len(parallel_tasks)} successful")


if __name__ == "__main__":
    print("Phase 7.2: Real Tool Execution Engine Test")
    print("=" * 50)
    
    # Run the comprehensive test
    asyncio.run(test_real_tool_execution())
    
    # Run advanced scenarios
    asyncio.run(test_advanced_workflow_scenarios())
    
    print("\nPhase 7.2 testing completed!")
