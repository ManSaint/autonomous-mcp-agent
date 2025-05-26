#!/usr/bin/env python3
"""Debug Phase 4 - Check method existence"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))

from task_planner import TaskPlanner

planner = TaskPlanner()
print("TaskPlanner methods:")
for method in dir(planner):
    if not method.startswith('_'):
        print(f"  {method}")

print("\nPrivate methods:")
for method in dir(planner):
    if method.startswith('_') and not method.startswith('__'):
        print(f"  {method}")

# Test specific method
if hasattr(planner, '_determine_execution_strategy'):
    print("\n_determine_execution_strategy method exists")
    
    # Test the analysis
    analysis = planner.analyze_task("test task")
    print(f"Analysis type: {type(analysis)}")
    print(f"Analysis fields: {analysis.__dict__.keys() if hasattr(analysis, '__dict__') else 'No dict'}")
    
    # Test the method
    try:
        strategy = planner._determine_execution_strategy(analysis)
        print(f"Strategy: {strategy}")
    except Exception as e:
        print(f"Error calling method: {e}")
else:
    print("\n_determine_execution_strategy method does NOT exist")
