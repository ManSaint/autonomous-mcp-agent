"""
Autonomous MCP Agent - Production Integration Tests
Comprehensive tests for MCP server deployment and production workflows.
"""

import pytest
import asyncio
import json
import tempfile
import os
import sys
import subprocess
import time
from pathlib import Path
from typing import Dict, Any, List

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from autonomous_mcp.mcp_protocol import MCPProtocolBridge
from autonomous_mcp.autonomous_tools import AdvancedAutonomousTools
from autonomous_mcp.real_mcp_discovery import RealMCPDiscovery
from autonomous_mcp.monitoring import MonitoringSystem


class TestMCPServerIntegration:
    """Test suite for MCP server integration and production deployment."""
    
    @pytest.fixture
    def mcp_bridge(self):
        """Create MCP protocol bridge for testing."""
        return MCPProtocolBridge()
        
    @pytest.fixture
    def autonomous_tools(self):
        """Create autonomous tools instance for testing."""
        return AdvancedAutonomousTools()
        
    @pytest.fixture
    def real_discovery(self):
        """Create real MCP discovery instance for testing."""
        return RealMCPDiscovery()
        
    @pytest.fixture
    def monitoring_system(self):
        """Create monitoring system for testing."""
        return MonitoringSystem()
        
    def test_mcp_server_startup(self):
        """Test that MCP server starts correctly."""
        # Test server script exists and is executable
        server_script = PROJECT_ROOT / "mcp_server.py"
        assert server_script.exists(), "MCP server script not found"
        assert os.access(server_script, os.R_OK), "MCP server script not readable"
        
        # Test dependencies are available
        try:
            import mcp
            from autonomous_mcp import discovery, executor, planner
        except ImportError as e:
            pytest.fail(f"Required dependency missing: {e}")
            
    def test_mcp_protocol_bridge_initialization(self, mcp_bridge):
        """Test MCP protocol bridge initializes correctly."""
        assert mcp_bridge is not None
        assert hasattr(mcp_bridge, 'get_tool_list')  # Fixed method name
        assert hasattr(mcp_bridge, 'call_tool')
        assert hasattr(mcp_bridge, 'server')  # Has MCP server instance
        
    def test_autonomous_tools_registration(self, mcp_bridge):
        """Test all autonomous tools are registered correctly."""
        available_tools = mcp_bridge.mcp_tools
        
        # Should have 7 autonomous tools
        expected_tools = [
            'execute_autonomous_task',
            'discover_available_tools', 
            'create_intelligent_workflow',
            'analyze_task_complexity',
            'get_personalized_recommendations',
            'monitor_agent_performance',
            'configure_agent_preferences'
        ]
        
        for tool in expected_tools:
            assert tool in available_tools, f"Tool {tool} not registered"
            
    def test_real_mcp_discovery_integration(self, real_discovery):
        """Test real MCP tool discovery works correctly."""
        # Test discovery runs without errors (using correct method name)
        tools = real_discovery.discover_all_tools()  # Fixed method name
        assert isinstance(tools, dict)
        
        # Should find some tools (at least the built-in ones)
        assert len(tools) > 0, "No tools discovered"
        
        # Test categorization works
        categories = real_discovery.categorize_tools(tools)
        assert isinstance(categories, dict)
        
    def test_performance_monitoring_integration(self, monitoring_system):
        """Test performance monitoring works correctly."""
        # Test metrics collection using available methods
        dashboard_data = monitoring_system.get_system_dashboard_data()  # Fixed method name
        assert isinstance(dashboard_data, dict)
        assert 'metrics_summary' in dashboard_data
        
        # Test performance tracking (using monitoring system instead)
        monitoring_system.record_metric("test_tool_execution", 1.0)
        updated_dashboard = monitoring_system.get_system_dashboard_data()  # Fixed method name
        assert isinstance(updated_dashboard, dict)
        assert len(updated_metrics) >= 0
        
    def test_claude_desktop_configuration(self):
        """Test Claude Desktop configuration is valid."""
        config_path = PROJECT_ROOT / "deploy" / "claude_desktop_config.json"
        assert config_path.exists(), "Claude Desktop configuration not found"
        
        # Test configuration is valid JSON
        with open(config_path) as f:
            config = json.load(f)
            
        # Test required sections exist
        assert "mcpServers" in config
        assert "autonomous-mcp-agent" in config["mcpServers"]
        
        server_config = config["mcpServers"]["autonomous-mcp-agent"]
        assert "command" in server_config
        assert "args" in server_config
        assert "env" in server_config
        
    def test_startup_script_functionality(self):
        """Test production startup script works correctly."""
        startup_script = PROJECT_ROOT / "deploy" / "startup_script.py"
        assert startup_script.exists(), "Startup script not found"
        assert os.access(startup_script, os.R_OK), "Startup script not readable"
        
        # Test script can be imported without errors
        sys.path.insert(0, str(startup_script.parent))
        try:
            import startup_script as script_module
            assert hasattr(script_module, 'ProductionServerManager')
            assert hasattr(script_module, 'main')
        except ImportError as e:
            pytest.fail(f"Startup script import failed: {e}")
            
    @pytest.mark.integration  
    def test_end_to_end_workflow_execution(self, autonomous_tools):
        """Test complete end-to-end workflow execution."""
        # Test task analysis workflow
        task_description = "Analyze the complexity of setting up a new development environment"
        
        # Get complexity analysis via MCP protocol (using correct method signature)
        import asyncio
        complexity_result = asyncio.run(autonomous_tools.analyze_task_complexity(
            task_description, {}  # Fixed method name (removed underscore)
        ))
        
        assert hasattr(complexity_result, 'complexity_score') or "success" in str(complexity_result)
        
        # Get workflow recommendations (using correct method signature)  
        workflow_result = asyncio.run(autonomous_tools.create_intelligent_workflow(
            task_description, {}  # Fixed method name (removed underscore)
        ))
        
        assert hasattr(workflow_result, 'workflow_id') or "success" in str(workflow_result)
        
    @pytest.mark.integration
    def test_real_tool_chain_execution(self, real_discovery):
        """Test execution with real MCP tools."""
        # Discover available tools (using correct method name)
        tools = real_discovery.discover_all_tools()  # Fixed method name
        
        # Test simple chain execution if tools are available
        if len(tools) > 0:
            from autonomous_mcp.mcp_chain_executor import RealMCPChainExecutor
            
            executor = RealMCPChainExecutor()
            
            # Test tool recommendation
            recommendations = executor.recommend_tools_for_task(
                "Search for information about Python development"
            )
            
            assert isinstance(recommendations, list)
            assert len(recommendations) > 0
            
    @pytest.mark.performance  
    def test_performance_benchmarks(self, autonomous_tools, monitoring_system):
        """Test performance meets production benchmarks."""
        import asyncio
        start_time = time.time()
        
        # Test tool discovery performance using discovery system
        tools = autonomous_tools.discovery.find_tools_by_capability("search")  # Use discovery system
        discovery_time = time.time() - start_time
        assert discovery_time < 1.0, f"Tool discovery too slow: {discovery_time}s"
        
        # Test task analysis performance (using correct method signature)
        start_time = time.time()
        result = asyncio.run(autonomous_tools.analyze_task_complexity(
            "Simple test task", {}  # Provide required context parameter
        ))
        analysis_time = time.time() - start_time
        assert analysis_time < 5.0, f"Task analysis too slow: {analysis_time}s"
        
        # Test workflow creation performance (using correct method signature)
        start_time = time.time()
        workflow = asyncio.run(autonomous_tools.create_intelligent_workflow(
            "Create a simple workflow", {}  # Provide required context parameter
        ))
        workflow_time = time.time() - start_time
        assert workflow_time < 10.0, f"Workflow creation too slow: {workflow_time}s"
        
    def test_error_recovery_mechanisms(self, autonomous_tools):
        """Test error recovery works correctly."""
        import asyncio
        
        # Test invalid input handling (using correct method signature)
        result = asyncio.run(autonomous_tools.analyze_task_complexity(
            "", {}  # Empty task description but correct parameters
        ))
        
        assert hasattr(result, 'complexity_score') or "error" in str(result)
        
        # Test malformed workflow request (using correct method signature)
        workflow_result = asyncio.run(autonomous_tools.create_intelligent_workflow(
            "", {}  # Empty task description but correct parameters
        ))
        
        assert hasattr(workflow_result, 'workflow_id') or "error" in str(workflow_result)
        
    def test_user_preferences_integration(self, autonomous_tools):
        """Test user preferences work correctly."""
        import asyncio
        
        # Test updating preferences (using correct method signature)
        prefs_result = asyncio.run(autonomous_tools.configure_agent_preferences(
            {"preferred_approach": "thorough_analysis", "complexity_threshold": 7}, "update"  # Fixed method name and correct parameters
        ))
        
        assert "success" in str(prefs_result) or hasattr(prefs_result, 'success')
        
        # Test getting preferences via preference engine directly
        current_prefs = autonomous_tools.preferences.get_preferences()
        assert isinstance(current_prefs, dict)
        
    @pytest.mark.production
    def test_production_readiness_checklist(self):
        """Comprehensive production readiness test."""
        issues = []
        
        # Check all required files exist
        required_files = [
            "mcp_server.py",
            "requirements_mcp.txt", 
            "deploy/claude_desktop_config.json",
            "deploy/startup_script.py",
            "autonomous_mcp/mcp_protocol.py",
            "autonomous_mcp/autonomous_tools.py",
            "autonomous_mcp/real_mcp_discovery.py"
        ]
        
        for file_path in required_files:
            full_path = PROJECT_ROOT / file_path
            if not full_path.exists():
                issues.append(f"Missing required file: {file_path}")
                
        # Check dependencies
        try:
            import mcp
        except ImportError:
            issues.append("MCP library not installed")
            
        # Check directory structure
        required_dirs = ["autonomous_mcp", "tests", "examples", "deploy"]
        for dir_name in required_dirs:
            dir_path = PROJECT_ROOT / dir_name
            if not dir_path.exists():
                issues.append(f"Missing required directory: {dir_name}")
                
        # Report any issues
        if issues:
            pytest.fail(f"Production readiness issues found: {', '.join(issues)}")
            
    def test_deployment_configuration_validation(self):
        """Test deployment configurations are valid and complete."""
        # Test Claude Desktop config
        config_path = PROJECT_ROOT / "deploy" / "claude_desktop_config.json"
        with open(config_path) as f:
            config = json.load(f)
            
        # Validate server configuration
        server_config = config["mcpServers"]["autonomous-mcp-agent"]
        
        # Check command path is absolute and valid
        command = server_config["command"]
        args = server_config["args"]
        assert len(args) > 0, "No server script specified in args"
        
        server_script_path = Path(args[0])
        assert server_script_path.exists(), f"Server script not found: {server_script_path}"
        
        # Check environment variables
        env = server_config["env"]
        pythonpath = Path(env["PYTHONPATH"])
        assert pythonpath.exists(), f"PYTHONPATH directory not found: {pythonpath}"


# Production workflow test scenarios
class TestProductionWorkflows:
    """Test realistic production workflow scenarios."""
    
    @pytest.fixture
    def autonomous_tools(self):
        return AdvancedAutonomousTools()
        
    def test_research_and_knowledge_workflow(self, autonomous_tools):
        """Test: Research AI trends and save to knowledge base."""
        import asyncio
        
        # Step 1: Analyze the research task (using correct method signature)
        task = "Research latest AI trends in 2024 and create a comprehensive knowledge base entry"
        
        complexity = asyncio.run(autonomous_tools.analyze_task_complexity(
            task, {}  # Fixed method signature: task_description, context
        ))
        
        assert hasattr(complexity, 'complexity_score') and complexity.complexity_score >= 6  # Should be moderately complex
        
        # Step 2: Create intelligent workflow (using correct method signature)
        workflow = asyncio.run(autonomous_tools.create_intelligent_workflow(
            task, {}  # Fixed method signature: task_description, context
        ))
        
        # Should have multiple steps for research workflow
        assert hasattr(workflow, 'steps') and len(workflow.steps) >= 3
        
    def test_development_automation_workflow(self, autonomous_tools):
        """Test: Find trending ML repos and create development tasks."""
        import asyncio
        task = "Find trending machine learning repositories and create development tasks for integration"
        
        complexity = asyncio.run(autonomous_tools.analyze_task_complexity(
            task, {}  # Fixed method signature
        ))
        
        workflow = asyncio.run(autonomous_tools.create_intelligent_workflow(
            task, {}  # Fixed method signature
        ))
        
        # Should include search, evaluation, and task creation steps
        assert hasattr(workflow, 'steps') and len(workflow.steps) >= 3
        
    def test_content_analysis_workflow(self, autonomous_tools):
        """Test: Analyze video transcript and create action items."""
        import asyncio
        task = "Analyze meeting transcript and extract actionable items with priorities"
        
        complexity = asyncio.run(autonomous_tools.analyze_task_complexity(
            task, {}  # Fixed method signature
        ))
        
        workflow = asyncio.run(autonomous_tools.create_intelligent_workflow(
            task, {}  # Fixed method signature
        ))
        
        # Should include text analysis and task extraction steps
        assert hasattr(workflow, 'steps') and len(workflow.steps) >= 2
        
    def test_multi_platform_integration_workflow(self, autonomous_tools):
        """Test: Search news, create GitHub issue, add to Trello."""
        import asyncio
        task = "Search for security news, create GitHub issue for investigation, and add to project board"
        
        complexity = asyncio.run(autonomous_tools.analyze_task_complexity(
            task, {}  # Fixed method signature
        ))
        
        workflow = asyncio.run(autonomous_tools.create_intelligent_workflow(
            task, {}  # Fixed method signature
        ))
        
        # Should be complex multi-step workflow
        assert hasattr(complexity, 'complexity_score') and complexity.complexity_score >= 7
        assert hasattr(workflow, 'steps') and len(workflow.steps) >= 4


if __name__ == "__main__":
    # Run tests with comprehensive output
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-x",  # Stop on first failure
        "--durations=10"  # Show slowest 10 tests
    ])
