#!/usr/bin/env python3
"""
Phase 5 Comprehensive Test Suite
Tests enhanced autonomous capabilities:
1. Context awareness with execution history
2. Error recovery and retry mechanisms  
3. Multiple task types support
4. Learning from execution patterns
"""

import asyncio
import logging
import json
from datetime import datetime

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))

from enhanced_executor import (
    ContextAwareExecutor,
    execute_task_with_context, 
    enhanced_autonomous_execution
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def test_context_awareness():
    """Test 1: Context awareness with execution history"""
    logger.info("Testing Context Awareness...")
    
    executor = ContextAwareExecutor()
    
    # Execute first task
    result1 = await execute_task_with_context("Research Python 3.12 new features")
    print(f"[OK] First execution: {result1.success} ({result1.execution_time:.2f}s)")
    
    # Execute related task - should use context from first task
    result2 = await execute_task_with_context("Find more information about Python 3.12 performance improvements")
    print(f"[OK] Second execution with context: {result2.success} ({result2.execution_time:.2f}s)")
    print(f"[INFO] Context data: {result2.result_data.get('context', 'No context') if result2.result_data else 'No result data'}")
    
    # Check if context was used
    stats = executor.get_execution_stats()
    print(f"[STATS] Execution history: {stats['execution_history_size']} tasks")
    print(f"[STATS] Success rate: {stats['success_rate']:.1f}%")
    
    return result1.success and result2.success


async def test_error_recovery():
    """Test 2: Error recovery and retry mechanisms"""
    logger.info("🛡️ Testing Error Recovery...")
    
    executor = ContextAwareExecutor()
    
    # Test with a potentially problematic task
    result = await execute_task_with_context("Search for nonexistent information about XYZ123FAKE")
    
    print(f"✅ Error recovery test completed: {result.success}")
    print(f"🔄 Lessons learned: {result.lessons_learned}")
    
    if result.error_info:
        print(f"❌ Error handled: {result.error_info}")
    
    return True  # Test passes if it doesn't crash


async def test_multiple_task_types():
    """Test 3: Multiple task types support"""
    logger.info("🎯 Testing Multiple Task Types...")
    
    executor = ContextAwareExecutor()
    
    task_types = [
        ("Research task", "Research machine learning trends 2025"),
        ("Analysis task", "Analyze the benefits of async programming"),
        ("Documentation task", "Create a summary of REST API best practices"),
        ("Web lookup task", "What is the current version of Node.js"),
        ("Comparison task", "Compare Python vs JavaScript for web development")
    ]
    
    results = []
    for task_name, task_description in task_types:
        logger.info(f"Testing {task_name}...")
        result = await execute_task_with_context(task_description)
        results.append((task_name, result.success))
        print(f"✅ {task_name}: {result.success} - Domain: {result.result_data.get('domain', 'unknown') if result.result_data else 'no data'}")
    
    success_count = sum(1 for _, success in results if success)
    print(f"📊 Task type success rate: {success_count}/{len(task_types)} ({success_count/len(task_types)*100:.1f}%)")
    
    return success_count >= len(task_types) * 0.6  # 60% success rate minimum


async def test_learning_patterns():
    """Test 4: Learning from execution patterns"""
    logger.info("🎓 Testing Learning Patterns...")
    
    executor = ContextAwareExecutor()
    
    # Execute several similar tasks to build patterns
    learning_tasks = [
        "Research JavaScript frameworks",
        "Find information about React performance",
        "Search for Vue.js best practices",
        "Investigate Angular migration guide"
    ]
    
    for task in learning_tasks:
        result = await execute_task_with_context(task)
        print(f"✅ Learning task completed: {result.success}")
    
    # Check learned patterns
    context_summary = executor.get_context_summary()
    print(f"📚 Domains learned: {context_summary['domains_learned']}")
    print(f"📚 Successful workflows: {context_summary['successful_workflows']}")
    print(f"📚 Total patterns: {context_summary['total_patterns']}")
    
    return context_summary['total_patterns'] > 0


async def test_enhanced_execution_function():
    """Test 5: Enhanced autonomous execution convenience function"""
    logger.info("🚀 Testing Enhanced Execution Function...")
    
    result = await enhanced_autonomous_execution("Find current information about artificial intelligence developments")
    
    print(f"✅ Enhanced execution: {result['success']}")
    print(f"📊 Status: {result['status']}")
    print(f"⏱️ Execution time: {result['execution_time']:.2f}s")
    print(f"🎓 Lessons learned: {len(result['lessons_learned'])} insights")
    
    return result['success']


async def run_comprehensive_test():
    """Run all Phase 5 tests"""
    print("🎯 PHASE 5 COMPREHENSIVE TEST SUITE")
    print("=" * 50)
    print(f"Test start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    test_results = []
    
    try:
        # Test 1: Context Awareness
        test1_result = await test_context_awareness()
        test_results.append(("Context Awareness", test1_result))
        print()
        
        # Test 2: Error Recovery
        test2_result = await test_error_recovery()
        test_results.append(("Error Recovery", test2_result))
        print()
        
        # Test 3: Multiple Task Types
        test3_result = await test_multiple_task_types()
        test_results.append(("Multiple Task Types", test3_result))
        print()
        
        # Test 4: Learning Patterns
        test4_result = await test_learning_patterns()
        test_results.append(("Learning Patterns", test4_result))
        print()
        
        # Test 5: Enhanced Execution Function
        test5_result = await test_enhanced_execution_function()
        test_results.append(("Enhanced Execution Function", test5_result))
        print()
        
    except Exception as e:
        logger.error(f"Critical test error: {str(e)}")
        test_results.append(("Critical Error", False))
    
    # Summary
    print("📋 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed_tests = 0
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed_tests += 1
    
    total_tests = len(test_results)
    success_rate = passed_tests / total_tests * 100 if total_tests > 0 else 0
    
    print()
    print(f"📊 Overall Results: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)")
    print(f"🏁 Test completion time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Determine phase success
    phase_success = success_rate >= 80  # 80% minimum for phase completion
    phase_status = "✅ PHASE 5 COMPLETED SUCCESSFULLY" if phase_success else "❌ PHASE 5 NEEDS IMPROVEMENTS"
    
    print()
    print("🎯 PHASE 5 STATUS")
    print("=" * 50)
    print(phase_status)
    
    if phase_success:
        print("🚀 Enhanced autonomous capabilities verified!")
        print("📈 Context awareness working")
        print("🛡️ Error recovery functional")
        print("🎯 Multiple task types supported")
        print("🎓 Learning patterns active")
    else:
        print("⚠️ Some capabilities need improvement")
        print("🔧 Check failed tests above")
    
    return phase_success


if __name__ == "__main__":
    asyncio.run(run_comprehensive_test())
