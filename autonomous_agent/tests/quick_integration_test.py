#!/usr/bin/env python3
"""
Quick Integration Verification - Phase 2 with All Components

Verify that Phase 2 works flawlessly with all existing components.
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Add paths for imports
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / "autonomous_agent" / "core"))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_full_integration():
    """Test that all components work together"""
    logger.info("="*60)
    logger.info("FULL INTEGRATION TEST - Phase 2 with All Components")
    logger.info("="*60)
    
    test_results = {}
    failures = []
    
    # Test 1: Phase 1 Foundation
    try:
        logger.info("1️⃣ Testing Phase 1 Foundation...")
        from foundation_test import FoundationTest
        foundation_test = FoundationTest()
        foundation_result = await foundation_test.run_all_tests()
        
        if foundation_result['ready_for_phase_2']:
            logger.info("✅ Phase 1 Foundation: WORKING")
            test_results['phase1'] = 'PASS'
        else:
            logger.error("❌ Phase 1 Foundation: BROKEN")
            test_results['phase1'] = 'FAIL'
            failures.append("Phase 1 foundation broken")
            
    except Exception as e:
        logger.error(f"❌ Phase 1 Foundation: ERROR - {e}")
        test_results['phase1'] = 'ERROR'
        failures.append(f"Phase 1 error: {e}")
    
    # Test 2: MCP Server Components
    try:
        logger.info("2️⃣ Testing MCP Server Components...")
        from mcp.server.stdio import stdio_server
        from mcp.server import Server
        from mcp import types
        
        test_server = Server("integration-test")
        logger.info("✅ MCP Server Components: WORKING")
        test_results['mcp_server'] = 'PASS'
        
    except Exception as e:
        logger.error(f"❌ MCP Server Components: ERROR - {e}")
        test_results['mcp_server'] = 'ERROR'
        failures.append(f"MCP server error: {e}")
    
    # Test 3: Phase 2 Tool Integrator
    try:
        logger.info("3️⃣ Testing Phase 2 Tool Integrator...")
        from tool_integrator import ToolIntegrator
        
        integrator = ToolIntegrator()
        
        # Test basic functionality
        search_result = await integrator.execute_web_search("integration test")
        repl_result = await integrator.execute_repl("console.log('test')")
        artifacts_result = await integrator.execute_artifacts("create", "test")
        
        if (search_result.get('integration_status') == 'phase_2_ready' and
            repl_result.get('integration_status') == 'phase_2_ready' and
            artifacts_result.get('integration_status') == 'phase_2_ready'):
            logger.info("✅ Phase 2 Tool Integrator: WORKING")
            test_results['tool_integrator'] = 'PASS'
        else:
            logger.error("❌ Phase 2 Tool Integrator: INCORRECT RESULTS")
            test_results['tool_integrator'] = 'FAIL'
            failures.append("Tool integrator incorrect results")
            
    except Exception as e:
        logger.error(f"❌ Phase 2 Tool Integrator: ERROR - {e}")
        test_results['tool_integrator'] = 'ERROR'
        failures.append(f"Tool integrator error: {e}")
    
    # Results Summary
    logger.info("="*60)
    logger.info("INTEGRATION TEST RESULTS")
    logger.info("="*60)
    
    passing_tests = sum(1 for result in test_results.values() if result == 'PASS')
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status_emoji = "✅" if result == 'PASS' else "❌" 
        logger.info(f"{status_emoji} {test_name}: {result}")
    
    logger.info(f"\nTests Passed: {passing_tests}/{total_tests}")
    
    if failures:
        logger.error("\n🚨 INTEGRATION FAILURES:")
        for failure in failures:
            logger.error(f"  - {failure}")
        logger.error("\n❌ PHASE 2 INTEGRATION FAILED")
        logger.error("🛑 DO NOT PROCEED TO PHASE 3")
        return False
    else:
        logger.info("\n🎉 ALL INTEGRATION TESTS PASSED!")
        logger.info("✅ Phase 2 integrates flawlessly with all components")
        logger.info("🚀 READY TO PROCEED TO PHASE 3")
        return True


if __name__ == "__main__":
    success = asyncio.run(test_full_integration())
    exit(0 if success else 1)