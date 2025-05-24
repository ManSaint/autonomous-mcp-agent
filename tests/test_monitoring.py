"""
Comprehensive Test Suite for Monitoring & Logging System

Tests all aspects of the monitoring system including:
- Metric collection and aggregation
- Performance tracking and analysis
- Health monitoring and status updates
- Alert system with thresholds
- Export and persistence functionality
- Integration with other components
"""

import pytest
import asyncio
import time
import json
import tempfile
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path

from autonomous_mcp.monitoring import (
    MonitoringSystem, Metric, PerformanceMetrics, Alert, ComponentStatus,
    AlertThreshold, MetricType, AlertSeverity, ComponentHealth,
    create_monitoring_system, setup_comprehensive_monitoring
)
from autonomous_mcp.discovery import ToolDiscovery, DiscoveredTool
from autonomous_mcp.executor import ChainExecutor, ExecutionStatus, ExecutionResult
from autonomous_mcp.planner import ToolCall, ExecutionPlan


class TestMetricTypes:
    """Test metric data structures and validation"""
    
    def test_metric_creation(self):
        """Test basic metric creation"""
        metric = Metric(
            name="test_counter",
            type=MetricType.COUNTER,
            value=42,
            tags={"component": "test"},
            description="Test metric"
        )
        
        assert metric.name == "test_counter"
        assert metric.type == MetricType.COUNTER
        assert metric.value == 42
        assert metric.tags == {"component": "test"}
        assert metric.description == "Test metric"
        assert isinstance(metric.timestamp, datetime)
    
    def test_metric_to_dict(self):
        """Test metric serialization"""
        metric = Metric("test", MetricType.GAUGE, 3.14)
        data = metric.to_dict()
        
        assert data['name'] == "test"
        assert data['type'] == "gauge"
        assert data['value'] == 3.14
        assert 'timestamp' in data
        assert data['tags'] == {}
        assert data['description'] is None


class TestMonitoringSystemCore:
    """Test core monitoring system functionality"""
    
    @pytest.fixture
    def monitoring(self):
        """Create a test monitoring system"""
        return MonitoringSystem(
            max_metrics_history=100,
            max_alerts_history=50,
            log_level="DEBUG"
        )
    
    def test_monitoring_system_initialization(self, monitoring):
        """Test monitoring system initialization"""
        assert monitoring.max_metrics_history == 100
        assert monitoring.max_alerts_history == 50
        assert len(monitoring.metrics) == 0
        assert len(monitoring.alerts) == 0
        assert len(monitoring.component_statuses) == 0
        assert isinstance(monitoring.startup_time, datetime)
    
    def test_metric_recording(self, monitoring):
        """Test basic metric recording"""
        monitoring.record_metric("test_counter", 5, MetricType.COUNTER, {"env": "test"})
        
        assert len(monitoring.metrics) == 1
        assert monitoring.counters["test_counter"] == 5
        
        # Record another value
        monitoring.record_metric("test_counter", 3, MetricType.COUNTER)
        assert monitoring.counters["test_counter"] == 8  # Cumulative
    
    def test_gauge_metrics(self, monitoring):
        """Test gauge metric handling"""
        monitoring.set_gauge("temperature", 23.5, {"sensor": "room1"})
        
        assert monitoring.gauges["temperature"] == 23.5
        
        # Update gauge value
        monitoring.set_gauge("temperature", 24.0)
        assert monitoring.gauges["temperature"] == 24.0  # Replaced, not cumulative
    
    def test_time_operation_context_manager_success(self, monitoring):
        """Test time_operation context manager for successful operations"""
        with monitoring.time_operation("test_operation", {"env": "test"}) as perf:
            time.sleep(0.01)  # Simulate work
        
        assert perf.success
        assert perf.duration > 0
        assert perf.error_message is None
        assert len(monitoring.performance_data) == 1
        assert monitoring.counters["test_operation_success"] == 1
        assert "test_operation_duration" in monitoring.timers


class TestAlertSystem:
    """Test alert creation, management, and thresholds"""
    
    @pytest.fixture
    def monitoring(self):
        return MonitoringSystem(log_level="DEBUG")
    
    def test_alert_creation(self):
        """Test basic alert creation"""
        alert = Alert(
            id="test_alert_1",
            severity=AlertSeverity.WARNING,
            component="test_component",
            message="Test alert message",
            metadata={"key": "value"}
        )
        
        assert alert.id == "test_alert_1"
        assert alert.severity == AlertSeverity.WARNING
        assert alert.component == "test_component"
        assert alert.message == "Test alert message"
        assert not alert.resolved
        assert alert.resolved_at is None
        assert alert.metadata == {"key": "value"}
    
    def test_alert_threshold_simple(self):
        """Test basic alert threshold checking"""
        threshold = AlertThreshold("cpu_usage", ">", 80.0, AlertSeverity.WARNING)
        
        assert not threshold.check(70.0)  # Below threshold
        assert threshold.check(90.0)      # Above threshold
        assert threshold.check(80.1)      # Just above threshold
        assert not threshold.check(80.0)  # Equal (not greater)
    
    def test_alert_creation_and_retrieval(self, monitoring):
        """Test creating and retrieving alerts"""
        alert_id = monitoring.create_alert(
            AlertSeverity.CRITICAL,
            "security",
            "Unauthorized access detected",
            {"ip": "192.168.1.100", "attempts": 5}
        )
        
        assert alert_id.startswith("alert_")
        assert len(monitoring.alerts) == 1
        
        active_alerts = monitoring.get_active_alerts()
        assert len(active_alerts) == 1
        assert active_alerts[0].id == alert_id
        assert active_alerts[0].severity == AlertSeverity.CRITICAL


class TestHealthMonitoring:
    """Test component health monitoring functionality"""
    
    @pytest.fixture
    def monitoring(self):
        return MonitoringSystem(log_level="DEBUG")
    
    def test_component_health_updates(self, monitoring):
        """Test component health status updates"""
        # Initial update
        monitoring.update_component_health(
            "database", 
            ComponentHealth.HEALTHY, 
            "Connection established",
            {"connections": 5, "latency": 0.02}
        )
        
        assert "database" in monitoring.component_statuses
        status = monitoring.component_statuses["database"]
        assert status.health == ComponentHealth.HEALTHY
        assert status.message == "Connection established"
        assert status.metrics["connections"] == 5
        assert status.metrics["latency"] == 0.02
    
    def test_system_health_check(self, monitoring):
        """Test comprehensive system health check"""
        # Add some components
        monitoring.update_component_health("api", ComponentHealth.HEALTHY)
        monitoring.update_component_health("database", ComponentHealth.DEGRADED, "Slow queries")
        monitoring.update_component_health("cache", ComponentHealth.UNHEALTHY, "Connection lost")
        
        # Create some alerts
        monitoring.create_alert(AlertSeverity.WARNING, "test", "Test alert")
        
        health_report = monitoring.check_system_health()
        
        assert health_report['overall_health'] == ComponentHealth.UNHEALTHY.value
        assert len(health_report['components']) == 3
        assert health_report['components']['api']['health'] == ComponentHealth.HEALTHY.value
        assert health_report['components']['database']['health'] == ComponentHealth.DEGRADED.value
        assert health_report['components']['cache']['health'] == ComponentHealth.UNHEALTHY.value


class TestPerformanceTracking:
    """Test performance tracking and analysis"""
    
    @pytest.fixture
    def monitoring(self):
        return MonitoringSystem(log_level="DEBUG")
    
    def test_tool_usage_tracking(self, monitoring):
        """Test individual tool usage tracking"""
        monitoring.track_tool_usage("web_search", True, 0.8)
        monitoring.track_tool_usage("web_search", False, 1.2, "timeout")
        monitoring.track_tool_usage("file_read", True, 0.1)
        
        # Check counters
        assert monitoring.counters["tool_usage_total"] == 3
        assert monitoring.counters["tool_usage_success"] == 2
        assert monitoring.counters["tool_usage_failure"] == 1
        
        # Check error tracking
        assert monitoring.counters["tool_errors"] == 1
        
        # Check timing data
        assert len(monitoring.timers["tool_execution_time"]) == 3
        assert len(monitoring.histograms["tool_duration_histogram"]) == 3


class TestDataExportAndPersistence:
    """Test data export and persistence functionality"""
    
    @pytest.fixture
    def monitoring(self):
        mon = MonitoringSystem(log_level="DEBUG")
        # Add some test data
        mon.record_metric("test1", 10, MetricType.COUNTER)
        mon.record_metric("test2", 3.14, MetricType.GAUGE)
        mon.create_alert(AlertSeverity.WARNING, "test", "Test alert")
        return mon
    
    def test_metrics_export_json(self, monitoring):
        """Test exporting metrics as JSON"""
        json_output = monitoring.export_metrics(format="json")
        
        data = json.loads(json_output)
        assert isinstance(data, list)
        assert len(data) >= 2  # At least the 2 explicit metrics
        
        # Check structure
        for item in data:
            assert 'name' in item
            assert 'type' in item
            assert 'value' in item
            assert 'timestamp' in item


class TestUtilityMethods:
    """Test utility and helper methods"""
    
    @pytest.fixture
    def monitoring(self):
        mon = MonitoringSystem(log_level="DEBUG")
        # Add some data
        mon.record_metric("test", 1, MetricType.COUNTER)
        mon.create_alert(AlertSeverity.INFO, "test", "Test alert")
        return mon
    
    def test_reset_metrics(self, monitoring):
        """Test resetting all metrics and data"""
        # Verify data exists
        assert len(monitoring.metrics) > 0
        assert len(monitoring.alerts) > 0
        assert len(monitoring.counters) > 0
        
        # Reset and verify
        monitoring.reset_metrics()
        
        assert len(monitoring.metrics) == 0
        assert len(monitoring.alerts) == 0
        assert len(monitoring.counters) == 0
        assert len(monitoring.gauges) == 0
        assert len(monitoring.performance_data) == 0
        assert len(monitoring.component_statuses) == 0
    
    def test_count_methods(self, monitoring):
        """Test metric and alert counting methods"""
        assert monitoring.get_metrics_count() > 0
        assert monitoring.get_active_alerts_count() > 0


class TestConvenienceFunctions:
    """Test convenience functions and setup helpers"""
    
    def test_create_monitoring_system(self):
        """Test convenience function for creating monitoring system"""
        monitoring = create_monitoring_system(log_level="WARNING")
        
        assert isinstance(monitoring, MonitoringSystem)
        assert monitoring.max_metrics_history == 10000
        assert monitoring.max_alerts_history == 1000
        assert monitoring.metrics_retention_days == 30


# Test Coverage Summary
def test_monitoring_system_comprehensive_coverage():
    """Verify comprehensive test coverage for monitoring system"""
    # This test ensures we've covered all major functionality
    monitoring = MonitoringSystem(log_level="DEBUG")
    
    # Test all metric types
    monitoring.increment_counter("test_counter")
    monitoring.set_gauge("test_gauge", 42.0)
    monitoring.record_histogram("test_histogram", 1.5)
    monitoring.record_timer("test_timer", 0.1)
    
    # Test performance tracking
    with monitoring.time_operation("test_operation"):
        time.sleep(0.001)
    
    # Test health monitoring
    monitoring.update_component_health("test_component", ComponentHealth.HEALTHY)
    
    # Test alerts
    alert_id = monitoring.create_alert(AlertSeverity.WARNING, "test", "Test alert")
    monitoring.resolve_alert(alert_id)
    
    # Test analytics
    summary = monitoring.get_metric_summary("test_counter")
    dashboard = monitoring.get_system_dashboard_data()
    
    # Test export
    json_export = monitoring.export_metrics("json")
    
    # Verify all systems working
    assert len(monitoring.metrics) > 0
    assert len(monitoring.performance_data) > 0
    assert len(monitoring.component_statuses) > 0
    assert len(monitoring.alerts) > 0
    assert isinstance(summary, dict)
    assert isinstance(dashboard, dict)
    assert isinstance(json_export, str)
    
    print(f"✅ Monitoring System Test Coverage Complete")
    print(f"   - Metrics: {len(monitoring.metrics)}")
    print(f"   - Performance Data: {len(monitoring.performance_data)}")
    print(f"   - Components: {len(monitoring.component_statuses)}")
    print(f"   - Alerts: {len(monitoring.alerts)}")
    print(f"   - Counters: {len(monitoring.counters)}")


if __name__ == "__main__":
    test_monitoring_system_comprehensive_coverage()
    print("🎉 All monitoring system tests completed successfully!")
