"""
Integration between User Preference Engine and Smart Tool Selector

This module extends the SmartToolSelector to incorporate user preferences
for truly personalized tool recommendations in the Autonomous MCP Agent.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

from .smart_selector import SmartToolSelector, SelectionStrategy, ToolScore
from .user_preferences import UserPreferenceEngine, PreferenceType

logger = logging.getLogger(__name__)


@dataclass
class PersonalizedRecommendation(ToolScore):
    """Enhanced tool recommendation with personalization metadata."""
    personalization_score: float = 0.0
    preference_factors: Dict[str, float] = None
    user_context: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.preference_factors is None:
            self.preference_factors = {}
        if self.user_context is None:
            self.user_context = {}


class PersonalizedToolSelector(SmartToolSelector):
    """
    Enhanced SmartToolSelector that incorporates user preferences
    for personalized tool recommendations.
    
    This class extends the SmartToolSelector to consider:
    - User tool preferences and usage history
    - Domain interests and engagement patterns
    - Execution style preferences
    - Explicit user feedback and preferences
    """
    
    def __init__(self, preference_engine: Optional[UserPreferenceEngine] = None):
        """
        Initialize the personalized tool selector.
        
        Args:
            preference_engine: Optional UserPreferenceEngine instance
        """
        super().__init__()
        self.preference_engine = preference_engine
        self.personalization_weight = 0.4  # Weight for preference factors
        
        # Add personalized selection strategy
        self.strategies[SelectionStrategy.PERSONALIZED] = self._personalized_selection
    
    def set_preference_engine(self, preference_engine: UserPreferenceEngine):
        """Set or update the preference engine."""
        self.preference_engine = preference_engine
    
    def recommend_tools(self, intent: str, available_tools: List[str], 
                       num_recommendations: int = 3,
                       strategy: SelectionStrategy = SelectionStrategy.PERSONALIZED,
                       context: Optional[Dict[str, Any]] = None) -> List[PersonalizedRecommendation]:
        """
        Get personalized tool recommendations based on user preferences.
        
        Args:
            intent: User's intent or task description
            available_tools: List of available tool names
            num_recommendations: Number of recommendations to return
            strategy: Selection strategy to use
            context: Additional context for selection
            
        Returns:
            List of PersonalizedRecommendation objects
        """
        # If no preference engine or using non-personalized strategy, fall back to base class
        if not self.preference_engine or strategy != SelectionStrategy.PERSONALIZED:
            base_recommendations = super().recommend_tools(
                intent, available_tools, num_recommendations, strategy, context
            )
            # Convert to PersonalizedRecommendation
            return [
                PersonalizedRecommendation(
                    tool_name=rec.tool_name,
                    confidence_score=rec.confidence_score,
                    reasoning=rec.reasoning,
                    performance_data=rec.performance_data,
                    capability_match=rec.capability_match,
                    context_relevance=rec.context_relevance
                )
                for rec in base_recommendations
            ]
        
        # Get personalized recommendations
        return self._personalized_selection(intent, available_tools, num_recommendations, context)
    
    def _personalized_selection(self, intent: str, available_tools: List[str], 
                               num_recommendations: int = 3,
                               context: Optional[Dict[str, Any]] = None) -> List[PersonalizedRecommendation]:
        """
        Personalized tool selection incorporating user preferences.
        
        Args:
            intent: User's intent or task description
            available_tools: List of available tool names
            num_recommendations: Number of recommendations to return
            context: Additional context for selection
            
        Returns:
            List of PersonalizedRecommendation objects
        """
        if not self.preference_engine:
            logger.warning("No preference engine available for personalized selection")
            return []
        
        # Get base recommendations from multiple strategies
        base_strategies = [SelectionStrategy.HYBRID, SelectionStrategy.ML_BASED, SelectionStrategy.CAPABILITY]
        all_base_recommendations = []
        
        for strategy in base_strategies:
            try:
                base_recs = super().recommend_tools(intent, available_tools, len(available_tools), strategy, context)
                all_base_recommendations.extend(base_recs)
            except Exception as e:
                logger.warning(f"Failed to get recommendations from {strategy}: {e}")
        
        # Get user preferences
        tool_preferences = self.preference_engine.get_tool_preferences(available_tools)
        domain_interests = self.preference_engine.get_domain_interests()
        execution_prefs = self.preference_engine.get_execution_preferences()
        
        # Extract domain from context or intent
        task_domain = self._extract_domain_from_intent(intent, context)
        
        # Create personalized recommendations
        personalized_recommendations = []
        
        for tool in available_tools:
            # Get base recommendation for this tool
            base_rec = next((rec for rec in all_base_recommendations if rec.tool_name == tool), None)
            if not base_rec:
                # Create minimal base recommendation
                base_rec = ToolRecommendation(
                    tool_name=tool,
                    confidence_score=0.1,
                    reasoning="No base recommendation available"
                )
            
            # Calculate personalization factors
            preference_factors = self._calculate_preference_factors(
                tool, intent, task_domain, tool_preferences, domain_interests, execution_prefs
            )
            
            # Calculate personalized score
            base_score = base_rec.confidence_score
            personalization_score = sum(preference_factors.values()) / len(preference_factors) if preference_factors else 0.0
            
            # Combine base score with personalization
            final_score = (base_score * (1 - self.personalization_weight) + 
                          personalization_score * self.personalization_weight)
            
            # Create personalized recommendation
            personalized_rec = PersonalizedRecommendation(
                tool_name=tool,
                confidence_score=final_score,
                reasoning=self._generate_personalized_reasoning(tool, base_rec, preference_factors),
                performance_data=base_rec.performance_data,
                capability_match=base_rec.capability_match,
                context_relevance=base_rec.context_relevance,
                personalization_score=personalization_score,
                preference_factors=preference_factors,
                user_context={
                    'task_domain': task_domain,
                    'user_id': self.preference_engine.current_user_id
                }
            )
            
            personalized_recommendations.append(personalized_rec)
        
        # Sort by final score and return top recommendations
        personalized_recommendations.sort(key=lambda x: x.confidence_score, reverse=True)
        return personalized_recommendations[:num_recommendations]
    
    def _calculate_preference_factors(self, tool: str, intent: str, task_domain: str,
                                    tool_preferences: Dict[str, float],
                                    domain_interests: Dict[str, float],
                                    execution_prefs: Dict[str, Any]) -> Dict[str, float]:
        """Calculate various preference factors for a tool."""
        factors = {}
        
        # Tool preference factor
        tool_pref_score = tool_preferences.get(tool, 0.0)
        factors['tool_preference'] = (tool_pref_score + 1.0) / 2.0  # Convert from [-1,1] to [0,1]
        
        # Domain interest factor
        if task_domain and task_domain in domain_interests:
            factors['domain_interest'] = domain_interests[task_domain]
        else:
            factors['domain_interest'] = 0.5  # Neutral if no domain match
        
        # Complexity tolerance factor
        complexity_tolerance = execution_prefs.get('complexity_tolerance', 0.5)
        tool_complexity = self._estimate_tool_complexity(tool, intent)
        
        if tool_complexity <= complexity_tolerance:
            factors['complexity_match'] = 1.0
        else:
            factors['complexity_match'] = max(0.0, 1.0 - (tool_complexity - complexity_tolerance))
        
        # Speed vs accuracy factor
        prefer_speed = execution_prefs.get('prefer_speed', False)
        tool_speed_score = self._estimate_tool_speed(tool)
        
        if prefer_speed:
            factors['speed_preference'] = tool_speed_score
        else:
            factors['speed_preference'] = 1.0 - tool_speed_score
        
        # Recent usage factor
        recent_usage_score = self._calculate_recent_usage_score(tool)
        factors['recent_usage'] = recent_usage_score
        
        return factors
    
    def _extract_domain_from_intent(self, intent: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Extract the primary domain from user intent."""
        if context and 'domain' in context:
            return context['domain']
        
        # Simple keyword-based domain extraction
        intent_lower = intent.lower()
        
        domain_keywords = {
            'web_search': ['search', 'find', 'look', 'google', 'web', 'internet'],
            'file_operations': ['file', 'folder', 'directory', 'save', 'read', 'write'],
            'data_analysis': ['analyze', 'data', 'statistics', 'chart', 'graph', 'csv'],
            'development': ['code', 'program', 'develop', 'git', 'github', 'repository'],
            'automation': ['automate', 'script', 'batch', 'schedule', 'workflow'],
            'communication': ['email', 'message', 'send', 'contact', 'notification'],
            'research': ['research', 'study', 'investigate', 'academic', 'paper']
        }
        
        domain_scores = {}
        for domain, keywords in domain_keywords.items():
            score = sum(1 for keyword in keywords if keyword in intent_lower)
            if score > 0:
                domain_scores[domain] = score
        
        if domain_scores:
            return max(domain_scores, key=domain_scores.get)
        
        return 'general'  # Default domain
    
    def _estimate_tool_complexity(self, tool: str, intent: str) -> float:
        """Estimate the complexity of using a tool for the given intent."""
        complexity_scores = {
            'web_search': 0.2,
            'file_operations': 0.3,
            'email': 0.4,
            'data_analysis': 0.7,
            'github_operations': 0.6,
            'automation': 0.8,
            'advanced_planning': 0.9
        }
        
        base_complexity = complexity_scores.get(tool, 0.5)
        
        # Adjust based on intent complexity
        intent_words = len(intent.split())
        if intent_words > 20:
            base_complexity += 0.2
        elif intent_words > 10:
            base_complexity += 0.1
        
        return min(1.0, base_complexity)
    
    def _estimate_tool_speed(self, tool: str) -> float:
        """Estimate the relative speed of a tool."""
        speed_scores = {
            'file_operations': 0.9,
            'web_search': 0.7,
            'email': 0.8,
            'data_analysis': 0.3,
            'github_operations': 0.5,
            'automation': 0.6,
            'advanced_planning': 0.2
        }
        
        return speed_scores.get(tool, 0.5)
    
    def _calculate_recent_usage_score(self, tool: str) -> float:
        """Calculate a score based on recent tool usage."""
        if not self.preference_engine:
            return 0.5
        
        profile = self.preference_engine.get_current_profile()
        if not profile:
            return 0.5
        
        usage_pref = profile.get_preference(PreferenceType.TOOL_USAGE, tool)
        if not usage_pref:
            return 0.3  # Slight penalty for never-used tools
        
        # Calculate recency score based on last update time
        import time
        current_time = time.time()
        time_since_use = current_time - usage_pref.last_updated
        
        # Convert to days
        days_since_use = time_since_use / (24 * 3600)
        
        # Exponential decay
        if days_since_use < 1:
            return 1.0
        elif days_since_use < 7:
            return 0.8
        elif days_since_use < 30:
            return 0.6
        else:
            return 0.4
    
    def _generate_personalized_reasoning(self, tool: str, base_rec: ToolRecommendation,
                                       preference_factors: Dict[str, float]) -> str:
        """Generate reasoning text that explains the personalized recommendation."""
        base_reasoning = base_rec.reasoning if base_rec.reasoning else "Base recommendation"
        
        # Add personalization factors to reasoning
        personalization_notes = []
        
        if preference_factors.get('tool_preference', 0.5) > 0.6:
            personalization_notes.append("you have shown preference for this tool")
        elif preference_factors.get('tool_preference', 0.5) < 0.4:
            personalization_notes.append("considering your mixed experience with this tool")
        
        if preference_factors.get('domain_interest', 0.5) > 0.7:
            personalization_notes.append("this aligns with your high interest in this domain")
        
        if preference_factors.get('complexity_match', 0.5) > 0.8:
            personalization_notes.append("the complexity matches your tolerance level")
        
        if preference_factors.get('recent_usage', 0.5) > 0.7:
            personalization_notes.append("you've used this tool recently with good results")
        
        if personalization_notes:
            return f"{base_reasoning}. Personalized because {', '.join(personalization_notes)}."
        else:
            return f"{base_reasoning}. (Standard recommendation)"
    
    def learn_from_recommendation_feedback(self, tool_name: str, was_selected: bool, 
                                         user_satisfaction: Optional[float] = None):
        """Learn from user feedback on recommendations to improve future suggestions."""
        if not self.preference_engine:
            return
        
        # Record the selection/rejection
        if was_selected:
            # Positive feedback for selected tools
            score_delta = 0.1
            if user_satisfaction is not None:
                score_delta += (user_satisfaction - 0.5) * 0.2
            
            profile = self.preference_engine.get_current_profile()
            if profile:
                profile.update_tool_preference(tool_name, score_delta)
        else:
            # Slight negative feedback for not selected tools
            profile = self.preference_engine.get_current_profile()
            if profile:
                profile.update_tool_preference(tool_name, -0.05)
        
        # Also update base selector's learning
        super().learn_from_usage(tool_name, was_selected, 1.0, user_satisfaction or 0.5)
    
    def get_personalization_explanation(self, recommendation: PersonalizedRecommendation) -> Dict[str, Any]:
        """Get detailed explanation of how personalization affected a recommendation."""
        return {
            'tool_name': recommendation.tool_name,
            'base_score': recommendation.confidence_score,
            'personalization_score': recommendation.personalization_score,
            'preference_factors': recommendation.preference_factors,
            'user_context': recommendation.user_context,
            'reasoning': recommendation.reasoning,
            'personalization_weight': self.personalization_weight
        }


# Convenience function to create an integrated intelligent agent
def create_intelligent_agent(preference_storage_path: Optional[str] = None) -> Tuple[PersonalizedToolSelector, UserPreferenceEngine]:
    """Create an integrated intelligent agent with both preference learning and smart tool selection."""
    preference_engine = UserPreferenceEngine(preference_storage_path)
    tool_selector = PersonalizedToolSelector(preference_engine)
    
    return tool_selector, preference_engine
