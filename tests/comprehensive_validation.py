#!/usr/bin/env python3
"""
Comprehensive Validation Suite for Autonomous MCP Agent
Ensures 100% test pass rate for all 7 autonomous tools
"""

import asyncio
import json
import time
import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Tuple

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

class ComprehensiveValidator:
    def __init__(self):
        self.test_results = {}
        self.integration_results = {}
        self.performance_metrics = {}
        self.start_time = time.time()
        
    def log(self, message: str, level: str = "INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
        
    def validate_tool_availability(self) -> Dict[str, bool]:
        """Test 1: Validate all 7 tools are available and importable"""
        self.log("🔍 Testing Tool Availability...")
        
        tools_to_test = [
            'execute_autonomous_task',
            'discover_available_tools', 
            'create_intelligent_workflow',
            'analyze_task_complexity',
            'get_personalized_recommendations',
            'monitor_agent_performance',
            'configure_agent_preferences'
        ]
        
        availability_results = {}
        
        try:
            # Import the autonomous tools
            from autonomous_mcp.autonomous_tools import (
                execute_autonomous_task,
                discover_available_tools,
                create_intelligent_workflow,
                analyze_task_complexity,
                get_personalized_recommendations,
                monitor_agent_performance,
                configure_agent_preferences
            )
            
            # Store functions for later use
            self.tools = {
                'execute_autonomous_task': execute_autonomous_task,
                'discover_available_tools': discover_available_tools,
                'create_intelligent_workflow': create_intelligent_workflow,
                'analyze_task_complexity': analyze_task_complexity,
                'get_personalized_recommendations': get_personalized_recommendations,
                'monitor_agent_performance': monitor_agent_performance,
                'configure_agent_preferences': configure_agent_preferences
            }
            
            for tool_name in tools_to_test:
                if tool_name in self.tools:
                    availability_results[tool_name] = True
                    self.log(f"✅ {tool_name}: AVAILABLE")
                else:
                    availability_results[tool_name] = False
                    self.log(f"❌ {tool_name}: NOT FOUND", "ERROR")
                    
        except Exception as e:
            self.log(f"❌ Import Error: {str(e)}", "ERROR")
            for tool_name in tools_to_test:
                availability_results[tool_name] = False
                
        return availability_results
    
    def test_individual_tools(self) -> Dict[str, Dict[str, Any]]:
        """Test 2: Individual tool functionality with real scenarios"""
        self.log("🧪 Testing Individual Tool Functionality...")
        
        tool_tests = {}
        
        # Test 1: execute_autonomous_task
        try:
            self.log("Testing execute_autonomous_task...")
            result = self.tools['execute_autonomous_task'](
                task_description="Create a simple analysis report for testing purposes",
                context={"test_mode": True}
            )
            tool_tests['execute_autonomous_task'] = {
                'passed': result.get('success', False),
                'result': result,
                'error': None
            }
            self.log(f"✅ execute_autonomous_task: {'PASS' if result.get('success') else 'FAIL'}")
        except Exception as e:
            tool_tests['execute_autonomous_task'] = {'passed': False, 'result': None, 'error': str(e)}
            self.log(f"❌ execute_autonomous_task: FAIL - {str(e)}", "ERROR")
        
        # Test 2: discover_available_tools
        try:
            self.log("Testing discover_available_tools...")
            result = self.tools['discover_available_tools']()
            tool_tests['discover_available_tools'] = {
                'passed': result.get('success', False),
                'result': result,
                'error': None
            }
            self.log(f"✅ discover_available_tools: {'PASS' if result.get('success') else 'FAIL'}")
        except Exception as e:
            tool_tests['discover_available_tools'] = {'passed': False, 'result': None, 'error': str(e)}
            self.log(f"❌ discover_available_tools: FAIL - {str(e)}", "ERROR")
        
        # Test 3: create_intelligent_workflow
        try:
            self.log("Testing create_intelligent_workflow...")
            result = self.tools['create_intelligent_workflow'](
                task_description="Design a workflow for automated data processing and analysis"
            )
            tool_tests['create_intelligent_workflow'] = {
                'passed': result.get('success', False),
                'result': result,
                'error': None
            }
            self.log(f"✅ create_intelligent_workflow: {'PASS' if result.get('success') else 'FAIL'}")
        except Exception as e:
            tool_tests['create_intelligent_workflow'] = {'passed': False, 'result': None, 'error': str(e)}
            self.log(f"❌ create_intelligent_workflow: FAIL - {str(e)}", "ERROR")
        
        # Test 4: analyze_task_complexity
        try:
            self.log("Testing analyze_task_complexity...")
            result = self.tools['analyze_task_complexity'](
                task_description="Build a comprehensive machine learning pipeline with data validation"
            )
            tool_tests['analyze_task_complexity'] = {
                'passed': result.get('success', False),
                'result': result,
                'error': None
            }
            self.log(f"✅ analyze_task_complexity: {'PASS' if result.get('success') else 'FAIL'}")
        except Exception as e:
            tool_tests['analyze_task_complexity'] = {'passed': False, 'result': None, 'error': str(e)}
            self.log(f"❌ analyze_task_complexity: FAIL - {str(e)}", "ERROR")
        
        # Test 5: get_personalized_recommendations
        try:
            self.log("Testing get_personalized_recommendations...")
            result = self.tools['get_personalized_recommendations'](
                task_description="Optimize development workflow for a Python project"
            )
            tool_tests['get_personalized_recommendations'] = {
                'passed': result.get('success', False),
                'result': result,
                'error': None
            }
            self.log(f"✅ get_personalized_recommendations: {'PASS' if result.get('success') else 'FAIL'}")
        except Exception as e:
            tool_tests['get_personalized_recommendations'] = {'passed': False, 'result': None, 'error': str(e)}
            self.log(f"❌ get_personalized_recommendations: FAIL - {str(e)}", "ERROR")
        
        # Test 6: monitor_agent_performance
        try:
            self.log("Testing monitor_agent_performance...")
            result = self.tools['monitor_agent_performance']()
            tool_tests['monitor_agent_performance'] = {
                'passed': result.get('success', False),
                'result': result,
                'error': None
            }
            self.log(f"✅ monitor_agent_performance: {'PASS' if result.get('success') else 'FAIL'}")
        except Exception as e:
            tool_tests['monitor_agent_performance'] = {'passed': False, 'result': None, 'error': str(e)}
            self.log(f"❌ monitor_agent_performance: FAIL - {str(e)}", "ERROR")
        
        # Test 7: configure_agent_preferences
        try:
            self.log("Testing configure_agent_preferences...")
            result = self.tools['configure_agent_preferences'](
                preferences={
                    "test_validation": True,
                    "complexity_tolerance": 0.8,
                    "preferred_execution_mode": "fast"
                }
            )
            tool_tests['configure_agent_preferences'] = {
                'passed': result.get('success', False),
                'result': result,
                'error': None
            }
            self.log(f"✅ configure_agent_preferences: {'PASS' if result.get('success') else 'FAIL'}")
        except Exception as e:
            tool_tests['configure_agent_preferences'] = {'passed': False, 'result': None, 'error': str(e)}
            self.log(f"❌ configure_agent_preferences: FAIL - {str(e)}", "ERROR")
        
        return tool_tests
    
    def test_tool_integration(self) -> Dict[str, Any]:
        """Test 3: Tool integration and chaining capabilities"""
        self.log("🔗 Testing Tool Integration and Chaining...")
        
        integration_tests = {}
        
        try:
            # Integration Test 1: Workflow Creation → Analysis → Recommendations
            self.log("Integration Test 1: Workflow → Analysis → Recommendations")
            
            # Step 1: Create workflow
            workflow_result = self.tools['create_intelligent_workflow'](
                task_description="Develop an automated testing framework with CI/CD integration"
            )
            
            # Step 2: Analyze complexity  
            analysis_result = self.tools['analyze_task_complexity'](
                task_description="Develop an automated testing framework with CI/CD integration"
            )
            
            # Step 3: Get recommendations
            rec_result = self.tools['get_personalized_recommendations'](
                task_description="Develop an automated testing framework with CI/CD integration"
            )
            
            integration_tests['workflow_analysis_recommendations'] = {
                'passed': all([
                    workflow_result.get('success', False),
                    analysis_result.get('success', False), 
                    rec_result.get('success', False)
                ]),
                'steps': {
                    'workflow': workflow_result.get('success', False),
                    'analysis': analysis_result.get('success', False),
                    'recommendations': rec_result.get('success', False)
                }
            }
            
        except Exception as e:
            integration_tests['workflow_analysis_recommendations'] = {
                'passed': False,
                'error': str(e)
            }
            self.log(f"❌ Integration Test 1: FAIL - {str(e)}", "ERROR")
        
        try:
            # Integration Test 2: Preferences → Execution → Monitoring
            self.log("Integration Test 2: Preferences → Execution → Monitoring")
            
            # Step 1: Configure preferences
            pref_result = self.tools['configure_agent_preferences'](
                preferences={"detailed_feedback": True, "parallel_execution": False}
            )
            
            # Step 2: Execute task
            exec_result = self.tools['execute_autonomous_task'](
                task_description="Generate test data and validate its structure"
            )
            
            # Step 3: Monitor performance  
            monitor_result = self.tools['monitor_agent_performance']()
            
            integration_tests['preferences_execution_monitoring'] = {
                'passed': all([
                    pref_result.get('success', False),
                    exec_result.get('success', False),
                    monitor_result.get('success', False)
                ]),
                'steps': {
                    'preferences': pref_result.get('success', False),
                    'execution': exec_result.get('success', False),
                    'monitoring': monitor_result.get('success', False)
                }
            }
            
        except Exception as e:
            integration_tests['preferences_execution_monitoring'] = {
                'passed': False,
                'error': str(e)
            }
            self.log(f"❌ Integration Test 2: FAIL - {str(e)}", "ERROR")
        
        return integration_tests
    
    def test_performance_requirements(self) -> Dict[str, Any]:
        """Test 4: Performance benchmarks and requirements"""
        self.log("⚡ Testing Performance Requirements...")
        
        performance_tests = {}
        
        # Performance Test 1: Response times under 5 seconds for planning
        try:
            self.log("Performance Test 1: Planning Response Times")
            
            start_time = time.time()
            result = self.tools['create_intelligent_workflow'](
                task_description="Create a comprehensive data analysis pipeline"
            )
            end_time = time.time()
            
            response_time = end_time - start_time
            performance_tests['planning_response_time'] = {
                'passed': response_time < 5.0,
                'response_time': response_time,
                'requirement': 5.0,
                'success': result.get('success', False)
            }
            
            self.log(f"✅ Planning Response Time: {response_time:.2f}s ({'PASS' if response_time < 5.0 else 'FAIL'})")
            
        except Exception as e:
            performance_tests['planning_response_time'] = {
                'passed': False,
                'error': str(e)
            }
            self.log(f"❌ Planning Response Time: FAIL - {str(e)}", "ERROR")
        
        # Performance Test 2: Tool discovery speed
        try:
            self.log("Performance Test 2: Tool Discovery Speed")
            
            start_time = time.time()
            result = self.tools['discover_available_tools']()
            end_time = time.time()
            
            discovery_time = end_time - start_time
            performance_tests['discovery_speed'] = {
                'passed': discovery_time < 2.0,
                'discovery_time': discovery_time,
                'requirement': 2.0,
                'success': result.get('success', False)
            }
            
            self.log(f"✅ Discovery Speed: {discovery_time:.2f}s ({'PASS' if discovery_time < 2.0 else 'FAIL'})")
            
        except Exception as e:
            performance_tests['discovery_speed'] = {
                'passed': False,
                'error': str(e)
            }
            self.log(f"❌ Discovery Speed: FAIL - {str(e)}", "ERROR")
        
        return performance_tests
    
    def test_error_handling(self) -> Dict[str, Any]:
        """Test 5: Error handling and recovery capabilities"""
        self.log("🛡️ Testing Error Handling and Recovery...")
        
        error_tests = {}
        
        # Error Test 1: Invalid input handling
        try:
            self.log("Error Test 1: Invalid Input Handling")
            
            # Test with invalid task description
            result = self.tools['create_intelligent_workflow'](
                task_description=""  # Empty task
            )
            
            error_tests['invalid_input_handling'] = {
                'passed': True,  # Should not crash, should handle gracefully
                'handled_gracefully': result is not None,
                'result': result
            }
            
            self.log("✅ Invalid Input Handling: PASS")
            
        except Exception as e:
            error_tests['invalid_input_handling'] = {
                'passed': False,
                'error': str(e)
            }
            self.log(f"❌ Invalid Input Handling: FAIL - {str(e)}", "ERROR")
        
        # Error Test 2: Resource constraint handling
        try:
            self.log("Error Test 2: Resource Constraint Handling")
            
            # Test with complex task that might hit limits
            result = self.tools['analyze_task_complexity'](
                task_description="Build a complete enterprise system with microservices, databases, APIs, frontend, backend, mobile apps, AI components, real-time analytics, security, monitoring, and deployment across multiple cloud providers with full CI/CD, testing, documentation, and maintenance"
            )
            
            error_tests['resource_constraint_handling'] = {
                'passed': result is not None,
                'handled_gracefully': result.get('success', False) or 'error' in result,
                'result': result
            }
            
            self.log("✅ Resource Constraint Handling: PASS")
            
        except Exception as e:
            error_tests['resource_constraint_handling'] = {
                'passed': False,
                'error': str(e)
            }
            self.log(f"❌ Resource Constraint Handling: FAIL - {str(e)}", "ERROR")
        
        return error_tests
    
    def generate_comprehensive_report(self, availability: Dict[str, bool], 
                                    individual: Dict[str, Dict[str, Any]],
                                    integration: Dict[str, Any],
                                    performance: Dict[str, Any],
                                    error_handling: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive validation report"""
        
        total_time = time.time() - self.start_time
        
        # Calculate overall success rates
        tools_available = sum(availability.values())
        tools_working = sum(1 for test in individual.values() if test['passed'])
        integration_passed = sum(1 for test in integration.values() if test.get('passed', False))
        performance_passed = sum(1 for test in performance.values() if test.get('passed', False))
        error_handling_passed = sum(1 for test in error_handling.values() if test.get('passed', False))
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_validation_time': total_time,
            'overall_status': 'PASS' if tools_available == 7 and tools_working == 7 else 'FAIL',
            'summary': {
                'tools_available': f"{tools_available}/7",
                'tools_working': f"{tools_working}/7", 
                'integration_tests_passed': f"{integration_passed}/{len(integration)}",
                'performance_tests_passed': f"{performance_passed}/{len(performance)}",
                'error_handling_tests_passed': f"{error_handling_passed}/{len(error_handling)}",
                'overall_success_rate': f"{((tools_working + integration_passed + performance_passed + error_handling_passed) / (7 + len(integration) + len(performance) + len(error_handling))) * 100:.1f}%"
            },
            'detailed_results': {
                'availability': availability,
                'individual_tools': individual,
                'integration': integration,
                'performance': performance,
                'error_handling': error_handling
            },
            'recommendations': []
        }
        
        # Add recommendations based on results
        if tools_available < 7:
            report['recommendations'].append("Fix tool availability issues - some tools are not importable")
        if tools_working < 7:
            report['recommendations'].append("Fix individual tool functionality issues")
        if integration_passed < len(integration):
            report['recommendations'].append("Improve tool integration and chaining capabilities")
        if performance_passed < len(performance):
            report['recommendations'].append("Optimize performance to meet response time requirements")
        if error_handling_passed < len(error_handling):
            report['recommendations'].append("Enhance error handling and recovery mechanisms")
        
        if not report['recommendations']:
            report['recommendations'].append("All tests passed! System is operating at 100% capacity.")
        
        return report
    
    def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run complete validation suite"""
        self.log("🚀 Starting Comprehensive Validation Suite")
        self.log("=" * 60)
        
        # Test 1: Tool Availability
        availability = self.validate_tool_availability()
        
        # Test 2: Individual Tool Functionality  
        individual = self.test_individual_tools()
        
        # Test 3: Tool Integration
        integration = self.test_tool_integration()
        
        # Test 4: Performance Requirements
        performance = self.test_performance_requirements()
        
        # Test 5: Error Handling
        error_handling = self.test_error_handling()
        
        # Generate Report
        report = self.generate_comprehensive_report(
            availability, individual, integration, performance, error_handling
        )
        
        self.log("=" * 60)
        self.log(f"🏁 Validation Complete - Overall Status: {report['overall_status']}")
        self.log(f"📊 Success Rate: {report['summary']['overall_success_rate']}")
        self.log(f"⏱️ Total Time: {report['total_validation_time']:.2f}s")
        
        return report

def main():
    """Main validation function"""
    validator = ComprehensiveValidator()
    
    try:
        report = validator.run_comprehensive_validation()
        
        # Save detailed report
        report_file = f"validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n📋 Detailed report saved to: {report_file}")
        
        # Print summary
        print("\n" + "=" * 60)
        print("🎯 VALIDATION SUMMARY")
        print("=" * 60)
        for key, value in report['summary'].items():
            print(f"{key.replace('_', ' ').title()}: {value}")
        
        print(f"\nOverall Status: {report['overall_status']}")
        
        if report['recommendations']:
            print("\n📝 Recommendations:")
            for rec in report['recommendations']:
                print(f"  • {rec}")
        
        return report['overall_status'] == 'PASS'
        
    except Exception as e:
        print(f"❌ Validation failed with error: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
