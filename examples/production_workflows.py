#!/usr/bin/env python3
"""
Autonomous MCP Agent - Production Workflows
Real-world usage examples demonstrating the autonomous agent capabilities.
"""

import asyncio
import json
import sys
import time
from pathlib import Path
from typing import Dict, Any, List

# Add project root to path  
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from autonomous_mcp.autonomous_tools import AdvancedAutonomousTools
from autonomous_mcp.real_mcp_discovery import RealMCPDiscovery
from autonomous_mcp.mcp_chain_executor import RealMCPChainExecutor
from autonomous_mcp.monitoring import MonitoringSystem


class ProductionWorkflowDemonstrator:
    """Demonstrates production-ready workflows using the autonomous MCP agent."""
    
    def __init__(self):
        self.autonomous_tools = AdvancedAutonomousTools()
        self.real_discovery = RealMCPDiscovery()
        self.chain_executor = RealMCPChainExecutor()
        self.monitoring_system = MonitoringSystem()
        
        print(">> Autonomous MCP Agent - Production Workflows")
        print("=" * 60)
        
    def run_research_workflow(self):
        """Workflow 1: Research & Knowledge Management"""
        return asyncio.run(self._run_research_workflow_async())
    
    async def _run_research_workflow_async(self):
        """Workflow 1: Research & Knowledge Management"""
        print("\n[📚] WORKFLOW 1: Research AI Trends and Save to Knowledge Base")
        print("-" * 60)
        
        task_description = """
        Research the latest AI trends in 2024, focusing on:
        - Large Language Models developments
        - Computer Vision breakthroughs  
        - AI Safety and Ethics progress
        - Industry adoption patterns
        
        Create a comprehensive knowledge base entry with sources and analysis.
        """
        
        start_time = time.time()
        
        try:
            # Step 1: Analyze task complexity
            print(">> Step 1: Analyzing task complexity...")
            complexity_result = await self.autonomous_tools._analyze_task_complexity(
                task_description.strip(), {}
            )
            
            print(f"   Complexity Score: {complexity_result.get('complexity_score', 'N/A')}/10")
            print(f"   Risk Factors: {len(complexity_result.get('risk_factors', []))}")
            print(f"   Success Probability: {complexity_result.get('success_probability', 'N/A')}%")
            
            # Step 2: Create intelligent workflow
            print("\n>> Step 2: Creating intelligent workflow...")
            workflow_result = await self.autonomous_tools._create_intelligent_workflow(
                task_description.strip(), {}
            )
            
            workflow = workflow_result.get("workflow_template", {})
            steps = workflow.get("steps", [])
            print(f"   Generated {len(steps)} workflow steps")
            
            for i, step in enumerate(steps[:3], 1):  # Show first 3 steps
                print(f"   {i}. {step.get('type', 'unknown').title()}: {step.get('description', 'No description')[:50]}...")
            
            # Step 3: Get tool recommendations
            print("\n>> Step 3: Getting tool recommendations...")
            available_tools = self.real_discovery.discover_available_tools()
            recommendations = self.chain_executor.recommend_tools_for_task(task_description.strip())
            
            print(f"   Available MCP Tools: {len(available_tools)}")
            print(f"   Recommended Tools: {len(recommendations)}")
            
            if recommendations:
                for tool in recommendations[:3]:  # Show top 3
                    print(f"   - {tool.get('name', 'Unknown')}: {tool.get('reason', 'No reason')[:40]}...")
            
            execution_time = time.time() - start_time
            print(f"\n✓ Research workflow planned in {execution_time:.2f}s")
            
            return {
                "status": "success",
                "complexity": complexity_result,
                "workflow": workflow_result,
                "recommendations": recommendations,
                "execution_time": execution_time
            }
            
        except Exception as e:
            print(f"\n❌ Research workflow failed: {e}")
            return {"status": "error", "error": str(e)}
            
    def run_development_workflow(self):
        """Workflow 2: Development Automation"""
        return asyncio.run(self._run_development_workflow_async())
    
    async def _run_development_workflow_async(self):
        """Workflow 2: Development Automation"""
        print("\n💻 WORKFLOW 2: Find Trending ML Repos and Create Tasks")
        print("-" * 60)
        
        task_description = """
        Find trending machine learning repositories on GitHub from the past month.
        Evaluate them for:
        - Code quality and documentation
        - Community activity and adoption
        - Integration potential with our projects
        - Learning opportunities
        
        Create development tasks for the most promising repositories.
        """
        
        start_time = time.time()
        
        try:
            # Analyze and plan
            print("🔍 Analyzing development automation task...")
            complexity_result = await self.autonomous_tools._analyze_task_complexity(
                task_description.strip(), {}
            )
            
            print(f"   Complexity: {complexity_result.get('complexity_score', 'N/A')}/10")
            
            # Create workflow
            workflow_result = await self.autonomous_tools._create_intelligent_workflow(
                task_description.strip(), {}
            )
            
            # Check for GitHub/search tools
            available_tools = self.real_discovery.discover_available_tools()
            github_tools = [name for name in available_tools.keys() if 'github' in name.lower()]
            search_tools = [name for name in available_tools.keys() if 'search' in name.lower()]
            
            print(f"   GitHub Tools Available: {len(github_tools)}")
            print(f"   Search Tools Available: {len(search_tools)}")
            
            if github_tools:
                print(f"   - Primary GitHub Tool: {github_tools[0]}")
            if search_tools:
                print(f"   - Primary Search Tool: {search_tools[0]}")
                
            execution_time = time.time() - start_time
            print(f"\n✅ Development workflow planned in {execution_time:.2f}s")
            
            return {
                "status": "success",
                "complexity": complexity_result,
                "workflow": workflow_result,
                "available_github_tools": github_tools,
                "available_search_tools": search_tools,
                "execution_time": execution_time
            }
            
        except Exception as e:
            print(f"\n❌ Development workflow failed: {e}")
            return {"status": "error", "error": str(e)}
            
    def run_content_analysis_workflow(self):
        """Workflow 3: Content Analysis & Action Items"""
        return asyncio.run(self._run_content_analysis_workflow_async())
    
    async def _run_content_analysis_workflow_async(self):
        """Workflow 3: Content Analysis & Action Items"""
        print("\n📝 WORKFLOW 3: Analyze Content and Create Action Items")
        print("-" * 60)
        
        task_description = """
        Analyze a meeting transcript or document content to:
        - Extract key decisions and commitments
        - Identify action items with owners and deadlines
        - Categorize items by priority and department
        - Generate follow-up tasks and reminders
        - Create summary report for stakeholders
        """
        
        start_time = time.time()
        
        try:
            print("🔍 Analyzing content analysis task...")
            
            # Task complexity analysis
            complexity_result = await self.autonomous_tools._analyze_task_complexity(
                task_description.strip(), {}
            )
            
            # Get personalized recommendations
            recommendations = await self.autonomous_tools._get_personalized_recommendations(
                task_description.strip(), {}, {}
            )
            
            print(f"   Complexity: {complexity_result.get('complexity_score', 'N/A')}/10")
            print(f"   Recommendations: {len(recommendations.get('recommendations', []))}")
            
            # Show key recommendations
            for rec in recommendations.get('recommendations', [])[:2]:
                print(f"   - {rec.get('type', 'General')}: {rec.get('suggestion', 'No suggestion')[:50]}...")
            
            execution_time = time.time() - start_time
            print(f"\n✅ Content analysis workflow planned in {execution_time:.2f}s")
            
            return {
                "status": "success", 
                "complexity": complexity_result,
                "recommendations": recommendations,
                "execution_time": execution_time
            }
            
        except Exception as e:
            print(f"\n❌ Content analysis workflow failed: {e}")
            return {"status": "error", "error": str(e)}
            
    def run_multi_platform_workflow(self):
        """Workflow 4: Multi-Platform Integration"""
        return asyncio.run(self._run_multi_platform_workflow_async())
    
    async def _run_multi_platform_workflow_async(self):
        """Workflow 4: Multi-Platform Integration"""
        print("\n🌐 WORKFLOW 4: Multi-Platform Task Integration")
        print("-" * 60)
        
        task_description = """
        Multi-platform workflow:
        1. Search for latest cybersecurity news and threats
        2. Analyze relevance to our infrastructure  
        3. Create GitHub issue for security review
        4. Add task to project management board
        5. Send notification to security team
        6. Schedule follow-up review meeting
        """
        
        start_time = time.time()
        
        try:
            print("🔍 Analyzing multi-platform integration task...")
            
            # Complex task analysis
            complexity_result = await self.autonomous_tools._analyze_task_complexity(
                task_description.strip(), {}
            )
            
            # Workflow creation
            workflow_result = await self.autonomous_tools._create_intelligent_workflow(
                task_description.strip(), {}
            )
            
            # Check available integration tools
            available_tools = self.real_discovery.discover_available_tools()
            integration_tools = []
            
            for tool_name in available_tools.keys():
                if any(platform in tool_name.lower() for platform in ['github', 'trello', 'slack', 'search']):
                    integration_tools.append(tool_name)
            
            print(f"   Complexity: {complexity_result.get('complexity_score', 'N/A')}/10")
            print(f"   Workflow Steps: {len(workflow_result.get('workflow_template', {}).get('steps', []))}")
            print(f"   Integration Tools: {len(integration_tools)}")
            
            if integration_tools:
                print("   Available Integration Tools:")
                for tool in integration_tools[:4]:  # Show first 4
                    print(f"   - {tool}")
            
            execution_time = time.time() - start_time
            print(f"\n✅ Multi-platform workflow planned in {execution_time:.2f}s")
            
            return {
                "status": "success",
                "complexity": complexity_result,
                "workflow": workflow_result,
                "integration_tools": integration_tools,
                "execution_time": execution_time
            }
            
        except Exception as e:
            print(f"\n❌ Multi-platform workflow failed: {e}")
            return {"status": "error", "error": str(e)}
            
    def run_performance_analysis(self):
        """Analyze agent performance across all workflows."""
        return asyncio.run(self._run_performance_analysis_async())
    
    async def _run_performance_analysis_async(self):
        """Analyze agent performance across all workflows."""
        print("\n📊 PERFORMANCE ANALYSIS")
        print("-" * 60)
        
        try:
            # Get current performance metrics
            metrics = await self.autonomous_tools._monitor_agent_performance(
                "24h", True
            )
            
            print("🎯 Agent Performance Summary:")
            
            if "current_metrics" in metrics:
                current = metrics["current_metrics"]
                print(f"   Total Executions: {current.get('total_executions', 0)}")
                print(f"   Success Rate: {current.get('success_rate', 0):.1f}%")
                print(f"   Average Response Time: {current.get('average_response_time', 0):.2f}s")
                
            if "tool_usage" in metrics:
                tool_usage = metrics["tool_usage"]
                print(f"\n🔧 Tool Usage Statistics:")
                for tool, count in list(tool_usage.items())[:5]:  # Top 5 tools
                    print(f"   - {tool}: {count} uses")
                    
            if "recommendations" in metrics:
                print(f"\n💡 Performance Recommendations:")
                for rec in metrics["recommendations"][:3]:  # Top 3 recommendations
                    print(f"   - {rec}")
                    
            return metrics
            
        except Exception as e:
            print(f"❌ Performance analysis failed: {e}")
            return {"status": "error", "error": str(e)}
            
    def save_workflow_results(self, results: Dict[str, Any]):
        """Save workflow results to file for analysis."""
        try:
            results_file = PROJECT_ROOT / "logs" / "production_workflow_results.json"
            results_file.parent.mkdir(exist_ok=True)
            
            # Add timestamp
            results["timestamp"] = time.time()
            results["execution_date"] = time.strftime("%Y-%m-%d %H:%M:%S")
            
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2)
                
            print(f"\n💾 Results saved to: {results_file}")
            
        except Exception as e:
            print(f"⚠️ Failed to save results: {e}")
            
    def run_all_workflows(self):
        """Execute all production workflows and collect results."""
        print("🎯 Starting Production Workflow Demonstration")
        print("=" * 60)
        
        results = {
            "workflows": {},
            "summary": {},
            "performance": {}
        }
        
        total_start_time = time.time()
        
        # Run each workflow
        workflows = [
            ("research", self.run_research_workflow),
            ("development", self.run_development_workflow), 
            ("content_analysis", self.run_content_analysis_workflow),
            ("multi_platform", self.run_multi_platform_workflow)
        ]
        
        successful_workflows = 0
        
        for workflow_name, workflow_func in workflows:
            try:
                result = workflow_func()
                results["workflows"][workflow_name] = result
                
                if result.get("status") == "success":
                    successful_workflows += 1
                    
            except Exception as e:
                print(f"❌ Workflow {workflow_name} failed: {e}")
                results["workflows"][workflow_name] = {"status": "error", "error": str(e)}
        
        # Performance analysis
        results["performance"] = self.run_performance_analysis()
        
        # Summary
        total_time = time.time() - total_start_time
        results["summary"] = {
            "total_workflows": len(workflows),
            "successful_workflows": successful_workflows,
            "success_rate": (successful_workflows / len(workflows)) * 100,
            "total_execution_time": total_time
        }
        
        print(f"\n🏆 PRODUCTION WORKFLOW SUMMARY")
        print("=" * 60)
        print(f"Total Workflows: {results['summary']['total_workflows']}")
        print(f"Successful: {results['summary']['successful_workflows']}")
        print(f"Success Rate: {results['summary']['success_rate']:.1f}%")
        print(f"Total Time: {results['summary']['total_execution_time']:.2f}s")
        
        # Save results
        self.save_workflow_results(results)
        
        return results


def main():
    """Main entry point for production workflow demonstration."""
    try:
        demonstrator = ProductionWorkflowDemonstrator()
        results = demonstrator.run_all_workflows()
        
        # Exit with appropriate code
        success_rate = results["summary"]["success_rate"]
        exit_code = 0 if success_rate >= 75 else 1
        
        print(f"\n{'✅' if exit_code == 0 else '❌'} Production workflows completed with {success_rate:.1f}% success rate")
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print("\n⚠️ Production workflow demonstration interrupted")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Critical error in production workflows: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
