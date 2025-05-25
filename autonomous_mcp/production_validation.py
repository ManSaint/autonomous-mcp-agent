"""
Phase 7.4: Production Multi-Server Validation

This module implements comprehensive testing and validation for the complete
multi-server MCP ecosystem to ensure production readiness and reliability.
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import statistics

try:
    from .multi_server_discovery import get_client_manager, get_tool_registry
    from .multi_server_executor import get_multi_server_executor
    from .cross_server_orchestration import get_cross_server_workflow_builder, get_server_coordination_engine
except ImportError:
    # Fallback for standalone testing
    pass


@dataclass
class ValidationResult:
    """Result of a validation test"""
    test_name: str
    success: bool
    execution_time: float
    details: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    metrics: Dict[str, float] = field(default_factory=dict)


@dataclass
class ServerValidationResult:
    """Validation result for a specific server"""
    server_name: str
    connection_success: bool
    tool_discovery_success: bool
    tool_execution_success: bool
    tools_discovered: int
    tools_tested: int
    avg_response_time: float
    success_rate: float
    errors: List[str] = field(default_factory=list)


class ProductionValidator:
    """Comprehensive validation for production multi-server deployment"""
    
    def __init__(self):
        """Initialize production validator"""
        self.logger = logging.getLogger(__name__)
        self.client_manager = get_client_manager()
        self.tool_registry = get_tool_registry()
        self.executor = get_multi_server_executor()
        self.workflow_builder = get_cross_server_workflow_builder()
        self.coordinator = get_server_coordination_engine()
        
        # Validation configuration
        self.validation_config = {
            'target_server_count': 19,
            'target_tool_count_range': (70, 95),
            'target_success_rate': 0.95,
            'max_response_time': 5.0,
            'parallel_execution_count': 5,
            'stress_test_duration': 60.0
        }
        
        # Validation state
        self.validation_results = {}
        self.server_results = {}
        self.overall_metrics = {}
        
        self.logger.info("Production validator initialized")
    
    async def comprehensive_server_testing(self) -> Dict[str, Any]:
        """
        Test connectivity to all 19 servers and validate tool discovery
        
        Returns:
            Comprehensive server testing results
        """
        self.logger.info("Starting comprehensive server testing...")
        start_time = time.time()
        
        try:
            # Phase 1: Server Discovery
            discovery_result = await self.client_manager.discover_all_servers()
            
            self.logger.info(f"Discovered {discovery_result['total_servers']} servers")
            
            # Phase 2: Individual Server Validation
            server_validations = {}
            for server_name in discovery_result['servers']:
                validation = await self._validate_individual_server(server_name)
                server_validations[server_name] = validation
                self.server_results[server_name] = validation
            
            # Phase 3: Tool Registry Validation
            await self.tool_registry.build_from_servers(self.client_manager.servers)
            registry_summary = self.tool_registry.get_registry_summary()
            
            # Phase 4: Cross-Server Tool Execution
            execution_tests = await self._test_cross_server_tool_execution()
            
            # Calculate overall metrics
            total_time = time.time() - start_time
            connected_servers = sum(1 for v in server_validations.values() if v.connection_success)
            total_tools = sum(v.tools_discovered for v in server_validations.values())
            avg_success_rate = statistics.mean([v.success_rate for v in server_validations.values() if v.success_rate >= 0])
            
            # Compile results
            comprehensive_results = {
                'discovery_results': discovery_result,
                'server_validations': {name: {
                    'connection_success': val.connection_success,
                    'tools_discovered': val.tools_discovered,
                    'success_rate': val.success_rate,
                    'avg_response_time': val.avg_response_time,
                    'errors': val.errors
                } for name, val in server_validations.items()},
                'registry_summary': registry_summary,
                'execution_tests': execution_tests,
                'overall_metrics': {
                    'total_execution_time': total_time,
                    'servers_discovered': discovery_result['total_servers'],
                    'servers_connected': connected_servers,
                    'connection_rate': connected_servers / max(discovery_result['total_servers'], 1),
                    'total_tools_discovered': total_tools,
                    'avg_server_success_rate': avg_success_rate,
                    'meets_target_server_count': discovery_result['total_servers'] >= self.validation_config['target_server_count'],
                    'meets_target_tool_count': self.validation_config['target_tool_count_range'][0] <= total_tools <= self.validation_config['target_tool_count_range'][1],
                    'meets_success_rate_target': avg_success_rate >= self.validation_config['target_success_rate']
                }
            }
            
            self.overall_metrics.update(comprehensive_results['overall_metrics'])
            
            self.logger.info(f"Comprehensive server testing completed in {total_time:.2f}s")
            self.logger.info(f"Results: {connected_servers}/{discovery_result['total_servers']} servers connected, {total_tools} tools discovered")
            
            return comprehensive_results
            
        except Exception as e:
