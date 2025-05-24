"""
Comprehensive Test Suite for User Preference Engine

Tests all aspects of user preference learning, storage, and personalization
features in the Autonomous MCP Agent.
"""

import pytest
import tempfile
import json
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import the modules we're testing
from autonomous_mcp.user_preferences import (
    UserPreferenceEngine, UserProfile, PreferenceItem, 
    PreferenceType, FeedbackType
)


class TestPreferenceItem:
    """Test cases for PreferenceItem class."""
    
    def test_preference_item_creation(self):
        """Test creating a preference item."""
        pref = PreferenceItem(
            preference_type=PreferenceType.TOOL_USAGE,
            key="web_search",
            value={"success_rate": 0.8},
            confidence=0.7
        )
        
        assert pref.preference_type == PreferenceType.TOOL_USAGE
        assert pref.key == "web_search"
        assert pref.value == {"success_rate": 0.8}
        assert pref.confidence == 0.7
        assert pref.weight == 1.0
        assert pref.usage_count == 0
        assert isinstance(pref.feedback_history, list)
    
    def test_update_confidence_positive(self):
        """Test updating confidence with positive feedback."""
        pref = PreferenceItem(
            preference_type=PreferenceType.TOOL_USAGE,
            key="test_tool",
            value=0.5,
            confidence=0.5
        )
        
        initial_confidence = pref.confidence
        pref.update_confidence(FeedbackType.POSITIVE, 0.2)
        
        assert pref.confidence == initial_confidence + 0.2
        assert len(pref.feedback_history) == 1
        assert pref.feedback_history[0]['feedback'] == 'positive'
    
    def test_update_confidence_negative(self):
        """Test updating confidence with negative feedback."""
        pref = PreferenceItem(
            preference_type=PreferenceType.TOOL_USAGE,
            key="test_tool",
            value=0.5,
            confidence=0.8
        )
        
        initial_confidence = pref.confidence
        pref.update_confidence(FeedbackType.NEGATIVE, 0.3)
        
        assert pref.confidence == initial_confidence - 0.3
        assert len(pref.feedback_history) == 1
        assert pref.feedback_history[0]['feedback'] == 'negative'
    
    def test_update_confidence_explicit(self):
        """Test updating confidence with explicit feedback."""
        pref = PreferenceItem(
            preference_type=PreferenceType.TOOL_USAGE,
            key="test_tool",
            value=0.5,
            confidence=0.3
        )
        
        pref.update_confidence(FeedbackType.EXPLICIT)
        
        assert pref.confidence == 0.9
        assert len(pref.feedback_history) == 1
        assert pref.feedback_history[0]['feedback'] == 'explicit'
    
    def test_confidence_bounds(self):
        """Test that confidence is bounded between 0 and 1."""
        pref = PreferenceItem(
            preference_type=PreferenceType.TOOL_USAGE,
            key="test_tool",
            value=0.5,
            confidence=0.1
        )
        
        # Test lower bound
        pref.update_confidence(FeedbackType.NEGATIVE, 0.5)
        assert pref.confidence == 0.0
        
        # Test upper bound
        pref.confidence = 0.9
        pref.update_confidence(FeedbackType.POSITIVE, 0.5)
        assert pref.confidence == 1.0


class TestUserProfile:
    """Test cases for UserProfile class."""
    
    def test_user_profile_creation(self):
        """Test creating a user profile."""
        profile = UserProfile(user_id="test_user")
        
        assert profile.user_id == "test_user"
        assert isinstance(profile.preferences, dict)
        assert profile.total_interactions == 0
        assert isinstance(profile.preferred_tools, dict)
        assert isinstance(profile.domain_interests, dict)
        assert profile.privacy_settings['learn_from_usage'] == True
    
    def test_add_preference(self):
        """Test adding a preference to profile."""
        profile = UserProfile(user_id="test_user")
        pref = PreferenceItem(
            preference_type=PreferenceType.TOOL_USAGE,
            key="web_search",
            value={"success_rate": 0.8}
        )
        
        profile.add_preference(pref)
        
        assert len(profile.preferences) == 1
        key = f"{PreferenceType.TOOL_USAGE.value}:web_search"
        assert key in profile.preferences
        assert profile.preferences[key] == pref
    
    def test_get_preference(self):
        """Test getting a preference from profile."""
        profile = UserProfile(user_id="test_user")
        pref = PreferenceItem(
            preference_type=PreferenceType.DOMAIN_INTEREST,
            key="data_analysis",
            value=0.9
        )
        
        profile.add_preference(pref)
        retrieved_pref = profile.get_preference(PreferenceType.DOMAIN_INTEREST, "data_analysis")
        
        assert retrieved_pref == pref
        
        # Test non-existent preference
        non_existent = profile.get_preference(PreferenceType.TOOL_USAGE, "non_existent")
        assert non_existent is None
    
    def test_update_tool_preference(self):
        """Test updating tool preference scores."""
        profile = UserProfile(user_id="test_user")
        
        # Test adding new tool preference
        profile.update_tool_preference("web_search", 0.3)
        assert profile.preferred_tools["web_search"] == 0.3
        
        # Test updating existing tool preference
        profile.update_tool_preference("web_search", 0.2)
        assert profile.preferred_tools["web_search"] == 0.5
        
        # Test bounds checking
        profile.update_tool_preference("web_search", 0.8)
        assert profile.preferred_tools["web_search"] == 1.0  # Capped at 1.0
        
        profile.update_tool_preference("web_search", -2.5)
        assert profile.preferred_tools["web_search"] == -1.0  # Floored at -1.0
    
    def test_update_domain_interest(self):
        """Test updating domain interest scores."""
        profile = UserProfile(user_id="test_user")
        
        # Test adding new domain interest
        profile.update_domain_interest("web_search", 0.4)
        assert profile.domain_interests["web_search"] == 0.4
        
        # Test updating existing domain interest
        profile.update_domain_interest("web_search", 0.3)
        assert profile.domain_interests["web_search"] == 0.7
        
        # Test bounds checking
        profile.update_domain_interest("web_search", 0.5)
        assert profile.domain_interests["web_search"] == 1.0  # Capped at 1.0
        
        profile.update_domain_interest("web_search", -1.5)
        assert profile.domain_interests["web_search"] == 0.0  # Floored at 0.0


class TestUserPreferenceEngine:
    """Test cases for UserPreferenceEngine class."""
    
    def setup_method(self):
        """Set up test environment."""
        # Create temporary storage path
        self.temp_dir = tempfile.mkdtemp()
        self.storage_path = Path(self.temp_dir) / "test_preferences.json"
        self.engine = UserPreferenceEngine(storage_path=str(self.storage_path))
    
    def test_engine_initialization(self):
        """Test engine initialization."""
        assert isinstance(self.engine.profiles, dict)
        assert self.engine.current_user_id is None
        assert self.engine.learning_enabled == True
        assert self.engine.storage_path == self.storage_path
    
    def test_create_user_profile(self):
        """Test creating a user profile."""
        initial_prefs = {
            "tool_usage": {"web_search": {"success_rate": 0.8}},
            "domain_interest": {"research": 0.9}
        }
        
        profile = self.engine.create_user_profile("test_user", initial_prefs)
        
        assert profile.user_id == "test_user"
        assert self.engine.current_user_id == "test_user"
        assert "test_user" in self.engine.profiles
        assert len(profile.preferences) == 2
        
        # Check if preferences were added correctly
        tool_pref = profile.get_preference(PreferenceType.TOOL_USAGE, "web_search")
        assert tool_pref is not None
        assert tool_pref.value == {"success_rate": 0.8}
        assert tool_pref.confidence == 0.8
    
    def test_set_current_user(self):
        """Test setting current user."""
        # Create a user first
        self.engine.create_user_profile("user1")
        self.engine.create_user_profile("user2")
        
        # Test setting existing user
        result = self.engine.set_current_user("user1")
        assert result == True
        assert self.engine.current_user_id == "user1"
        
        # Test setting non-existent user
        result = self.engine.set_current_user("non_existent")
        assert result == False
        assert self.engine.current_user_id == "user1"  # Should remain unchanged
    
    def test_learn_from_tool_usage_success(self):
        """Test learning from successful tool usage."""
        profile = self.engine.create_user_profile("test_user")
        
        # Learn from successful usage
        self.engine.learn_from_tool_usage("web_search", success=True, execution_time=0.5, user_satisfaction=0.8)
        
        updated_profile = self.engine.get_current_profile()
        
        # Check tool preference was updated positively
        assert "web_search" in updated_profile.preferred_tools
        assert updated_profile.preferred_tools["web_search"] > 0
        
        # Check tool usage preference was created
        usage_pref = updated_profile.get_preference(PreferenceType.TOOL_USAGE, "web_search")
        assert usage_pref is not None
        assert usage_pref.value["success_rate"] == 1.0
        assert usage_pref.usage_count == 1
        
        assert updated_profile.total_interactions == 1
    
    def test_learn_from_tool_usage_failure(self):
        """Test learning from failed tool usage."""
        profile = self.engine.create_user_profile("test_user")
        
        # Learn from failed usage
        self.engine.learn_from_tool_usage("web_search", success=False, execution_time=5.0, user_satisfaction=0.2)
        
        updated_profile = self.engine.get_current_profile()
        
        # Check tool preference was updated negatively
        assert "web_search" in updated_profile.preferred_tools
        assert updated_profile.preferred_tools["web_search"] < 0
        
        # Check tool usage preference reflects failure
        usage_pref = updated_profile.get_preference(PreferenceType.TOOL_USAGE, "web_search")
        assert usage_pref is not None
        assert usage_pref.value["success_rate"] == 0.0
    
    def test_learn_from_domain_interaction(self):
        """Test learning from domain interactions."""
        profile = self.engine.create_user_profile("test_user")
        
        # Learn from high engagement
        self.engine.learn_from_domain_interaction("web_search", engagement_level=0.9)
        
        updated_profile = self.engine.get_current_profile()
        
        # Check domain interest was updated
        assert "web_search" in updated_profile.domain_interests
        assert updated_profile.domain_interests["web_search"] > 0.05  # Should be positive
        
        # Check domain preference was created
        domain_pref = updated_profile.get_preference(PreferenceType.DOMAIN_INTEREST, "web_search")
        assert domain_pref is not None
        assert domain_pref.usage_count == 1
    
    def test_record_explicit_preference(self):
        """Test recording explicit user preferences."""
        profile = self.engine.create_user_profile("test_user")
        
        self.engine.record_explicit_preference(
            PreferenceType.SPEED_VS_ACCURACY, 
            "preference", 
            0.8, 
            weight=0.9
        )
        
        updated_profile = self.engine.get_current_profile()
        speed_pref = updated_profile.get_preference(PreferenceType.SPEED_VS_ACCURACY, "preference")
        
        assert speed_pref is not None
        assert speed_pref.value == 0.8
        assert speed_pref.confidence == 0.9
        assert speed_pref.weight == 0.9
    
    def test_get_tool_preferences(self):
        """Test getting tool preferences."""
        profile = self.engine.create_user_profile("test_user")
        
        # Set up some tool preferences
        profile.update_tool_preference("web_search", 0.3)
        profile.update_tool_preference("file_operations", -0.2)
        
        # Add usage preference
        usage_pref = PreferenceItem(
            preference_type=PreferenceType.TOOL_USAGE,
            key="web_search",
            value={"success_rate": 0.8}
        )
        profile.add_preference(usage_pref)
        
        available_tools = ["web_search", "file_operations", "data_analysis"]
        preferences = self.engine.get_tool_preferences(available_tools)
        
        assert len(preferences) == 3
        assert preferences["web_search"] > 0.3  # Should be boosted by usage success
        assert preferences["file_operations"] == -0.2
        assert preferences["data_analysis"] == 0.0  # Default for unknown tools
    
    def test_get_personalized_tool_ranking(self):
        """Test getting personalized tool ranking."""
        profile = self.engine.create_user_profile("test_user")
        
        # Set up preferences
        profile.update_tool_preference("web_search", 0.5)
        profile.update_tool_preference("file_operations", -0.2)
        profile.update_tool_preference("data_analysis", 0.3)
        profile.update_domain_interest("research", 0.8)
        
        tools = ["web_search", "file_operations", "data_analysis"]
        context = {"domain": "research"}
        
        ranking = self.engine.get_personalized_tool_ranking(tools, context)
        
        # Should be sorted by preference score
        assert len(ranking) == 3
        assert ranking[0][0] == "web_search"  # Highest preference + domain boost
        assert ranking[2][0] == "file_operations"  # Lowest preference
        
        # All tools should have scores
        for tool, score in ranking:
            assert isinstance(score, float)
    
    def test_provide_feedback(self):
        """Test providing feedback on preferences."""
        profile = self.engine.create_user_profile("test_user")
        
        # Create a preference
        pref = PreferenceItem(
            preference_type=PreferenceType.TOOL_USAGE,
            key="web_search",
            value={"success_rate": 0.5},
            confidence=0.5
        )
        profile.add_preference(pref)
        
        pref_key = f"{PreferenceType.TOOL_USAGE.value}:web_search"
        
        # Provide positive feedback
        self.engine.provide_feedback(pref_key, FeedbackType.POSITIVE, 0.2)
        
        updated_pref = profile.preferences[pref_key]
        assert updated_pref.confidence == 0.7
        assert len(updated_pref.feedback_history) == 1
    
    def test_export_import_profile(self):
        """Test exporting and importing user profiles."""
        # Create and populate a profile
        profile = self.engine.create_user_profile("test_user")
        profile.update_tool_preference("web_search", 0.5)
        profile.update_domain_interest("research", 0.8)
        
        self.engine.record_explicit_preference(
            PreferenceType.COMPLEXITY_TOLERANCE,
            "level",
            0.7
        )
        
        # Export profile
        export_data = self.engine.export_profile()
        
        assert export_data["user_id"] == "test_user"
        assert "web_search" in export_data["preferred_tools"]
        assert "research" in export_data["domain_interests"]
        assert len(export_data["preferences"]) >= 1
        
        # Create new engine and import profile
        new_engine = UserPreferenceEngine()
        success = new_engine.import_profile(export_data)
        
        assert success == True
        assert "test_user" in new_engine.profiles
        
        imported_profile = new_engine.profiles["test_user"]
        assert imported_profile.preferred_tools["web_search"] == 0.5
        assert imported_profile.domain_interests["research"] == 0.8
    
    def test_get_statistics(self):
        """Test getting engine statistics."""
        # Create multiple users
        self.engine.create_user_profile("user1")
        self.engine.create_user_profile("user2")
        self.engine.set_current_user("user1")
        
        # Add some interactions
        profile = self.engine.get_current_profile()
        profile.total_interactions = 5
        profile.update_tool_preference("web_search", 0.3)
        
        stats = self.engine.get_statistics()
        
        assert stats["total_users"] == 2
        assert stats["current_user"] == "user1"
        assert stats["learning_enabled"] == True
        assert stats["user_interactions"] == 5
        assert stats["user_preferred_tools_count"] >= 1
    
    @patch('autonomous_mcp.user_preferences.logger')
    def test_learning_disabled(self, mock_logger):
        """Test behavior when learning is disabled."""
        self.engine.create_user_profile("test_user")
        self.engine.learning_enabled = False
        
        # Try to learn - should be ignored
        self.engine.learn_from_tool_usage("web_search", success=True, execution_time=0.5)
        self.engine.learn_from_domain_interaction("research", 0.8)
        
        profile = self.engine.get_current_profile()
        assert len(profile.preferred_tools) == 0
        assert len(profile.domain_interests) == 0
        assert profile.total_interactions == 0
    
    def test_no_current_user(self):
        """Test behavior when no current user is set."""
        # Try to learn without current user - should be ignored
        self.engine.learn_from_tool_usage("web_search", success=True, execution_time=0.5)
        
        # Try to record preference without current user - should be ignored
        self.engine.record_explicit_preference(
            PreferenceType.TOOL_USAGE,
            "test",
            0.5
        )
        
        # Should have no profiles
        assert len(self.engine.profiles) == 0
    
    def test_persistence(self):
        """Test profile persistence across engine instances."""
        # Create and populate profile
        profile = self.engine.create_user_profile("test_user")
        profile.update_tool_preference("web_search", 0.5)
        
        # Force save
        self.engine._save_profiles()
        
        # Create new engine with same storage path
        new_engine = UserPreferenceEngine(storage_path=str(self.storage_path))
        
        # Check profile was loaded
        assert "test_user" in new_engine.profiles
        loaded_profile = new_engine.profiles["test_user"]
        assert loaded_profile.preferred_tools["web_search"] == 0.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
