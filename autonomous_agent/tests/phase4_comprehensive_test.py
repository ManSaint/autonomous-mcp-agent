#!/usr/bin/env python3
"""Phase 4 Real Execution Test"""

import asyncio
import sys
import os

# Add the core directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))

from task_planner import TaskPlanner, autonomous_task_planning


async def test_real_autonomous_execution():
    """Test actual autonomous task execution"""
    print("🚀 TESTING PHASE 4 - REAL AUTONOMOUS EXECUTION")
    
    planner = TaskPlanner()
    
    # Test with a simple task that should work
    task = "Find information about Python 3.12"
    
    print(f"\nTask: {task}")
    print("=" * 50)
    
    # Step 1: Plan the task
    planning_result = await planner.plan_task_execution(task)
    
    if not planning_result.success:
        print(f"❌ Planning failed: {planning_result.error_message}")
        return False
    
    print(f"✅ Planning successful:")
    print(f"   Task Type: {planning_result.analysis.task_type}")
    print(f"   Complexity: {planning_result.analysis.complexity}")
    print(f"   Tools: {planning_result.analysis.required_tools}")
    print(f"   Workflow: {planning_result.workflow_plan['workflow_name']}")
    print(f"   Strategy: {planning_result.execution_strategy}")
    
    # Step 2: Execute the planned task using the orchestrator
    try:
        print(f"\n🔄 Executing workflow...")
        
        workflow_plan = planning_result.workflow_plan
        parameters = workflow_plan['parameters']
        
        # Execute via orchestrator
        result = await planner.orchestrator.execute_workflow(
            workflow_plan['workflow_name'], 
            parameters
        )
        
        if result.success:
            print(f"✅ Execution successful!")
            print(f"   Execution time: {result.execution_time:.2f}s")
            print(f"   Steps completed: {len(result.results)}")
            print(f"   Chain ID: {result.chain_id}")
            
            # Show some results
            for i, step_result in enumerate(result.results):
                print(f"   Step {i+1}: {step_result.get('tool', 'Unknown')} - {'✅' if step_result.get('success') else '❌'}")
            
            return True
        else:
            print(f"❌ Execution failed: {result.error}")
            return False
            
    except Exception as e:
        print(f"❌ Execution error: {str(e)}")
        return False


async def test_multiple_task_types():
    """Test multiple different task types"""
    print("\n\n🧪 TESTING MULTIPLE TASK TYPES")
    
    test_tasks = [
        "What is the capital of France?",
        "Research Python asyncio patterns", 
        "Calculate the square root of 144",
        "Find latest AI developments"
    ]
    
    success_count = 0
    
    for i, task in enumerate(test_tasks, 1):
        print(f"\n{i}. Testing: {task}")
        
        planning_result = await autonomous_task_planning(task)
        
        if planning_result.success:
            print(f"   ✅ Planned as {planning_result.analysis.task_type} ({planning_result.analysis.complexity})")
            success_count += 1
        else:
            print(f"   ❌ Planning failed: {planning_result.error_message}")
    
    print(f"\nTask Planning Results: {success_count}/{len(test_tasks)} successful")
    return success_count == len(test_tasks)


async def run_comprehensive_phase4_test():
    """Run comprehensive Phase 4 tests"""
    print("🎯 COMPREHENSIVE PHASE 4 TEST SUITE")
    print("=" * 60)
    
    tests = []
    
    # Test 1: Real autonomous execution
    print("\nTEST 1: Real Autonomous Execution")
    test1_result = await test_real_autonomous_execution()
    tests.append(("Real Execution", test1_result))
    
    # Test 2: Multiple task types
    print("\nTEST 2: Multiple Task Types")
    test2_result = await test_multiple_task_types()
    tests.append(("Multiple Tasks", test2_result))
    
    # Results summary
    print("\n" + "=" * 60)
    print("PHASE 4 TEST RESULTS")
    print("=" * 60)
    
    passed = 0
    for test_name, result in tests:
        status = "✅ PASS" if result else "❌ FAIL" 
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 ALL PHASE 4 TESTS PASSED!")
        print("✅ Phase 4 - Simple Autonomous Planning - COMPLETED")
        return True
    else:
        print("❌ Some tests failed.")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_comprehensive_phase4_test())
    exit(0 if success else 1)
