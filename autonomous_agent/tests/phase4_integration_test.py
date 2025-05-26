#!/usr/bin/env python3
"""Phase 4 Integration Test - Autonomous Task Planning"""

import asyncio
import sys
import os
import logging
from datetime import datetime

# Add the core directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))

from task_planner import TaskPlanner, autonomous_task_planning

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_phase4_functionality():
    """Test Phase 4 autonomous planning functionality"""
    print("🚀 TESTING PHASE 4 - AUTONOMOUS TASK PLANNING")
    
    planner = TaskPlanner()
    
    # Test 1: Task Analysis
    print("\n1. Testing task analysis...")
    task = "Research Python asyncio best practices"
    analysis = planner.analyze_task(task)
    print(f"   Task type: {analysis.task_type}")
    print(f"   Complexity: {analysis.complexity}")
    print(f"   Tools: {analysis.required_tools}")
    
    # Test 2: Workflow Generation
    print("\n2. Testing workflow generation...")
    workflow_plan = planner.generate_workflow_plan(analysis)
    print(f"   Workflow: {workflow_plan['workflow_name']}")
    print(f"   Steps: {workflow_plan['estimated_steps']}")
    
    # Test 3: Complete Planning
    print("\n3. Testing complete planning process...")
    planning_result = await autonomous_task_planning("Find info about Claude 4")
    
    if planning_result.success:
        print("   ✅ Planning successful")
        print(f"   Task type: {planning_result.analysis.task_type}")
        print(f"   Workflow: {planning_result.workflow_plan['workflow_name']}")
        return True
    else:
        print(f"   ❌ Planning failed: {planning_result.error_message}")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_phase4_functionality())
    print(f"\nPhase 4 Test Result: {'✅ PASSED' if success else '❌ FAILED'}")
