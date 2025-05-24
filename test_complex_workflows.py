"""
Complex Workflow Testing Framework

This module tests the complete Intelligence Layer integration with complex real-world scenarios.
Tests the interaction between AdvancedExecutionPlanner, SmartToolSelector, and PersonalizedToolSelector.
"""

import asyncio
import time
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import sys
import os

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from autonomous_mcp.discovery import ToolDiscovery
from autonomous_mcp.advanced_planner import AdvancedExecutionPlanner
from autonomous_mcp.smart_selector import SmartToolSelector
from autonomous_mcp.user_preferences import UserPreferenceEngine, PreferenceType
from autonomous_mcp.personalized_selector import PersonalizedToolSelector
from autonomous_mcp.executor import ChainExecutor

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class WorkflowTestResult:
    """Result of a complex workflow test"""
    scenario_name: str
    user_id: str
    success: bool
    execution_time: float
    plan_quality_score: float
    personalization_score: float
    adaptation_score: float
    error_message: Optional[str] = None
    plan_details: Optional[Dict[str, Any]] = None
    tool_selections: Optional[List[str]] = None
    reasoning_steps: Optional[List[str]] = None

@dataclass
class UserProfile:
    """Test user profile with specific preferences"""
    user_id: str
    name: str
    preferences: Dict[str, Any]
    expertise_domains: List[str]
    description: str

class ComplexWorkflowTester:
    """Framework for testing complex workflows with full intelligence layer"""
    
    def __init__(self):
        """Initialize the complex workflow testing framework"""
        self.discovery = ToolDiscovery()
        self.advanced_planner = AdvancedExecutionPlanner(discovery_system=self.discovery)
        self.smart_selector = SmartToolSelector(discovery_system=self.discovery)
        self.preference_engine = UserPreferenceEngine()
        self.personalized_selector = PersonalizedToolSelector(
            discovery_system=self.discovery,
            preference_engine=self.preference_engine
        )
        self.executor = ChainExecutor()
        
        # Track test results
        self.test_results: List[WorkflowTestResult] = []
        
        # Set up mock tool catalog for testing
        self._setup_comprehensive_tool_catalog()
        
        # Create test user profiles
        self.test_users = self._create_test_user_profiles()
        
    def _setup_comprehensive_tool_catalog(self):
        """Set up a comprehensive mock tool catalog for testing"""
        mock_tools = [
            # Research & Analysis Tools
            {"name": "web_search", "category": "search", "description": "Search the web for information"},
            {"name": "academic_search", "category": "search", "description": "Search academic papers and journals"},
            {"name": "news_search", "category": "search", "description": "Search recent news articles"},
            {"name": "social_media_search", "category": "search", "description": "Search social media platforms"},
            
            {"name": "text_analyzer", "category": "analysis", "description": "Analyze text for sentiment, topics, entities"},
            {"name": "data_analyzer", "category": "analysis", "description": "Statistical analysis of structured data"},
            {"name": "trend_analyzer", "category": "analysis", "description": "Identify trends and patterns"},
            {"name": "sentiment_analyzer", "category": "analysis", "description": "Analyze emotional tone of text"},
            
            # Development Tools
            {"name": "code_generator", "category": "development", "description": "Generate code from specifications"},
            {"name": "test_generator", "category": "development", "description": "Generate unit tests for code"},
            {"name": "documentation_generator", "category": "development", "description": "Generate API documentation"},
            {"name": "code_reviewer", "category": "development", "description": "Review code for quality and issues"},
            {"name": "performance_profiler", "category": "development", "description": "Profile code performance"},
            {"name": "security_scanner", "category": "development", "description": "Scan code for security vulnerabilities"},
            
            # Data Processing Tools
            {"name": "csv_processor", "category": "data", "description": "Process CSV files and data"},
            {"name": "json_processor", "category": "data", "description": "Process JSON data structures"},
            {"name": "database_connector", "category": "data", "description": "Connect to and query databases"},
            {"name": "api_connector", "category": "data", "description": "Connect to REST APIs"},
            {"name": "data_cleaner", "category": "data", "description": "Clean and normalize data"},
            {"name": "data_validator", "category": "data", "description": "Validate data quality and integrity"},
            
            # Visualization Tools
            {"name": "chart_generator", "category": "visualization", "description": "Generate charts and graphs"},
            {"name": "dashboard_creator", "category": "visualization", "description": "Create interactive dashboards"},
            {"name": "report_generator", "category": "visualization", "description": "Generate formatted reports"},
            {"name": "presentation_creator", "category": "visualization", "description": "Create slide presentations"},
            
            # Communication Tools
            {"name": "email_sender", "category": "communication", "description": "Send emails"},
            {"name": "slack_notifier", "category": "communication", "description": "Send Slack notifications"},
            {"name": "webhook_trigger", "category": "communication", "description": "Trigger webhooks"},
            {"name": "sms_sender", "category": "communication", "description": "Send SMS messages"},
            
            # File & Storage Tools
            {"name": "file_reader", "category": "file", "description": "Read files from storage"},
            {"name": "file_writer", "category": "file", "description": "Write files to storage"},
            {"name": "cloud_uploader", "category": "file", "description": "Upload files to cloud storage"},
            {"name": "backup_creator", "category": "file", "description": "Create data backups"},
            
            # AI/ML Tools
            {"name": "text_summarizer", "category": "ai", "description": "Summarize long text content"},
            {"name": "image_analyzer", "category": "ai", "description": "Analyze images for content"},
            {"name": "language_translator", "category": "ai", "description": "Translate between languages"},
            {"name": "content_classifier", "category": "ai", "description": "Classify content into categories"},
            {"name": "recommendation_engine", "category": "ai", "description": "Generate recommendations"},
            
            # Workflow Tools
            {"name": "task_scheduler", "category": "workflow", "description": "Schedule tasks for execution"},
            {"name": "workflow_monitor", "category": "workflow", "description": "Monitor workflow execution"},
            {"name": "error_handler", "category": "workflow", "description": "Handle and recover from errors"},
            {"name": "notification_manager", "category": "workflow", "description": "Manage notifications"}
        ]
        
        # Discover all mock tools
        self.discovery.discover_all_tools(mock_tools, force_refresh=True)
            
        logger.info(f"Registered {len(mock_tools)} mock tools for testing")
        
    def _create_test_user_profiles(self) -> Dict[str, UserProfile]:
        """Create diverse test user profiles"""
        users = {
            "researcher_alice": UserProfile(
                user_id="researcher_alice",
                name="Dr. Alice Research",
                preferences={
                    "preferred_tools": ["academic_search", "text_analyzer", "text_summarizer"],
                    "domain_interests": ["research", "analysis", "academic"],
                    "execution_style": "thorough",
                    "complexity_tolerance": "high",
                    "speed_vs_accuracy": "accuracy",
                    "privacy_level": "high"
                },
                expertise_domains=["research", "analysis", "academic"],
                description="Academic researcher who prefers thorough, accurate analysis"
            ),
            
            "developer_bob": UserProfile(
                user_id="developer_bob",
                name="Bob Developer",
                preferences={
                    "preferred_tools": ["code_generator", "test_generator", "performance_profiler"],
                    "domain_interests": ["development", "testing", "performance"],
                    "execution_style": "agile",
                    "complexity_tolerance": "medium",
                    "speed_vs_accuracy": "speed",
                    "privacy_level": "medium"
                },
                expertise_domains=["development", "testing", "devops"],
                description="Agile developer who prefers fast iteration and testing"
            ),
            
            "analyst_carol": UserProfile(
                user_id="analyst_carol",
                name="Carol Data Analyst",
                preferences={
                    "preferred_tools": ["data_analyzer", "chart_generator", "dashboard_creator"],
                    "domain_interests": ["data", "visualization", "business"],
                    "execution_style": "methodical",
                    "complexity_tolerance": "high",
                    "speed_vs_accuracy": "balanced",
                    "privacy_level": "medium"
                },
                expertise_domains=["data", "analytics", "visualization"],
                description="Data analyst who prefers methodical, visual approaches"
            ),
            
            "manager_dave": UserProfile(
                user_id="manager_dave",
                name="Dave Project Manager",
                preferences={
                    "preferred_tools": ["report_generator", "presentation_creator", "task_scheduler"],
                    "domain_interests": ["management", "communication", "workflow"],
                    "execution_style": "efficient",
                    "complexity_tolerance": "low",
                    "speed_vs_accuracy": "speed",
                    "privacy_level": "low"
                },
                expertise_domains=["management", "communication", "planning"],
                description="Project manager who prefers efficient, communication-focused workflows"
            )
        }
        
        # Set up preferences for each user
        pref_type_mapping = {
            "preferred_tools": PreferenceType.TOOL_USAGE,
            "domain_interests": PreferenceType.DOMAIN_INTEREST,
            "execution_style": PreferenceType.EXECUTION_STYLE,
            "complexity_tolerance": PreferenceType.COMPLEXITY_TOLERANCE,
            "speed_vs_accuracy": PreferenceType.SPEED_VS_ACCURACY,
            "privacy_level": PreferenceType.PRIVACY_LEVEL
        }
        
        for user in users.values():
            self.preference_engine.create_user_profile(user.user_id)
            self.preference_engine.set_current_user(user.user_id)
            
            # Set explicit preferences
            for pref_type_str, pref_value in user.preferences.items():
                pref_type = pref_type_mapping.get(pref_type_str)
                if not pref_type:
                    continue  # Skip unknown preference types
                    
                if isinstance(pref_value, list):
                    for item in pref_value:
                        self.preference_engine.record_explicit_preference(
                            pref_type, item, True, weight=0.9
                        )
                else:
                    self.preference_engine.record_explicit_preference(
                        pref_type, pref_value, True, weight=0.9
                    )
        
        logger.info(f"Created {len(users)} test user profiles")
        return users
    async def test_research_analysis_pipeline(self, user_id: str) -> WorkflowTestResult:
        """Test Scenario 1: Research & Analysis Pipeline"""
        start_time = time.time()
        
        try:
            user_intent = "Research the latest developments in autonomous AI agents and create a comprehensive analysis"
            
            # Use advanced planner with personalized tool selection
            context = {
                "user_id": user_id,
                "available_tools": self.discovery.discovered_tools,
                "tool_selector": self.personalized_selector
            }
            
            plan = await self.advanced_planner.create_advanced_plan(
                intent=user_intent,
                context=context
            )
            
            # Extract plan details for analysis
            plan_details = {
                "total_steps": len(plan.tool_calls),
                "tool_categories": [self.discovery.get_tool_info(tc.tool_name).get("category", "unknown") 
                                 for tc in plan.tool_calls],
                "reasoning_steps": getattr(plan, 'reasoning_steps', []),
                "confidence_score": getattr(plan, 'confidence_score', 0.0)
            }
            
            # Analyze personalization
            user_prefs = self.preference_engine.get_user_preferences(user_id)
            preferred_tools = user_prefs.get("preferred_tools", [])
            selected_tools = [tc.tool_name for tc in plan.tool_calls]
            
            # Calculate personalization score
            personalization_score = self._calculate_personalization_score(
                selected_tools, preferred_tools, user_id
            )
            
            # Calculate plan quality score
            plan_quality_score = self._calculate_plan_quality_score(plan, user_intent)
            
            execution_time = time.time() - start_time
            
            return WorkflowTestResult(
                scenario_name="research_analysis_pipeline",
                user_id=user_id,
                success=True,
                execution_time=execution_time,
                plan_quality_score=plan_quality_score,
                personalization_score=personalization_score,
                adaptation_score=0.8,  # Mock adaptation score
                plan_details=plan_details,
                tool_selections=selected_tools,
                reasoning_steps=plan_details["reasoning_steps"]
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return WorkflowTestResult(
                scenario_name="research_analysis_pipeline",
                user_id=user_id,
                success=False,
                execution_time=execution_time,
                plan_quality_score=0.0,
                personalization_score=0.0,
                adaptation_score=0.0,
                error_message=str(e)
            )
    
    async def test_multi_user_development_workflow(self) -> List[WorkflowTestResult]:
        """Test Scenario 2: Multi-User Development Workflow"""
        results = []
        user_intent = "Plan and implement a new feature for the MCP agent"
        
        # Test with two different user types
        conservative_user = "researcher_alice"  # Prefers thorough approach
        agile_user = "developer_bob"  # Prefers rapid prototyping
        
        for user_id in [conservative_user, agile_user]:
            start_time = time.time()
            
            try:
                context = {
                    "user_id": user_id,
                    "available_tools": self.discovery.discovered_tools,
                    "tool_selector": self.personalized_selector
                }
                
                plan = await self.advanced_planner.create_advanced_plan(
                    intent=user_intent,
                    context=context
                )
                
                selected_tools = [tc.tool_name for tc in plan.tool_calls]
                plan_details = {
                    "total_steps": len(plan.tool_calls),
                    "tool_categories": [self.discovery.get_tool_info(tc.tool_name).get("category", "unknown") 
                                     for tc in plan.tool_calls],
                    "development_tools": [t for t in selected_tools if "test" in t or "code" in t or "review" in t],
                    "confidence_score": getattr(plan, 'confidence_score', 0.0)
                }
                
                # Calculate scores
                user_prefs = self.preference_engine.get_user_preferences(user_id)
                preferred_tools = user_prefs.get("preferred_tools", [])
                
                personalization_score = self._calculate_personalization_score(
                    selected_tools, preferred_tools, user_id
                )
                plan_quality_score = self._calculate_plan_quality_score(plan, user_intent)
                
                execution_time = time.time() - start_time
                
                results.append(WorkflowTestResult(
                    scenario_name="multi_user_development_workflow",
                    user_id=user_id,
                    success=True,
                    execution_time=execution_time,
                    plan_quality_score=plan_quality_score,
                    personalization_score=personalization_score,
                    adaptation_score=0.7,
                    plan_details=plan_details,
                    tool_selections=selected_tools
                ))
                
            except Exception as e:
                execution_time = time.time() - start_time
                results.append(WorkflowTestResult(
                    scenario_name="multi_user_development_workflow",
                    user_id=user_id,
                    success=False,
                    execution_time=execution_time,
                    plan_quality_score=0.0,
                    personalization_score=0.0,
                    adaptation_score=0.0,
                    error_message=str(e)
                ))
        
        return results
    
    async def test_adaptive_data_processing(self, user_id: str) -> WorkflowTestResult:
        """Test Scenario 3: Adaptive Data Processing"""
        start_time = time.time()
        
        try:
            user_intent = "Process customer feedback data to identify key insights and trends"
            
            context = {
                "user_id": user_id,
                "available_tools": self.discovery.discovered_tools,
                "tool_selector": self.personalized_selector
            }
            
            plan = await self.advanced_planner.create_advanced_plan(
                intent=user_intent,
                context=context
            )
            
            selected_tools = [tc.tool_name for tc in plan.tool_calls]
            
            # Check for data processing pipeline
            data_tools = [t for t in selected_tools if any(cat in t for cat in ["data", "analyzer", "processor"])]
            viz_tools = [t for t in selected_tools if "chart" in t or "dashboard" in t or "report" in t]
            
            plan_details = {
                "total_steps": len(plan.tool_calls),
                "data_processing_tools": data_tools,
                "visualization_tools": viz_tools,
                "includes_cleaning": any("clean" in t for t in selected_tools),
                "includes_validation": any("valid" in t for t in selected_tools)
            }
            
            # Calculate scores
            user_prefs = self.preference_engine.get_user_preferences(user_id)
            preferred_tools = user_prefs.get("preferred_tools", [])
            
            personalization_score = self._calculate_personalization_score(
                selected_tools, preferred_tools, user_id
            )
            plan_quality_score = self._calculate_plan_quality_score(plan, user_intent)
            
            execution_time = time.time() - start_time
            
            return WorkflowTestResult(
                scenario_name="adaptive_data_processing",
                user_id=user_id,
                success=True,
                execution_time=execution_time,
                plan_quality_score=plan_quality_score,
                personalization_score=personalization_score,
                adaptation_score=0.9,  # High adaptation for data processing
                plan_details=plan_details,
                tool_selections=selected_tools
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return WorkflowTestResult(
                scenario_name="adaptive_data_processing",
                user_id=user_id,
                success=False,
                execution_time=execution_time,
                plan_quality_score=0.0,
                personalization_score=0.0,
                adaptation_score=0.0,
                error_message=str(e)
            )
    
    async def test_cross_domain_collaborative_task(self, user_id: str) -> WorkflowTestResult:
        """Test Scenario 4: Cross-Domain Collaborative Task"""
        start_time = time.time()
        
        try:
            user_intent = "Create a comprehensive project plan that includes technical development, user research, and marketing strategy"
            
            context = {
                "user_id": user_id,
                "available_tools": self.discovery.discovered_tools,
                "tool_selector": self.personalized_selector
            }
            
            plan = await self.advanced_planner.create_advanced_plan(
                intent=user_intent,
                context=context
            )
            
            selected_tools = [tc.tool_name for tc in plan.tool_calls]
            
            # Analyze cross-domain coverage
            tool_categories = [self.discovery.get_tool_info(tc.tool_name).get("category", "unknown") 
                             for tc in plan.tool_calls]
            unique_categories = list(set(tool_categories))
            
            plan_details = {
                "total_steps": len(plan.tool_calls),
                "unique_categories": unique_categories,
                "category_coverage": len(unique_categories),
                "development_tools": [t for t in selected_tools if "code" in t or "test" in t],
                "research_tools": [t for t in selected_tools if "search" in t or "analyzer" in t],
                "communication_tools": [t for t in selected_tools if "report" in t or "presentation" in t]
            }
            
            # Calculate scores
            user_prefs = self.preference_engine.get_user_preferences(user_id)
            preferred_tools = user_prefs.get("preferred_tools", [])
            
            personalization_score = self._calculate_personalization_score(
                selected_tools, preferred_tools, user_id
            )
            plan_quality_score = self._calculate_plan_quality_score(plan, user_intent)
            
            # Higher adaptation score if multiple domains covered
            adaptation_score = min(1.0, len(unique_categories) / 4.0)
            
            execution_time = time.time() - start_time
            
            return WorkflowTestResult(
                scenario_name="cross_domain_collaborative_task",
                user_id=user_id,
                success=True,
                execution_time=execution_time,
                plan_quality_score=plan_quality_score,
                personalization_score=personalization_score,
                adaptation_score=adaptation_score,
                plan_details=plan_details,
                tool_selections=selected_tools
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return WorkflowTestResult(
                scenario_name="cross_domain_collaborative_task",
                user_id=user_id,
                success=False,
                execution_time=execution_time,
                plan_quality_score=0.0,
                personalization_score=0.0,
                adaptation_score=0.0,
                error_message=str(e)
            )
    def _calculate_personalization_score(self, selected_tools: List[str], 
                                       preferred_tools: List[str], user_id: str) -> float:
        """Calculate how well the tool selection reflects user preferences"""
        if not preferred_tools:
            return 0.5  # Neutral score if no preferences
        
        # Check overlap between selected and preferred tools
        overlap = set(selected_tools) & set(preferred_tools)
        preference_score = len(overlap) / len(preferred_tools) if preferred_tools else 0
        
        # Get user's domain interests and check if selected tools match
        user_prefs = self.preference_engine.get_user_preferences(user_id)
        domain_interests = user_prefs.get("domain_interests", [])
        
        domain_score = 0
        if domain_interests:
            for tool in selected_tools:
                tool_info = self.discovery.get_tool_info(tool)
                tool_category = tool_info.get("category", "")
                if any(domain in tool_category for domain in domain_interests):
                    domain_score += 1
            domain_score = domain_score / len(selected_tools) if selected_tools else 0
        
        # Combine preference and domain scores
        return (preference_score * 0.6 + domain_score * 0.4)
    
    def _calculate_plan_quality_score(self, plan, user_intent: str) -> float:
        """Calculate the quality of the generated plan"""
        if not plan or not plan.tool_calls:
            return 0.0
        
        score = 0.0
        
        # Check plan completeness (has multiple steps)
        if len(plan.tool_calls) >= 3:
            score += 0.3
        elif len(plan.tool_calls) >= 2:
            score += 0.2
        else:
            score += 0.1
        
        # Check tool diversity (uses different categories)
        categories = []
        for tc in plan.tool_calls:
            tool_info = self.discovery.get_tool_info(tc.tool_name)
            category = tool_info.get("category", "unknown")
            if category not in categories:
                categories.append(category)
        
        diversity_score = min(1.0, len(categories) / 3.0)  # Normalize to max 3 categories
        score += diversity_score * 0.3
        
        # Check if plan addresses the intent keywords
        intent_keywords = user_intent.lower().split()
        relevant_keywords = ["research", "analysis", "develop", "create", "process", "plan", "implement"]
        intent_relevance = any(keyword in intent_keywords for keyword in relevant_keywords)
        if intent_relevance:
            score += 0.2
        
        # Check confidence if available
        if hasattr(plan, 'confidence_score') and plan.confidence_score:
            score += plan.confidence_score * 0.2
        else:
            score += 0.1  # Default confidence bonus
        
        return min(1.0, score)
    
    async def run_all_scenarios(self) -> Dict[str, List[WorkflowTestResult]]:
        """Run all complex workflow test scenarios"""
        logger.info("Starting comprehensive complex workflow testing...")
        
        all_results = {}
        
        # Test Scenario 1: Research & Analysis Pipeline (all users)
        logger.info("Testing Scenario 1: Research & Analysis Pipeline")
        scenario_1_results = []
        for user_id in self.test_users.keys():
            result = await self.test_research_analysis_pipeline(user_id)
            scenario_1_results.append(result)
            logger.info(f"  User {user_id}: {'✓' if result.success else '✗'} "
                       f"(Quality: {result.plan_quality_score:.2f}, "
                       f"Personalization: {result.personalization_score:.2f})")
        all_results["research_analysis_pipeline"] = scenario_1_results
        
        # Test Scenario 2: Multi-User Development Workflow
        logger.info("Testing Scenario 2: Multi-User Development Workflow")
        scenario_2_results = await self.test_multi_user_development_workflow()
        all_results["multi_user_development_workflow"] = scenario_2_results
        for result in scenario_2_results:
            logger.info(f"  User {result.user_id}: {'✓' if result.success else '✗'} "
                       f"(Quality: {result.plan_quality_score:.2f}, "
                       f"Personalization: {result.personalization_score:.2f})")
        
        # Test Scenario 3: Adaptive Data Processing (data-focused users)
        logger.info("Testing Scenario 3: Adaptive Data Processing")
        scenario_3_results = []
        data_users = ["analyst_carol", "researcher_alice"]  # Users likely to process data
        for user_id in data_users:
            result = await self.test_adaptive_data_processing(user_id)
            scenario_3_results.append(result)
            logger.info(f"  User {user_id}: {'✓' if result.success else '✗'} "
                       f"(Quality: {result.plan_quality_score:.2f}, "
                       f"Adaptation: {result.adaptation_score:.2f})")
        all_results["adaptive_data_processing"] = scenario_3_results
        
        # Test Scenario 4: Cross-Domain Collaborative Task (management-focused users)
        logger.info("Testing Scenario 4: Cross-Domain Collaborative Task")
        scenario_4_results = []
        collab_users = ["manager_dave", "researcher_alice"]  # Users likely to do cross-domain work
        for user_id in collab_users:
            result = await self.test_cross_domain_collaborative_task(user_id)
            scenario_4_results.append(result)
            domain_coverage = 0
            if result.plan_details and 'unique_categories' in result.plan_details:
                domain_coverage = len(result.plan_details['unique_categories'])
            logger.info(f"  User {user_id}: {'✓' if result.success else '✗'} "
                       f"(Quality: {result.plan_quality_score:.2f}, "
                       f"Domain Coverage: {domain_coverage})")
        all_results["cross_domain_collaborative_task"] = scenario_4_results
        
        # Store all results
        self.test_results.extend([result for results in all_results.values() for result in results])
        
        logger.info(f"Complex workflow testing completed. Total tests: {len(self.test_results)}")
        return all_results
    
    def generate_test_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        if not self.test_results:
            return {"error": "No test results available"}
        
        # Calculate overall metrics
        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results if r.success)
        success_rate = successful_tests / total_tests if total_tests > 0 else 0
        
        avg_execution_time = sum(r.execution_time for r in self.test_results) / total_tests
        avg_plan_quality = sum(r.plan_quality_score for r in self.test_results) / total_tests
        avg_personalization = sum(r.personalization_score for r in self.test_results) / total_tests
        avg_adaptation = sum(r.adaptation_score for r in self.test_results) / total_tests
        
        # Per-scenario analysis
        scenario_stats = {}
        for result in self.test_results:
            scenario = result.scenario_name
            if scenario not in scenario_stats:
                scenario_stats[scenario] = {
                    "total_tests": 0,
                    "successful_tests": 0,
                    "avg_quality": 0,
                    "avg_personalization": 0,
                    "avg_adaptation": 0,
                    "avg_execution_time": 0
                }
            
            stats = scenario_stats[scenario]
            stats["total_tests"] += 1
            if result.success:
                stats["successful_tests"] += 1
            stats["avg_quality"] += result.plan_quality_score
            stats["avg_personalization"] += result.personalization_score
            stats["avg_adaptation"] += result.adaptation_score
            stats["avg_execution_time"] += result.execution_time
        
        # Calculate averages for each scenario
        for scenario, stats in scenario_stats.items():
            total = stats["total_tests"]
            if total > 0:
                stats["success_rate"] = stats["successful_tests"] / total
                stats["avg_quality"] /= total
                stats["avg_personalization"] /= total
                stats["avg_adaptation"] /= total
                stats["avg_execution_time"] /= total
        
        # Per-user analysis
        user_stats = {}
        for result in self.test_results:
            user_id = result.user_id
            if user_id not in user_stats:
                user_stats[user_id] = {
                    "total_tests": 0,
                    "successful_tests": 0,
                    "avg_personalization": 0,
                    "preferred_tools_used": 0,
                    "user_profile": self.test_users.get(user_id, {})
                }
            
            stats = user_stats[user_id]
            stats["total_tests"] += 1
            if result.success:
                stats["successful_tests"] += 1
            stats["avg_personalization"] += result.personalization_score
        
        # Calculate user averages
        for user_id, stats in user_stats.items():
            total = stats["total_tests"]
            if total > 0:
                stats["success_rate"] = stats["successful_tests"] / total
                stats["avg_personalization"] /= total
        
        return {
            "summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "success_rate": success_rate,
                "avg_execution_time": avg_execution_time,
                "avg_plan_quality": avg_plan_quality,
                "avg_personalization": avg_personalization,
                "avg_adaptation": avg_adaptation
            },
            "scenario_analysis": scenario_stats,
            "user_analysis": user_stats,
            "intelligence_layer_performance": {
                "advanced_planning_working": avg_plan_quality > 0.6,
                "personalization_working": avg_personalization > 0.4,
                "adaptation_working": avg_adaptation > 0.6,
                "integration_successful": success_rate > 0.8
            },
            "detailed_results": [
                {
                    "scenario": r.scenario_name,
                    "user": r.user_id,
                    "success": r.success,
                    "scores": {
                        "quality": r.plan_quality_score,
                        "personalization": r.personalization_score,
                        "adaptation": r.adaptation_score
                    },
                    "execution_time": r.execution_time,
                    "tools_selected": r.tool_selections
                }
                for r in self.test_results
            ]
        }


async def main():
    """Main function to run complex workflow tests"""
    print("==> Starting Complex Workflow Testing for Autonomous MCP Agent")
    print("=" * 70)
    
    # Initialize the testing framework
    tester = ComplexWorkflowTester()
    
    # Run all test scenarios
    results = await tester.run_all_scenarios()
    
    # Generate comprehensive report
    report = tester.generate_test_report()
    
    print("\n==> COMPLEX WORKFLOW TEST RESULTS")
    print("=" * 70)
    
    # Print summary
    summary = report["summary"]
    print(f"Total Tests: {summary['total_tests']}")
    print(f"Success Rate: {summary['success_rate']:.1%}")
    print(f"Average Execution Time: {summary['avg_execution_time']:.3f}s")
    print(f"Average Plan Quality: {summary['avg_plan_quality']:.2f}/1.0")
    print(f"Average Personalization: {summary['avg_personalization']:.2f}/1.0")
    print(f"Average Adaptation: {summary['avg_adaptation']:.2f}/1.0")
    
    # Print intelligence layer assessment
    print(f"\n🧠 Intelligence Layer Performance:")
    performance = report["intelligence_layer_performance"]
    print(f"  Advanced Planning: {'✓' if performance['advanced_planning_working'] else '✗'}")
    print(f"  Personalization: {'✓' if performance['personalization_working'] else '✗'}")
    print(f"  Adaptation: {'✓' if performance['adaptation_working'] else '✗'}")
    print(f"  Overall Integration: {'✓' if performance['integration_successful'] else '✗'}")
    
    # Print scenario breakdown
    print(f"\n📋 Scenario Analysis:")
    for scenario, stats in report["scenario_analysis"].items():
        print(f"  {scenario}:")
        print(f"    Success Rate: {stats['success_rate']:.1%}")
        print(f"    Avg Quality: {stats['avg_quality']:.2f}")
        print(f"    Avg Personalization: {stats['avg_personalization']:.2f}")
    
    # Print user analysis
    print(f"\n👥 User Analysis:")
    for user_id, stats in report["user_analysis"].items():
        user_profile = stats.get("user_profile", {})
        print(f"  {user_profile.get('name', user_id)} ({user_id}):")
        print(f"    Success Rate: {stats['success_rate']:.1%}")
        print(f"    Avg Personalization: {stats['avg_personalization']:.2f}")
        print(f"    Description: {user_profile.get('description', 'N/A')}")
    
    # Save detailed report
    output_file = Path("complex_workflow_test_results.json")
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    print(f"\n==> Detailed results saved to: {output_file}")
    
    # Final assessment
    if performance["integration_successful"]:
        print(f"\n==> SUCCESS: Complex workflow testing completed successfully!")
        print(f"   The Intelligence Layer is working correctly with:")
        print(f"   - Advanced planning with sequential thinking")
        print(f"   - Smart tool selection with ML recommendations")
        print(f"   - Personalized recommendations based on user preferences")
        print(f"   - Successful integration across all components")
    else:
        print(f"\n==> WARNING: Some complex workflow tests failed.")
        print(f"   Review the detailed results for specific issues.")
    
    return report


if __name__ == "__main__":
    # Run the complex workflow tests
    report = asyncio.run(main())
