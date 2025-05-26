#!/usr/bin/env python3
"""Phase 3 Integration Test - Tool Chaining"""

import asyncio
import sys
import os
from datetime import datetime

# Add the autonomous_agent directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from autonomous_agent.core.tool_chainer import real_tool_chainer
    from autonomous_agent.core.workflow_orchestrator import workflow_orchestrator
    print("SUCCESS: Successfully imported Phase 3 components")
except ImportError as e:
    print(f"ERROR: Import failed: {e}")
    sys.exit(1)


async def test_basic_tool_chain():
    """Test basic tool chain creation and execution"""
    print("\nTesting basic tool chain...")
    
    try:
        # Create a simple 3-step chain
        steps = [
            {'tool': 'web_search', 'parameters': {'query': 'Python asyncio best practices 2025'}},
            {'tool': 'repl', 'parameters': {'code': 'console.log("Processing search results")', 'use_previous_output': True}},
            {'tool': 'artifacts', 'parameters': {'command': 'create', 'content': 'Analysis Report', 'use_previous_output': True}}
        ]
        
        # Create and execute chain
        chain_id = real_tool_chainer.create_tool_chain(steps, "Test Basic Chain")
        print(f"SUCCESS: Created chain: {chain_id}")
        
        result = await real_tool_chainer.execute_chain(chain_id)
        
        # Verify results
        assert result.status == "completed", f"Expected completed, got {result.status}"
        assert len(result.steps_executed) == 3, f"Expected 3 steps, got {len(result.steps_executed)}"
        assert result.error_count == 0, f"Expected 0 errors, got {result.error_count}"
        
        print(f"SUCCESS: Chain executed successfully in {result.get_duration():.2f} seconds")
        print(f"SUCCESS: All 3 steps completed without errors")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Basic tool chain test failed: {e}")
        return False


async def test_data_flow():
    """Test data flow between tools"""
    print("\nTesting data flow between tools...")
    
    try:
        steps = [
            {'tool': 'web_search', 'parameters': {'query': 'machine learning trends 2025'}},
            {'tool': 'repl', 'parameters': {'code': 'console.log("Data received:", typeof data)', 'use_previous_output': True}}
        ]
        
        chain_id = real_tool_chainer.create_tool_chain(steps, "Data Flow Test")
        result = await real_tool_chainer.execute_chain(chain_id, {'initial': 'test_data'})
        
        # Verify data flow occurred
        assert len(result.steps_executed) == 2
        
        # Check that second step received data from first step
        second_step = result.steps_executed[1]
        assert second_step.result is not None
        
        print("SUCCESS: Data flow between tools verified")
        return True
        
    except Exception as e:
        print(f"ERROR: Data flow test failed: {e}")
        return False


async def test_workflow_orchestration():
    """Test workflow orchestration"""
    print("\nTesting workflow orchestration...")
    
    try:
        # Execute research workflow
        result = await workflow_orchestrator.execute_workflow(
            'research', 
            {'query': 'autonomous AI agents 2025'}
        )
        
        assert result.status == "completed"
        assert len(result.steps_executed) == 3  # web_search -> repl -> artifacts
        
        print("SUCCESS: Workflow orchestration working")
        return True
        
    except Exception as e:
        print(f"ERROR: Workflow orchestration test failed: {e}")
        return False


async def test_integration_with_phase2():
    """Test integration with Phase 2 components"""
    print("\nTesting integration with Phase 2...")
    
    try:
        # Import Phase 2 components
        from autonomous_agent.core.tool_integrator import tool_integrator
        
        # Verify Phase 2 still works
        search_result = await tool_integrator.execute_web_search("test query")
        assert search_result['status'] == 'ready_for_real_execution'
        
        print("SUCCESS: Phase 2 integration maintained")
        return True
        
    except Exception as e:
        print(f"ERROR: Phase 2 integration test failed: {e}")
        return False


async def run_all_tests():
    """Run all Phase 3 tests"""
    print("Starting Phase 3 Integration Tests")
    print("=" * 50)
    
    tests = [
        test_basic_tool_chain,
        test_data_flow,
        test_workflow_orchestration,
        test_integration_with_phase2
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if await test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"Phase 3 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("SUCCESS: ALL PHASE 3 TESTS PASSED!")
        return True
    else:
        print(f"ERROR: {total - passed} tests failed")
        return False


if __name__ == "__main__":
    asyncio.run(run_all_tests())
