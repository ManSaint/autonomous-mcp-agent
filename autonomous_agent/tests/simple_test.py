#!/usr/bin/env python3
"""Simple Task Planner Test"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))

from task_planner import TaskPlanner

def test_simple():
    """Simple test"""
    print("Creating TaskPlanner...")
    planner = TaskPlanner()
    
    print("Testing task analysis...")
    analysis = planner.analyze_task("Research Python features")
    print(f"Analysis: {analysis.task_type}, {analysis.complexity}")
    
    print("Checking if method exists...")
    if hasattr(planner, '_determine_execution_strategy'):
        print("Method exists")
        strategy = planner._determine_execution_strategy(analysis)
        print(f"Strategy: {strategy}")
    else:
        print("Method missing")
        print(f"Available methods: {[m for m in dir(planner) if not m.startswith('__')]}")

if __name__ == "__main__":
    test_simple()
