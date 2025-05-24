"""
Advanced Execution Planner for Autonomous MCP Agent
Task 2.1: Enhanced planning with Sequential Thinking capabilities

Extends BasicExecutionPlanner with intelligent reasoning for complex task decomposition,
optimal tool selection, and dynamic plan adaptation.
"""

import asyncio
import json
import re
from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime
import logging

from .planner import BasicExecutionPlanner, ToolCall, ExecutionPlan
from .smart_selector import SmartToolSelector, SelectionContext, SelectionStrategy, ToolScore

logger = logging.getLogger(__name__)


@dataclass
class ReasoningStep:
    """Represents a reasoning step in the planning process"""
    step_number: int
    thought: str
    conclusion: str
    confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EnhancedExecutionPlan(ExecutionPlan):
    """Extended execution plan with reasoning metadata"""
    reasoning_steps: List[ReasoningStep] = field(default_factory=list)
    complexity_score: float = 0.0
    planning_method: str = "basic"  # "basic", "sequential_thinking", "hybrid"
    alternative_plans: List['ExecutionPlan'] = field(default_factory=list)
    adaptability_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation with reasoning data"""
        base_dict = super().to_dict()
        base_dict.update({
            'reasoning_steps': [
                {
                    'step_number': step.step_number,
                    'thought': step.thought,
                    'conclusion': step.conclusion,
                    'confidence': step.confidence,
                    'metadata': step.metadata
                }
                for step in self.reasoning_steps
            ],
            'complexity_score': self.complexity_score,
            'planning_method': self.planning_method,
            'adaptability_score': self.adaptability_score,
            'alternative_plans_count': len(self.alternative_plans)
        })
        return base_dict


class AdvancedExecutionPlanner(BasicExecutionPlanner):
    """
    Advanced execution planner with sequential thinking capabilities.
    
    Provides intelligent task decomposition, optimal tool selection,
    and dynamic plan adaptation for complex user intents.
    """
    
    def __init__(self, discovery_system=None, sequential_thinking_tool=None, smart_selector=None):
        """
        Initialize the advanced planner
        
        Args:
            discovery_system: Instance of ToolDiscoverySystem for tool selection
            sequential_thinking_tool: Function to call sequential thinking tool
            smart_selector: SmartToolSelector instance for intelligent tool selection
        """
        super().__init__(discovery_system)
        self.sequential_thinking_tool = sequential_thinking_tool
        self.smart_selector = smart_selector or (SmartToolSelector(discovery_system) if discovery_system else None)
        self.complexity_threshold = 0.6  # Above this, use sequential thinking
        self.reasoning_timeout = 30.0  # Max time for reasoning process
        
        # Complexity indicators
        self.complex_keywords = {
            'analyze', 'research', 'compare', 'comprehensive', 'detailed',
            'multi-step', 'workflow', 'pipeline', 'orchestrate', 'coordinate',
            'integrate', 'synthesize', 'investigate', 'evaluate', 'assess'
        }
        
        self.complexity_patterns = [
            r'\band\s+(?:then|also|after|subsequently)\s+',  # Sequential actions
            r'\bif\s+.*\bthen\b',  # Conditional logic
            r'\bdepending\s+on\b',  # Conditional logic
            r'\bmultiple\s+(?:steps|phases|stages)\b',  # Multi-step processes
            r'\bfirst\s+.*\bthen\s+.*\bfinally\b'  # Sequential indicators
        ]
    
    async def create_advanced_plan(self, intent: str, context: Dict[str, Any] = None) -> EnhancedExecutionPlan:
        """
        Create an enhanced execution plan using advanced reasoning
        
        Args:
            intent: User's intended action
            context: Additional context for planning
            
        Returns:
            EnhancedExecutionPlan with reasoning metadata
        """
        try:
            # Step 1: Analyze intent complexity
            complexity_analysis = await self.analyze_intent_complexity(intent, context)
            
            # Step 2: Choose planning approach based on complexity
            if complexity_analysis['score'] >= self.complexity_threshold and self.sequential_thinking_tool:
                plan = await self.create_reasoning_based_plan(intent, context, complexity_analysis)
            else:
                # Fall back to basic planning for simple intents
                basic_plan = self.create_plan(intent, context)
                plan = self._convert_to_enhanced_plan(basic_plan, complexity_analysis)
            
            # Step 3: Validate and optimize the plan
            plan = await self.optimize_advanced_plan(plan)
            
            return plan
            
        except Exception as e:
            logger.error(f"Advanced planning failed: {e}")
            # Graceful fallback to basic planning
            basic_plan = self.create_plan(intent, context)
            return self._convert_to_enhanced_plan(basic_plan, {'score': 0.0, 'reasoning': 'Fallback to basic planning'})
    
    async def analyze_intent_complexity(self, intent: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze the complexity of a user intent
        
        Args:
            intent: User's intended action
            context: Additional context
            
        Returns:
            Dict with complexity score, reasoning, and factors
        """
        factors = {}
        
        # Keyword-based complexity
        intent_lower = intent.lower()
        keyword_matches = [kw for kw in self.complex_keywords if kw in intent_lower]
        factors['complex_keywords'] = len(keyword_matches) / len(self.complex_keywords)
        
        # Pattern-based complexity
        pattern_matches = sum(1 for pattern in self.complexity_patterns if re.search(pattern, intent_lower))
        factors['complex_patterns'] = min(pattern_matches / len(self.complexity_patterns), 1.0)
        
        # Length and structure complexity
        words = intent.split()
        factors['length_complexity'] = min(len(words) / 20.0, 1.0)  # Normalize to 20 words
        
        # Entity count (simple heuristic)
        # Count potential entities (capitalized words, quoted strings)
        entities = re.findall(r'[A-Z][a-z]+|"[^"]*"', intent)
        factors['entity_complexity'] = min(len(entities) / 5.0, 1.0)  # Normalize to 5 entities
        
        # Context complexity
        context_score = 0.0
        if context:
            context_score = min(len(context) / 10.0, 1.0)  # Normalize to 10 context items
        factors['context_complexity'] = context_score
        
        # Calculate weighted complexity score
        weights = {
            'complex_keywords': 0.3,
            'complex_patterns': 0.25,
            'length_complexity': 0.2,
            'entity_complexity': 0.15,
            'context_complexity': 0.1
        }
        
        complexity_score = sum(factors[factor] * weights[factor] for factor in factors)
        
        return {
            'score': complexity_score,
            'factors': factors,
            'reasoning': f"Complexity analysis: {keyword_matches} complex keywords, {pattern_matches} patterns, {len(words)} words, {len(entities)} entities",
            'requires_advanced_planning': complexity_score >= self.complexity_threshold
        }
    
    async def create_reasoning_based_plan(self, intent: str, context: Dict[str, Any], 
                                        complexity_analysis: Dict[str, Any]) -> EnhancedExecutionPlan:
        """
        Create an execution plan using sequential thinking for complex reasoning
        
        Args:
            intent: User's intended action
            context: Additional context
            complexity_analysis: Results from complexity analysis
            
        Returns:
            EnhancedExecutionPlan with reasoning steps
        """
        reasoning_steps = []
        
        try:
            # Step 1: Decompose the task using sequential thinking
            decomposition_step = await self._reason_about_task_decomposition(intent, context)
            reasoning_steps.append(decomposition_step)
            
            # Step 2: Select optimal tools for each subtask
            tool_selection_step = await self._reason_about_tool_selection(
                decomposition_step.conclusion, intent, context
            )
            reasoning_steps.append(tool_selection_step)
            
            # Step 3: Plan execution order and dependencies
            execution_step = await self._reason_about_execution_order(
                tool_selection_step.conclusion, decomposition_step.conclusion
            )
            reasoning_steps.append(execution_step)
            
            # Step 4: Create the actual execution plan from reasoning
            tool_calls = self._create_tool_calls_from_reasoning(reasoning_steps, intent, context)
            
            # Create enhanced plan
            plan = EnhancedExecutionPlan(
                plan_id=f"advanced_plan_{self.plan_counter:04d}",
                intent=intent,
                tools=tool_calls,
                reasoning_steps=reasoning_steps,
                complexity_score=complexity_analysis['score'],
                planning_method="sequential_thinking",
                confidence_score=self._calculate_reasoning_confidence(reasoning_steps),
                estimated_duration=self._estimate_duration(tool_calls),
                metadata={'context': context or {}, 'complexity_analysis': complexity_analysis}
            )
            
            self.plan_counter += 1
            return plan
            
        except Exception as e:
            logger.error(f"Reasoning-based planning failed: {e}")
            # Fallback to basic planning
            basic_plan = self.create_plan(intent, context)
            return self._convert_to_enhanced_plan(basic_plan, complexity_analysis)
    
    async def _reason_about_task_decomposition(self, intent: str, context: Dict[str, Any]) -> ReasoningStep:
        """Use sequential thinking to decompose a complex task"""
        if not self.sequential_thinking_tool:
            return ReasoningStep(
                step_number=1,
                thought="Sequential thinking not available",
                conclusion="Treat as single task",
                confidence=0.5
            )
        
        reasoning_prompt = f"""
        I need to break down this complex task into manageable subtasks:
        
        Task: {intent}
        Context: {json.dumps(context) if context else 'None'}
        
        What are the logical subtasks needed to accomplish this goal?
        Consider dependencies, prerequisites, and the optimal sequence.
        """
        
        try:
            # Call sequential thinking tool
            result = await self._call_sequential_thinking(reasoning_prompt, 3)
            
            return ReasoningStep(
                step_number=1,
                thought=reasoning_prompt,
                conclusion=result.get('final_thought', 'Unable to decompose task'),
                confidence=0.8,
                metadata={'reasoning_result': result}
            )
        except Exception as e:
            logger.error(f"Task decomposition reasoning failed: {e}")
            return ReasoningStep(
                step_number=1,
                thought="Decomposition failed",
                conclusion="Treat as single task",
                confidence=0.3
            )
    
    async def _reason_about_tool_selection(self, subtasks: str, intent: str, context: Dict[str, Any]) -> ReasoningStep:
        """Use smart tool selection combined with sequential thinking for optimal tool choice"""
        if not self.discovery:
            return ReasoningStep(
                step_number=2,
                thought="No discovery system available",
                conclusion="Cannot select optimal tools",
                confidence=0.2
            )
        
        # Use Smart Tool Selector if available
        if self.smart_selector:
            try:
                # Create selection context
                selection_context = SelectionContext(
                    user_intent=intent,
                    task_complexity=self._calculate_complexity_score(intent),
                    required_capabilities=self._extract_capabilities_from_intent(intent),
                    previous_tools=context.get('previous_tools', []) if context else []
                )
                
                # Get smart tool recommendations
                tool_scores = await self.smart_selector.select_best_tools(
                    selection_context,
                    strategy=SelectionStrategy.HYBRID,
                    max_results=8
                )
                
                if tool_scores:
                    # Use sequential thinking to reason about the recommended tools
                    tool_descriptions = [
                        f"{score.tool_name}: Score {score.total_score:.2f}, {', '.join(score.reasons[:2])}"
                        for score in tool_scores
                    ]
                    
                    reasoning_prompt = f"""
                    Based on these subtasks: {subtasks}
                    
                    Smart-recommended tools (with AI scoring):
                    {chr(10).join(tool_descriptions)}
                    
                    Which combination of these AI-recommended tools would be most effective?
                    Consider the AI confidence scores and how tools chain together for the subtasks.
                    """
                    
                    result = await self._call_sequential_thinking(reasoning_prompt, 3)
                    
                    return ReasoningStep(
                        step_number=2,
                        thought=f"Smart selector recommended {len(tool_scores)} tools. {reasoning_prompt[:100]}...",
                        conclusion=result.get('final_thought', 'Use smart-recommended tools in sequence'),
                        confidence=0.85,
                        metadata={
                            'reasoning_result': result, 
                            'smart_recommendations': [(s.tool_name, s.total_score) for s in tool_scores],
                            'selection_strategy': 'smart_hybrid'
                        }
                    )
                
            except Exception as e:
                logger.warning(f"Smart tool selection failed, falling back to basic: {e}")
        
        # Fallback to basic tool discovery
        available_tools = self.discovery.get_tools_for_intent(intent)
        tool_descriptions = [
            f"{tool.name}: {tool.description if hasattr(tool, 'description') else 'No description'}"
            for tool in available_tools[:10]  # Limit for reasoning clarity
        ]
        
        reasoning_prompt = f"""
        Based on these subtasks: {subtasks}
        
        Available tools:
        {chr(10).join(tool_descriptions)}
        
        Which tools would be most effective for each subtask?
        Consider tool capabilities, performance, and how they chain together.
        """
        
        try:
            result = await self._call_sequential_thinking(reasoning_prompt, 3)
            
            return ReasoningStep(
                step_number=2,
                thought=reasoning_prompt,
                conclusion=result.get('final_thought', 'Use available tools in order'),
                confidence=0.75,
                metadata={'reasoning_result': result, 'available_tools': len(available_tools)}
            )
        except Exception as e:
            logger.error(f"Tool selection reasoning failed: {e}")
            return ReasoningStep(
                step_number=2,
                thought="Tool selection failed",
                conclusion="Use first available tools",
                confidence=0.4
            )
    
    async def _reason_about_execution_order(self, tool_selection: str, subtasks: str) -> ReasoningStep:
        """Use sequential thinking to determine optimal execution order"""
        reasoning_prompt = f"""
        Given these subtasks: {subtasks}
        And these tool selections: {tool_selection}
        
        What is the optimal execution order?
        Consider dependencies, parallel opportunities, and error recovery.
        """
        
        try:
            result = await self._call_sequential_thinking(reasoning_prompt, 2)
            
            return ReasoningStep(
                step_number=3,
                thought=reasoning_prompt,
                conclusion=result.get('final_thought', 'Execute tools in linear order'),
                confidence=0.7,
                metadata={'reasoning_result': result}
            )
        except Exception as e:
            logger.error(f"Execution order reasoning failed: {e}")
            return ReasoningStep(
                step_number=3,
                thought="Execution ordering failed",
                conclusion="Linear execution order",
                confidence=0.5
            )
    
    async def _call_sequential_thinking(self, prompt: str, max_thoughts: int = 3) -> Dict[str, Any]:
        """
        Call the sequential thinking tool with proper error handling
        
        Args:
            prompt: The reasoning prompt
            max_thoughts: Maximum number of thinking steps
            
        Returns:
            Dict with thinking results
        """
        if not self.sequential_thinking_tool:
            raise ValueError("Sequential thinking tool not available")
        
        try:
            # Start the thinking process
            result = await asyncio.wait_for(
                self.sequential_thinking_tool(
                    thought=prompt,
                    nextThoughtNeeded=True,
                    thoughtNumber=1,
                    totalThoughts=max_thoughts
                ),
                timeout=self.reasoning_timeout
            )
            
            # Continue thinking if needed
            thoughts = [result]
            thought_num = 2
            
            while result.get('nextThoughtNeeded', False) and thought_num <= max_thoughts:
                result = await asyncio.wait_for(
                    self.sequential_thinking_tool(
                        thought=f"Continuing from previous thought...",
                        nextThoughtNeeded=thought_num < max_thoughts,
                        thoughtNumber=thought_num,
                        totalThoughts=max_thoughts
                    ),
                    timeout=self.reasoning_timeout
                )
                thoughts.append(result)
                thought_num += 1
            
            return {
                'thoughts': thoughts,
                'final_thought': thoughts[-1].get('thought', '') if thoughts else '',
                'total_steps': len(thoughts)
            }
            
        except asyncio.TimeoutError:
            logger.warning("Sequential thinking timed out")
            return {'error': 'Reasoning timeout', 'final_thought': 'Timeout during reasoning'}
        except Exception as e:
            logger.error(f"Sequential thinking error: {e}")
            return {'error': str(e), 'final_thought': 'Error during reasoning'}
    
    def _create_tool_calls_from_reasoning(self, reasoning_steps: List[ReasoningStep], 
                                        intent: str, context: Dict[str, Any]) -> List[ToolCall]:
        """Convert reasoning steps into concrete tool calls"""
        tool_calls = []
        
        if not self.discovery:
            logger.warning("No discovery system available for tool call creation")
            return tool_calls
        
        # Extract tool recommendations from reasoning
        available_tools = self.discovery.get_tools_for_intent(intent)
        
        # For now, create a simple linear plan based on available tools
        # In the future, this would parse the reasoning conclusions more intelligently
        for i, tool in enumerate(available_tools[:5]):  # Limit to 5 tools for now
            tool_call = ToolCall(
                tool_name=tool.name,
                tool_id=tool.name,
                parameters=self._generate_parameters(tool.__dict__, intent, context),
                order=i,
                dependencies=[i-1] if i > 0 else [],
                expected_output_type=self._infer_output_type(tool.__dict__)
            )
            tool_calls.append(tool_call)
        
        return tool_calls
    
    def _calculate_reasoning_confidence(self, reasoning_steps: List[ReasoningStep]) -> float:
        """Calculate overall confidence based on reasoning quality"""
        if not reasoning_steps:
            return 0.0
        
        # Average confidence of all reasoning steps
        confidences = [step.confidence for step in reasoning_steps]
        return sum(confidences) / len(confidences)
    
    def _convert_to_enhanced_plan(self, basic_plan: ExecutionPlan, 
                                complexity_analysis: Dict[str, Any]) -> EnhancedExecutionPlan:
        """Convert a basic plan to an enhanced plan"""
        return EnhancedExecutionPlan(
            plan_id=basic_plan.plan_id,
            intent=basic_plan.intent,
            tools=basic_plan.tools,
            created_at=basic_plan.created_at,
            estimated_duration=basic_plan.estimated_duration,
            confidence_score=basic_plan.confidence_score,
            metadata=basic_plan.metadata,
            complexity_score=complexity_analysis.get('score', 0.0),
            planning_method="basic",
            reasoning_steps=[],
            alternative_plans=[],
            adaptability_score=0.5
        )
    
    async def optimize_advanced_plan(self, plan: EnhancedExecutionPlan) -> EnhancedExecutionPlan:
        """Optimize an enhanced execution plan"""
        # Validate the plan
        is_valid, errors = plan.validate()
        if not is_valid:
            logger.warning(f"Plan validation failed: {errors}")
            plan.metadata['validation_errors'] = errors
        
        # Calculate adaptability score based on plan structure
        plan.adaptability_score = self._calculate_adaptability_score(plan)
        
        return plan
    
    def _calculate_adaptability_score(self, plan: EnhancedExecutionPlan) -> float:
        """Calculate how adaptable a plan is to changes"""
        factors = []
        
        # Less dependencies = more adaptable
        total_deps = sum(len(tool.dependencies) for tool in plan.tools)
        dep_factor = max(0, 1.0 - (total_deps / max(len(plan.tools), 1)))
        factors.append(dep_factor)
        
        # More reasoning steps = more adaptable (better understanding)
        reasoning_factor = min(len(plan.reasoning_steps) / 3.0, 1.0)
        factors.append(reasoning_factor)
        
        # Higher confidence = more adaptable
        factors.append(plan.confidence_score)
        
        return sum(factors) / len(factors) if factors else 0.5
    
    async def adapt_plan_dynamically(self, plan: EnhancedExecutionPlan, 
                                   new_context: Dict[str, Any]) -> EnhancedExecutionPlan:
        """
        Adapt an existing plan based on new context or requirements
        
        Args:
            plan: Original execution plan
            new_context: New context or requirements
            
        Returns:
            Adapted execution plan
        """
        try:
            # Check if adaptation is needed based on new context
            if not new_context or plan.adaptability_score < 0.3:
                logger.info("Plan adaptation not needed or not feasible")
                return plan
            
            # Use sequential thinking to reason about adaptations
            if self.sequential_thinking_tool and plan.planning_method == "sequential_thinking":
                adaptation_reasoning = await self._reason_about_adaptation(plan, new_context)
                
                # Apply adaptations based on reasoning
                adapted_plan = await self._apply_adaptations(plan, adaptation_reasoning, new_context)
                return adapted_plan
            else:
                # Simple adaptation for basic plans
                return self._simple_adaptation(plan, new_context)
                
        except Exception as e:
            logger.error(f"Plan adaptation failed: {e}")
            return plan
    
    async def _reason_about_adaptation(self, plan: EnhancedExecutionPlan, 
                                     new_context: Dict[str, Any]) -> ReasoningStep:
        """Use sequential thinking to reason about how to adapt a plan"""
        reasoning_prompt = f"""
        I have an existing execution plan:
        Intent: {plan.intent}
        Tools: {[tool.tool_name for tool in plan.tools]}
        
        New context has emerged: {json.dumps(new_context)}
        
        How should I adapt this plan to account for the new context?
        What changes are needed to maintain effectiveness?
        """
        
        try:
            result = await self._call_sequential_thinking(reasoning_prompt, 2)
            
            return ReasoningStep(
                step_number=len(plan.reasoning_steps) + 1,
                thought=reasoning_prompt,
                conclusion=result.get('final_thought', 'No adaptation needed'),
                confidence=0.7,
                metadata={'reasoning_result': result, 'adaptation_context': new_context}
            )
        except Exception as e:
            logger.error(f"Adaptation reasoning failed: {e}")
            return ReasoningStep(
                step_number=len(plan.reasoning_steps) + 1,
                thought="Adaptation reasoning failed",
                conclusion="Maintain original plan",
                confidence=0.4
            )
    
    async def _apply_adaptations(self, plan: EnhancedExecutionPlan, 
                               adaptation_reasoning: ReasoningStep,
                               new_context: Dict[str, Any]) -> EnhancedExecutionPlan:
        """Apply adaptations to a plan based on reasoning"""
        # Create a copy of the plan
        adapted_plan = EnhancedExecutionPlan(
            plan_id=f"{plan.plan_id}_adapted",
            intent=plan.intent,
            tools=plan.tools.copy(),
            reasoning_steps=plan.reasoning_steps + [adaptation_reasoning],
            complexity_score=plan.complexity_score,
            planning_method=plan.planning_method,
            confidence_score=plan.confidence_score * 0.9,  # Slight confidence penalty for changes
            estimated_duration=plan.estimated_duration,
            metadata={**plan.metadata, 'adapted_context': new_context},
            adaptability_score=plan.adaptability_score
        )
        
        # For now, just update metadata
        # In the future, parse adaptation_reasoning.conclusion for specific changes
        adapted_plan.metadata['adaptation_applied'] = True
        adapted_plan.metadata['adaptation_reasoning'] = adaptation_reasoning.conclusion
        
        return adapted_plan
    
    def _simple_adaptation(self, plan: EnhancedExecutionPlan, 
                          new_context: Dict[str, Any]) -> EnhancedExecutionPlan:
        """Simple adaptation for basic plans"""
        # Just update context and metadata
        adapted_plan = EnhancedExecutionPlan(
            plan_id=f"{plan.plan_id}_simple_adapted",
            intent=plan.intent,
            tools=plan.tools,
            reasoning_steps=plan.reasoning_steps,
            complexity_score=plan.complexity_score,
            planning_method=plan.planning_method,
            confidence_score=plan.confidence_score,
            estimated_duration=plan.estimated_duration,
            metadata={**plan.metadata, 'adapted_context': new_context},
            adaptability_score=plan.adaptability_score
        )
        
        return adapted_plan
    
    def _extract_capabilities_from_intent(self, intent: str) -> List[str]:
        """Extract required capabilities from user intent"""
        capabilities = []
        intent_lower = intent.lower()
        
        # Map intent keywords to capabilities
        capability_mapping = {
            'search': ['web', 'search', 'information'],
            'analyze': ['data', 'analysis', 'processing'],
            'read': ['file', 'read', 'data'],
            'write': ['file', 'write', 'storage'],
            'create': ['creation', 'generation'],
            'research': ['web', 'search', 'research'],
            'process': ['data', 'processing'],
            'generate': ['creative', 'generation'],
            'reason': ['reasoning', 'ai'],
            'download': ['web', 'fetch'],
            'upload': ['file', 'storage'],
            'execute': ['execution', 'runtime']
        }
        
        for keyword, caps in capability_mapping.items():
            if keyword in intent_lower:
                capabilities.extend(caps)
        
        return list(set(capabilities))  # Remove duplicates


# Example usage
if __name__ == "__main__":
    async def test_advanced_planner():
        """Test the advanced planner functionality"""
        
        # Mock sequential thinking function
        async def mock_sequential_thinking(**kwargs):
            return {
                'thought': kwargs.get('thought', 'Mock thinking'),
                'nextThoughtNeeded': False
            }
        
        # Create planner
        planner = AdvancedExecutionPlanner(sequential_thinking_tool=mock_sequential_thinking)
        
        # Test complexity analysis
        complex_intent = "Research the latest AI developments, analyze their impact on software development, and create a comprehensive report with recommendations"
        
        complexity = await planner.analyze_intent_complexity(complex_intent)
        print(f"Complexity analysis: {complexity}")
        
        # Test plan creation
        plan = await planner.create_advanced_plan(complex_intent)
        print(f"Created plan: {plan.plan_id} with {len(plan.tools)} tools")
        print(f"Planning method: {plan.planning_method}")
        print(f"Complexity score: {plan.complexity_score}")
        
    # Run test
    asyncio.run(test_advanced_planner())
