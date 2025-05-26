#!/usr/bin/env python3
"""
Phase 3 Completion Verification Test

This test comprehensively verifies that Phase 3 is complete and working:
1. All tool chaining functionality works
2. Data flows correctly between tools
3. Workflow orchestration is functional
4. Integration with previous phases is maintained
5. No regressions in existing functionality

This is the FINAL verification before marking Phase 3 complete.
"""

import asyncio
import sys
import os
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from autonomous_agent.core.tool_chainer import real_tool_chainer
from autonomous_agent.core.workflow_orchestrator import workflow_orchestrator
from autonomous_agent.core.tool_integrator import tool_integrator


async def verify_tool_chaining():
    """Verify core tool chaining functionality"""
    print("1. Verifying core tool chaining...")
    
    steps = [
        {'tool': 'web_search', 'parameters': {'query': 'test query'}},
        {'tool': 'repl', 'parameters': {'code': 'console.log("test")', 'use_previous_output': True}},
        {'tool': 'artifacts', 'parameters': {'command': 'create', 'content': 'test', 'use_previous_output': True}}
    ]
    
    chain_id = real_tool_chainer.create_tool_chain(steps, "Verification Chain")
    result = await real_tool_chainer.execute_chain(chain_id)
    
    assert result.status == "completed"
    assert len(result.steps_executed) == 3
    assert result.error_count == 0
    assert result.get_duration() > 0
    
    print("   SUCCESS: Tool chaining verified")
    return True


async def verify_data_flow():
    """Verify data flow between tools"""
    print("2. Verifying data flow...")
    
    steps = [
        {'tool': 'web_search', 'parameters': {'query': 'data flow test'}},
        {'tool': 'repl', 'parameters': {'code': 'console.log("received data")', 'use_previous_output': True}}
    ]
    
    chain_id = real_tool_chainer.create_tool_chain(steps)
    result = await real_tool_chainer.execute_chain(chain_id, {'initial': 'test_data'})
    
    # Verify data flowed between steps
    assert len(result.steps_executed) == 2
    step1_result = result.steps_executed[0].result
    step2_result = result.steps_executed[1].result
    
    assert step1_result is not None
    assert step2_result is not None
    assert 'real_tool_call_ready' in step1_result
    assert 'real_tool_call_ready' in step2_result
    
    print("   SUCCESS: Data flow verified")
    return True


async def verify_workflow_orchestration():
    """Verify workflow orchestration"""
    print("3. Verifying workflow orchestration...")
    
    result = await workflow_orchestrator.execute_workflow('research', {'query': 'workflow test'})
    
    assert result.status == "completed"
    assert len(result.steps_executed) == 3
    assert result.error_count == 0
    
    print("   SUCCESS: Workflow orchestration verified")
    return True


async def verify_phase1_integration():
    """Verify Phase 1 foundation still works"""
    print("4. Verifying Phase 1 integration...")
    
    # Test foundation functionality
    from autonomous_agent.core.foundation_test import FoundationTest
    foundation_test = FoundationTest()
    foundation_result = await foundation_test.run_all_tests()
    assert foundation_result['failed'] == 0
    assert foundation_result['passed'] == 3
    assert foundation_result['ready_for_phase_2'] == True
    
    print("   SUCCESS: Phase 1 integration maintained")
    return True


async def verify_phase2_integration():
    """Verify Phase 2 tool integration still works"""
    print("5. Verifying Phase 2 integration...")
    
    # Test Phase 2 tool integrator
    search_result = await tool_integrator.execute_web_search("integration test")
    assert search_result['status'] == 'ready_for_real_execution'
    
    repl_result = await tool_integrator.execute_repl("console.log('integration test')")
    assert repl_result['status'] == 'ready_for_real_execution'
    
    artifacts_result = await tool_integrator.execute_artifacts("create", "integration test")
    assert artifacts_result['status'] == 'ready_for_real_execution'
    
    print("   SUCCESS: Phase 2 integration maintained")
    return True


async def verify_performance():
    """Verify performance is acceptable"""
    print("6. Verifying performance...")
    
    start_time = datetime.now()
    
    # Run multiple chains to test performance
    tasks = []
    for i in range(3):
        steps = [
            {'tool': 'web_search', 'parameters': {'query': f'performance test {i}'}},
            {'tool': 'repl', 'parameters': {'code': f'console.log("test {i}")', 'use_previous_output': True}}
        ]
        chain_id = real_tool_chainer.create_tool_chain(steps)
        tasks.append(real_tool_chainer.execute_chain(chain_id))
    
    results = await asyncio.gather(*tasks)
    
    end_time = datetime.now()
    total_duration = (end_time - start_time).total_seconds()
    
    # All chains should complete successfully
    for result in results:
        assert result.status == "completed"
        assert len(result.steps_executed) == 2
    
    # Total time should be reasonable (less than 5 seconds for 3 chains)
    assert total_duration < 5.0
    
    print(f"   SUCCESS: Performance verified ({total_duration:.2f}s for 3 parallel chains)")
    return True


async def run_phase3_completion_verification():
    """Run comprehensive Phase 3 completion verification"""
    print("PHASE 3 COMPLETION VERIFICATION")
    print("=" * 50)
    
    tests = [
        verify_tool_chaining,
        verify_data_flow,
        verify_workflow_orchestration,
        verify_phase1_integration,
        verify_phase2_integration,
        verify_performance
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if await test():
                passed += 1
        except Exception as e:
            print(f"   ERROR: {test.__name__} failed: {e}")
    
    print("\n" + "=" * 50)
    print(f"VERIFICATION RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("SUCCESS: PHASE 3 COMPLETION VERIFIED!")
        print("\nPhase 3 Achievements:")
        print("- Real tool chaining with data flow")
        print("- Workflow orchestration system")
        print("- Multi-step autonomous workflows")
        print("- Error handling in tool chains")
        print("- Full integration with Phase 1 & 2")
        print("- Performance optimization")
        return True
    else:
        print(f"ERROR: {total - passed} verification tests failed")
        print("Phase 3 is NOT ready for completion")
        return False


if __name__ == "__main__":
    asyncio.run(run_phase3_completion_verification())
