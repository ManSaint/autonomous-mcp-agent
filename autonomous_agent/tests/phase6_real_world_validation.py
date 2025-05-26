#!/usr/bin/env python3
"""Phase 6: Real-World Validation"""
import sys, os, time, asyncio

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))
from enhanced_executor import ContextAwareExecutor

async def run_validation():
    print("PHASE 6: REAL-WORLD VALIDATION")
    print("=" * 50)
    
    executor = ContextAwareExecutor()
    start_time = time.time()
    
    tests = [
        "Research latest quantum computing developments in 2025",
        "Analyze current cryptocurrency market trends", 
        "Create a beginner's guide to machine learning",
        "Summarize recent renewable energy policy news",
        "Research Python asyncio best practices"
    ]
    
    results = []
    
    for i, task in enumerate(tests, 1):
        print(f"Test {i}: {task}")
        
        test_start = time.time()
        try:
            # Use the async interface
            context = executor.build_execution_context(task)
            result = await executor.execute_with_context(context)
            execution_time = time.time() - test_start
            success = result.status.value == 'completed'
            
            results.append({
                'task': task, 'success': success, 'time': round(execution_time, 2),
                'tools': []  # Will extract from result if available
            })
            
            status = "SUCCESS" if success else "FAILED"
            print(f"   {status} ({execution_time:.2f}s)")
            
        except Exception as e:
            results.append({
                'task': task, 'success': False, 'time': round(time.time() - test_start, 2), 'error': str(e)
            })
            print(f"   ERROR: {str(e)}")
        
        print()
    
    # Analysis
    total_tests = len(results)
    successful = sum(1 for r in results if r['success'])
    success_rate = (successful / total_tests) * 100
    avg_time = sum(r['time'] for r in results) / total_tests
    
    print("RESULTS SUMMARY")
    print(f"Success Rate: {success_rate:.1f}% ({successful}/{total_tests})")
    print(f"Average Time: {avg_time:.2f}s")
    print(f"Total Time: {time.time() - start_time:.2f}s")
    
    # Tool usage analysis
    all_tools = []
    for r in results:
        if 'tools' in r:
            all_tools.extend(r['tools'])
    
    tool_usage = {}
    for tool in all_tools:
        tool_usage[tool] = tool_usage.get(tool, 0) + 1
    
    if tool_usage:
        print("\nTool Usage:")
        for tool, count in sorted(tool_usage.items(), key=lambda x: x[1], reverse=True):
            print(f"   {tool}: {count} times")
    
    return {
        'success_rate': success_rate,
        'avg_time': avg_time,
        'results': results,
        'tool_usage': tool_usage
    }

if __name__ == "__main__":
    validation_results = asyncio.run(run_validation())
