"""
Test Suite for Personalized Tool Selector

Tests the integration between User Preference Engine and Smart Tool Selector
to ensure personalized recommendations work correctly.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

# Import modules
from autonomous_mcp.personalized_selector import (
    PersonalizedToolSelector, PersonalizedRecommendation, create_intelligent_agent
)
from autonomous_mcp.user_preferences import UserPreferenceEngine, PreferenceType
from autonomous_mcp.smart_selector import SelectionStrategy


class TestPersonalizedRecommendation:
    """Test cases for PersonalizedRecommendation class."""
    
    def test_personalized_recommendation_creation(self):
        """Test creating a personalized recommendation."""
        rec = PersonalizedRecommendation(
            tool_name="web_search",
            confidence_score=0.85,
            reasoning="Good match for search tasks",
            personalization_score=0.7,
            preference_factors={"tool_preference": 0.8, "domain_interest": 0.6}
        )
        
        assert rec.tool_name == "web_search"
        assert rec.confidence_score == 0.85
        assert rec.personalization_score == 0.7
        assert rec.preference_factors["tool_preference"] == 0.8
        assert isinstance(rec.user_context, dict)


class TestPersonalizedToolSelector:
    """Test cases for PersonalizedToolSelector class."""
    
    def setup_method(self):
        """Set up test environment."""
        # Create temporary storage
        self.temp_dir = tempfile.mkdtemp()
        self.storage_path = Path(self.temp_dir) / "test_prefs.json"
        
        # Create preference engine and tool selector
        self.preference_engine = UserPreferenceEngine(str(self.storage_path))
        self.selector = PersonalizedToolSelector(self.preference_engine)
        
        # Create test user profile
        self.test_user = "test_user"
        self.profile = self.preference_engine.create_user_profile(self.test_user)
    
    def test_initialization(self):
        """Test PersonalizedToolSelector initialization."""
        selector = PersonalizedToolSelector()
        assert selector.preference_engine is None
        assert selector.personalization_weight == 0.4
        assert SelectionStrategy.PERSONALIZED in selector.strategies
        
        # Test with preference engine
        selector_with_prefs = PersonalizedToolSelector(self.preference_engine)
        assert selector_with_prefs.preference_engine == self.preference_engine
    
    def test_set_preference_engine(self):
        """Test setting preference engine after initialization."""
        selector = PersonalizedToolSelector()
        selector.set_preference_engine(self.preference_engine)
        assert selector.preference_engine == self.preference_engine
    
    def test_recommend_tools_without_preference_engine(self):
        """Test recommendations without preference engine (fallback)."""
        selector = PersonalizedToolSelector()  # No preference engine
        
        tools = ["web_search", "file_operations"]
        recommendations = selector.recommend_tools(
            "search for information",
            tools,
            strategy=SelectionStrategy.PERSONALIZED
        )
        
        # Should fall back to base recommendations
        assert isinstance(recommendations, list)
        for rec in recommendations:
            assert isinstance(rec, PersonalizedRecommendation)
    
    def test_recommend_tools_with_preferences(self):
        """Test personalized recommendations with user preferences."""
        # Set up user preferences
        self.profile.update_tool_preference("web_search", 0.8)
        self.profile.update_tool_preference("file_operations", -0.3)
        self.profile.update_domain_interest("research", 0.9)
        
        tools = ["web_search", "file_operations", "data_analysis"]
        
        # Mock the base recommendation methods to avoid dependencies
        with patch.object(self.selector, '_get_base_recommendations') as mock_base:
            mock_base.return_value = [
                Mock(tool_name="web_search", confidence_score=0.7, reasoning="Good for search"),
                Mock(tool_name="file_operations", confidence_score=0.6, reasoning="File handling"),
                Mock(tool_name="data_analysis", confidence_score=0.5, reasoning="Data processing")
            ]
            
            recommendations = self.selector.recommend_tools(
                "search for research information",
                tools,
                strategy=SelectionStrategy.PERSONALIZED,
                context={"domain": "research"}
            )
        
        assert len(recommendations) <= 3
        assert all(isinstance(rec, PersonalizedRecommendation) for rec in recommendations)
        
        # web_search should be ranked higher due to positive preference and domain match
        web_search_rec = next((r for r in recommendations if r.tool_name == "web_search"), None)
        assert web_search_rec is not None
        assert web_search_rec.personalization_score > 0.5
    
    def test_extract_domain_from_intent(self):
        """Test domain extraction from user intent."""
        test_cases = [
            ("search for information on the web", "web_search"),
            ("analyze this CSV data file", "data_analysis"),
            ("write code for the project", "development"),
            ("send an email to the team", "communication"),
            ("research academic papers", "research"),
            ("some random task", "general")
        ]
        
        for intent, expected_domain in test_cases:
            domain = self.selector._extract_domain_from_intent(intent)
            assert domain == expected_domain
    
    def test_extract_domain_from_context(self):
        """Test domain extraction from context."""
        intent = "do something"
        context = {"domain": "automation"}
        
        domain = self.selector._extract_domain_from_intent(intent, context)
        assert domain == "automation"
    
    def test_estimate_tool_complexity(self):
        """Test tool complexity estimation."""
        complexity = self.selector._estimate_tool_complexity("web_search", "simple search")
        assert 0 <= complexity <= 1
        assert complexity < 0.5  # web_search should be relatively simple
        
        complexity = self.selector._estimate_tool_complexity("data_analysis", "complex analysis task")
        assert complexity > 0.5  # data_analysis should be more complex
    
    def test_estimate_tool_speed(self):
        """Test tool speed estimation."""
        speed = self.selector._estimate_tool_speed("file_operations")
        assert 0 <= speed <= 1
        assert speed > 0.5  # file_operations should be relatively fast
        
        speed = self.selector._estimate_tool_speed("data_analysis")
        assert speed < 0.5  # data_analysis should be slower
    
    def test_calculate_preference_factors(self):
        """Test calculation of preference factors."""
        # Set up preferences
        self.profile.update_tool_preference("web_search", 0.6)
        self.profile.update_domain_interest("research", 0.8)
        
        tool_prefs = {"web_search": 0.6, "file_operations": -0.2}
        domain_interests = {"research": 0.8}
        exec_prefs = {"complexity_tolerance": 0.7, "prefer_speed": True}
        
        factors = self.selector._calculate_preference_factors(
            "web_search", "research task", "research",
            tool_prefs, domain_interests, exec_prefs
        )
        
        assert "tool_preference" in factors
        assert "domain_interest" in factors
        assert "complexity_match" in factors
        assert "speed_preference" in factors
        assert "recent_usage" in factors
        
        # Check ranges
        for factor_name, score in factors.items():
            assert 0 <= score <= 1, f"Factor {factor_name} out of range: {score}"
        
        # Tool preference should be positive (converted from 0.6 to range [0,1])
        assert factors["tool_preference"] > 0.5
        
        # Domain interest should be high
        assert factors["domain_interest"] == 0.8
    
    def test_calculate_recent_usage_score(self):
        """Test recent usage score calculation."""
        # Test with no usage history
        score = self.selector._calculate_recent_usage_score("unknown_tool")
        assert score == 0.3  # Penalty for never-used tools
        
        # Add some usage history
        from autonomous_mcp.user_preferences import PreferenceItem
        import time
        
        usage_pref = PreferenceItem(
            preference_type=PreferenceType.TOOL_USAGE,
            key="web_search",
            value={"success_rate": 0.8},
            last_updated=time.time() - 3600  # 1 hour ago
        )
        self.profile.add_preference(usage_pref)
        
        score = self.selector._calculate_recent_usage_score("web_search")
        assert score == 1.0  # Recent usage within 24 hours
    
    def test_generate_personalized_reasoning(self):
        """Test generation of personalized reasoning text."""
        base_rec = Mock(reasoning="Good tool for the task")
        
        preference_factors = {
            "tool_preference": 0.8,
            "domain_interest": 0.9,
            "complexity_match": 0.85,
            "recent_usage": 0.7
        }
        
        reasoning = self.selector._generate_personalized_reasoning(
            "web_search", base_rec, preference_factors
        )
        
        assert "Good tool for the task" in reasoning
        assert "you have shown preference for this tool" in reasoning
        assert "this aligns with your high interest in this domain" in reasoning
        assert "the complexity matches your tolerance level" in reasoning
    
    def test_learn_from_recommendation_feedback(self):
        """Test learning from recommendation feedback."""
        initial_pref = self.profile.preferred_tools.get("web_search", 0.0)
        
        # Positive feedback
        self.selector.learn_from_recommendation_feedback("web_search", was_selected=True, user_satisfaction=0.8)
        
        updated_pref = self.profile.preferred_tools.get("web_search", 0.0)
        assert updated_pref > initial_pref
        
        # Negative feedback
        initial_pref = self.profile.preferred_tools.get("file_operations", 0.0)
        self.selector.learn_from_recommendation_feedback("file_operations", was_selected=False)
        
        updated_pref = self.profile.preferred_tools.get("file_operations", 0.0)
        assert updated_pref < initial_pref
    
    def test_get_personalization_explanation(self):
        """Test getting personalization explanation."""
        rec = PersonalizedRecommendation(
            tool_name="web_search",
            confidence_score=0.85,
            reasoning="Personalized recommendation",
            personalization_score=0.7,
            preference_factors={"tool_preference": 0.8},
            user_context={"task_domain": "research"}
        )
        
        explanation = self.selector.get_personalization_explanation(rec)
        
        assert explanation["tool_name"] == "web_search"
        assert explanation["base_score"] == 0.85
        assert explanation["personalization_score"] == 0.7
        assert "tool_preference" in explanation["preference_factors"]
        assert explanation["user_context"]["task_domain"] == "research"
    
    def test_integration_with_user_preferences(self):
        """Test full integration with user preferences."""
        # Simulate user interactions
        self.preference_engine.learn_from_tool_usage("web_search", success=True, execution_time=0.5, user_satisfaction=0.9)
        self.preference_engine.learn_from_tool_usage("file_operations", success=False, execution_time=5.0, user_satisfaction=0.2)
        self.preference_engine.learn_from_domain_interaction("research", 0.9)
        
        # Mock base recommendations
        with patch.object(self.selector, '_get_base_recommendations') as mock_base:
            mock_base.return_value = [
                Mock(tool_name="web_search", confidence_score=0.6, reasoning="Search tool"),
                Mock(tool_name="file_operations", confidence_score=0.7, reasoning="File tool")
            ]
            
            recommendations = self.selector.recommend_tools(
                "search for research papers",
                ["web_search", "file_operations"],
                strategy=SelectionStrategy.PERSONALIZED,
                context={"domain": "research"}
            )
        
        # web_search should be ranked higher due to positive history and domain match
        assert len(recommendations) == 2
        assert recommendations[0].tool_name == "web_search"
        assert recommendations[0].confidence_score > recommendations[1].confidence_score


class TestIntelligentAgentCreation:
    """Test cases for integrated intelligent agent creation."""
    
    def test_create_intelligent_agent(self):
        """Test creating an integrated intelligent agent."""
        temp_dir = tempfile.mkdtemp()
        storage_path = Path(temp_dir) / "agent_prefs.json"
        
        selector, preference_engine = create_intelligent_agent(str(storage_path))
        
        assert isinstance(selector, PersonalizedToolSelector)
        assert isinstance(preference_engine, UserPreferenceEngine)
        assert selector.preference_engine == preference_engine
        assert preference_engine.storage_path == storage_path
    
    def test_create_intelligent_agent_without_storage(self):
        """Test creating agent without explicit storage path."""
        selector, preference_engine = create_intelligent_agent()
        
        assert isinstance(selector, PersonalizedToolSelector)
        assert isinstance(preference_engine, UserPreferenceEngine)
        assert selector.preference_engine == preference_engine


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
