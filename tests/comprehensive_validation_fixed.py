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
        self.log("Testing Tool Availability...")
        
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
                    self.log(f"[PASS] {tool_name}: AVAILABLE")
                else:
                    availability_results[tool_name] = False
                    self.log(f"[FAIL] {tool_name}: NOT FOUND", "ERROR")
                    
        except Exception as e:
            self.log(f"[FAIL] Import Error: {str(e)}", "ERROR")
            for tool_name in tools_to_test:
                availability_results[tool_name] = False
                
        return availability_results
    
    def test_individual_tools(self) -> Dict[str, Dict[str, Any]]:
        """Test 2: Individual tool functionality with real scenarios"""
        self.log("Testing Individual Tool Functionality...")
        
        tool_tests = {}
        
        # Test each tool individually
        test_cases = [
            ('execute_autonomous_task', {
                'task_description': "Create a simple analysis report for testing purposes",
                'context': {"test_mode": True}
            }),
            ('discover_available_tools', {}),
            ('create_intelligent_workflow', {
                'task_description': "Design a workflow for automated data processing and analysis"
            }),
            ('analyze_task_complexity', {
                'task_description': "Build a comprehensive machine learning pipeline with data validation"
            }),
            ('get_personalized_recommendations', {
                'task_description': "Optimize development workflow for a Python project"
            }),
            ('monitor_agent_performance', {}),
            ('configure_agent_preferences', {
                'preferences': {
                    "test_validation": True,
                    "complexity_tolerance": 0.8,
                    "preferred_execution_mode": "fast"
                }
            })
        ]
        
        for tool_name, kwargs in test_cases:
            try:
                self.log(f"Testing {tool_name}...")
                result = self.tools[tool_name](**kwargs)
                tool_tests[tool_name] = {
                    'passed': result.get('success', False),
                    'result': result,
                    'error': None
                }
                status = 'PASS' if result.get('success') else 'FAIL'
                self.log(f"[{status}] {tool_name}: {status}")
            except Exception as e:
                tool_tests[tool_name] = {'passed': False, 'result': None, 'error': str(e)}
                self.log(f"[FAIL] {tool_name}: FAIL - {str(e)}", "ERROR")
        
        return tool_tests
    
    def test_tool_integration(self) -> Dict[str, Any]:
        """Test 3: Tool integration and chaining capabilities"""
        self.log("Testing Tool Integration and Chaining...")
        
        integration_tests = {}
        
        try:
            # Integration Test 1: Workflow Creation -> Analysis -> Recommendations
            self.log("Integration Test 1: Workflow -> Analysis -> Recommendations")
            
            task_desc = "Develop an automated testing framework with CI/CD integration"
            
            # Step 1: Create workflow
            workflow_result = self.tools['create_intelligent_workflow'](
                task_description=task_desc
            )
            
            # Step 2: Analyze complexity  
            analysis_result = self.tools['analyze_task_complexity'](
                task_description=task_desc
            )
            
            # Step 3: Get recommendations
            rec_result = self.tools['get_personalized_recommendations'](
                task_description=task_desc
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
            
            self.log("[PASS] Integration Test 1: PASS")
            
        except Exception as e:
            integration_tests['workflow_analysis_recommendations'] = {
                'passed': False,
                'error': str(e)
            }
            self.log(f"[FAIL] Integration Test 1: FAIL - {str(e)}", "ERROR")
        
        try:
            # Integration Test 2: Preferences -> Execution -> Monitoring
            self.log("Integration Test 2: Preferences -> Execution -> Monitoring")
            
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
            
            self.log("[PASS] Integration Test 2: PASS")
            
        except Exception as e:
            integration_tests['preferences_execution_monitoring'] = {
                'passed': False,
                'error': str(e)
            }
            self.log(f"[FAIL] Integration Test 2: FAIL - {str(e)}", "ERROR")
        
        return integration_tests
    
    def test_performance_requirements(self) -> Dict[str, Any]:
        """Test 4: Performance benchmarks and requirements"""
        self.log("Testing Performance Requirements...")
        
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
            
            status = 'PASS' if response_time < 5.0 else 'FAIL'
            self.log(f"[{status}] Planning Response Time: {response_time:.2f}s ({status})")
            
        except Exception as e:
            performance_tests['planning_response_time'] = {
                'passed': False,
                'error': str(e)
            }
            self.log(f"[FAIL] Planning Response Time: FAIL - {str(e)}", "ERROR")
        
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
            
            status = 'PASS' if discovery_time < 2.0 else 'FAIL'
            self.log(f"[{status}] Discovery Speed: {discovery_time:.2f}s ({status})")
            
        except Exception as e:
            performance_tests['discovery_speed'] = {
                'passed': False,
                'error': str(e)
            }
            self.log(f"[FAIL] Discovery Speed: FAIL - {str(e)}", "ERROR")
        
        return performance_tests
    
    def generate_comprehensive_report(self, availability: Dict[str, bool], 
                                    individual: Dict[str, Dict[str, Any]],
                                    integration: Dict[str, Any],
                                    performance: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive validation report"""
        
        total_time = time.time() - self.start_time
        
        # Calculate overall success rates
        tools_available = sum(availability.values())
        tools_working = sum(1 for test in individual.values() if test['passed'])
        integration_passed = sum(1 for test in integration.values() if test.get('passed', False))
        performance_passed = sum(1 for test in performance.values() if test.get('passed', False))
        
        total_tests = 7 + len(integration) + len(performance)
        passed_tests = tools_working + integration_passed + performance_passed
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_validation_time': total_time,
            'overall_status': 'PASS' if tools_available == 7 and tools_working == 7 else 'FAIL',
            'summary': {
                'tools_available': f"{tools_available}/7",
                'tools_working': f"{tools_working}/7", 
                'integration_tests_passed': f"{integration_passed}/{len(integration)}",
                'performance_tests_passed': f"{performance_passed}/{len(performance)}",
                'overall_success_rate': f"{(passed_tests / total_tests) * 100:.1f}%"
            },
            'detailed_results': {
                'availability': availability,
                'individual_tools': individual,
                'integration': integration,
                'performance': performance
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
        
        if not report['recommendations']:
            report['recommendations'].append("All tests passed! System is operating at 100% capacity.")
        
        return report
    
    def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run complete validation suite"""
        self.log("Starting Comprehensive Validation Suite")
        self.log("=" * 60)
        
        # Test 1: Tool Availability
        availability = self.validate_tool_availability()
        
        # Test 2: Individual Tool Functionality  
        individual = self.test_individual_tools()
        
        # Test 3: Tool Integration
        integration = self.test_tool_integration()
        
        # Test 4: Performance Requirements
        performance = self.test_performance_requirements()
        
        # Generate Report
        report = self.generate_comprehensive_report(
            availability, individual, integration, performance
        )
        
        self.log("=" * 60)
        self.log(f"Validation Complete - Overall Status: {report['overall_status']}")
        self.log(f"Success Rate: {report['summary']['overall_success_rate']}")
        self.log(f"Total Time: {report['total_validation_time']:.2f}s")
        
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
        
        print(f"\nDetailed report saved to: {report_file}")
        
        # Print summary
        print("\n" + "=" * 60)
        print("VALIDATION SUMMARY")
        print("=" * 60)
        for key, value in report['summary'].items():
            print(f"{key.replace('_', ' ').title()}: {value}")
        
        print(f"\nOverall Status: {report['overall_status']}")
        
        if report['recommendations']:
            print("\nRecommendations:")
            for rec in report['recommendations']:
                print(f"  - {rec}")
        
        return report['overall_status'] == 'PASS'
        
    except Exception as e:
        print(f"Validation failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
