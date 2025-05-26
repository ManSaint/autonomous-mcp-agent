#!/usr/bin/env python3
"""Phase 4 Real Execution Test - Simple"""

import asyncio
import sys
import os

# Add the core directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))

from task_planner import TaskPlanner, autonomous_task_planning


async def test_real_execution():
    """Test actual autonomous task execution"""
    print("TESTING PHASE 4 - REAL AUTONOMOUS EXECUTION")
    
    planner = TaskPlanner()
    
    # Test with a simple task
    task = "Find information about Python 3.12"
    
    print(f"\nTask: {task}")
    print("=" * 50)
    
    # Step 1: Plan the task
    planning_result = await planner.plan_task_execution(task)
    
    if not planning_result.success:
        print(f"Planning failed: {planning_result.error_message}")
        return False
    
    print(f"Planning successful:")
    print(f"   Task Type: {planning_result.analysis.task_type}")
    print(f"   Complexity: {planning_result.analysis.complexity}")
    print(f"   Tools: {planning_result.analysis.required_tools}")
    print(f"   Workflow: {planning_result.workflow_plan['workflow_name']}")
    
    # Step 2: Execute the planned task
    try:
        print(f"\nExecuting workflow...")
        
        workflow_plan = planning_result.workflow_plan
        parameters = workflow_plan['parameters']
        
        # Execute via orchestrator
        result = await planner.orchestrator.execute_workflow(
            workflow_plan['workflow_name'], 
            parameters
        )
        
        if result.status == "completed":
            print(f"Execution successful!")
            print(f"   Execution time: {result.get_duration():.2f}s")
            print(f"   Steps completed: {len(result.steps_executed)}")
            print(f"   Error count: {result.error_count}")
            
            return True
        else:
            print(f"Execution failed with status: {result.status}")
            print(f"   Error count: {result.error_count}")
            return False
            
    except Exception as e:
        print(f"Execution error: {str(e)}")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_real_execution())
    if success:
        print("\nRESULT: PHASE 4 REAL EXECUTION TEST PASSED!")
    else:
        print("\nRESULT: PHASE 4 REAL EXECUTION TEST FAILED!")
    exit(0 if success else 1)
