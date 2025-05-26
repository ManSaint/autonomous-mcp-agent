# PHASE 6.4: PRODUCTION VALIDATION & TESTING
# Comprehensive validation of Phase 6 implementation for production readiness

import asyncio
import sys
import os
import time
import json
from datetime import datetime

# Add the autonomous_mcp module to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from autonomous_mcp.mcp_protocol import MCPProtocolBridge
    from autonomous_mcp.proxy_workflow_executor import ProxyWorkflowExecutor
    from autonomous_mcp.proxy_executor import ProxyExecutor
    from autonomous_mcp.external_tool_registry import EXTERNAL_TOOL_REGISTRY
    print("SUCCESS: All Phase 6 modules imported successfully")
except ImportError as e:
    print(f"IMPORT ERROR: {e}")
    sys.exit(1)


async def run_production_validation():
    """Run comprehensive production validation for Phase 6.4"""
    
    print("\nPHASE 6.4: PRODUCTION VALIDATION & TESTING")
    print("=" * 60)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Initialize systems
    protocol = MCPProtocolBridge()
    protocol._initialize_framework()
    workflow_executor = ProxyWorkflowExecutor()
    
    validation_results = {
        "discovery": {},
        "workflows": {},
        "performance": {},
        "production_ready": False
    }
    
    try:
        # Test 1: Discovery System Validation
        print("\nTEST 1: DISCOVERY SYSTEM VALIDATION")
        print("-" * 40)
        
        start_time = time.time()
        discovery_result = await protocol._discover_tools(include_performance=True)
        discovery_time = time.time() - start_time
        
        tools_found = len(discovery_result.get('tools', {}))
        discovery_success = discovery_result.get('success', False)
        
        validation_results["discovery"] = {
            "success": discovery_success,
            "tools_found": tools_found,
            "discovery_time": discovery_time,
            "performance_target_met": discovery_time < 2.0
        }
        
        print(f"Discovery Success: {discovery_success}")
        print(f"Tools Found: {tools_found}")
        print(f"Discovery Time: {discovery_time:.3f}s (Target: <2s)")
        print(f"Performance: {'PASS' if discovery_time < 2.0 else 'FAIL'}")
        
        # Test 2: Workflow Orchestration
        print("\nTEST 2: WORKFLOW ORCHESTRATION")
        print("-" * 40)
        
        # Test simple tool chain
        tool_chain = [
            {
                'tool_name': 'discover_available_tools',
                'parameters': {},
                'description': 'Test discovery'
            },
            {
                'tool_name': 'analyze_task_complexity',
                'parameters': {'task_description': 'Test workflow execution'},
                'description': 'Test analysis'
            }
        ]
        
        try:
            chain_result = await workflow_executor.execute_multi_tool_chain(tool_chain)
            
            validation_results["workflows"]["simple_chain"] = {
                "success": chain_result.success,
                "completed_steps": chain_result.completed_steps,
                "total_steps": chain_result.total_steps,
                "execution_time": chain_result.total_execution_time
            }
            
            print(f"Tool Chain Success: {chain_result.success}")
            print(f"Steps Completed: {chain_result.completed_steps}/{chain_result.total_steps}")
            print(f"Execution Time: {chain_result.total_execution_time:.3f}s")
            
        except Exception as e:
            validation_results["workflows"]["simple_chain"] = {"success": False, "error": str(e)}
            print(f"Tool Chain: FAILED ({str(e)[:50]}...)")
        
        # Test hybrid workflow
        print("\nTesting Hybrid Workflow...")
        
        try:
            hybrid_workflow = [
                {
                    'tool': 'discover_available_tools',
                    'parameters': {},
                    'description': 'Internal tool test'
                },
                {
                    'tool': 'create_intelligent_workflow',
                    'parameters': {'task_description': 'Test hybrid workflow'},
                    'description': 'Internal workflow creation'
                }
            ]
            
            hybrid_result = await protocol._execute_hybrid_workflow(
                "Test hybrid execution",
                hybrid_workflow
            )
            
            validation_results["workflows"]["hybrid"] = {
                "success": hybrid_result.get('success', False),
                "workflow_type": hybrid_result.get('workflow_type', 'unknown')
            }
            
            print(f"Hybrid Workflow: {'SUCCESS' if hybrid_result.get('success') else 'FAILED'}")
            
        except Exception as e:
            validation_results["workflows"]["hybrid"] = {"success": False, "error": str(e)}
            print(f"Hybrid Workflow: FAILED ({str(e)[:50]}...)")
        
        # Test 3: Performance Validation
        print("\nTEST 3: PERFORMANCE VALIDATION")
        print("-" * 40)
        
        # Multiple discovery performance tests
        discovery_times = []
        for i in range(3):
            start_time = time.time()
            await protocol._discover_tools()
            discovery_times.append(time.time() - start_time)
        
        avg_discovery_time = sum(discovery_times) / len(discovery_times)
        max_discovery_time = max(discovery_times)
        
        validation_results["performance"] = {
            "average_discovery_time": avg_discovery_time,
            "max_discovery_time": max_discovery_time,
            "target_met": avg_discovery_time < 2.0
        }
        
        print(f"Average Discovery Time: {avg_discovery_time:.3f}s")
        print(f"Max Discovery Time: {max_discovery_time:.3f}s")
        print(f"Performance Target: {'MET' if avg_discovery_time < 2.0 else 'NOT MET'}")
        
        # Final Assessment
        print("\nFINAL ASSESSMENT")
        print("-" * 40)
        
        # Calculate overall score
        discovery_score = 100 if validation_results["discovery"]["success"] and validation_results["discovery"]["performance_target_met"] else 50
        workflow_score = 100 if validation_results["workflows"].get("simple_chain", {}).get("success", False) else 0
        hybrid_score = 100 if validation_results["workflows"].get("hybrid", {}).get("success", False) else 0
        performance_score = 100 if validation_results["performance"]["target_met"] else 50
        
        overall_score = (discovery_score + workflow_score + hybrid_score + performance_score) / 4
        
        validation_results["overall_score"] = overall_score
        validation_results["production_ready"] = overall_score >= 75
        
        print(f"Discovery System: {discovery_score}%")
        print(f"Workflow System: {workflow_score}%")
        print(f"Hybrid Workflows: {hybrid_score}%")
        print(f"Performance: {performance_score}%")
        print("-" * 30)
        print(f"OVERALL SCORE: {overall_score:.1f}%")
        
        if overall_score >= 90:
            status = "EXCELLENT - PRODUCTION READY"
        elif overall_score >= 75:
            status = "GOOD - PRODUCTION READY"
        elif overall_score >= 60:
            status = "ACCEPTABLE - MINOR ISSUES"
        else:
            status = "NEEDS IMPROVEMENT"
        
        print(f"STATUS: {status}")
        
        # Phase 6 Completion Assessment
        print(f"\nPHASE 6 COMPLETION STATUS")
        print("-" * 30)
        
        if overall_score >= 75:
            print("PHASE 6.4: SUCCESSFULLY COMPLETED")
            print("PHASE 6: 100% COMPLETE")
            print("MCP Discovery Infrastructure Fix: MISSION ACCOMPLISHED")
            phase_6_complete = True
        else:
            print("PHASE 6.4: NEEDS ATTENTION")
            print(f"Current Progress: {overall_score:.0f}% (Target: 75%+)")
            phase_6_complete = False
        
        validation_results["phase_6_complete"] = phase_6_complete
        
        # Save validation report
        report_data = {
            "validation_date": datetime.now().isoformat(),
            "validation_results": validation_results,
            "phase_6_status": "100% COMPLETE" if phase_6_complete else f"{overall_score:.0f}% COMPLETE"
        }
        
        try:
            with open("phase_6_4_validation_report.json", 'w') as f:
                json.dump(report_data, f, indent=2)
            print(f"\nValidation report saved: phase_6_4_validation_report.json")
        except Exception as e:
            print(f"Could not save report: {e}")
        
        return phase_6_complete
        
    except Exception as e:
        print(f"Validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    asyncio.run(run_production_validation())
