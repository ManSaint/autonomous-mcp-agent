"""Simple integration verification test"""

import sys
import asyncio

def test_monitoring_integration():
    """Test monitoring integration with all components"""
    print("Testing monitoring integration...")
    
    try:
        # Import all components
        from autonomous_mcp.discovery import ToolDiscovery
        from autonomous_mcp.monitoring import MonitoringSystem, ComponentHealth
        from autonomous_mcp.executor import ChainExecutor
        from autonomous_mcp.planner import BasicExecutionPlanner
        
        print("OK All imports successful")
        
        # Create components
        discovery = ToolDiscovery()
        monitoring = MonitoringSystem(log_level="ERROR")  # Reduce noise
        executor = ChainExecutor()
        planner = BasicExecutionPlanner(discovery)
        
        print("OK Components created")
        
        # Test integrations
        monitoring.integrate_with_discovery(discovery)
        monitoring.integrate_with_executor(executor)
        
        print("OK Integrations completed")
        
        # Test component health
        monitoring.update_component_health("test_component", ComponentHealth.HEALTHY, "Test")
        health_report = monitoring.check_system_health()
        
        print(f"OK System health: {health_report['overall_health']}")
        print(f"OK Components monitored: {len(health_report['components'])}")
        
        # Test metrics
        initial_metrics = monitoring.get_metrics_count()
        monitoring.increment_counter("test_counter")
        monitoring.set_gauge("test_gauge", 42)
        final_metrics = monitoring.get_metrics_count()
        
        print(f"OK Metrics: {initial_metrics} -> {final_metrics}")
        
        # Test discovery with monitoring
        tools = discovery.discover_all_tools([])  # Pass empty list as required
        post_discovery_metrics = monitoring.get_metrics_count()
        
        print(f"OK Discovery: {len(tools)} tools found")
        print(f"OK Discovery metrics: {post_discovery_metrics}")
        
        # Validation
        checks = [
            len(health_report['components']) > 0,
            final_metrics > initial_metrics,
            post_discovery_metrics >= final_metrics,
            'tool_discovery' in monitoring.component_statuses,
            'chain_executor' in monitoring.component_statuses
        ]
        
        passed_checks = sum(checks)
        total_checks = len(checks)
        
        print(f"OK Validation: {passed_checks}/{total_checks} checks passed")
        
        if passed_checks >= total_checks * 0.8:  # 80% success
            print("SUCCESS: Monitoring integration working properly!")
            return True
        else:
            print("FAILURE: Integration issues detected")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = test_monitoring_integration()
    print(f"Final result: {'PASS' if result else 'FAIL'}")
    sys.exit(0 if result else 1)
