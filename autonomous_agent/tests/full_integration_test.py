#!/usr/bin/env python3
"""Phase 1-4 Integration Verification Test"""

import asyncio
import sys
import os

# Add the core directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))

from task_planner import TaskPlanner, autonomous_task_planning
from tool_chainer import real_tool_chainer
from workflow_orchestrator import workflow_orchestrator


async def test_full_integration():
    """Test full integration across all phases"""
    print("TESTING PHASE 1-4 FULL INTEGRATION")
    print("=" * 50)
    
    results = []
    
    # Test 1: Phase 1 - Foundation still works
    print("\n1. Testing Phase 1 Foundation...")
    try:
        available_tools = real_tool_chainer.get_available_tools()
        print(f"   Available tools: {len(available_tools)}")
        results.append(len(available_tools) > 0)
    except Exception as e:
        print(f"   Error: {e}")
        results.append(False)
    
    # Test 2: Phase 2 - Tool integration still works
    print("\n2. Testing Phase 2 Tool Integration...")
    try:
        # Test simple tool chain
        steps = [{'tool': 'web_search', 'parameters': {'query': 'test'}}]
        chain_id = real_tool_chainer.create_tool_chain(steps, "Integration Test")
        print(f"   Tool chain created: {chain_id}")
        results.append(True)
    except Exception as e:
        print(f"   Error: {e}")
        results.append(False)
    
    # Test 3: Phase 3 - Workflow orchestration still works
    print("\n3. Testing Phase 3 Workflow Orchestration...")
    try:
        available_workflows = workflow_orchestrator.get_available_workflows()
        print(f"   Available workflows: {available_workflows}")
        results.append(len(available_workflows) > 0)
    except Exception as e:
        print(f"   Error: {e}")
        results.append(False)
    
    # Test 4: Phase 4 - Autonomous planning works
    print("\n4. Testing Phase 4 Autonomous Planning...")
    try:
        planning_result = await autonomous_task_planning("Test integration")
        print(f"   Planning result: {planning_result.success}")
        print(f"   Task type: {planning_result.analysis.task_type}")
        results.append(planning_result.success)
    except Exception as e:
        print(f"   Error: {e}")
        results.append(False)
    
    # Test 5: End-to-end autonomous execution
    print("\n5. Testing End-to-End Autonomous Execution...")
    try:
        planner = TaskPlanner()
        planning_result = await planner.plan_task_execution("Find info about autonomous agents")
        
        if planning_result.success:
            # Execute the planned workflow
            result = await planner.orchestrator.execute_workflow(
                planning_result.workflow_plan['workflow_name'],
                planning_result.workflow_plan['parameters']
            )
            
            success = result.status == "completed"
            print(f"   Execution result: {result.status}")
            print(f"   Steps: {len(result.steps_executed)}")
            print(f"   Duration: {result.get_duration():.2f}s")
            results.append(success)
        else:
            print(f"   Planning failed: {planning_result.error_message}")
            results.append(False)
    except Exception as e:
        print(f"   Error: {e}")
        results.append(False)
    
    # Summary
    print("\n" + "=" * 50)
    print("INTEGRATION TEST RESULTS")
    print("=" * 50)
    
    test_names = [
        "Phase 1 Foundation",
        "Phase 2 Tool Integration", 
        "Phase 3 Workflow Orchestration",
        "Phase 4 Autonomous Planning",
        "End-to-End Execution"
    ]
    
    passed = 0
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "PASS" if result else "FAIL"
        print(f"{name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("ALL INTEGRATION TESTS PASSED!")
        print("Phase 4 Successfully Integrated with All Previous Phases")
        return True
    else:
        print("Some integration tests failed.")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_full_integration())
    exit(0 if success else 1)
