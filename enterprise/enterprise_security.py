failures) > 5:
                scan_results["issues"].append({
                    "type": "high_failure_rate",
                    "severity": "medium",
                    "description": f"High failure rate detected: {len(recent_failures)} failures in last hour"
                })
                scan_results["security_score"] -= 10
            
            # Generate recommendations
            if scan_results["security_score"] < 90:
                scan_results["recommendations"].extend([
                    "Implement stricter access controls",
                    "Enable detailed audit logging",
                    "Set up automated security monitoring"
                ])
            
            return scan_results
            
        except Exception as e:
            self.logger.error(f"❌ Security scan failed for {server_name}: {str(e)}")
            return {
                "server_name": server_name,
                "scan_timestamp": datetime.now().isoformat(),
                "error": str(e)
            }

class MonitoringDashboard:
    """
    📊 Enterprise Monitoring Dashboard
    
    Real-time monitoring and alerting for the 15-server ecosystem
    with comprehensive health tracking and performance monitoring.
    """
    
    def __init__(self, security_manager: EnterpriseSecurityManager):
        self.logger = logging.getLogger(__name__)
        self.security_manager = security_manager
        
        # Monitoring state
        self.server_health: Dict[str, Dict[str, Any]] = {}
        self.tool_availability: Dict[str, Dict[str, bool]] = {}
        self.alerts: List[Dict[str, Any]] = []
        self.metrics_history: List[Dict[str, Any]] = []
        
        # Monitoring configuration
        self.health_check_interval = 60  # seconds
        self.alert_thresholds = {
            "response_time": 5.0,  # seconds
            "error_rate": 10.0,    # percentage
            "availability": 95.0   # percentage
        }
        
        # Background monitoring tasks
        self.monitoring_active = False
        
        self.logger.info("📊 Monitoring Dashboard initialized")
    
    async def start_monitoring(self):
        """Start background monitoring tasks"""
        self.monitoring_active = True
        
        # Start monitoring loops
        asyncio.create_task(self._server_health_monitor())
        asyncio.create_task(self._tool_availability_monitor())
        asyncio.create_task(self._performance_monitor())
        asyncio.create_task(self._alert_processor())
        
        self.logger.info("🚀 Enterprise monitoring started")
    
    async def stop_monitoring(self):
        """Stop background monitoring"""
        self.monitoring_active = False
        self.logger.info("🛑 Enterprise monitoring stopped")
    
    async def _server_health_monitor(self):
        """Monitor health of all 15 servers"""
        while self.monitoring_active:
            try:
                current_time = datetime.now()
                
                # Mock server health data (in production, implement real health checks)
                servers = [
                    "github", "postman", "trello", "youtube", "commander",
                    "memory", "browser", "magicui", "taskmaster", "toolagent",
                    "artifacts", "web_search", "movies", "mcp_tools", "autonomous"
                ]
                
                for server_name in servers:
                    health_data = await self._check_server_health(server_name)
                    self.server_health[server_name] = health_data
                    
                    # Generate alerts for unhealthy servers
                    if health_data["status"] != "healthy":
                        await self._create_alert(
                            alert_type="server_health",
                            message=f"Server {server_name} is {health_data['status']}",
                            severity="high" if health_data["status"] == "down" else "medium",
                            server_name=server_name
                        )
                
                await asyncio.sleep(self.health_check_interval)
                
            except Exception as e:
                self.logger.error(f"❌ Server health monitoring error: {str(e)}")
                await asyncio.sleep(30)
    
    async def _check_server_health(self, server_name: str) -> Dict[str, Any]:
        """Check health of individual server"""
        try:
            # Mock health check (implement real checks in production)
            import random
            
            # Simulate 95% uptime
            is_healthy = random.random() < 0.95
            response_time = random.uniform(0.1, 2.0) if is_healthy else random.uniform(5.0, 10.0)
            
            status = "healthy" if is_healthy and response_time < 3.0 else "degraded" if is_healthy else "down"
            
            return {
                "status": status,
                "response_time": response_time,
                "last_check": datetime.now().isoformat(),
                "uptime_percentage": 95.0 + random.uniform(-5, 5),
                "cpu_usage": random.uniform(10, 80),
                "memory_usage": random.uniform(20, 70),
                "connections": random.randint(1, 10)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "last_check": datetime.now().isoformat()
            }
    
    async def _tool_availability_monitor(self):
        """Monitor availability of all 202 tools"""
        while self.monitoring_active:
            try:
                # Mock tool availability monitoring
                servers_tools = {
                    "github": ["search_repositories", "create_repository", "get_file_contents"],
                    "postman": ["list_collections", "create_collection", "run_monitor"],
                    "trello": ["get_lists", "add_card_to_list", "update_card_details"],
                    "youtube": ["get_transcript"],
                    "commander": ["read_file", "write_file", "execute_command"]
                }
                
                for server_name, tools in servers_tools.items():
                    if server_name not in self.tool_availability:
                        self.tool_availability[server_name] = {}
                    
                    for tool_name in tools:
                        # Mock availability check
                        is_available = random.random() < 0.98  # 98% availability
                        self.tool_availability[server_name][tool_name] = is_available
                        
                        if not is_available:
                            await self._create_alert(
                                alert_type="tool_unavailable",
                                message=f"Tool {tool_name} on {server_name} is unavailable",
                                severity="medium",
                                server_name=server_name,
                                details={"tool_name": tool_name}
                            )
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                self.logger.error(f"❌ Tool availability monitoring error: {str(e)}")
                await asyncio.sleep(60)
    
    async def _performance_monitor(self):
        """Monitor overall system performance"""
        while self.monitoring_active:
            try:
                current_time = datetime.now()
                
                # Collect performance metrics
                metrics = {
                    "timestamp": current_time.isoformat(),
                    "total_servers": len(self.server_health),
                    "healthy_servers": len([s for s in self.server_health.values() 
                                          if s.get("status") == "healthy"]),
                    "average_response_time": self._calculate_average_response_time(),
                    "overall_availability": self._calculate_overall_availability(),
                    "active_alerts": len([a for a in self.alerts if a["status"] == "active"]),
                    "security_events": len(self.security_manager.security_events)
                }
                
                self.metrics_history.append(metrics)
                
                # Limit history size
                if len(self.metrics_history) > 1440:  # 24 hours of minute-by-minute data
                    self.metrics_history = self.metrics_history[-720:]  # Keep last 12 hours
                
                # Check performance thresholds
                if metrics["average_response_time"] > self.alert_thresholds["response_time"]:
                    await self._create_alert(
                        alert_type="performance",
                        message=f"High average response time: {metrics['average_response_time']:.2f}s",
                        severity="medium"
                    )
                
                if metrics["overall_availability"] < self.alert_thresholds["availability"]:
                    await self._create_alert(
                        alert_type="availability",
                        message=f"Low system availability: {metrics['overall_availability']:.1f}%",
                        severity="high"
                    )
                
                await asyncio.sleep(60)  # Collect metrics every minute
                
            except Exception as e:
                self.logger.error(f"❌ Performance monitoring error: {str(e)}")
                await asyncio.sleep(60)
    
    def _calculate_average_response_time(self) -> float:
        """Calculate average response time across all servers"""
        response_times = []
        for server_health in self.server_health.values():
            if "response_time" in server_health:
                response_times.append(server_health["response_time"])
        
        return sum(response_times) / len(response_times) if response_times else 0.0
    
    def _calculate_overall_availability(self) -> float:
        """Calculate overall system availability"""
        if not self.server_health:
            return 0.0
        
        healthy_count = len([s for s in self.server_health.values() 
                           if s.get("status") == "healthy"])
        
        return (healthy_count / len(self.server_health)) * 100
    
    async def _alert_processor(self):
        """Process and manage alerts"""
        while self.monitoring_active:
            try:
                current_time = datetime.now()
                
                # Auto-resolve old alerts
                for alert in self.alerts:
                    if alert["status"] == "active":
                        alert_time = datetime.fromisoformat(alert["timestamp"])
                        if current_time - alert_time > timedelta(hours=1):
                            alert["status"] = "auto_resolved"
                            alert["resolved_at"] = current_time.isoformat()
                
                await asyncio.sleep(300)  # Process alerts every 5 minutes
                
            except Exception as e:
                self.logger.error(f"❌ Alert processing error: {str(e)}")
                await asyncio.sleep(60)
    
    async def _create_alert(self, alert_type: str, message: str, severity: str,
                           server_name: str = None, details: Dict[str, Any] = None):
        """Create monitoring alert"""
        alert = {
            "id": secrets.token_urlsafe(16),
            "type": alert_type,
            "message": message,
            "severity": severity,
            "server_name": server_name,
            "timestamp": datetime.now().isoformat(),
            "status": "active",
            "details": details or {}
        }
        
        self.alerts.append(alert)
        
        # Log high-severity alerts
        if severity == "high":
            self.logger.error(f"🚨 HIGH ALERT: {message}")
        elif severity == "medium":
            self.logger.warning(f"⚠️ MEDIUM ALERT: {message}")
        else:
            self.logger.info(f"ℹ️ LOW ALERT: {message}")
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data"""
        current_time = datetime.now()
        
        # Recent metrics
        recent_metrics = [m for m in self.metrics_history 
                         if datetime.fromisoformat(m["timestamp"]) > current_time - timedelta(hours=1)]
        
        # Active alerts by severity
        active_alerts = [a for a in self.alerts if a["status"] == "active"]
        alerts_by_severity = {
            "high": len([a for a in active_alerts if a["severity"] == "high"]),
            "medium": len([a for a in active_alerts if a["severity"] == "medium"]),
            "low": len([a for a in active_alerts if a["severity"] == "low"])
        }
        
        return {
            "overview": {
                "total_servers": len(self.server_health),
                "healthy_servers": len([s for s in self.server_health.values() 
                                      if s.get("status") == "healthy"]),
                "total_tools": sum(len(tools) for tools in self.tool_availability.values()),
                "available_tools": sum(
                    sum(1 for available in tools.values() if available)
                    for tools in self.tool_availability.values()
                ),
                "overall_availability": self._calculate_overall_availability(),
                "average_response_time": self._calculate_average_response_time()
            },
            "server_health": self.server_health,
            "tool_availability": self.tool_availability,
            "alerts": {
                "active_count": len(active_alerts),
                "by_severity": alerts_by_severity,
                "recent": active_alerts[-10:]  # Last 10 alerts
            },
            "performance": {
                "recent_metrics": recent_metrics[-60:],  # Last hour
                "trends": self._calculate_performance_trends()
            },
            "security": self.security_manager.get_security_summary(),
            "last_updated": current_time.isoformat()
        }
    
    def _calculate_performance_trends(self) -> Dict[str, str]:
        """Calculate performance trends"""
        if len(self.metrics_history) < 2:
            return {"availability": "stable", "response_time": "stable"}
        
        recent = self.metrics_history[-10:]  # Last 10 data points
        older = self.metrics_history[-20:-10] if len(self.metrics_history) >= 20 else []
        
        trends = {}
        
        if older:
            # Availability trend
            recent_avg_avail = sum(m["overall_availability"] for m in recent) / len(recent)
            older_avg_avail = sum(m["overall_availability"] for m in older) / len(older)
            
            if recent_avg_avail > older_avg_avail + 1:
                trends["availability"] = "improving"
            elif recent_avg_avail < older_avg_avail - 1:
                trends["availability"] = "degrading"
            else:
                trends["availability"] = "stable"
            
            # Response time trend
            recent_avg_resp = sum(m["average_response_time"] for m in recent) / len(recent)
            older_avg_resp = sum(m["average_response_time"] for m in older) / len(older)
            
            if recent_avg_resp < older_avg_resp - 0.1:
                trends["response_time"] = "improving"
            elif recent_avg_resp > older_avg_resp + 0.1:
                trends["response_time"] = "degrading"
            else:
                trends["response_time"] = "stable"
        else:
            trends = {"availability": "stable", "response_time": "stable"}
        
        return trends
