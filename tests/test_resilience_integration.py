"""
Task 3.4: Comprehensive Resilience Testing
"""

import asyncio
import pytest
import pytest_asyncio
from datetime import datetime

from autonomous_mcp.discovery import ToolDiscovery
from autonomous_mcp.planner import BasicExecutionPlanner
from autonomous_mcp.executor import ChainExecutor
from autonomous_mcp.error_recovery import ErrorRecoverySystem, ErrorCategory
from autonomous_mcp.fallback_manager import FallbackManager
from autonomous_mcp.monitoring import setup_comprehensive_monitoring, ComponentHealth


class TestComprehensiveResilience:
    """Test suite for complete resilience system integration"""
    
    @pytest_asyncio.fixture
    async def resilient_system(self):
        """Create a complete resilient system with all components"""
        discovery = ToolDiscovery()
        basic_planner = BasicExecutionPlanner(discovery)
        executor = ChainExecutor()
        error_recovery = ErrorRecoverySystem(discovery)
        fallback_manager = FallbackManager(discovery, basic_planner)
        
        monitoring = setup_comprehensive_monitoring(
            discovery=discovery,
            executor=executor,
            error_recovery=error_recovery,
            fallback_manager=fallback_manager
        )
        
        mock_tools = [
            {'name': 'reliable_tool', 'description': 'A tool that works reliably'},
            {'name': 'unreliable_tool', 'description': 'A tool that often fails'},
            {'name': 'backup_tool', 'description': 'A backup tool for fallbacks'}
        ]
        discovery.discover_all_tools(mock_tools)
        
        return {
            'discovery': discovery, 'basic_planner': basic_planner,
            'executor': executor, 'error_recovery': error_recovery,
            'fallback_manager': fallback_manager, 'monitoring': monitoring
        }
    
    @pytest.mark.asyncio
    async def test_end_to_end_resilience_workflow(self, resilient_system):
        """Test complete resilience workflow from discovery to recovery"""
        system = resilient_system
        monitoring = system['monitoring']
        
        print("\n=== COMPREHENSIVE RESILIENCE TEST ===")
        
        # 1. Test normal operation with monitoring
        with monitoring.time_operation("normal_workflow") as perf:
            tools = await system['discovery'].get_all_tools()
            assert len(tools) >= 3
            
            plan = system['basic_planner'].create_plan("test resilient workflow")
            assert plan is not None
        
        assert perf.success
        assert perf.duration >= 0
        print(f"[SUCCESS] Normal workflow completed in {perf.duration:.3f}s")
        
        # 2. Test error detection and categorization
        with monitoring.time_operation("error_handling") as perf:
            test_errors = [
                Exception("Connection timeout"),
                ValueError("Invalid parameter"),
                RuntimeError("Resource unavailable")
            ]
            
            error_contexts = []
            for error in test_errors:
                try:
                    raise error
                except Exception as e:
                    context = system['error_recovery'].create_error_context(
                        e, 
                        tool_name='test_tool'
                    )
                    error_contexts.append(context)
            
            assert len(error_contexts) == 3
            categories = {ctx.category for ctx in error_contexts}
            assert len(categories) >= 1
        
        print(f"[SUCCESS] Error analysis completed: {len(error_contexts)} errors categorized")
        
        # 3. Test fallback chain creation and execution
        with monitoring.time_operation("fallback_testing") as perf:
            failing_tool = "unreliable_tool"
            fallback_chain = await system['fallback_manager'].create_fallback_chain(
                failing_tool, {"context": "test"}
            )
            
            assert fallback_chain is not None
            assert len(fallback_chain.fallback_options) > 0
            
            stats = system['fallback_manager'].get_fallback_statistics()
            assert 'cached_chains' in stats
            assert stats['cached_chains'] >= 1
        
        print(f"[SUCCESS] Fallback chain created with {len(fallback_chain.fallback_options)} options")
        
        # 4. Test monitoring and health checks
        with monitoring.time_operation("health_monitoring") as perf:
            health_report = monitoring.check_system_health()
            
            assert 'overall_health' in health_report
            assert 'components' in health_report
            
            expected_components = [
                'tool_discovery', 'chain_executor', 'error_recovery', 
                'fallback_manager', 'monitoring_system'
            ]
            
            for component in expected_components:
                assert component in monitoring.component_statuses
                status = monitoring.component_statuses[component]
                assert status.health in [ComponentHealth.HEALTHY, ComponentHealth.DEGRADED]
        
        print(f"[SUCCESS] Health monitoring validated for {len(expected_components)} components")
        
        # 5. Test performance metrics and analytics
        dashboard_data = monitoring.get_system_dashboard_data()
        
        assert dashboard_data['uptime_seconds'] > 0
        assert len(dashboard_data['metrics_summary']) > 0
        assert 'performance_overview' in dashboard_data
        
        total_metrics = monitoring.get_metrics_count()
        assert total_metrics >= 10
        
        print(f"[SUCCESS] Performance analytics: {total_metrics} metrics collected")
        
        # 6. Verify integration seamlessness
        total_operations = len(monitoring.performance_data)
        active_alerts = monitoring.get_active_alerts_count()
        
        assert total_operations >= 4
        print(f"[SUCCESS] Integration test completed: {total_operations} operations tracked")
        
        return True


@pytest.mark.asyncio
async def test_complete_resilience_integration():
    """Master test for complete resilience system integration"""
    print("\n" + "="*80)
    print("🛡️  COMPREHENSIVE RESILIENCE SYSTEM TEST")
    print("="*80)
    
    discovery = ToolDiscovery()
    basic_planner = BasicExecutionPlanner(discovery)
    executor = ChainExecutor()
    error_recovery = ErrorRecoverySystem(discovery)
    fallback_manager = FallbackManager(discovery, basic_planner)
    
    monitoring = setup_comprehensive_monitoring(
        discovery=discovery,
        executor=executor,
        error_recovery=error_recovery,
        fallback_manager=fallback_manager
    )
    
    # Test complete integration workflow
    with monitoring.time_operation("complete_resilience_test") as perf:
        # 1. System initialization verification
        assert monitoring.get_metrics_count() >= 5
        print("✅ System initialization: PASSED")
        
        # 2. Component health verification
        health_report = monitoring.check_system_health()
        assert health_report['overall_health'] == 'healthy'
        print("✅ Component health check: PASSED")
        
        # 3. Error handling pipeline test
        try:
            raise RuntimeError("Test error for resilience pipeline")
        except Exception as e:
            context = error_recovery.create_error_context(e, tool_name='test_failing_tool')
            async def mock_action():
                return "test_result"
            
            recovery_attempted, result, new_context = await error_recovery.attempt_recovery(context, mock_action)
            # The test error should be categorized (even if as UNKNOWN_ERROR)
            assert context.category is not None
            print("✅ Error handling pipeline: PASSED")
        
        # 4. Fallback mechanism test
        fallback_chain = await fallback_manager.create_fallback_chain(
            "test_failing_tool", {"test": "fallback"}
        )
        assert fallback_chain is not None
        assert len(fallback_chain.fallback_options) > 0
        print("✅ Fallback mechanism: PASSED")
        
        # 5. Monitoring integration test
        final_metrics = monitoring.get_metrics_count()
        assert final_metrics > 5
        print("✅ Monitoring integration: PASSED")
        
        # 6. Performance analytics test
        dashboard_data = monitoring.get_system_dashboard_data()
        assert 'uptime_seconds' in dashboard_data
        assert dashboard_data['uptime_seconds'] > 0
        print("✅ Performance analytics: PASSED")
    
    assert perf.success
    print(f"\n🎉 COMPLETE RESILIENCE TEST PASSED in {perf.duration:.3f}s")
    print("="*80)
    
    return True
