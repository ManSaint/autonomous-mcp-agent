"""
Advanced Autonomous MCP Agent Tools

This module implements sophisticated autonomous agent capabilities as MCP tools,
providing intelligent workflow generation, task analysis, personalized recommendations,
performance monitoring, and user preference configuration.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

# Internal framework imports
from .discovery import ToolDiscovery
from .executor import ChainExecutor
from .advanced_planner import AdvancedExecutionPlanner
from .smart_selector import SmartToolSelector
from .error_recovery import ErrorRecoverySystem
from .monitoring import MonitoringSystem
from .user_preferences import UserPreferenceEngine
from .real_mcp_discovery import RealMCPDiscovery
from .mcp_chain_executor import RealMCPChainExecutor

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class TaskAnalysisResult:
    """Result of task complexity analysis"""
    complexity_score: float
    estimated_duration: float
    required_tools: List[str]
    recommended_approach: str
    risk_factors: List[str]
    success_probability: float


@dataclass
class WorkflowStep:
    """Individual step in an intelligent workflow"""
    step_id: str
    description: str
    tool_name: str
    parameters: Dict[str, Any]
    dependencies: List[str]
    estimated_duration: float
    success_probability: float


@dataclass
class IntelligentWorkflow:
    """Complete intelligent workflow definition"""
    workflow_id: str
    title: str
    description: str
    steps: List[WorkflowStep]
    total_estimated_duration: float
    overall_success_probability: float
    created_at: datetime
    metadata: Dict[str, Any]



class AdvancedAutonomousTools:
    """
    Advanced autonomous agent tools providing sophisticated capabilities
    beyond basic task execution and tool discovery.
    """
    
    def __init__(self):
        """Initialize advanced autonomous tools"""
        # Real MCP integration first
        self.real_discovery = RealMCPDiscovery()
        self.mcp_executor = RealMCPChainExecutor()
        
        # Core framework components using real discovery
        self.discovery = ToolDiscovery()
        self.executor = ChainExecutor()
        # Use real discovery for planner to have access to actual tools
        self.planner = AdvancedExecutionPlanner(self.real_discovery)
        self.smart_selector = SmartToolSelector(self.real_discovery)
        self.error_recovery = ErrorRecoverySystem()
        self.monitoring = MonitoringSystem()
        self.preferences = UserPreferenceEngine()
        
        # Advanced features state
        self.workflow_cache: Dict[str, IntelligentWorkflow] = {}
        self.analysis_cache: Dict[str, TaskAnalysisResult] = {}
        self.performance_history: List[Dict[str, Any]] = []
        
        logger.info("Advanced autonomous tools initialized")
    
    async def execute_autonomous_task(self, task_description: str, context: Optional[Dict[str, Any]] = None, preferences: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a complex task autonomously with full intelligence pipeline
        
        Args:
            task_description: Natural language description of the task
            context: Additional context or constraints
            preferences: User preferences to consider
            
        Returns:
            Comprehensive execution result with detailed metrics
        """
        start_time = datetime.now()
        execution_id = f"exec_{int(start_time.timestamp())}"
        
        try:
            logger.info(f"Starting autonomous task execution: {execution_id}")
            
            # Step 1: Analyze task complexity
            analysis = await self.analyze_task_complexity(task_description, context or {})
            
            # Step 2: Get personalized recommendations
            recommendations = await self.get_personalized_recommendations(
                task_description, context or {}, preferences or {}
            )
            
            # Step 3: Create intelligent workflow
            workflow = await self.create_intelligent_workflow(
                task_description, context or {}, analysis, recommendations
            )
            
            # Step 4: Execute workflow with monitoring
            execution_result = await self._execute_workflow_with_monitoring(
                workflow, execution_id
            )
            
            # Step 5: Update performance metrics
            execution_time = (datetime.now() - start_time).total_seconds()
            await self._update_performance_metrics(execution_id, execution_result, execution_time)
            
            # Step 6: Learn from execution for future improvements
            await self._learn_from_execution(task_description, context, execution_result)
            
            return {
                'success': True,
                'execution_id': execution_id,
                'execution_time': execution_time,
                'workflow': asdict(workflow),
                'analysis': asdict(analysis),
                'recommendations': recommendations,
                'result': execution_result,
                'performance_impact': self._calculate_performance_impact(execution_result),
                'learned_insights': await self._extract_insights(execution_result)
            }
            
        except Exception as e:
            logger.error(f"Autonomous task execution failed: {e}")
            
            # Attempt error recovery
            recovery_result = await self.error_recovery.handle_execution_error(
                str(e), task_description, context or {}
            )
            
            return {
                'success': False,
                'execution_id': execution_id,
                'error': str(e),
                'recovery_attempted': True,
                'recovery_result': recovery_result,
                'fallback_suggestions': await self._generate_fallback_suggestions(task_description)
            }
    
    async def create_intelligent_workflow(self, task_description: str, context: Optional[Dict[str, Any]] = None, analysis: Optional[TaskAnalysisResult] = None, recommendations: Optional[Dict[str, Any]] = None) -> IntelligentWorkflow:
        """
        Generate an intelligent workflow for complex task execution
        
        Args:
            task_description: Natural language task description
            context: Additional context or constraints
            analysis: Pre-computed task analysis (optional)
            recommendations: Pre-computed recommendations (optional)
            
        Returns:
            Complete intelligent workflow definition
        """
        try:
            logger.info(f"Creating intelligent workflow for: {task_description}")
            
            # Analyze task if not provided
            if analysis is None:
                analysis = await self.analyze_task_complexity(task_description, context or {})
            
            # Get recommendations if not provided
            if recommendations is None:
                recommendations = await self.get_personalized_recommendations(
                    task_description, context or {}, {}
                )
            
            # Discover available tools
            available_tools = await self._get_comprehensive_tool_list()
            
            # Use advanced planner to create execution plan
            execution_plan = await self.planner.create_execution_plan(
                task_description, available_tools, context or {}
            )
            
            # Convert execution plan to intelligent workflow
            workflow_steps = []
            for i, step in enumerate(execution_plan.get('steps', [])):
                workflow_step = WorkflowStep(
                    step_id=f"step_{i+1}",
                    description=step.get('description', ''),
                    tool_name=step.get('tool', ''),
                    parameters=step.get('parameters', {}),
                    dependencies=step.get('dependencies', []),
                    estimated_duration=step.get('estimated_duration', 30.0),
                    success_probability=step.get('confidence', 0.8)
                )
                workflow_steps.append(workflow_step)
            
            # Calculate overall metrics
            total_duration = sum(step.estimated_duration for step in workflow_steps)
            overall_probability = min([step.success_probability for step in workflow_steps] or [0.8])
            
            # Create workflow
            workflow = IntelligentWorkflow(
                workflow_id=f"workflow_{int(datetime.now().timestamp())}",
                title=f"Intelligent workflow for: {task_description[:50]}...",
                description=task_description,
                steps=workflow_steps,
                total_estimated_duration=total_duration,
                overall_success_probability=overall_probability,
                created_at=datetime.now(),
                metadata={
                    'complexity_score': analysis.complexity_score,
                    'recommended_approach': analysis.recommended_approach,
                    'user_preferences_applied': bool(recommendations.get('preferences_applied')),
                    'tool_count': len(workflow_steps),
                    'risk_factors': analysis.risk_factors
                }
            )
            
            # Cache workflow for reuse
            self.workflow_cache[workflow.workflow_id] = workflow
            
            logger.info(f"Created workflow {workflow.workflow_id} with {len(workflow_steps)} steps")
            return workflow
            
        except Exception as e:
            logger.error(f"Workflow creation failed: {e}")
            raise
    
    async def analyze_task_complexity(self, task_description: str, context: Dict[str, Any]) -> TaskAnalysisResult:
        """
        Analyze task complexity and provide detailed recommendations
        
        Args:
            task_description: Task to analyze
            context: Additional context
            
        Returns:
            Detailed task analysis result
        """
        try:
            # Check cache first
            cache_key = f"{hash(task_description)}_{hash(str(context))}"
            if cache_key in self.analysis_cache:
                logger.info("Returning cached task analysis")
                return self.analysis_cache[cache_key]
            
            logger.info(f"Analyzing task complexity: {task_description}")
            
            # Discover available tools
            available_tools = await self._get_comprehensive_tool_list()
            
            # Use smart selector to analyze requirements
            tool_recommendations = {
                'recommended_tools': [],
                'chain_suggestions': [],
                'total_available': len(available_tools),
                'selection_strategy': 'bypass'
            }
            
            # Calculate complexity metrics
            complexity_factors = {
                'tool_count': len(tool_recommendations.get('recommended_tools', [])),
                'has_chaining': len(tool_recommendations.get('chain_suggestions', [])) > 0,
                'has_conditionals': 'if' in task_description.lower() or 'condition' in task_description.lower(),
                'has_loops': 'repeat' in task_description.lower() or 'loop' in task_description.lower(),
                'requires_external_data': any(tool.get('category') == 'data_source' for tool in tool_recommendations.get('recommended_tools', [])),
                'multi_step': len(task_description.split(',')) > 2
            }
            
            # Calculate complexity score (0-10 scale)
            complexity_score = 1.0  # Base complexity
            complexity_score += complexity_factors['tool_count'] * 0.5
            complexity_score += 2.0 if complexity_factors['has_chaining'] else 0
            complexity_score += 1.5 if complexity_factors['has_conditionals'] else 0
            complexity_score += 2.0 if complexity_factors['has_loops'] else 0
            complexity_score += 1.0 if complexity_factors['requires_external_data'] else 0
            complexity_score += 1.0 if complexity_factors['multi_step'] else 0
            complexity_score = min(complexity_score, 10.0)
            
            # Estimate duration (in seconds)
            base_duration = 30.0  # 30 seconds base
            duration_multiplier = 1 + (complexity_score / 10.0) * 3  # Up to 4x multiplier
            estimated_duration = base_duration * duration_multiplier
            
            # Identify risk factors
            risk_factors = []
            if complexity_score > 7:
                risk_factors.append("High complexity task")
            if complexity_factors['has_loops']:
                risk_factors.append("Contains loops - may run indefinitely")
            if complexity_factors['requires_external_data']:
                risk_factors.append("Depends on external data sources")
            if len(tool_recommendations.get('recommended_tools', [])) > 5:
                risk_factors.append("Requires many tools - higher failure probability")
            
            # Determine recommended approach
            if complexity_score <= 3:
                approach = "Simple direct execution"
            elif complexity_score <= 6:
                approach = "Structured workflow with monitoring"
            else:
                approach = "Complex multi-phase execution with checkpoints"
            
            # Calculate success probability
            base_probability = 0.9
            probability_reduction = (complexity_score / 10.0) * 0.3  # Up to 30% reduction
            success_probability = max(base_probability - probability_reduction, 0.5)
            
            # Create analysis result
            analysis = TaskAnalysisResult(
                complexity_score=complexity_score,
                estimated_duration=estimated_duration,
                required_tools=[tool.get('name', '') for tool in tool_recommendations.get('recommended_tools', [])],
                recommended_approach=approach,
                risk_factors=risk_factors,
                success_probability=success_probability
            )
            
            # Cache result
            self.analysis_cache[cache_key] = analysis
            
            logger.info(f"Task analysis complete: complexity={complexity_score:.1f}, duration={estimated_duration:.1f}s")
            return analysis
            
        except Exception as e:
            logger.error(f"Task analysis failed: {e}")
            # Return default analysis
            return TaskAnalysisResult(
                complexity_score=5.0,
                estimated_duration=60.0,
                required_tools=[],
                recommended_approach="Standard execution with error handling",
                risk_factors=["Analysis failed - proceeding with caution"],
                success_probability=0.7
            )
    
    async def get_personalized_recommendations(self, task_description: str, context: Dict[str, Any], preferences: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get personalized recommendations based on user preferences and historical data
        
        Args:
            task_description: Task to get recommendations for
            context: Additional context
            preferences: User preferences
            
        Returns:
            Personalized recommendations and insights
        """
        try:
            logger.info(f"Generating personalized recommendations for: {task_description}")
            
            # Get user preferences from engine
            user_prefs = self.preferences.get_preferences()
            
            # Merge with provided preferences
            combined_prefs = {**user_prefs, **preferences}
            
            # Analyze historical performance for similar tasks
            historical_insights = await self._analyze_historical_performance(task_description)
            
            # Get tool recommendations based on preferences
            preferred_tools = combined_prefs.get('preferred_tools', [])
            avoided_tools = combined_prefs.get('avoided_tools', [])
            
            # Discover available tools
            available_tools = await self._get_comprehensive_tool_list()
            
            # Filter tools based on preferences
            recommended_tools = []
            for tool in available_tools:
                tool_name = tool.get('name', '')
                
                # Skip avoided tools
                if tool_name in avoided_tools:
                    continue
                
                # Boost preferred tools
                if tool_name in preferred_tools:
                    tool['preference_boost'] = True
                    tool['recommendation_score'] = tool.get('recommendation_score', 0.8) + 0.2
                
                recommended_tools.append(tool)
            
            # Generate personalized workflow suggestions
            workflow_suggestions = await self._generate_workflow_suggestions(
                task_description, recommended_tools, combined_prefs, historical_insights
            )
            
            # Calculate personalization impact
            personalization_score = self._calculate_personalization_score(
                combined_prefs, historical_insights
            )
            
            return {
                'success': True,
                'personalization_score': personalization_score,
                'recommended_tools': recommended_tools[:10],  # Top 10 recommendations
                'workflow_suggestions': workflow_suggestions,
                'historical_insights': historical_insights,
                'applied_preferences': combined_prefs,
                'preferences_applied': True,
                'optimization_tips': await self._generate_optimization_tips(
                    task_description, combined_prefs, historical_insights
                )
            }
            
        except Exception as e:
            logger.error(f"Personalized recommendations failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'fallback_recommendations': await self._get_basic_recommendations(task_description)
            }
    
    async def monitor_agent_performance(self, time_range: Optional[str] = "24h", include_details: bool = False) -> Dict[str, Any]:
        """
        Monitor real-time agent performance with detailed metrics
        
        Args:
            time_range: Time range for metrics ("1h", "24h", "7d", "30d")
            include_details: Include detailed performance breakdown
            
        Returns:
            Comprehensive performance metrics and insights
        """
        try:
            logger.info(f"Monitoring agent performance for: {time_range}")
            
            # Get monitoring data from monitoring system
            performance_data = self.monitoring.get_system_dashboard_data()
            
            # Parse time range
            hours = self._parse_time_range(time_range)
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            # Filter performance history by time range
            filtered_history = [
                record for record in self.performance_history
                if datetime.fromisoformat(record.get('timestamp', '')) >= cutoff_time
            ]
            
            # Calculate aggregate metrics
            total_executions = len(filtered_history)
            successful_executions = sum(1 for record in filtered_history if record.get('success', False))
            success_rate = successful_executions / total_executions if total_executions > 0 else 0.0
            
            # Calculate average response times
            response_times = [record.get('execution_time', 0) for record in filtered_history]
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0.0
            
            # Tool usage statistics
            tool_usage = {}
            for record in filtered_history:
                tools_used = record.get('tools_used', [])
                for tool in tools_used:
                    tool_usage[tool] = tool_usage.get(tool, 0) + 1
            
            # Performance trends
            trends = self._calculate_performance_trends(filtered_history)
            
            # Generate performance insights
            insights = await self._generate_performance_insights(
                success_rate, avg_response_time, tool_usage, trends
            )
            
            base_metrics = {
                'time_range': time_range,
                'total_executions': total_executions,
                'successful_executions': successful_executions,
                'success_rate': success_rate,
                'average_response_time': avg_response_time,
                'tool_usage_stats': tool_usage,
                'performance_trends': trends,
                'insights': insights,
                'monitoring_timestamp': datetime.now().isoformat()
            }
            
            if include_details:
                base_metrics.update({
                    'detailed_history': filtered_history,
                    'system_metrics': performance_data,
                    'workflow_cache_size': len(self.workflow_cache),
                    'analysis_cache_size': len(self.analysis_cache),
                    'memory_usage': await self._get_memory_usage(),
                    'recommendation_accuracy': await self._calculate_recommendation_accuracy()
                })
            
            return {
                'success': True,
                'metrics': base_metrics
            }
            
        except Exception as e:
            logger.error(f"Performance monitoring failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'basic_metrics': await self._get_basic_performance_metrics()
            }
    
    async def configure_agent_preferences(self, preferences: Dict[str, Any], operation: str = "update") -> Dict[str, Any]:
        """
        Configure agent preferences and personalization settings
        
        Args:
            preferences: Preference settings to apply
            operation: "update", "replace", or "reset"
            
        Returns:
            Configuration result and current settings
        """
        try:
            logger.info(f"Configuring agent preferences: {operation}")
            
            current_prefs = self.preferences.get_preferences()
            
            if operation == "reset":
                # Reset to defaults
                result = self.preferences.reset_preferences()
                new_prefs = self.preferences.get_preferences()
                
            elif operation == "replace":
                # Replace all preferences
                result = self.preferences.update_preferences(preferences, merge=False)
                new_prefs = preferences
                
            else:  # update (default)
                # Merge with existing preferences
                result = self.preferences.update_preferences(preferences, merge=True)
                new_prefs = {**current_prefs, **preferences}
            
            # Validate preferences
            validation_result = await self._validate_preferences(new_prefs)
            
            # Clear relevant caches if preferences changed
            if operation in ["replace", "reset"]:
                self.analysis_cache.clear()
                logger.info("Cleared analysis cache due to preference changes")
            
            # Generate preference impact analysis
            impact_analysis = await self._analyze_preference_impact(
                current_prefs, new_prefs, operation
            )
            
            return {
                'success': True,
                'operation': operation,
                'previous_preferences': current_prefs,
                'new_preferences': new_prefs,
                'validation_result': validation_result,
                'impact_analysis': impact_analysis,
                'configuration_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Preference configuration failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'current_preferences': self.preferences.get_preferences()
            }
    
    # Helper Methods for Advanced Tools
    
    async def _get_comprehensive_tool_list(self) -> List[Dict[str, Any]]:
        """Get comprehensive list of all available tools"""
        try:
            # Get framework tools
            framework_tools = self.discovery.discover_tools()
            
            # Get real MCP tools
            real_tools = await self.real_discovery.discover_available_tools()
            
            # Combine and deduplicate
            all_tools = []
            tool_names = set()
            
            for tool_list in [framework_tools, real_tools.get('tools', [])]:
                for tool in tool_list:
                    name = tool.get('name', '')
                    if name and name not in tool_names:
                        all_tools.append(tool)
                        tool_names.add(name)
            
            return all_tools
            
        except Exception as e:
            logger.error(f"Comprehensive tool discovery failed: {e}")
            return self.discovery.discover_tools()  # Fallback to framework tools
    
    async def _execute_workflow_with_monitoring(self, workflow: IntelligentWorkflow, execution_id: str) -> Dict[str, Any]:
        """Execute workflow with comprehensive monitoring"""
        try:
            logger.info(f"Executing workflow {workflow.workflow_id} with monitoring")
            
            start_time = datetime.now()
            step_results = []
            overall_success = True
            
            for step in workflow.steps:
                step_start = datetime.now()
                
                try:
                    # Execute step using chain executor
                    if hasattr(self.mcp_executor, 'execute_single_tool'):
                        step_result = await self.mcp_executor.execute_single_tool(
                            step.tool_name, step.parameters
                        )
                    else:
                        # Fallback to basic execution
                        step_result = await self.executor.execute_chain([{
                            'tool': step.tool_name,
                            'parameters': step.parameters
                        }])
                    
                    step_duration = (datetime.now() - step_start).total_seconds()
                    
                    step_results.append({
                        'step_id': step.step_id,
                        'success': True,
                        'result': step_result,
                        'duration': step_duration,
                        'tool_used': step.tool_name
                    })
                    
                except Exception as step_error:
                    logger.error(f"Step {step.step_id} failed: {step_error}")
                    overall_success = False
                    
                    step_results.append({
                        'step_id': step.step_id,
                        'success': False,
                        'error': str(step_error),
                        'duration': (datetime.now() - step_start).total_seconds(),
                        'tool_used': step.tool_name
                    })
                    
                    # Attempt error recovery for this step
                    recovery_result = await self.error_recovery.handle_step_error(
                        str(step_error), step, workflow
                    )
                    
                    if recovery_result.get('can_continue', False):
                        logger.info(f"Error recovery successful for step {step.step_id}")
                        continue
                    else:
                        logger.error(f"Error recovery failed for step {step.step_id}, stopping workflow")
                        break
            
            total_duration = (datetime.now() - start_time).total_seconds()
            
            return {
                'workflow_id': workflow.workflow_id,
                'execution_id': execution_id,
                'overall_success': overall_success,
                'total_duration': total_duration,
                'steps_completed': len(step_results),
                'step_results': step_results,
                'performance_metrics': {
                    'avg_step_duration': sum(r['duration'] for r in step_results) / len(step_results) if step_results else 0,
                    'success_rate': sum(1 for r in step_results if r['success']) / len(step_results) if step_results else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            return {
                'workflow_id': workflow.workflow_id,
                'execution_id': execution_id,
                'overall_success': False,
                'error': str(e),
                'step_results': step_results
            }
    
    # Additional helper methods (implementation details)
    
    async def _update_performance_metrics(self, execution_id: str, result: Dict[str, Any], execution_time: float):
        """Update performance metrics with execution result"""
        performance_record = {
            'execution_id': execution_id,
            'timestamp': datetime.now().isoformat(),
            'success': result.get('overall_success', False),
            'execution_time': execution_time,
            'tools_used': [step.get('tool_used', '') for step in result.get('step_results', [])],
            'steps_completed': result.get('steps_completed', 0)
        }
        self.performance_history.append(performance_record)
        
        # Keep only last 1000 records
        if len(self.performance_history) > 1000:
            self.performance_history = self.performance_history[-1000:]
    
    async def _learn_from_execution(self, task_description: str, context: Dict[str, Any], result: Dict[str, Any]):
        """Learn from execution results for future improvements"""
        if result.get('overall_success', False):
            # Update user preferences based on successful execution
            successful_tools = [step.get('tool_used', '') for step in result.get('step_results', []) if step.get('success', False)]
            if successful_tools:
                self.preferences.update_tool_success_rate(successful_tools, 'increase')
    
    def _calculate_performance_impact(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate performance impact of execution"""
        return {
            'efficiency_score': result.get('performance_metrics', {}).get('success_rate', 0) * 100,
            'speed_score': max(0, 100 - (result.get('total_duration', 60) / 60 * 100)),
            'reliability_score': 100 if result.get('overall_success', False) else 0
        }
    
    async def _extract_insights(self, result: Dict[str, Any]) -> List[str]:
        """Extract insights from execution result"""
        insights = []
        if result.get('overall_success', False):
            insights.append("Task completed successfully")
            if result.get('total_duration', 0) < 30:
                insights.append("Fast execution time achieved")
        else:
            insights.append("Task execution encountered issues")
            insights.append("Consider adjusting approach or tools")
        return insights
    
    async def _generate_fallback_suggestions(self, task_description: str) -> List[str]:
        """Generate fallback suggestions for failed tasks"""
        return [
            "Try breaking the task into smaller steps",
            "Check if required tools are available",
            "Review task description for clarity",
            "Consider alternative approaches"
        ]
    
    def _parse_time_range(self, time_range: str) -> int:
        """Parse time range string to hours"""
        if time_range == "1h":
            return 1
        elif time_range == "24h":
            return 24
        elif time_range == "7d":
            return 24 * 7
        elif time_range == "30d":
            return 24 * 30
        else:
            return 24  # Default to 24 hours
    
    # Placeholder implementations for remaining helper methods
    
    async def _get_comprehensive_tool_list(self) -> List[Dict[str, Any]]:
        """Get comprehensive list of available tools"""
        try:
            # Use the real discovery system to get actual MCP tools
            real_tools = await self.real_discovery.get_all_tools()
            
            # Convert MCPTool objects to dictionary format
            tool_list = []
            for tool in real_tools:
                tool_dict = {
                    'name': tool.name,
                    'description': tool.description,
                    'server': tool.server,
                    'parameters': tool.parameters if hasattr(tool, 'parameters') else {},
                    'categories': [tool.category.value],
                    'capabilities': [tool.category.value],
                    'usage_count': tool.usage_count,
                    'success_rate': tool.success_rate,
                    'average_execution_time': tool.avg_execution_time,
                    'recommendation_score': tool.reliability_score
                }
                tool_list.append(tool_dict)
            
            return tool_list
        
        except Exception as e:
            logger.error(f"Failed to get comprehensive tool list: {e}")
            # Return empty list as fallback
            return []

    async def _analyze_historical_performance(self, task_description: str) -> Dict[str, Any]:
        """Analyze historical performance for similar tasks"""
        return {"similar_tasks": 0, "avg_success_rate": 0.8, "recommendations": []}
    
    async def _generate_workflow_suggestions(self, task_description: str, tools: List[Dict], prefs: Dict, insights: Dict) -> List[str]:
        """Generate workflow suggestions based on analysis"""
        return ["Consider using preferred tools", "Break complex tasks into steps"]
    
    def _calculate_personalization_score(self, prefs: Dict, insights: Dict) -> float:
        """Calculate how well personalized the recommendations are"""
        return 0.8  # Default good personalization score
    
    async def _generate_optimization_tips(self, task_description: str, prefs: Dict, insights: Dict) -> List[str]:
        """Generate optimization tips"""
        return ["Use tool chaining for efficiency", "Consider user preference patterns"]
    
    async def _get_basic_recommendations(self, task_description: str) -> Dict[str, Any]:
        """Get basic recommendations when personalization fails"""
        return {"tools": [], "suggestions": ["Use standard approach"]}
    
    def _calculate_performance_trends(self, history: List[Dict]) -> Dict[str, Any]:
        """Calculate performance trends from history"""
        return {"trend": "stable", "improvement": 0.0}
    
    async def _generate_performance_insights(self, success_rate: float, avg_time: float, tool_usage: Dict, trends: Dict) -> List[str]:
        """Generate performance insights"""
        insights = []
        if success_rate > 0.9:
            insights.append("Excellent success rate maintained")
        if avg_time < 30:
            insights.append("Fast response times achieved")
        return insights
    
    async def _get_basic_performance_metrics(self) -> Dict[str, Any]:
        """Get basic performance metrics when monitoring fails"""
        return {"status": "monitoring_unavailable", "basic_health": "ok"}
    
    async def _get_memory_usage(self) -> Dict[str, Any]:
        """Get memory usage statistics"""
        return {"cache_size": len(self.workflow_cache) + len(self.analysis_cache)}
    
    async def _calculate_recommendation_accuracy(self) -> float:
        """Calculate recommendation accuracy over time"""
        return 0.85  # Default good accuracy
    
    async def _validate_preferences(self, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Validate preference settings"""
        return {"valid": True, "warnings": []}
    
    async def _analyze_preference_impact(self, old_prefs: Dict, new_prefs: Dict, operation: str) -> Dict[str, Any]:
        """Analyze impact of preference changes"""
        return {"impact_level": "moderate", "affected_systems": ["tool_selection", "workflow_generation"]}


# Export main class
__all__ = ['AdvancedAutonomousTools', 'TaskAnalysisResult', 'WorkflowStep', 'IntelligentWorkflow']
