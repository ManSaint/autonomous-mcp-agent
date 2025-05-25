"""
Phase 8.4: Production MCP Validation Test

This test validates the complete real MCP protocol implementation
and ensures 100% connectivity and production readiness.
"""

import asyncio
import json
import logging
import time
from pathlib import Path
import sys
import os

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from autonomous_mcp.real_mcp_validator import RealMCPValidator
from autonomous_mcp.mcp_client_manager import RealMCPClientManager
from autonomous_mcp.real_mcp_client import RealMCPClient


class ProductionValidationTest:
    """Comprehensive production validation of real MCP implementation"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.validator = RealMCPValidator(self.logger)
        self.test_results = {}
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def load_server_configs(self) -> dict:
        """Load MCP server configurations from Claude Desktop config"""
        try:
            # Common config locations
            config_paths = [
                Path.home() / "AppData/Roaming/Claude/claude_desktop_config.json",  # Windows
                Path.home() / ".config/claude/claude_desktop_config.json",         # Linux
                Path.home() / "Library/Application Support/Claude/claude_desktop_config.json"  # macOS
            ]
            
            for config_path in config_paths:
                if config_path.exists():
                    with open(config_path, 'r') as f:
                        config = json.load(f)
                        return config.get('mcpServers', {})
            
            # Fallback to example configurations for testing
            return {
                "memory": {
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-memory"],
                    "env": {}
                },
                "filesystem": {
                    "command": "npx", 
                    "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
                    "env": {}
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to load server configs: {e}")
            return {}
    
    async def run_comprehensive_validation(self) -> dict:
        """Run comprehensive validation of real MCP implementation"""
        self.logger.info("🚀 Starting Phase 8.4: Production MCP Validation")
        
        start_time = time.time()
        
        # Load server configurations
        server_configs = self.load_server_configs()
        if not server_configs:
            self.logger.error("No server configurations found - cannot run validation")
            return {"status": "FAILED", "reason": "No server configurations"}
        
        self.logger.info(f"📋 Found {len(server_configs)} server configurations")
        
        # Test 1: Connection Testing
        self.logger.info("🧪 Test 1: Real Server Connection Testing")
        connection_results = await self.validator.test_all_server_connections(server_configs)
        self.test_results["connection_test"] = connection_results
        
        # Test 2: Tool Execution Testing
        self.logger.info("🧪 Test 2: Real Tool Execution Testing")
        execution_results = await self.validator.validate_real_tool_execution(server_configs)
        self.test_results["execution_test"] = execution_results
        
        # Test 3: Performance Benchmarking
        self.logger.info("🧪 Test 3: Performance Benchmarking")
        performance_results = await self.validator.benchmark_real_performance(server_configs)
        self.test_results["performance_test"] = performance_results
        
        # Generate comprehensive report
        validation_report = self.validator.generate_validation_report(
            connection_results,
            execution_results, 
            performance_results
        )
        
        validation_report["total_validation_time"] = time.time() - start_time
        self.test_results["final_report"] = validation_report
        
        # Save results
        await self.save_validation_results()
        
        # Print summary
        self.print_validation_summary(validation_report)
        
        return validation_report
    
    async def save_validation_results(self):
        """Save validation results to file"""
        try:
            results_file = project_root / "phase_8_validation_report.json"
            with open(results_file, 'w') as f:
                json.dump(self.test_results, f, indent=2, default=str)
            
            self.logger.info(f"💾 Validation results saved to {results_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to save validation results: {e}")
    
    def print_validation_summary(self, report: dict):
        """Print validation summary"""
        summary = report.get("summary", {})
        
        print("\n" + "="*80)
        print("🎯 PHASE 8.4: PRODUCTION MCP VALIDATION RESULTS")
        print("="*80)
        print(f"📊 Total Servers Tested: {summary.get('total_servers_tested', 0)}")
        print(f"✅ Successful Connections: {summary.get('successful_connections', 0)}")
        print(f"📈 Connection Success Rate: {summary.get('connection_success_rate', '0%')}")
        print(f"🔧 Total Tools Discovered: {summary.get('total_tools_discovered', 0)}")
        print(f"⚡ Tools Tested: {summary.get('tools_tested', 0)}")
        print(f"🎯 Tool Execution Success Rate: {summary.get('tool_execution_success_rate', '0%')}")
        print(f"⏱️  Total Validation Time: {report.get('total_validation_time', 0):.2f}s")
        print(f"🏆 Overall Status: {report.get('validation_status', 'UNKNOWN')}")
        
        # Recommendations
        recommendations = report.get("recommendations", [])
        if recommendations:
            print("\n📋 RECOMMENDATIONS:")
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. {rec}")
        
        print("="*80)
        
        # Determine Phase 8 success
        success_rate = float(summary.get('connection_success_rate', '0%').rstrip('%'))
        if success_rate >= 90:
            print("🎊 PHASE 8 SUCCESS: Real MCP Protocol Implementation Complete!")
            print("✅ Target achieved: 90%+ server connectivity via real MCP protocol")
        else:
            print("⚠️  PHASE 8 PARTIAL SUCCESS: Some servers failed to connect")
            print(f"🎯 Target: 90%+ connectivity, Achieved: {success_rate}%")
        
        print("="*80 + "\n")


async def main():
    """Main entry point for Phase 8.4 validation"""
    test = ProductionValidationTest()
    
    try:
        results = await test.run_comprehensive_validation()
        
        # Determine exit code based on results
        status = results.get("validation_status", "FAIL")
        if status == "PASS":
            print("🎊 All Phase 8.4 validation tests passed!")
            sys.exit(0)
        else:
            print("⚠️  Some Phase 8.4 validation tests failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Phase 8.4 validation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
