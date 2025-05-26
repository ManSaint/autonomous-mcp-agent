#!/usr/bin/env python3
"""
Phase 2 Full Integration Test - COMPREHENSIVE VERIFICATION

This test verifies that Phase 2 integrates flawlessly with ALL existing components:
- Phase 1 foundation (MCP server, tools, foundation test)
- Phase 2 tool integration (web_search, repl, artifacts)
- All imports work correctly
- No regressions from previous phases
- Everything works together seamlessly

This is MANDATORY before claiming Phase 2 complete.
"""

import asyncio
import logging
import sys
import importlib
import traceback
from datetime import datetime
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class FullIntegrationTest:
    """
    Comprehensive integration test for Phase 2 with all existing components
    """
    
    def __init__(self):
        """Initialize full integration test"""
        self.test_results = {}
        self.failures = []
        self.start_time = datetime.now()
        logger.info("Full integration test initialized - verifying Phase 2 with all components")
    
    async def test_phase1_foundation_still_works(self) -> bool:
        """Test that Phase 1 foundation components still work after Phase 2"""
        try:
            logger.info("🔍 Testing Phase 1 foundation integration...")
            
            # Test foundation test still works
            sys.path.append(str(Path(__file__).parent.parent / "core"))
            foundation_test = importlib.import_module("foundation_test")
            
            # Run foundation test
            foundation_result = await foundation_test.main()
            
            if foundation_result.get('ready_for_phase_2'):
                logger.info("✅ Phase 1 foundation still working correctly")
                self.test_results['phase1_foundation'] = {'status': 'working', 'details': foundation_result}
                return True
            else:
                logger.error("❌ Phase 1 foundation broken after Phase 2 changes")
                self.failures.append("Phase 1 foundation no longer working")
                return False
                
        except Exception as e:
            logger.error(f"❌ Phase 1 foundation test failed: {e}")
            self.failures.append(f"Phase 1 foundation error: {str(e)}")
            self.test_results['phase1_foundation'] = {'status': 'failed', 'error': str(e)}
            return False
    
    async def test_mcp_server_imports(self) -> bool:
        """Test that MCP server components still import correctly"""
        try:
            logger.info("🔍 Testing MCP server imports...")
            
            # Test MCP imports that Phase 1 verified
            from mcp.server.stdio import stdio_server
            from mcp.server import Server
            from mcp import types
            
            # Test server creation
            test_server = Server("integration-test-server")
            
            logger.info("✅ MCP server imports working correctly")
            self.test_results['mcp_imports'] = {'status': 'working'}
            return True
            
        except Exception as e:
            logger.error(f"❌ MCP server imports failed: {e}")
            self.failures.append(f"MCP imports broken: {str(e)}")
            self.test_results['mcp_imports'] = {'status': 'failed', 'error': str(e)}
            return False
    
    async def test_phase2_tool_integrator(self) -> bool:
        """Test that Phase 2 tool integrator works correctly"""
        try:
            logger.info("🔍 Testing Phase 2 tool integrator...")
            
            # Import and test tool integrator
            tool_integrator_module = importlib.import_module("tool_integrator")
            tool_integrator = tool_integrator_module.tool_integrator
            
            # Test each tool integration
            search_result = await tool_integrator.execute_web_search("test integration query")
            repl_result = await tool_integrator.execute_repl("console.log('integration test')")
            artifacts_result = await tool_integrator.execute_artifacts("create", "test content")
            
            # Verify results structure
            if (search_result.get('integration_status') == 'phase_2_ready' and
                repl_result.get('integration_status') == 'phase_2_ready' and
                artifacts_result.get('integration_status') == 'phase_2_ready'):
                
                logger.info("✅ Phase 2 tool integrator working correctly")
                self.test_results['tool_integrator'] = {
                    'status': 'working',
                    'search': search_result,
                    'repl': repl_result, 
                    'artifacts': artifacts_result
                }
                return True
            else:
                logger.error("❌ Phase 2 tool integrator not returning expected results")
                self.failures.append("Tool integrator results incorrect")
                return False
                
        except Exception as e:
            logger.error(f"❌ Phase 2 tool integrator failed: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            self.failures.append(f"Tool integrator error: {str(e)}")
            self.test_results['tool_integrator'] = {'status': 'failed', 'error': str(e)}
            return False