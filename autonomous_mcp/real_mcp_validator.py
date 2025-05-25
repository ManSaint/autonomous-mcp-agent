"""
Real MCP Validator

This module validates real MCP protocol connections and ensures production
readiness of the MCP client implementation.
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import statistics

from .real_mcp_client import RealMCPClient
from .mcp_client_manager import RealMCPClientManager
from .mcp_protocol_validator import MCPProtocolValidator
from .universal_mcp_adapter import UniversalMCPAdapter


@dataclass
class ConnectionTestResult:
    """Result of testing a single server connection"""
    server_name: str
    success: bool
    connection_time: float
    tool_count: int
    error_message: Optional[str] = None
    tools_discovered: List[str] = field(default_factory=list)
    capabilities: Optional[Dict[str, Any]] = None


@dataclass
class PerformanceMetrics:
    """Performance metrics for MCP operations"""
    operation_type: str
    server_name: str
    duration: float
    success: bool
    timestamp: float = field(default_factory=time.time)


class RealMCPValidator:
    """
    Validate real MCP protocol connections
    
    Provides comprehensive testing and validation of real MCP client
    implementation, ensuring production readiness.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.client_manager = RealMCPClientManager(logger)
        self.protocol_validator = MCPProtocolValidator(logger)
        self.adapter = UniversalMCPAdapter(logger)
        self.performance_metrics: List[PerformanceMetrics] = []
        
    async def test_all_server_connections(self, server_configs: Dict[str, Dict[str, Any]]) -> Dict[str, ConnectionTestResult]:
        """
        Test real connections to all installed servers
        
        Args:
            server_configs: Dictionary of server configurations
            
        Returns:
            Dictionary mapping server names to test results
        """
        self.logger.info(f"🧪 Testing connections to {len(server_configs)} MCP servers...")
        
        results = {}
        await self.client_manager.start()
        
        try:
            # Test each server connection
            for server_name, config in server_configs.items():
                result = await self._test_single_server(server_name, config)
                results[server_name] = result
                
                if result.success:
                    self.logger.info(f"✅ {server_name}: Connected ({result.connection_time:.3f}s, {result.tool_count} tools)")
                else:
                    self.logger.error(f"❌ {server_name}: Failed - {result.error_message}")
        
        finally:
            await self.client_manager.stop()
        
        # Generate summary
        successful = sum(1 for r in results.values() if r.success)
        total = len(results)
        success_rate = (successful / total * 100) if total > 0 else 0
        
        self.logger.info(f"🎯 Connection test complete: {successful}/{total} servers ({success_rate:.1f}% success rate)")
        
        return results
    
    async def _test_single_server(self, server_name: str, config: Dict[str, Any]) -> ConnectionTestResult:
        """Test connection to a single server"""
        start_time = time.time()
        
        try:
            # Attempt connection
            connected = await self.client_manager.connect_to_server(server_name, config)
            
            if not connected:
                return ConnectionTestResult(
                    server_name=server_name,
                    success=False,
                    connection_time=time.time() - start_time,
                    tool_count=0,
                    error_message="Failed to establish connection"
                )
            
            # Discover tools
            tools = await self.client_manager.get_server_tools(server_name)
            tool_names = [tool.get("name", "unnamed") for tool in tools]
            
            # Get server status for additional info
            status = self.client_manager.get_server_status(server_name)
            
            connection_time = time.time() - start_time
            
            return ConnectionTestResult(
                server_name=server_name,
                success=True,
                connection_time=connection_time,
                tool_count=len(tools),
                tools_discovered=tool_names,
                capabilities=status
            )
            
        except Exception as e:
            return ConnectionTestResult(
                server_name=server_name,
                success=False,
                connection_time=time.time() - start_time,
                tool_count=0,
                error_message=str(e)
            )
    
    async def validate_real_tool_execution(self, server_configs: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Test actual tool calls via MCP protocol
        
        Args:
            server_configs: Dictionary of server configurations
            
        Returns:
            Validation results
        """
        self.logger.info("🧪 Testing real tool execution...")
        
        results = {
            "tested_tools": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "server_results": {},
            "performance_stats": {}
        }
        
        await self.client_manager.start()
        
        try:
            # Connect to servers and discover tools
            for server_name, config in server_configs.items():
                server_results = {
                    "connected": False,
                    "tools_tested": 0,
                    "successful_tools": 0,
                    "test_results": []
                }
                
                # Connect to server
                if await self.client_manager.connect_to_server(server_name, config):
                    server_results["connected"] = True
                    
                    # Get tools
                    tools = await self.client_manager.get_server_tools(server_name)
                    
                    # Test a sample of tools (safe ones only)
                    safe_tools = self._identify_safe_tools(tools)
                    
                    for tool in safe_tools[:3]:  # Test up to 3 safe tools per server
                        tool_result = await self._test_tool_execution(server_name, tool)
                        server_results["test_results"].append(tool_result)
                        server_results["tools_tested"] += 1
                        results["tested_tools"] += 1
                        
                        if tool_result["success"]:
                            server_results["successful_tools"] += 1
                            results["successful_calls"] += 1
                        else:
                            results["failed_calls"] += 1
                
                results["server_results"][server_name] = server_results
        
        finally:
            await self.client_manager.stop()
        
        # Calculate performance statistics
        if self.performance_metrics:
            durations = [m.duration for m in self.performance_metrics if m.success]
            if durations:
                results["performance_stats"] = {
                    "avg_duration": statistics.mean(durations),
                    "median_duration": statistics.median(durations),
                    "min_duration": min(durations),
                    "max_duration": max(durations),
                    "total_operations": len(self.performance_metrics)
                }
        
        success_rate = (results["successful_calls"] / results["tested_tools"] * 100) if results["tested_tools"] > 0 else 0
        self.logger.info(f"🎯 Tool execution test complete: {results['successful_calls']}/{results['tested_tools']} tools ({success_rate:.1f}% success rate)")
        
        return results
    
    def _identify_safe_tools(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify tools that are safe to test"""
        safe_tools = []
        
        for tool in tools:
            tool_name = tool.get("name", "").lower()
            description = tool.get("description", "").lower()
            
            # Identify read-only or safe operations
            safe_keywords = [
                "list", "get", "read", "search", "find", "query", "info",
                "status", "health", "version", "help", "describe"
            ]
            
            unsafe_keywords = [
                "delete", "remove", "create", "write", "update", "modify",
                "execute", "run", "install", "uninstall", "commit", "push"
            ]
            
            # Check if tool appears safe
            is_safe = any(keyword in tool_name or keyword in description for keyword in safe_keywords)
            is_unsafe = any(keyword in tool_name or keyword in description for keyword in unsafe_keywords)
            
            if is_safe and not is_unsafe:
                safe_tools.append(tool)
        
        return safe_tools
    
    async def _test_tool_execution(self, server_name: str, tool: Dict[str, Any]) -> Dict[str, Any]:
        """Test execution of a single tool"""
        tool_name = tool.get("name", "unknown")
        
        start_time = time.time()
        result = {
            "tool_name": tool_name,
            "success": False,
            "duration": 0.0,
            "error_message": None,
            "result_type": None
        }
        
        try:
            # Prepare minimal test arguments
            test_args = self._generate_test_arguments(tool)
            
            # Execute tool
            execution_result = await self.client_manager.execute_tool(server_name, tool_name, test_args)
            
            duration = time.time() - start_time
            result["duration"] = duration
            
            # Record performance metric
            self.performance_metrics.append(
                PerformanceMetrics("tool_call", server_name, duration, execution_result is not None)
            )
            
            if execution_result:
                result["success"] = True
                result["result_type"] = type(execution_result).__name__
            else:
                result["error_message"] = "Tool returned no result"
        
        except Exception as e:
            result["duration"] = time.time() - start_time
            result["error_message"] = str(e)
            
            # Record failed performance metric
            self.performance_metrics.append(
                PerformanceMetrics("tool_call", server_name, result["duration"], False)
            )
        
        return result
    
    def _generate_test_arguments(self, tool: Dict[str, Any]) -> Dict[str, Any]:
        """Generate safe test arguments for a tool"""
        args = {}
        
        input_schema = tool.get("inputSchema", {})
        properties = input_schema.get("properties", {})
        
        for prop_name, prop_schema in properties.items():
            prop_type = prop_schema.get("type", "string")
            
            # Generate safe default values
            if prop_type == "string":
                # Use safe string values
                if "path" in prop_name.lower():
                    args[prop_name] = "."  # Current directory
                elif "query" in prop_name.lower():
                    args[prop_name] = "test"
                else:
                    args[prop_name] = "test"
            elif prop_type == "integer":
                args[prop_name] = 1
            elif prop_type == "number":
                args[prop_name] = 1.0
            elif prop_type == "boolean":
                args[prop_name] = False
            elif prop_type == "array":
                args[prop_name] = []
            elif prop_type == "object":
                args[prop_name] = {}
        
        return args
    
    async def benchmark_real_performance(self, server_configs: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Performance testing of real MCP calls
        
        Args:
            server_configs: Dictionary of server configurations
            
        Returns:
            Performance benchmark results
        """
        self.logger.info("🚀 Benchmarking real MCP performance...")
        
        benchmark_results = {
            "connection_times": {},
            "tool_discovery_times": {},
            "tool_execution_times": {},
            "overall_stats": {}
        }
        
        await self.client_manager.start()
        
        try:
            for server_name, config in server_configs.items():
                server_benchmark = {
                    "connection_time": 0.0,
                    "discovery_time": 0.0,
                    "execution_times": [],
                    "total_time": 0.0
                }
                
                overall_start = time.time()
                
                # Benchmark connection
                conn_start = time.time()
                connected = await self.client_manager.connect_to_server(server_name, config)
                server_benchmark["connection_time"] = time.time() - conn_start
                
                if connected:
                    # Benchmark tool discovery
                    disc_start = time.time()
                    tools = await self.client_manager.get_server_tools(server_name)
                    server_benchmark["discovery_time"] = time.time() - disc_start
                    
                    # Benchmark tool execution (safe tools only)
                    safe_tools = self._identify_safe_tools(tools)
                    for tool in safe_tools[:2]:  # Test 2 tools for performance
                        exec_start = time.time()
                        try:
                            test_args = self._generate_test_arguments(tool)
                            await self.client_manager.execute_tool(server_name, tool.get("name"), test_args)
                            exec_time = time.time() - exec_start
                            server_benchmark["execution_times"].append(exec_time)
                        except Exception:
                            pass  # Skip failed executions in benchmarking
                
                server_benchmark["total_time"] = time.time() - overall_start
                
                benchmark_results["connection_times"][server_name] = server_benchmark["connection_time"]
                benchmark_results["tool_discovery_times"][server_name] = server_benchmark["discovery_time"]
                benchmark_results["tool_execution_times"][server_name] = server_benchmark["execution_times"]
        
        finally:
            await self.client_manager.stop()
        
        # Calculate overall statistics
        all_conn_times = list(benchmark_results["connection_times"].values())
        all_disc_times = list(benchmark_results["tool_discovery_times"].values())
        all_exec_times = []
        for exec_list in benchmark_results["tool_execution_times"].values():
            all_exec_times.extend(exec_list)
        
        if all_conn_times:
            benchmark_results["overall_stats"]["avg_connection_time"] = statistics.mean(all_conn_times)
            benchmark_results["overall_stats"]["max_connection_time"] = max(all_conn_times)
        
        if all_disc_times:
            benchmark_results["overall_stats"]["avg_discovery_time"] = statistics.mean(all_disc_times)
            
        if all_exec_times:
            benchmark_results["overall_stats"]["avg_execution_time"] = statistics.mean(all_exec_times)
            benchmark_results["overall_stats"]["median_execution_time"] = statistics.median(all_exec_times)
        
        self.logger.info("🎯 Performance benchmarking complete")
        return benchmark_results
    
    def generate_validation_report(self, 
                                 connection_results: Dict[str, ConnectionTestResult],
                                 execution_results: Dict[str, Any],
                                 performance_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive validation report"""
        
        # Connection statistics
        total_servers = len(connection_results)
        connected_servers = sum(1 for r in connection_results.values() if r.success)
        connection_rate = (connected_servers / total_servers * 100) if total_servers > 0 else 0
        
        total_tools = sum(r.tool_count for r in connection_results.values())
        
        # Execution statistics
        exec_stats = execution_results
        
        # Performance statistics
        perf_stats = performance_results.get("overall_stats", {})
        
        report = {
            "validation_timestamp": datetime.now().isoformat(),
            "summary": {
                "total_servers_tested": total_servers,
                "successful_connections": connected_servers,
                "connection_success_rate": f"{connection_rate:.1f}%",
                "total_tools_discovered": total_tools,
                "tools_tested": exec_stats.get("tested_tools", 0),
                "tool_execution_success_rate": f"{(exec_stats.get('successful_calls', 0) / max(exec_stats.get('tested_tools', 1), 1) * 100):.1f}%"
            },
            "connection_details": {
                name: {
                    "success": result.success,
                    "connection_time": f"{result.connection_time:.3f}s",
                    "tool_count": result.tool_count,
                    "error": result.error_message
                }
                for name, result in connection_results.items()
            },
            "performance_metrics": perf_stats,
            "validation_status": "PASS" if connection_rate >= 90 else "FAIL",
            "recommendations": self._generate_recommendations(connection_results, exec_stats, perf_stats)
        }
        
        return report
    
    def _generate_recommendations(self, conn_results, exec_results, perf_results) -> List[str]:
        """Generate recommendations based on validation results"""
        recommendations = []
        
        connection_rate = sum(1 for r in conn_results.values() if r.success) / len(conn_results) * 100
        
        if connection_rate < 90:
            recommendations.append("Connection rate below 90% - investigate failed server connections")
        
        avg_conn_time = perf_results.get("avg_connection_time", 0)
        if avg_conn_time > 5.0:
            recommendations.append("Average connection time exceeds 5 seconds - optimize connection process")
        
        avg_exec_time = perf_results.get("avg_execution_time", 0)
        if avg_exec_time > 3.0:
            recommendations.append("Average tool execution time exceeds 3 seconds - consider performance optimization")
        
        failed_tools = exec_results.get("failed_calls", 0)
        total_tools = exec_results.get("tested_tools", 1)
        if failed_tools / total_tools > 0.1:
            recommendations.append("Tool execution failure rate above 10% - review tool compatibility")
        
        if not recommendations:
            recommendations.append("All validation criteria met - system ready for production")
        
        return recommendations
