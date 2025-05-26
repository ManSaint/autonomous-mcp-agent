#!/usr/bin/env python3
"""
Phase 5 Simple Test - Enhanced Autonomous Capabilities
Tests: Context awareness, Error recovery, Multiple task types
"""

import asyncio
import logging
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))

from enhanced_executor import (
    ContextAwareExecutor,
    execute_task_with_context, 
    enhanced_autonomous_execution
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_basic_functionality():
    """Test basic enhanced execution functionality"""
    print("PHASE 5 BASIC FUNCTIONALITY TEST")
    print("=" * 40)
    
    try:
        # Test 1: Basic execution
        print("\n1. Testing basic enhanced execution...")
        result1 = await enhanced_autonomous_execution("Find information about Python asyncio")
        print(f"   Success: {result1['success']}")
        print(f"   Status: {result1['status']}")
        print(f"   Time: {result1['execution_time']:.2f}s")
        
        # Test 2: Context awareness
        print("\n2. Testing context awareness...")
        executor = ContextAwareExecutor()
        
        # First task
        context1 = executor.build_execution_context("Research machine learning trends")
        result_ctx1 = await executor.execute_with_context(context1)
        print(f"   First task success: {result_ctx1.success}")
        
        # Related task - should use context
        context2 = executor.build_execution_context("Find more about AI developments")
        result_ctx2 = await executor.execute_with_context(context2)
        print(f"   Second task success: {result_ctx2.success}")
        print(f"   Context used: {len(context2.previous_results) > 0}")
        
        # Test 3: Multiple task types
        print("\n3. Testing multiple task types...")
        task_results = []
        
        tasks = [
            "Research current JavaScript trends",
            "Analyze benefits of microservices architecture", 
            "What is the latest version of React",
            "Compare Python vs Java performance"
        ]
        
        for i, task in enumerate(tasks):
            result = await execute_task_with_context(task)
            task_results.append(result.success)
            print(f"   Task {i+1}: {result.success}")
        
        # Test 4: Statistics and learning
        print("\n4. Testing learning and statistics...")
        stats = executor.get_execution_stats()
        context_summary = executor.get_context_summary()
        
        print(f"   Total executions: {stats['total_executions']}")
        print(f"   Success rate: {stats['success_rate']:.1f}%")
        print(f"   Domains learned: {len(context_summary['domains_learned'])}")
        print(f"   Patterns stored: {context_summary['total_patterns']}")
        
        # Overall assessment
        print("\n" + "=" * 40)
        print("PHASE 5 TEST RESULTS:")
        
        basic_works = result1['success']
        context_works = result_ctx1.success and result_ctx2.success
        multiple_types_work = sum(task_results) >= len(task_results) * 0.5  # 50% success
        learning_works = context_summary['total_patterns'] > 0
        
        print(f"Basic execution: {'PASS' if basic_works else 'FAIL'}")
        print(f"Context awareness: {'PASS' if context_works else 'FAIL'}")
        print(f"Multiple task types: {'PASS' if multiple_types_work else 'FAIL'}")
        print(f"Learning patterns: {'PASS' if learning_works else 'FAIL'}")
        
        overall_success = basic_works and context_works and multiple_types_work and learning_works
        print(f"\nOVERALL PHASE 5: {'SUCCESS' if overall_success else 'NEEDS IMPROVEMENT'}")
        
        return overall_success
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        logger.error(f"Test failed with error: {str(e)}")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_basic_functionality())
    exit(0 if success else 1)
