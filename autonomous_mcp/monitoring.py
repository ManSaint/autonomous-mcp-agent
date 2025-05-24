"""
Monitoring & Logging System for Autonomous MCP Agent

This module provides comprehensive monitoring, logging, and observability
capabilities for tracking system performance, health, and operational metrics.

Key Features:
- Centralized metrics collection and aggregation
- Performance monitoring with detailed timing analysis
- Health monitoring for all system components
- Structured logging with configurable levels and formats
- Alert system with threshold-based notifications
- Metrics export in multiple formats (JSON, CSV, Prometheus)
- Real-time dashboard data collection
- Historical trend analysis
- Resource usage tracking
- Error correlation and analysis
"""

import asyncio
import time
import logging
import json
import csv
import threading
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Set, Any, Callable, Union, Tuple, NamedTuple
from dataclasses import dataclass, field, asdict
from collections import defaultdict, deque
from pathlib import Path
import statistics
import psutil
import os
from contextlib import contextmanager

from .discovery import ToolDiscovery, DiscoveredTool
from .planner import ToolCall, ExecutionPlan
from .executor import ChainExecutor, ExecutionStatus, ExecutionResult
from .error_recovery import ErrorRecoverySystem, ErrorContext, ErrorCategory, ErrorSeverity
from .fallback_manager import FallbackManager, FallbackStrategy


class MetricType(Enum):
    """Types of metrics collected by the monitoring system"""
    COUNTER = "counter"           # Monotonically increasing values
    GAUGE = "gauge"              # Point-in-time values
    HISTOGRAM = "histogram"       # Distribution of values
    TIMER = "timer"              # Duration measurements
    RATE = "rate"                # Events per time unit
    PERCENTAGE = "percentage"     # Ratio values (0-100)


class AlertSeverity(Enum):
    """Alert severity levels for notification prioritization"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class ComponentHealth(Enum):
    """Health status for system components"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class Metric:
    """Individual metric data point"""
    name: str
    type: MetricType
    value: Union[int, float]
    timestamp: datetime = field(default_factory=datetime.now)
    tags: Dict[str, str] = field(default_factory=dict)
    description: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metric to dictionary for serialization"""
        return {
            'name': self.name,
            'type': self.type.value,
            'value': self.value,
            'timestamp': self.timestamp.isoformat(),
            'tags': self.tags,
            'description': self.description
        }


@dataclass 
class PerformanceMetrics:
    """Performance metrics for a specific operation"""
    operation_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None  # seconds
    success: bool = False
    error_message: Optional[str] = None
    resource_usage: Dict[str, float] = field(default_factory=dict)
    tags: Dict[str, str] = field(default_factory=dict)
    
    def finish(self, success: bool = True, error_message: Optional[str] = None):
        """Mark operation as finished and calculate duration"""
        self.end_time = datetime.now()
        self.duration = (self.end_time - self.start_time).total_seconds()
        self.success = success
        self.error_message = error_message
        
        # Capture current resource usage
        try:
            process = psutil.Process()
            self.resource_usage = {
                'cpu_percent': process.cpu_percent(),
                'memory_mb': process.memory_info().rss / 1024 / 1024,
                'memory_percent': process.memory_percent(),
                'num_threads': process.num_threads()
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass


@dataclass
class Alert:
    """System alert/notification"""
    id: str
    severity: AlertSeverity
    component: str
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def resolve(self):
        """Mark alert as resolved"""
        self.resolved = True
        self.resolved_at = datetime.now()


@dataclass
class ComponentStatus:
    """Health status for a system component"""
    component_name: str
    health: ComponentHealth
    last_check: datetime
    message: Optional[str] = None
    metrics: Dict[str, float] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    
    def update_health(self, health: ComponentHealth, message: Optional[str] = None):
        """Update component health status"""
        self.health = health
        self.last_check = datetime.now()
        self.message = message


class AlertThreshold:
    """Configurable alert threshold"""
    
    def __init__(self, metric_name: str, operator: str, value: float, 
                 severity: AlertSeverity = AlertSeverity.WARNING,
                 duration_seconds: float = 0):
        self.metric_name = metric_name
        self.operator = operator  # '>', '<', '>=', '<=', '==', '!='
        self.value = value
        self.severity = severity
        self.duration_seconds = duration_seconds
        self.triggered_at: Optional[datetime] = None
        
    def check(self, metric_value: float) -> bool:
        """Check if threshold is breached"""
        operators = {
            '>': lambda x, y: x > y,
            '<': lambda x, y: x < y,
            '>=': lambda x, y: x >= y,
            '<=': lambda x, y: x <= y,
            '==': lambda x, y: x == y,
            '!=': lambda x, y: x != y
        }
        
        op_func = operators.get(self.operator)
        if not op_func:
            raise ValueError(f"Unknown operator: {self.operator}")
            
        is_breached = op_func(metric_value, self.value)
        
        if is_breached and self.triggered_at is None:
            self.triggered_at = datetime.now()
        elif not is_breached:
            self.triggered_at = None
            
        # Check duration requirement
        if is_breached and self.triggered_at:
            breach_duration = (datetime.now() - self.triggered_at).total_seconds()
            return breach_duration >= self.duration_seconds
            
        return False


class MonitoringSystem:
    """
    Comprehensive monitoring and logging system for the Autonomous MCP Agent.
    
    Provides centralized collection, analysis, and export of system metrics,
    performance data, health status, and operational logs.
    """
    
    def __init__(self, 
                 max_metrics_history: int = 10000,
                 max_alerts_history: int = 1000,
                 metrics_retention_days: int = 30,
                 log_level: str = "INFO",
                 log_file: Optional[str] = None,
                 enable_structured_logging: bool = True):
        """
        Initialize the monitoring system.
        
        Args:
            max_metrics_history: Maximum number of metrics to keep in memory
            max_alerts_history: Maximum number of alerts to keep in memory
            metrics_retention_days: How long to retain metrics data
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: Optional log file path
            enable_structured_logging: Use structured JSON logging
        """
        self.max_metrics_history = max_metrics_history
        self.max_alerts_history = max_alerts_history
        self.metrics_retention_days = metrics_retention_days
        
        # Storage for metrics and operational data
        self.metrics: deque = deque(maxlen=max_metrics_history)
        self.performance_data: List[PerformanceMetrics] = []
        self.alerts: deque = deque(maxlen=max_alerts_history)
        self.component_statuses: Dict[str, ComponentStatus] = {}
        self.alert_thresholds: List[AlertThreshold] = []
        
        # Thread-safe access
        self._metrics_lock = threading.Lock()
        self._alerts_lock = threading.Lock()
        self._performance_lock = threading.Lock()
        
        # Counters and aggregated metrics
        self.counters: Dict[str, int] = defaultdict(int)
        self.gauges: Dict[str, float] = {}
        self.histograms: Dict[str, List[float]] = defaultdict(list)
        self.timers: Dict[str, List[float]] = defaultdict(list)
        
        # System startup time
        self.startup_time = datetime.now()
        
        # Initialize logging
        self._setup_logging(log_level, log_file, enable_structured_logging)
        
        # Built-in alert thresholds
        self._setup_default_thresholds()
        
        self.logger.info("MonitoringSystem initialized", extra={
            'component': 'monitoring',
            'max_metrics_history': max_metrics_history,
            'max_alerts_history': max_alerts_history,
            'log_level': log_level
        })
    
    def _setup_logging(self, log_level: str, log_file: Optional[str], 
                      structured: bool):
        """Configure logging with appropriate handlers and formatters"""
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Remove any existing handlers
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        if structured:
            # Structured JSON formatter
            class JSONFormatter(logging.Formatter):
                def format(self, record):
                    log_entry = {
                        'timestamp': datetime.fromtimestamp(record.created).isoformat(),
                        'level': record.levelname,
                        'logger': record.name,
                        'message': record.getMessage(),
                        'module': record.module,
                        'function': record.funcName,
                        'line': record.lineno
                    }
                    
                    # Add extra fields if present
                    if hasattr(record, '__dict__'):
                        for key, value in record.__dict__.items():
                            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 
                                         'pathname', 'filename', 'module', 'lineno',
                                         'funcName', 'created', 'msecs', 'relativeCreated',
                                         'thread', 'threadName', 'processName', 'process',
                                         'getMessage', 'message']:
                                log_entry[key] = value
                    
                    return json.dumps(log_entry)
            
            formatter = JSONFormatter()
        else:
            # Standard formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler if specified
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def _setup_default_thresholds(self):
        """Setup default alert thresholds for common metrics"""
        default_thresholds = [
            AlertThreshold("execution_error_rate", ">", 0.1, AlertSeverity.WARNING, 60),
            AlertThreshold("execution_error_rate", ">", 0.25, AlertSeverity.CRITICAL, 30),
            AlertThreshold("avg_execution_time", ">", 30.0, AlertSeverity.WARNING, 300),
            AlertThreshold("memory_usage_mb", ">", 1000, AlertSeverity.WARNING, 120),
            AlertThreshold("cpu_usage_percent", ">", 80, AlertSeverity.WARNING, 180),
            AlertThreshold("active_alerts", ">", 10, AlertSeverity.CRITICAL, 0)
        ]
        
        self.alert_thresholds.extend(default_thresholds)
    
    # Metric Collection Methods
    
    def record_metric(self, name: str, value: Union[int, float], 
                     metric_type: MetricType, tags: Optional[Dict[str, str]] = None,
                     description: Optional[str] = None):
        """Record a single metric value"""
        metric = Metric(
            name=name,
            type=metric_type,
            value=value,
            tags=tags or {},
            description=description
        )
        
        with self._metrics_lock:
            self.metrics.append(metric)
            
            # Update aggregated storage
            if metric_type == MetricType.COUNTER:
                self.counters[name] += value
            elif metric_type == MetricType.GAUGE:
                self.gauges[name] = value
            elif metric_type == MetricType.HISTOGRAM:
                self.histograms[name].append(value)
            elif metric_type == MetricType.TIMER:
                self.timers[name].append(value)
        
        # Check alert thresholds
        self._check_alert_thresholds(name, value)
        
        self.logger.debug(f"Recorded metric: {name}={value}", extra={
            'component': 'monitoring',
            'metric_name': name,
            'metric_type': metric_type.value,
            'metric_value': value,
            'tags': tags
        })
    
    def increment_counter(self, name: str, value: int = 1, 
                         tags: Optional[Dict[str, str]] = None):
        """Increment a counter metric"""
        self.record_metric(name, value, MetricType.COUNTER, tags)
    
    def set_gauge(self, name: str, value: Union[int, float], 
                  tags: Optional[Dict[str, str]] = None):
        """Set a gauge metric value"""
        self.record_metric(name, value, MetricType.GAUGE, tags)
    
    def record_histogram(self, name: str, value: Union[int, float], 
                        tags: Optional[Dict[str, str]] = None):
        """Record a histogram data point"""
        self.record_metric(name, value, MetricType.HISTOGRAM, tags)
    
    def record_timer(self, name: str, duration: float, 
                    tags: Optional[Dict[str, str]] = None):
        """Record a timer measurement in seconds"""
        self.record_metric(name, duration, MetricType.TIMER, tags)
    
    @contextmanager
    def time_operation(self, operation_name: str, 
                      tags: Optional[Dict[str, str]] = None):
        """Context manager for timing operations"""
        perf_metrics = PerformanceMetrics(
            operation_name=operation_name,
            start_time=datetime.now(),
            tags=tags or {}
        )
        
        try:
            yield perf_metrics
            perf_metrics.finish(success=True)
            self.record_timer(f"{operation_name}_duration", perf_metrics.duration, tags)
            self.increment_counter(f"{operation_name}_success", tags=tags)
        except Exception as e:
            perf_metrics.finish(success=False, error_message=str(e))
            self.record_timer(f"{operation_name}_duration", perf_metrics.duration, tags)
            self.increment_counter(f"{operation_name}_error", tags=tags)
            raise
        finally:
            with self._performance_lock:
                self.performance_data.append(perf_metrics)
    
    # Performance Tracking Methods
    
    def track_execution_performance(self, execution_result: ExecutionResult,
                                  operation_type: str = "execution"):
        """Track performance metrics from execution results"""
        tags = {
            'status': execution_result.status.value,
            'operation_type': operation_type
        }
        
        # Record timing metrics
        self.record_timer(f"{operation_type}_total_time", 
                         execution_result.total_execution_time, tags)
        
        # Record success/failure counters
        if execution_result.status == ExecutionStatus.SUCCESS:
            self.increment_counter(f"{operation_type}_success", tags=tags)
        else:
            self.increment_counter(f"{operation_type}_failure", tags=tags)
            if execution_result.error_message:
                self.increment_counter(f"{operation_type}_error", 
                                     tags={**tags, 'error_type': 'execution_error'})
        
        # Record step-level metrics
        for step_id, step_result in execution_result.step_results.items():
            step_tags = {**tags, 'step_id': step_id}
            if step_result.execution_time:
                self.record_timer(f"{operation_type}_step_time", 
                                step_result.execution_time, step_tags)
    
    def track_tool_usage(self, tool_name: str, success: bool, 
                        execution_time: float, error_type: Optional[str] = None):
        """Track individual tool usage metrics"""
        tags = {'tool_name': tool_name}
        
        # Usage counters
        self.increment_counter("tool_usage_total", tags=tags)
        if success:
            self.increment_counter("tool_usage_success", tags=tags)
        else:
            self.increment_counter("tool_usage_failure", tags=tags)
            if error_type:
                self.increment_counter("tool_errors", 
                                     tags={**tags, 'error_type': error_type})
        
        # Performance metrics
        self.record_timer("tool_execution_time", execution_time, tags)
        self.record_histogram("tool_duration_histogram", execution_time, tags)
    
    def track_discovery_performance(self, discovery_result: Dict[str, Any]):
        """Track tool discovery performance metrics"""
        tags = {'discovery_type': 'tool_discovery'}
        
        # Discovery metrics
        if 'tools_found' in discovery_result:
            self.set_gauge("tools_discovered", discovery_result['tools_found'], tags)
        if 'discovery_time' in discovery_result:
            self.record_timer("discovery_time", discovery_result['discovery_time'], tags)
        if 'cache_hits' in discovery_result:
            self.increment_counter("discovery_cache_hits", 
                                 discovery_result['cache_hits'], tags)
    
    # Health Monitoring Methods
    
    def update_component_health(self, component_name: str, health: ComponentHealth,
                              message: Optional[str] = None, 
                              metrics: Optional[Dict[str, float]] = None):
        """Update health status for a system component"""
        if component_name not in self.component_statuses:
            self.component_statuses[component_name] = ComponentStatus(
                component_name=component_name,
                health=ComponentHealth.UNKNOWN,
                last_check=datetime.now()
            )
        
        status = self.component_statuses[component_name]
        old_health = status.health
        status.update_health(health, message)
        
        if metrics:
            status.metrics.update(metrics)
        
        # Record health change metric
        if old_health != health:
            self.increment_counter("component_health_change", 
                                 tags={'component': component_name, 
                                      'old_health': old_health.value,
                                      'new_health': health.value})
            
            # Generate alert for health degradation
            if health in [ComponentHealth.DEGRADED, ComponentHealth.UNHEALTHY]:
                self.create_alert(
                    severity=AlertSeverity.WARNING if health == ComponentHealth.DEGRADED 
                            else AlertSeverity.CRITICAL,
                    component=component_name,
                    message=f"Component health changed from {old_health.value} to {health.value}",
                    metadata={'previous_health': old_health.value, 'message': message}
                )
        
        self.logger.info(f"Component health updated: {component_name} = {health.value}",
                        extra={'component': 'monitoring', 'component_name': component_name,
                              'health': health.value, 'health_message': message})
    
    def check_system_health(self) -> Dict[str, Any]:
        """Perform comprehensive system health check"""
        health_report = {
            'timestamp': datetime.now().isoformat(),
            'overall_health': ComponentHealth.HEALTHY.value,
            'components': {},
            'system_metrics': {},
            'alerts': {'active': 0, 'resolved': 0}
        }
        
        # Check component health
        unhealthy_components = 0
        degraded_components = 0
        
        for name, status in self.component_statuses.items():
            health_report['components'][name] = {
                'health': status.health.value,
                'last_check': status.last_check.isoformat(),
                'message': status.message,
                'metrics': status.metrics
            }
            
            if status.health == ComponentHealth.UNHEALTHY:
                unhealthy_components += 1
            elif status.health == ComponentHealth.DEGRADED:
                degraded_components += 1
        
        # Determine overall health
        if unhealthy_components > 0:
            health_report['overall_health'] = ComponentHealth.UNHEALTHY.value
        elif degraded_components > 0:
            health_report['overall_health'] = ComponentHealth.DEGRADED.value
        
        # System metrics
        try:
            process = psutil.Process()
            health_report['system_metrics'] = {
                'cpu_percent': process.cpu_percent(),
                'memory_mb': process.memory_info().rss / 1024 / 1024,
                'memory_percent': process.memory_percent(),
                'num_threads': process.num_threads(),
                'uptime_seconds': (datetime.now() - self.startup_time).total_seconds()
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            health_report['system_metrics'] = {'error': 'Unable to collect system metrics'}
        
        # Alert summary
        with self._alerts_lock:
            active_alerts = sum(1 for alert in self.alerts if not alert.resolved)
            resolved_alerts = sum(1 for alert in self.alerts if alert.resolved)
            health_report['alerts']['active'] = active_alerts
            health_report['alerts']['resolved'] = resolved_alerts
        
        return health_report
    
    # Alert System Methods
    
    def create_alert(self, severity: AlertSeverity, component: str, message: str,
                    metadata: Optional[Dict[str, Any]] = None) -> str:
        """Create a new system alert"""
        alert_id = f"alert_{int(time.time())}_{len(self.alerts)}"
        alert = Alert(
            id=alert_id,
            severity=severity,
            component=component,
            message=message,
            metadata=metadata or {}
        )
        
        with self._alerts_lock:
            self.alerts.append(alert)
        
        # Log the alert
        log_level = {
            AlertSeverity.INFO: logging.INFO,
            AlertSeverity.WARNING: logging.WARNING,
            AlertSeverity.CRITICAL: logging.ERROR,
            AlertSeverity.EMERGENCY: logging.CRITICAL
        }.get(severity, logging.WARNING)
        
        self.logger.log(log_level, f"Alert created: {message}", extra={
            'component': 'monitoring',
            'alert_id': alert_id,
            'severity': severity.value,
            'alert_component': component,
            'metadata': metadata
        })
        
        # Update alert counter
        self.increment_counter("alerts_created", 
                              tags={'severity': severity.value, 'component': component})
        
        return alert_id
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an existing alert"""
        with self._alerts_lock:
            for alert in self.alerts:
                if alert.id == alert_id and not alert.resolved:
                    alert.resolve()
                    self.logger.info(f"Alert resolved: {alert_id}", extra={
                        'component': 'monitoring',
                        'alert_id': alert_id
                    })
                    self.increment_counter("alerts_resolved", 
                                          tags={'severity': alert.severity.value})
                    return True
        return False
    
    def get_active_alerts(self, severity: Optional[AlertSeverity] = None) -> List[Alert]:
        """Get all active alerts, optionally filtered by severity"""
        with self._alerts_lock:
            alerts = [alert for alert in self.alerts if not alert.resolved]
            if severity:
                alerts = [alert for alert in alerts if alert.severity == severity]
            return alerts
    
    def _check_alert_thresholds(self, metric_name: str, value: float):
        """Check if any alert thresholds are breached by a metric"""
        for threshold in self.alert_thresholds:
            if threshold.metric_name == metric_name and threshold.check(value):
                self.create_alert(
                    severity=threshold.severity,
                    component="metrics",
                    message=f"Threshold breached: {metric_name} {threshold.operator} {threshold.value} (current: {value})",
                    metadata={
                        'metric_name': metric_name,
                        'threshold_value': threshold.value,
                        'current_value': value,
                        'operator': threshold.operator
                    }
                )
    
    def add_alert_threshold(self, threshold: AlertThreshold):
        """Add a custom alert threshold"""
        self.alert_thresholds.append(threshold)
        self.logger.info(f"Added alert threshold: {threshold.metric_name} {threshold.operator} {threshold.value}",
                        extra={'component': 'monitoring'})
    
    # Analytics and Reporting Methods
    
    def get_metric_summary(self, metric_name: str, 
                          time_window_minutes: Optional[int] = None) -> Dict[str, Any]:
        """Get statistical summary for a metric"""
        cutoff_time = None
        if time_window_minutes:
            cutoff_time = datetime.now() - timedelta(minutes=time_window_minutes)
        
        values = []
        with self._metrics_lock:
            for metric in self.metrics:
                if (metric.name == metric_name and 
                    (cutoff_time is None or metric.timestamp >= cutoff_time)):
                    values.append(metric.value)
        
        if not values:
            return {'error': f'No data found for metric: {metric_name}'}
        
        return {
            'metric_name': metric_name,
            'count': len(values),
            'min': min(values),
            'max': max(values),
            'mean': statistics.mean(values),
            'median': statistics.median(values),
            'std_dev': statistics.stdev(values) if len(values) > 1 else 0,
            'time_window_minutes': time_window_minutes
        }
    
    def get_performance_summary(self, operation_name: Optional[str] = None,
                               time_window_minutes: Optional[int] = None) -> Dict[str, Any]:
        """Get performance summary for operations"""
        cutoff_time = None
        if time_window_minutes:
            cutoff_time = datetime.now() - timedelta(minutes=time_window_minutes)
        
        with self._performance_lock:
            filtered_data = []
            for perf in self.performance_data:
                if (cutoff_time is None or perf.start_time >= cutoff_time):
                    if operation_name is None or perf.operation_name == operation_name:
                        filtered_data.append(perf)
        
        if not filtered_data:
            return {'error': 'No performance data found'}
        
        # Calculate statistics
        durations = [p.duration for p in filtered_data if p.duration is not None]
        success_count = sum(1 for p in filtered_data if p.success)
        
        summary = {
            'operation_name': operation_name or 'all',
            'total_operations': len(filtered_data),
            'successful_operations': success_count,
            'failed_operations': len(filtered_data) - success_count,
            'success_rate': success_count / len(filtered_data) if filtered_data else 0,
            'time_window_minutes': time_window_minutes
        }
        
        if durations:
            summary.update({
                'avg_duration': statistics.mean(durations),
                'min_duration': min(durations),
                'max_duration': max(durations),
                'median_duration': statistics.median(durations),
                'total_duration': sum(durations)
            })
        
        return summary
    
    def get_system_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data for real-time monitoring"""
        dashboard = {
            'timestamp': datetime.now().isoformat(),
            'uptime_seconds': (datetime.now() - self.startup_time).total_seconds(),
            'health': self.check_system_health(),
            'metrics_summary': {},
            'top_errors': [],
            'recent_alerts': [],
            'performance_overview': {}
        }
        
        # Key metrics summary
        key_metrics = ['execution_success', 'execution_failure', 'tool_usage_total',
                      'discovery_cache_hits', 'alerts_created']
        
        for metric in key_metrics:
            if metric in self.counters:
                dashboard['metrics_summary'][metric] = self.counters[metric]
        
        # Add gauge metrics
        for name, value in self.gauges.items():
            dashboard['metrics_summary'][name] = value
        
        # Recent alerts (last 10)
        with self._alerts_lock:
            recent_alerts = sorted(self.alerts, key=lambda x: x.timestamp, reverse=True)[:10]
            dashboard['recent_alerts'] = [
                {
                    'id': alert.id,
                    'severity': alert.severity.value,
                    'component': alert.component,
                    'message': alert.message,
                    'timestamp': alert.timestamp.isoformat(),
                    'resolved': alert.resolved
                }
                for alert in recent_alerts
            ]
        
        # Performance overview
        dashboard['performance_overview'] = self.get_performance_summary(time_window_minutes=60)
        
        return dashboard
    
    # Export and Persistence Methods
    
    def export_metrics(self, format: str = "json", 
                      file_path: Optional[str] = None,
                      time_window_minutes: Optional[int] = None) -> str:
        """Export metrics data to file or return as string"""
        cutoff_time = None
        if time_window_minutes:
            cutoff_time = datetime.now() - timedelta(minutes=time_window_minutes)
        
        # Collect metrics
        export_data = []
        with self._metrics_lock:
            for metric in self.metrics:
                if cutoff_time is None or metric.timestamp >= cutoff_time:
                    export_data.append(metric.to_dict())
        
        # Format data
        if format.lower() == "json":
            output = json.dumps(export_data, indent=2)
        elif format.lower() == "csv":
            if not export_data:
                output = "No data to export"
            else:
                import io
                output_io = io.StringIO()
                fieldnames = ['name', 'type', 'value', 'timestamp', 'description']
                writer = csv.DictWriter(output_io, fieldnames=fieldnames)
                writer.writeheader()
                
                for item in export_data:
                    row = {k: v for k, v in item.items() if k in fieldnames}
                    writer.writerow(row)
                
                output = output_io.getvalue()
        else:
            raise ValueError(f"Unsupported export format: {format}")
        
        # Write to file if specified
        if file_path:
            with open(file_path, 'w') as f:
                f.write(output)
            self.logger.info(f"Metrics exported to {file_path}", extra={'component': 'monitoring'})
        
        return output
    
    def export_performance_data(self, file_path: Optional[str] = None) -> str:
        """Export performance data as JSON"""
        with self._performance_lock:
            export_data = []
            for perf in self.performance_data:
                data = asdict(perf)
                # Convert datetime objects to ISO strings
                data['start_time'] = perf.start_time.isoformat()
                if perf.end_time:
                    data['end_time'] = perf.end_time.isoformat()
                export_data.append(data)
        
        output = json.dumps(export_data, indent=2)
        
        if file_path:
            with open(file_path, 'w') as f:
                f.write(output)
            self.logger.info(f"Performance data exported to {file_path}", extra={'component': 'monitoring'})
        
        return output
    
    def save_state(self, file_path: str):
        """Save complete monitoring state to file"""
        state = {
            'timestamp': datetime.now().isoformat(),
            'startup_time': self.startup_time.isoformat(),
            'counters': dict(self.counters),
            'gauges': self.gauges,
            'component_statuses': {
                name: {
                    'component_name': status.component_name,
                    'health': status.health.value,
                    'last_check': status.last_check.isoformat(),
                    'message': status.message,
                    'metrics': status.metrics,
                    'errors': status.errors
                }
                for name, status in self.component_statuses.items()
            },
            'alerts': [
                {
                    'id': alert.id,
                    'severity': alert.severity.value,
                    'component': alert.component,
                    'message': alert.message,
                    'timestamp': alert.timestamp.isoformat(),
                    'resolved': alert.resolved,
                    'resolved_at': alert.resolved_at.isoformat() if alert.resolved_at else None,
                    'metadata': alert.metadata
                }
                for alert in self.alerts
            ]
        }
        
        with open(file_path, 'w') as f:
            json.dump(state, f, indent=2)
        
        self.logger.info(f"Monitoring state saved to {file_path}", extra={'component': 'monitoring'})
    
    def cleanup_old_data(self):
        """Clean up old metrics and performance data based on retention policy"""
        cutoff_time = datetime.now() - timedelta(days=self.metrics_retention_days)
        
        # Clean metrics
        with self._metrics_lock:
            original_count = len(self.metrics)
            self.metrics = deque(
                (metric for metric in self.metrics if metric.timestamp >= cutoff_time),
                maxlen=self.max_metrics_history
            )
            cleaned_count = original_count - len(self.metrics)
        
        # Clean performance data
        with self._performance_lock:
            original_perf_count = len(self.performance_data)
            self.performance_data = [
                perf for perf in self.performance_data 
                if perf.start_time >= cutoff_time
            ]
            cleaned_perf_count = original_perf_count - len(self.performance_data)
        
        if cleaned_count > 0 or cleaned_perf_count > 0:
            self.logger.info(f"Cleaned up old data: {cleaned_count} metrics, {cleaned_perf_count} performance records",
                           extra={'component': 'monitoring'})

    # Integration Helper Methods
    
    def integrate_with_discovery(self, discovery: ToolDiscovery):
        """Integrate monitoring with tool discovery system"""
        original_discover = discovery.discover_tools
        
        def monitored_discover(*args, **kwargs):
            with self.time_operation("tool_discovery"):
                result = original_discover(*args, **kwargs)
                self.track_discovery_performance({
                    'tools_found': len(result),
                    'discovery_time': 0  # Will be set by time_operation
                })
                return result
        
        discovery.discover_tools = monitored_discover
        self.update_component_health("tool_discovery", ComponentHealth.HEALTHY,
                                   "Discovery monitoring integration active")
    
    def integrate_with_executor(self, executor: ChainExecutor):
        """Integrate monitoring with chain executor"""
        original_execute = executor.execute_plan
        
        async def monitored_execute(*args, **kwargs):
            with self.time_operation("chain_execution"):
                result = await original_execute(*args, **kwargs)
                self.track_execution_performance(result, "chain_execution")
                return result
        
        executor.execute_plan = monitored_execute
        self.update_component_health("chain_executor", ComponentHealth.HEALTHY,
                                   "Executor monitoring integration active")
    
    def integrate_with_error_recovery(self, error_recovery: ErrorRecoverySystem):
        """Integrate monitoring with error recovery system"""
        original_handle = error_recovery.handle_error
        
        async def monitored_handle(error_context, *args, **kwargs):
            # Track error occurrence
            self.increment_counter("errors_handled", tags={
                'category': error_context.category.value,
                'severity': error_context.severity.value
            })
            
            with self.time_operation("error_recovery"):
                result = await original_handle(error_context, *args, **kwargs)
                
                # Track recovery success/failure
                if result and result.get('recovered', False):
                    self.increment_counter("error_recovery_success", tags={
                        'category': error_context.category.value
                    })
                else:
                    self.increment_counter("error_recovery_failure", tags={
                        'category': error_context.category.value
                    })
                
                return result
        
        error_recovery.handle_error = monitored_handle
        self.update_component_health("error_recovery", ComponentHealth.HEALTHY,
                                   "Error recovery monitoring integration active")
    
    def integrate_with_fallback_manager(self, fallback_manager: FallbackManager):
        """Integrate monitoring with fallback management system"""
        original_execute = fallback_manager.execute_with_fallback
        
        async def monitored_execute(*args, **kwargs):
            with self.time_operation("fallback_execution"):
                result = await original_execute(*args, **kwargs)
                
                # Track fallback usage
                if hasattr(result, 'metadata') and result.metadata.get('used_fallback', False):
                    self.increment_counter("fallback_used", tags={
                        'fallback_type': result.metadata.get('fallback_type', 'unknown')
                    })
                
                return result
        
        fallback_manager.execute_with_fallback = monitored_execute
        self.update_component_health("fallback_manager", ComponentHealth.HEALTHY,
                                   "Fallback manager monitoring integration active")
    
    # Utility Methods
    
    def reset_metrics(self):
        """Reset all metrics and counters (useful for testing)"""
        with self._metrics_lock:
            self.metrics.clear()
            self.counters.clear()
            self.gauges.clear()
            self.histograms.clear()
            self.timers.clear()
        
        with self._performance_lock:
            self.performance_data.clear()
        
        with self._alerts_lock:
            self.alerts.clear()
        
        self.component_statuses.clear()
        self.logger.info("All metrics and data reset", extra={'component': 'monitoring'})
    
    def get_metrics_count(self) -> int:
        """Get total number of metrics stored"""
        with self._metrics_lock:
            return len(self.metrics)
    
    def get_active_alerts_count(self) -> int:
        """Get number of active alerts"""
        with self._alerts_lock:
            return sum(1 for alert in self.alerts if not alert.resolved)
    
    def __str__(self) -> str:
        """String representation of monitoring system status"""
        return (f"MonitoringSystem(metrics={self.get_metrics_count()}, "
                f"alerts={self.get_active_alerts_count()}, "
                f"components={len(self.component_statuses)}, "
                f"uptime={int((datetime.now() - self.startup_time).total_seconds())}s)")
    
    def __repr__(self) -> str:
        return self.__str__()


# Convenience Functions

def create_monitoring_system(log_level: str = "INFO", 
                           log_file: Optional[str] = None) -> MonitoringSystem:
    """Create a pre-configured monitoring system"""
    return MonitoringSystem(
        max_metrics_history=10000,
        max_alerts_history=1000,
        metrics_retention_days=30,
        log_level=log_level,
        log_file=log_file,
        enable_structured_logging=True
    )


def setup_comprehensive_monitoring(discovery: ToolDiscovery,
                                 executor: ChainExecutor,
                                 error_recovery: Optional[ErrorRecoverySystem] = None,
                                 fallback_manager: Optional[FallbackManager] = None,
                                 log_file: Optional[str] = None) -> MonitoringSystem:
    """
    Setup comprehensive monitoring with all component integrations.
    
    This is the recommended way to add monitoring to an existing
    Autonomous MCP Agent system.
    """
    monitoring = create_monitoring_system(log_file=log_file)
    
    # Integrate with core components
    monitoring.integrate_with_discovery(discovery)
    monitoring.integrate_with_executor(executor)
    
    # Integrate with optional resilience components
    if error_recovery:
        monitoring.integrate_with_error_recovery(error_recovery)
    
    if fallback_manager:
        monitoring.integrate_with_fallback_manager(fallback_manager)
    
    # Set initial health status
    monitoring.update_component_health("monitoring_system", ComponentHealth.HEALTHY,
                                     "Comprehensive monitoring initialized")
    
    return monitoring


# Export the main classes and functions
__all__ = [
    'MonitoringSystem',
    'Metric', 
    'PerformanceMetrics',
    'Alert',
    'ComponentStatus',
    'AlertThreshold',
    'MetricType',
    'AlertSeverity', 
    'ComponentHealth',
    'create_monitoring_system',
    'setup_comprehensive_monitoring'
]
