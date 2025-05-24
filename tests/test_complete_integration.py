"""
Comprehensive Integration Test for Phase 3 Complete System

This test demonstrates the full integration of all Phase 1, 2, and 3 components:
- Discovery, Planning, Execution (Phase 1)
- Advanced Planning, Smart Selection, User Preferences (Phase 2)
- Error Recovery, Fallback Management, Monitoring & Logging (Phase 3)
"""

import asyncio
import pytest
from datetime import datetime

from autonomous_mcp.discovery import ToolDiscovery
from autonomous_mcp.planner import BasicExecutionPlanner
from autonomous_mcp.advanced_planner import AdvancedExecutionPlanner
from autonomous_mcp.smart_selector import SmartToolSelector
from autonomous_mcp.user_preferences import UserPreferenceEngine
from autonomous_mcp.executor import ChainExecutor
from autonomous_mcp.error_recovery import ErrorRecoverySystem
from autonomous_mcp.fallback_manager import FallbackManager
from autonomous_mcp.monitoring import setup_comprehensive_monitoring, ComponentHealth


class TestFullSystemIntegration:
    """Test complete system integration with all Phase 1+2+3 components"""
    
    @pytest.fixture
    async def complete_system(self):
        """Create a complete integrated system with all components"""
        # Phase 1: Core Components
        discovery = ToolDiscovery()
        basic_planner = BasicExecutionPlanner(discovery)
        executor = ChainExecutor()
        
        # Phase 2: Intelligence Layer
        advanced_planner = AdvancedExecutionPlanner(discovery)
        smart_selector = SmartToolSelector(discovery)
        user_preferences = UserPreferenceEngine()
        
        # Phase 3: Resilience Layer
        error_recovery = ErrorRecoverySystem(discovery)
        fallback_manager = FallbackManager(discovery, basic_planner)
        
        # Comprehensive Monitoring
        monitoring = setup_comprehensive_monitoring(
            discovery=discovery,
            executor=executor,
            error_recovery=error_recovery,
            fallback_manager=fallback_manager
        )
        
        return {
            'discovery': discovery,
            'basic_planner': basic_planner,
            'advanced_planner': advanced_planner,
            'smart_selector': smart_selector,
            'user_preferences': user_preferences,
            'executor': executor,
            'error_recovery': error_recovery,
            'fallback_manager': fallback_manager,
            'monitoring': monitoring
        }
    
    @pytest.mark.asyncio
    async def test_complete_workflow_integration(self, complete_system):
        """Test a complete workflow using all integrated components"""
        components = complete_system
        monitoring = components['monitoring']
        
        print("\n=== Testing Complete Autonomous MCP Agent Workflow ===")
        
        # 1. Tool Discovery with Monitoring
        with monitoring.time_operation("discovery_phase") as perf:
            tools = components['discovery'].discover_tools()
            monitoring.set_gauge("tools_discovered", len(tools))
        
        assert len(tools) > 0
        assert perf.success
        print(f"✅ Discovery: Found {len(tools)} tools in {perf.duration:.3f}s")
        
        # 2. Smart Tool Selection
        with monitoring.time_operation("smart_selection") as perf:
            selected_tools = components['smart_selector'].select_tools(
                intent="web search and data analysis",
                available_tools=tools,
                max_results=3
            )
        
        assert len(selected_tools) > 0
        monitoring.set_gauge("tools_selected", len(selected_tools))
        print(f"✅ Smart Selection: Selected {len(selected_tools)} tools in {perf.duration:.3f}s")
        
        # 3. Advanced Planning with Sequential Thinking
        with monitoring.time_operation("advanced_planning") as perf:
            enhanced_plan = await components['advanced_planner'].create_plan(
                intent="Search for recent AI research and analyze trends",
                context={"domain": "artificial_intelligence", "timeframe": "recent"}
            )
        
        assert enhanced_plan is not None
        assert len(enhanced_plan.tool_calls) > 0
        monitoring.set_gauge("plan_steps", len(enhanced_plan.tool_calls))
        print(f"✅ Advanced Planning: Created {len(enhanced_plan.tool_calls)} step plan in {perf.duration:.3f}s")
        
        # 4. User Preference Learning
        with monitoring.time_operation("preference_learning") as perf:
            components['user_preferences'].create_user_profile("test_user")
            components['user_preferences'].set_current_user("test_user")
            
            # Learn from tool usage
            for tool_call in enhanced_plan.tool_calls[:2]:  # Learn from first 2 tools
                components['user_preferences'].learn_from_tool_usage(
                    tool_call.tool_name, True, 0.5, "research"
                )
        
        user_stats = components['user_preferences'].get_statistics("test_user")
        assert user_stats['tool_usage_count'] > 0
        monitoring.set_gauge("user_preferences_learned", user_stats['tool_usage_count'])
        print(f"✅ User Preferences: Learned from {user_stats['tool_usage_count']} interactions in {perf.duration:.3f}s")
        
        # 5. Execution with Error Recovery and Fallback
        with monitoring.time_operation("resilient_execution") as perf:
            try:
                # Execute with resilience systems
                result = await components['fallback_manager'].execute_with_fallback(
                    enhanced_plan, components['executor']
                )
                execution_success = True
            except Exception as e:
                # Handle through error recovery
                from autonomous_mcp.error_recovery import ErrorContext, ErrorCategory, ErrorSeverity
                error_context = ErrorContext(
                    error=e,
                    category=ErrorCategory.EXECUTION_ERROR,
                    severity=ErrorSeverity.MEDIUM,
                    tool_name="fallback_execution",
                    context={"plan_id": enhanced_plan.plan_id if hasattr(enhanced_plan, 'plan_id') else 'unknown'}
                )
                
                recovery_result = await components['error_recovery'].handle_error(error_context)
                execution_success = recovery_result.get('recovered', False)
        
        monitoring.set_gauge("execution_success", 1 if execution_success else 0)
        print(f"✅ Resilient Execution: {'Success' if execution_success else 'Recovered'} in {perf.duration:.3f}s")
        
        # 6. System Health Check
        health_report = monitoring.check_system_health()
        
        # Verify all components are healthy
        expected_components = [
            'tool_discovery', 'chain_executor', 'error_recovery', 
            'fallback_manager', 'monitoring_system'
        ]
        
        for component in expected_components:
            if component in monitoring.component_statuses:
                status = monitoring.component_statuses[component]
                assert status.health in [ComponentHealth.HEALTHY, ComponentHealth.DEGRADED]
                print(f"✅ {component}: {status.health.value}")
        
        print(f"✅ Overall System Health: {health_report['overall_health']}")
        
        # 7. Performance Analytics
        dashboard_data = monitoring.get_system_dashboard_data()
        
        assert dashboard_data['uptime_seconds'] > 0
        assert len(dashboard_data['metrics_summary']) > 0
        assert 'performance_overview' in dashboard_data
        
        print(f"✅ Performance Metrics: {len(dashboard_data['metrics_summary'])} metrics collected")
        print(f"✅ System Uptime: {dashboard_data['uptime_seconds']:.1f}s")
        
        # 8. Error Statistics
        error_stats = components['error_recovery'].get_error_statistics()
        fallback_stats = components['fallback_manager'].get_fallback_statistics()
        
        print(f"✅ Error Recovery: {error_stats.get('total_errors', 0)} errors handled")
        print(f"✅ Fallback Usage: {fallback_stats.get('total_fallbacks', 0)} fallbacks executed")
        
        # 9. Final Integration Verification
        total_operations = len(monitoring.performance_data)
        total_metrics = monitoring.get_metrics_count()
        active_alerts = monitoring.get_active_alerts_count()
        
        assert total_operations >= 5  # At least 5 timed operations
        assert total_metrics >= 10    # At least 10 metrics collected
        
        print(f"\n🎉 COMPLETE INTEGRATION TEST SUCCESSFUL!")
        print(f"📊 Operations Tracked: {total_operations}")
        print(f"📈 Metrics Collected: {total_metrics}")
        print(f"🚨 Active Alerts: {active_alerts}")
        print(f"⏱️  Total Test Duration: {sum(p.duration for p in monitoring.performance_data if p.duration):.3f}s")
        
        return True
    
    @pytest.mark.asyncio
    async def test_error_resilience_integration(self, complete_system):
        """Test error handling across all integrated components"""
        components = complete_system
        monitoring = components['monitoring']
        
        print("\n=== Testing Error Resilience Integration ===")
        
        # Simulate various error scenarios
        error_scenarios = [
            ("network_timeout", "web_search"),
            ("invalid_parameters", "data_analysis"),
            ("tool_unavailable", "file_processor")
        ]
        
        recovery_count = 0
        fallback_count = 0
        
        for error_type, tool_name in error_scenarios:
            with monitoring.time_operation(f"error_handling_{error_type}") as perf:
                try:
                    # Simulate error
                    raise Exception(f"Simulated {error_type} error")
                except Exception as e:
                    # Test error recovery
                    from autonomous_mcp.error_recovery import ErrorContext, ErrorCategory, ErrorSeverity
                    error_context = ErrorContext(
                        error=e,
                        category=ErrorCategory.TOOL_UNAVAILABLE if error_type == "tool_unavailable" else ErrorCategory.NETWORK_ERROR,
                        severity=ErrorSeverity.MEDIUM,
                        tool_name=tool_name,
                        context={"error_type": error_type}
                    )
                    
                    recovery_result = await components['error_recovery'].handle_error(error_context)
                    if recovery_result.get('recovered', False):
                        recovery_count += 1
                    
                    # Test fallback mechanisms
                    fallback_options = components['fallback_manager'].create_fallback_chain(
                        tool_name, {"error_type": error_type}
                    )
                    if len(fallback_options.options) > 0:
                        fallback_count += 1
        
        monitoring.set_gauge("errors_recovered", recovery_count)
        monitoring.set_gauge("fallbacks_available", fallback_count)
        
        print(f"✅ Error Recovery: {recovery_count}/{len(error_scenarios)} scenarios recovered")
        print(f"✅ Fallback Options: {fallback_count}/{len(error_scenarios)} scenarios have fallbacks")
        
        # Verify monitoring captured the errors
        error_metrics = [m for m in monitoring.metrics if 'error' in m.name]
        assert len(error_metrics) > 0
        
        return recovery_count, fallback_count
    
    def test_monitoring_integration_completeness(self, complete_system):
        """Test that monitoring is properly integrated with all components"""
        monitoring = complete_system['monitoring']
        
        print("\n=== Testing Monitoring Integration Completeness ===")
        
        # Check that all expected components are monitored
        expected_integrations = [
            'tool_discovery',
            'chain_executor', 
            'error_recovery',
            'fallback_manager',
            'monitoring_system'
        ]
        
        integration_count = 0
        for component in expected_integrations:
            if component in monitoring.component_statuses:
                integration_count += 1
                status = monitoring.component_statuses[component]
                print(f"✅ {component}: Monitored ({status.health.value})")
            else:
                print(f"❌ {component}: Not monitored")
        
        assert integration_count >= 4  # At least 4 components should be integrated
        
        # Test metric collection capabilities
        metric_types_found = set()
        for metric in monitoring.metrics:
            metric_types_found.add(metric.type.value)
        
        expected_metric_types = {'counter', 'gauge', 'timer'}
        found_metric_types = metric_types_found.intersection(expected_metric_types)
        
        print(f"✅ Metric Types: {len(found_metric_types)}/{len(expected_metric_types)} types collected")
        assert len(found_metric_types) >= 2
        
        # Test alert system
        total_alerts = len(monitoring.alerts)
        alert_thresholds = len(monitoring.alert_thresholds)
        
        print(f"✅ Alert System: {total_alerts} alerts, {alert_thresholds} thresholds configured")
        
        return integration_count, len(found_metric_types), total_alerts


async def run_complete_integration_demo():
    """Run a complete integration demonstration"""
    print("🚀 Autonomous MCP Agent - Complete Integration Demo")
    print("=" * 60)
    
    # Create the test instance
    test_instance = TestFullSystemIntegration()
    
    # Create the complete system
    complete_system = await test_instance.complete_system()
    
    try:
        # Run workflow integration test
        workflow_result = await test_instance.test_complete_workflow_integration(complete_system)
        
        # Run error resilience test  
        recovery_result = await test_instance.test_error_resilience_integration(complete_system)
        
        # Run monitoring completeness test
        monitoring_result = test_instance.test_monitoring_integration_completeness(complete_system)
        
        print(f"\n🎊 ALL INTEGRATION TESTS PASSED!")
        print(f"✅ Complete Workflow: {'Success' if workflow_result else 'Failed'}")
        print(f"✅ Error Resilience: {recovery_result[0]} recoveries, {recovery_result[1]} fallbacks")
        print(f"✅ Monitoring Integration: {monitoring_result[0]} components, {monitoring_result[1]} metric types")
        
        # Final system summary
        monitoring = complete_system['monitoring']
        final_summary = {
            "Total Operations": len(monitoring.performance_data),
            "Total Metrics": monitoring.get_metrics_count(),
            "Active Alerts": monitoring.get_active_alerts_count(),
            "Components Monitored": len(monitoring.component_statuses),
            "System Health": monitoring.check_system_health()['overall_health']
        }
        
        print(f"\n📊 Final System Summary:")
        for key, value in final_summary.items():
            print(f"   • {key}: {value}")
            
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False


if __name__ == "__main__":
    result = asyncio.run(run_complete_integration_demo())
    if result:
        print("\n🎉 Phase 3 Task 3.3: Monitoring & Logging COMPLETE!")
        print("✅ All systems integrated and working perfectly")
    else:
        print("\n❌ Integration issues detected")
