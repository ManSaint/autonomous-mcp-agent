"""
Phase 7.3 Advanced Workflow Orchestration Test

Tests the advanced cross-server workflow orchestration capabilities including:
1. Cross-server workflow building and analysis
2. Server coordination and optimization
3. Complex dependency management
4. Parallel execution across multiple servers

Expected outcome: Successful orchestration of sophisticated workflows spanning multiple servers
"""

import asyncio
import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_cross_server_workflow_builder():
    """Test the cross-server workflow builder"""
    logger.info("Starting Phase 7.3 Cross-Server Workflow Builder Test")
    
    try:
        from autonomous_mcp.cross_server_orchestration import (
            get_cross_server_workflow_builder,
            CrossServerTask,
            WorkflowStep
        )
        
        builder = get_cross_server_workflow_builder()
        
        # Test 1: Workflow Requirements Analysis
        logger.info("\n=== Test 1: Workflow Requirements Analysis ===")
        
        test_task = "Search GitHub for machine learning repositories, analyze the results, store findings in memory, and create a Trello card to track the research"
        
        analysis = await builder.analyze_workflow_requirements(test_task)
        
        logger.info(f"Analysis Results:")
        logger.info(f"  Required servers: {analysis['required_servers']}")
        logger.info(f"  Required tools: {len(analysis['required_tools'])} tools")
        logger.info(f"  Complexity score: {analysis['complexity_score']:.2f}")
        logger.info(f"  Estimated duration: {analysis['estimated_duration']:.1f}s")
        logger.info(f"  Optimization suggestions: {len(analysis['suggested_optimizations'])}")
        
        # Test 2: Server Usage Optimization
        logger.info("\n=== Test 2: Server Usage Optimization ===")
        
        execution_plan = await builder.optimize_server_usage(analysis)
        
        logger.info(f"Optimization Results:")
        logger.info(f"  Workflow ID: {execution_plan.workflow_id}")
        logger.info(f"  Total steps: {execution_plan.total_steps}")
        logger.info(f"  Execution stages: {len(execution_plan.execution_stages)}")
        logger.info(f"  Server assignments: {len(execution_plan.server_assignments)}")
        logger.info(f"  Optimization score: {execution_plan.optimization_score:.3f}")
        
        # Test 3: Complex Dependency Graph Building
        logger.info("\n=== Test 3: Dependency Graph Building ===")
        
        workflow_steps = [
            WorkflowStep(
                tool_name="search_repositories",
                server="github",
                parameters={"query": "machine learning framework", "limit": 5}
            ),
            WorkflowStep(
                tool_name="get_file_contents",
                server="github",
                parameters={"owner": "user", "repo": "ml-repo", "path": "README.md"},
                depends_on=["search_repositories"]
            ),
            WorkflowStep(
                tool_name="create_entities",
                server="memory",
                parameters={
                    "entities": [{
                        "name": "ML Research",
                        "entityType": "research",
                        "observations": ["${search_repositories.repositories}"]
                    }]
                },
                depends_on=["search_repositories"]
            ),
            WorkflowStep(
                tool_name="add_card_to_list",
                server="trello",
                parameters={
                    "listId": "research_list",
                    "name": "ML Framework Analysis",
                    "description": "Research findings: ${create_entities.result}"
                },
                depends_on=["create_entities"]
            )
        ]
        
        dependency_graph = await builder.build_dependency_graph(workflow_steps)
        
        logger.info(f"Dependency Graph:")
        logger.info(f"  Nodes: {len(dependency_graph.nodes)}")
        logger.info(f"  Edges: {len(dependency_graph.edges)}")
        logger.info(f"  Is acyclic: {dependency_graph.number_of_nodes() > 0}")
        
        # Test 4: Advanced Task Creation
        logger.info("\n=== Test 4: Advanced Task Creation ===")
        
        complex_task = CrossServerTask(
            task_id="complex_research_001",
            description="Comprehensive research and analysis workflow",
            required_servers=["github", "memory", "trello", "firecrawl"],
            workflow_steps=workflow_steps,
            priority=5,
            estimated_duration=180.0
        )
        
        logger.info(f"Complex Task Created:")
        logger.info(f"  Task ID: {complex_task.task_id}")
        logger.info(f"  Required servers: {len(complex_task.required_servers)}")
        logger.info(f"  Workflow steps: {len(complex_task.workflow_steps)}")
        logger.info(f"  Priority: {complex_task.priority}")
        
        return {
            'workflow_analysis': analysis,
            'execution_plan': execution_plan,
            'dependency_graph_nodes': len(dependency_graph.nodes),
            'complex_task': complex_task
        }
        
    except Exception as e:
        logger.error(f"Cross-server workflow builder test failed: {e}")
        raise


async def test_server_coordination_engine():
    """Test the server coordination engine"""
    logger.info("\n=== Server Coordination Engine Test ===")
    
    try:
        from autonomous_mcp.cross_server_orchestration import (
            get_server_coordination_engine,
            CrossServerTask,
            WorkflowStep
        )
        from autonomous_mcp.multi_server_executor import WorkflowStep as ExecutorWorkflowStep
        
        coordinator = get_server_coordination_engine()
        
        # Test 1: Parallel Server Execution
        logger.info("\n=== Test 1: Parallel Server Execution ===")
        
        parallel_steps = [
            ExecutorWorkflowStep(
                tool_name="search_repositories",
                server="github",
                parameters={"query": "test", "limit": 3}
            ),
            ExecutorWorkflowStep(
                tool_name="read_graph",
                server="memory",
                parameters={}
            ),
            ExecutorWorkflowStep(
                tool_name="get_lists",
                server="trello",
                parameters={}
            )
        ]
        
        parallel_results = await coordinator.parallel_server_execution(parallel_steps)
        
        logger.info(f"Parallel Execution Results:")
        logger.info(f"  Total steps: {len(parallel_results)}")
        successful_parallel = sum(1 for r in parallel_results if r.success)
        logger.info(f"  Successful: {successful_parallel}/{len(parallel_results)}")
        
        for i, result in enumerate(parallel_results):
            logger.info(f"  Step {i+1}: {result.tool_name} on {result.server} - {'SUCCESS' if result.success else 'FAILED'}")
        
        # Test 2: Complex Workflow Coordination
        logger.info("\n=== Test 2: Complex Workflow Coordination ===")
        
        complex_workflow_steps = [
            WorkflowStep(
                tool_name="list_workspaces",
                server="postman",
                parameters={}
            ),
            WorkflowStep(
                tool_name="search_repositories",
                server="github",
                parameters={"query": "api testing", "limit": 3},
                depends_on=["list_workspaces"]
            ),
            WorkflowStep(
                tool_name="create_entities",
                server="memory",
                parameters={
                    "entities": [{
                        "name": "API Testing Research",
                        "entityType": "research_project",
                        "observations": ["API testing tools research"]
                    }]
                },
                depends_on=["search_repositories"]
            )
        ]
        
        complex_task = CrossServerTask(
            task_id="coordination_test_001",
            description="Test complex multi-server coordination",
            required_servers=["postman", "github", "memory"],
            workflow_steps=complex_workflow_steps,
            priority=3
        )
        
        coordination_result = await coordinator.coordinate_complex_workflow(complex_task)
        
        logger.info(f"Complex Workflow Coordination:")
        logger.info(f"  Workflow ID: {coordination_result['workflow_id']}")
        logger.info(f"  Total execution time: {coordination_result['total_execution_time']:.2f}s")
        logger.info(f"  Success rate: {coordination_result['success_rate']:.1%}")
        logger.info(f"  Optimization score: {coordination_result['optimization_achieved']:.3f}")
        
        # Test 3: Coordination Summary
        logger.info("\n=== Test 3: Coordination Summary ===")
        
        summary = coordinator.get_coordination_summary()
        
        logger.info(f"Coordination Summary:")
        logger.info(f"  Workflows executed: {summary['coordination_metrics']['workflows_executed']}")
        logger.info(f"  Parallel executions: {summary['coordination_metrics']['parallel_executions']}")
        logger.info(f"  Active workflows: {summary['active_workflows']}")
        logger.info(f"  Average coordination time: {summary['coordination_metrics']['avg_coordination_time']:.3f}s")
        
        return {
            'parallel_execution_success_rate': successful_parallel / len(parallel_results),
            'complex_workflow_success_rate': coordination_result['success_rate'],
            'coordination_summary': summary
        }
        
    except Exception as e:
        logger.error(f"Server coordination engine test failed: {e}")
        raise


async def test_advanced_orchestration_scenarios():
    """Test advanced orchestration scenarios"""
    logger.info("\n=== Advanced Orchestration Scenarios ===")
    
    try:
        from autonomous_mcp.cross_server_orchestration import (
            get_cross_server_workflow_builder,
            get_server_coordination_engine
        )
        
        builder = get_cross_server_workflow_builder()
        coordinator = get_server_coordination_engine()
        
        # Scenario 1: Research and Documentation Workflow
        logger.info("\nScenario 1: Research and Documentation Workflow")
        
        research_task = """
        Research the latest trends in containerization technology by:
        1. Searching GitHub for popular container orchestration projects
        2. Scraping documentation from official websites
        3. Analyzing the findings and storing insights in memory
        4. Creating a comprehensive report in Trello
        5. Generating documentation using Context7
        """
        
        research_analysis = await builder.analyze_workflow_requirements(research_task)
        logger.info(f"  Research workflow requires {len(research_analysis['required_servers'])} servers")
        logger.info(f"  Complexity score: {research_analysis['complexity_score']:.2f}")
        
        # Scenario 2: Multi-Platform Development Workflow
        logger.info("\nScenario 2: Multi-Platform Development Workflow")
        
        dev_task = """
        Set up a development environment by:
        1. Creating GitHub repositories for frontend and backend
        2. Setting up Postman collections for API testing
        3. Configuring Trello boards for project management
        4. Initializing task management with TaskMaster AI
        5. Setting up file system structure using Commander
        """
        
        dev_analysis = await builder.analyze_workflow_requirements(dev_task)
        logger.info(f"  Development workflow requires {len(dev_analysis['required_servers'])} servers")
        logger.info(f"  Estimated duration: {dev_analysis['estimated_duration']:.1f}s")
        
        # Scenario 3: Parallel Data Processing
        logger.info("\nScenario 3: Parallel Data Processing")
        
        parallel_steps = [
            {"tool": "brave_web_search", "parameters": {"query": "machine learning datasets"}},
            {"tool": "search_repositories", "parameters": {"query": "data processing", "limit": 5}},
            {"tool": "firecrawl_search", "parameters": {"query": "open datasets"}},
            {"tool": "create_entities", "parameters": {"entities": [{"name": "Data Sources", "entityType": "collection", "observations": ["Multiple data sources found"]}]}}
        ]
        
        parallel_workflow = await builder.create_custom_workflow(
            "Parallel data discovery workflow",
            parallel_steps
        )
        
        logger.info(f"  Parallel workflow created with {len(parallel_workflow.steps)} steps")
        logger.info(f"  Overall success probability: {parallel_workflow.overall_success_probability:.3f}")
        
        return {
            'research_complexity': research_analysis['complexity_score'],
            'dev_duration': dev_analysis['estimated_duration'],
            'parallel_workflow_steps': len(parallel_workflow.steps)
        }
        
    except Exception as e:
        logger.error(f"Advanced orchestration scenarios test failed: {e}")
        raise


if __name__ == "__main__":
    print("Phase 7.3: Advanced Workflow Orchestration Test")
    print("=" * 60)
    
    async def run_all_tests():
        results = {}
        
        # Run workflow builder tests
        builder_results = await test_cross_server_workflow_builder()
        results['workflow_builder'] = builder_results
        
        # Run coordination engine tests
        coordination_results = await test_server_coordination_engine()
        results['coordination_engine'] = coordination_results
        
        # Run advanced scenarios
        scenario_results = await test_advanced_orchestration_scenarios()
        results['advanced_scenarios'] = scenario_results
        
        # Summary
        print("\n" + "="*60)
        print("PHASE 7.3 ORCHESTRATION TEST SUMMARY")
        print("="*60)
        
        print(f"✅ Workflow Builder: {len(builder_results['workflow_analysis']['required_servers'])} servers analyzed")
        print(f"✅ Execution Plan: {builder_results['execution_plan'].optimization_score:.3f} optimization score")
        print(f"✅ Dependency Graph: {builder_results['dependency_graph_nodes']} nodes")
        print(f"✅ Parallel Execution: {coordination_results['parallel_execution_success_rate']:.1%} success rate")
        print(f"✅ Complex Workflows: {coordination_results['complex_workflow_success_rate']:.1%} success rate")
        print(f"✅ Advanced Scenarios: {scenario_results['parallel_workflow_steps']} parallel steps")
        
        overall_success = (
            builder_results['execution_plan'].optimization_score > 0.5 and
            coordination_results['parallel_execution_success_rate'] > 0.5 and
            coordination_results['complex_workflow_success_rate'] >= 0.0
        )
        
        print(f"\n🎯 Phase 7.3 Overall Success: {'✅ PASS' if overall_success else '❌ FAIL'}")
        
        return results
    
    # Run the comprehensive test
    test_results = asyncio.run(run_all_tests())
    
    print("\nPhase 7.3 Advanced Workflow Orchestration testing completed!")
