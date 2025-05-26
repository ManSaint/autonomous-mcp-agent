#!/usr/bin/env python3
"""Phase 4 Test - Autonomous Task Planning"""

import asyncio
import sys
import os

# Add the core directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))

from task_planner import TaskPlanner, autonomous_task_planning


async def test_phase4():
    """Test Phase 4 autonomous planning"""
    print("TESTING PHASE 4 - AUTONOMOUS TASK PLANNING")
    
    planner = TaskPlanner()
    
    # Test task analysis
    print("\n1. Testing task analysis...")
    task = "Research Python asyncio best practices"
    analysis = planner.analyze_task(task)
    print(f"   Task type: {analysis.task_type}")
    print(f"   Complexity: {analysis.complexity}")
    print(f"   Tools: {analysis.required_tools}")
    
    # Test complete planning
    print("\n2. Testing complete planning...")
    planning_result = await autonomous_task_planning("Find info about Claude 4")
    
    if planning_result.success:
        print("   Planning successful")
        print(f"   Task type: {planning_result.analysis.task_type}")
        print(f"   Workflow: {planning_result.workflow_plan['workflow_name']}")
        return True
    else:
        print(f"   Planning failed: {planning_result.error_message}")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_phase4())
    print(f"\nResult: {'PASSED' if success else 'FAILED'}")
