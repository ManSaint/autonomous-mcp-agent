"""
User Preference Engine for Autonomous MCP Agent

This module implements a comprehensive user preference learning and management system
that integrates with the smart tool selection algorithms to provide personalized
agent experiences.

Key Features:
- User preference learning from tool usage patterns
- Preference-based tool filtering and ranking
- User profile management with persistence
- Integration with SmartToolSelector for personalized recommendations
- Adaptive preference weights based on user feedback
- Privacy-aware preference storage
"""

import json
import time
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, asdict, field
from enum import Enum
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class PreferenceType(Enum):
    """Types of user preferences that can be learned and stored."""
    TOOL_USAGE = "tool_usage"
    DOMAIN_INTEREST = "domain_interest"
    EXECUTION_STYLE = "execution_style"
    COMPLEXITY_TOLERANCE = "complexity_tolerance"
    SPEED_VS_ACCURACY = "speed_vs_accuracy"
    PRIVACY_LEVEL = "privacy_level"
    FEEDBACK_PREFERENCE = "feedback_preference"


class FeedbackType(Enum):
    """Types of user feedback for preference learning."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    EXPLICIT = "explicit"  # User explicitly states preference


@dataclass
class PreferenceItem:
    """Individual preference item with metadata."""
    preference_type: PreferenceType
    key: str
    value: Any
    confidence: float = 0.5
    weight: float = 1.0
    last_updated: float = field(default_factory=time.time)
    usage_count: int = 0
    feedback_history: List[Dict[str, Any]] = field(default_factory=list)
    
    def update_confidence(self, feedback: FeedbackType, impact: float = 0.1):
        """Update confidence based on user feedback."""
        if feedback == FeedbackType.POSITIVE:
            self.confidence = min(1.0, self.confidence + impact)
        elif feedback == FeedbackType.NEGATIVE:
            self.confidence = max(0.0, self.confidence - impact)
        elif feedback == FeedbackType.EXPLICIT:
            self.confidence = 0.9  # High confidence for explicit preferences
        
        self.last_updated = time.time()
        self.feedback_history.append({
            'feedback': feedback.value,
            'impact': impact,
            'timestamp': self.last_updated
        })


@dataclass
class UserProfile:
    """Comprehensive user profile with preferences and metadata."""
    user_id: str
    preferences: Dict[str, PreferenceItem] = field(default_factory=dict)
    creation_time: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    total_interactions: int = 0
    preferred_tools: Dict[str, float] = field(default_factory=dict)  # tool_name -> preference_score
    domain_interests: Dict[str, float] = field(default_factory=dict)  # domain -> interest_score
    execution_preferences: Dict[str, Any] = field(default_factory=dict)
    privacy_settings: Dict[str, bool] = field(default_factory=lambda: {
        'learn_from_usage': True,
        'store_history': True,
        'share_anonymous_data': False
    })
    
    def add_preference(self, pref_item: PreferenceItem):
        """Add or update a preference item."""
        key = f"{pref_item.preference_type.value}:{pref_item.key}"
        self.preferences[key] = pref_item
        self.last_activity = time.time()
    
    def get_preference(self, pref_type: PreferenceType, key: str) -> Optional[PreferenceItem]:
        """Get a specific preference item."""
        pref_key = f"{pref_type.value}:{key}"
        return self.preferences.get(pref_key)
    
    def update_tool_preference(self, tool_name: str, score_delta: float):
        """Update preference score for a specific tool."""
        current_score = self.preferred_tools.get(tool_name, 0.0)
        new_score = max(-1.0, min(1.0, current_score + score_delta))
        self.preferred_tools[tool_name] = new_score
        self.last_activity = time.time()
    
    def update_domain_interest(self, domain: str, interest_delta: float):
        """Update interest score for a specific domain."""
        current_interest = self.domain_interests.get(domain, 0.0)
        new_interest = max(0.0, min(1.0, current_interest + interest_delta))
        self.domain_interests[domain] = new_interest
        self.last_activity = time.time()


class UserPreferenceEngine:
    """
    Advanced user preference learning and management system.
    
    This engine learns from user interactions, stores preferences,
    and provides personalized recommendations for tool selection.
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize the user preference engine.
        
        Args:
            storage_path: Path to store user preference data
        """
        self.storage_path = Path(storage_path) if storage_path else Path("user_preferences.json")
        self.profiles: Dict[str, UserProfile] = {}
        self.current_user_id: Optional[str] = None
        self.learning_enabled = True
        self.adaptation_rate = 0.2  # Increased for stronger learning
        
        # Load existing profiles
        self._load_profiles()
    
    def create_user_profile(self, user_id: str, 
                          initial_preferences: Optional[Dict[str, Any]] = None) -> UserProfile:
        """
        Create a new user profile with optional initial preferences.
        
        Args:
            user_id: Unique identifier for the user
            initial_preferences: Optional dictionary of initial preferences
            
        Returns:
            UserProfile: The created user profile
        """
        profile = UserProfile(user_id=user_id)
        
        if initial_preferences:
            for pref_type_str, prefs in initial_preferences.items():
                try:
                    pref_type = PreferenceType(pref_type_str)
                    if isinstance(prefs, dict):
                        for key, value in prefs.items():
                            pref_item = PreferenceItem(
                                preference_type=pref_type,
                                key=key,
                                value=value,
                                confidence=0.8  # Higher confidence for explicit initial preferences
                            )
                            profile.add_preference(pref_item)
                except ValueError:
                    logger.warning(f"Unknown preference type: {pref_type_str}")
        
        self.profiles[user_id] = profile
        self.current_user_id = user_id
        self._save_profiles()
        
        logger.info(f"Created user profile for {user_id}")
        return profile
    
    def set_current_user(self, user_id: str) -> bool:
        """
        Set the current active user.
        
        Args:
            user_id: ID of the user to set as current
            
        Returns:
            bool: True if user exists and was set, False otherwise
        """
        if user_id in self.profiles:
            self.current_user_id = user_id
            return True
        return False
    
    def get_current_profile(self) -> Optional[UserProfile]:
        """Get the current user's profile."""
        if self.current_user_id:
            return self.profiles.get(self.current_user_id)
        return None
    
    def learn_from_tool_usage(self, tool_name: str, success: bool, 
                            execution_time: float, user_satisfaction: Optional[float] = None):
        """
        Learn user preferences from tool usage patterns.
        
        Args:
            tool_name: Name of the tool used
            success: Whether the tool execution was successful
            execution_time: How long the tool took to execute
            user_satisfaction: Optional user satisfaction score (0-1)
        """
        if not self.learning_enabled or not self.current_user_id:
            return
        
        profile = self.get_current_profile()
        if not profile:
            return
        
        # Update tool preference based on success and satisfaction
        score_delta = 0.0
        if success:
            score_delta += 0.1
        else:
            score_delta -= 0.1
        
        if user_satisfaction is not None:
            score_delta += (user_satisfaction - 0.5) * 0.2
        
        # Adjust for execution time (faster tools get slight preference)
        if execution_time < 1.0:  # Fast execution
            score_delta += 0.05
        elif execution_time > 10.0:  # Slow execution
            score_delta -= 0.05
        
        profile.update_tool_preference(tool_name, score_delta)
        profile.total_interactions += 1
        
        # Create or update tool usage preference
        usage_pref = profile.get_preference(PreferenceType.TOOL_USAGE, tool_name)
        if usage_pref:
            usage_pref.usage_count += 1
            usage_pref.value = {'success_rate': 
                              (usage_pref.value.get('success_rate', 0.5) * 0.9 + 
                               (1.0 if success else 0.0) * 0.1)}
        else:
            usage_pref = PreferenceItem(
                preference_type=PreferenceType.TOOL_USAGE,
                key=tool_name,
                value={'success_rate': 1.0 if success else 0.0},
                usage_count=1
            )
            profile.add_preference(usage_pref)
        
        self._save_profiles()
        logger.debug(f"Learned from tool usage: {tool_name}, success: {success}")
    
    def learn_from_domain_interaction(self, domain: str, engagement_level: float):
        """
        Learn user preferences from domain-specific interactions.
        
        Args:
            domain: Domain category (e.g., 'web_search', 'file_operations', 'data_analysis')
            engagement_level: User engagement level (0-1)
        """
        if not self.learning_enabled or not self.current_user_id:
            return
        
        profile = self.get_current_profile()
        if not profile:
            return
        
        # Update domain interest
        interest_delta = (engagement_level - 0.5) * self.adaptation_rate
        profile.update_domain_interest(domain, interest_delta)
        
        # Create or update domain interest preference
        domain_pref = profile.get_preference(PreferenceType.DOMAIN_INTEREST, domain)
        if domain_pref:
            domain_pref.value = profile.domain_interests[domain]
            domain_pref.usage_count += 1
        else:
            domain_pref = PreferenceItem(
                preference_type=PreferenceType.DOMAIN_INTEREST,
                key=domain,
                value=profile.domain_interests[domain],
                usage_count=1
            )
            profile.add_preference(domain_pref)
        
        self._save_profiles()
        logger.debug(f"Learned domain interest: {domain}, level: {engagement_level}")
    
    def record_explicit_preference(self, pref_type: PreferenceType, 
                                 key: str, value: Any, weight: float = 1.0):
        """
        Record an explicit user preference.
        
        Args:
            pref_type: Type of preference
            key: Preference key
            value: Preference value
            weight: Importance weight (0-1)
        """
        if not self.current_user_id:
            return
        
        profile = self.get_current_profile()
        if not profile:
            return
        
        pref_item = PreferenceItem(
            preference_type=pref_type,
            key=key,
            value=value,
            confidence=0.9,  # High confidence for explicit preferences
            weight=weight
        )
        
        profile.add_preference(pref_item)
        self._save_profiles()
        
        logger.info(f"Recorded explicit preference: {pref_type.value}:{key} = {value}")
    
    def get_tool_preferences(self, available_tools: List[str]) -> Dict[str, float]:
        """
        Get preference scores for available tools.
        
        Args:
            available_tools: List of available tool names
            
        Returns:
            Dict mapping tool names to preference scores (-1 to 1)
        """
        profile = self.get_current_profile()
        if not profile:
            return {tool: 0.0 for tool in available_tools}
        
        preferences = {}
        for tool in available_tools:
            # Get stored preference score
            base_score = profile.preferred_tools.get(tool, 0.0)
            
            # Get usage-based preference
            usage_pref = profile.get_preference(PreferenceType.TOOL_USAGE, tool)
            usage_score = 0.0
            if usage_pref and usage_pref.value:
                success_rate = usage_pref.value.get('success_rate', 0.5)
                usage_score = (success_rate - 0.5) * 0.5  # Convert to -0.25 to 0.25 range
            
            # Combine scores
            final_score = base_score + usage_score
            preferences[tool] = max(-1.0, min(1.0, final_score))
        
        return preferences
    
    def get_domain_interests(self) -> Dict[str, float]:
        """
        Get user's domain interest scores.
        
        Returns:
            Dict mapping domain names to interest scores (0-1)
        """
        profile = self.get_current_profile()
        if not profile:
            return {}
        
        return profile.domain_interests.copy()
    
    def get_execution_preferences(self) -> Dict[str, Any]:
        """
        Get user's execution-related preferences.
        
        Returns:
            Dict containing execution preferences
        """
        profile = self.get_current_profile()
        if not profile:
            return {
                'prefer_speed': False,
                'complexity_tolerance': 0.5,
                'parallel_execution': True,
                'detailed_feedback': True
            }
        
        # Extract execution preferences from stored preferences
        exec_prefs = profile.execution_preferences.copy()
        
        # Add derived preferences
        complexity_pref = profile.get_preference(PreferenceType.COMPLEXITY_TOLERANCE, 'level')
        if complexity_pref:
            exec_prefs['complexity_tolerance'] = complexity_pref.value
        
        speed_pref = profile.get_preference(PreferenceType.SPEED_VS_ACCURACY, 'preference')
        if speed_pref:
            exec_prefs['prefer_speed'] = speed_pref.value > 0.5
        
        return exec_prefs
    
    def provide_feedback(self, preference_key: str, feedback: FeedbackType, 
                        impact: float = 0.1):
        """
        Provide feedback on a specific preference to improve learning.
        
        Args:
            preference_key: Key of the preference to update
            feedback: Type of feedback
            impact: Strength of the feedback (0-1)
        """
        profile = self.get_current_profile()
        if not profile:
            return
        
        if preference_key in profile.preferences:
            profile.preferences[preference_key].update_confidence(feedback, impact)
            self._save_profiles()
            logger.debug(f"Updated preference feedback: {preference_key}, {feedback.value}")
    
    def get_personalized_tool_ranking(self, tools: List[str], 
                                    task_context: Optional[Dict[str, Any]] = None) -> List[Tuple[str, float]]:
        """
        Get personalized tool ranking based on user preferences.
        
        Args:
            tools: List of tool names to rank
            task_context: Optional context about the current task
            
        Returns:
            List of (tool_name, score) tuples sorted by preference
        """
        tool_preferences = self.get_tool_preferences(tools)
        domain_interests = self.get_domain_interests()
        
        # Calculate personalized scores
        personalized_scores = []
        for tool in tools:
            score = tool_preferences.get(tool, 0.0)
            
            # Boost score based on domain interests if context provided
            if task_context and 'domain' in task_context:
                domain = task_context['domain']
                domain_interest = domain_interests.get(domain, 0.5)
                score += (domain_interest - 0.5) * 0.3
            
            personalized_scores.append((tool, score))
        
        # Sort by score descending
        personalized_scores.sort(key=lambda x: x[1], reverse=True)
        return personalized_scores
    
    def export_profile(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Export user profile data for backup or transfer.
        
        Args:
            user_id: User ID to export (current user if None)
            
        Returns:
            Dict containing profile data
        """
        target_user = user_id or self.current_user_id
        if not target_user or target_user not in self.profiles:
            return {}
        
        profile = self.profiles[target_user]
        
        # Convert to serializable format
        export_data = {
            'user_id': profile.user_id,
            'creation_time': profile.creation_time,
            'last_activity': profile.last_activity,
            'total_interactions': profile.total_interactions,
            'preferred_tools': profile.preferred_tools,
            'domain_interests': profile.domain_interests,
            'execution_preferences': profile.execution_preferences,
            'privacy_settings': profile.privacy_settings,
            'preferences': {}
        }
        
        # Convert preference items
        for key, pref_item in profile.preferences.items():
            export_data['preferences'][key] = {
                'preference_type': pref_item.preference_type.value,
                'key': pref_item.key,
                'value': pref_item.value,
                'confidence': pref_item.confidence,
                'weight': pref_item.weight,
                'last_updated': pref_item.last_updated,
                'usage_count': pref_item.usage_count,
                'feedback_history': pref_item.feedback_history
            }
        
        return export_data
    
    def import_profile(self, profile_data: Dict[str, Any]) -> bool:
        """
        Import user profile data from backup or transfer.
        
        Args:
            profile_data: Dict containing profile data
            
        Returns:
            bool: True if import was successful
        """
        try:
            user_id = profile_data['user_id']
            
            # Create new profile
            profile = UserProfile(
                user_id=user_id,
                creation_time=profile_data.get('creation_time', time.time()),
                last_activity=profile_data.get('last_activity', time.time()),
                total_interactions=profile_data.get('total_interactions', 0),
                preferred_tools=profile_data.get('preferred_tools', {}),
                domain_interests=profile_data.get('domain_interests', {}),
                execution_preferences=profile_data.get('execution_preferences', {}),
                privacy_settings=profile_data.get('privacy_settings', {})
            )
            
            # Import preference items
            for key, pref_data in profile_data.get('preferences', {}).items():
                pref_item = PreferenceItem(
                    preference_type=PreferenceType(pref_data['preference_type']),
                    key=pref_data['key'],
                    value=pref_data['value'],
                    confidence=pref_data.get('confidence', 0.5),
                    weight=pref_data.get('weight', 1.0),
                    last_updated=pref_data.get('last_updated', time.time()),
                    usage_count=pref_data.get('usage_count', 0),
                    feedback_history=pref_data.get('feedback_history', [])
                )
                profile.preferences[key] = pref_item
            
            self.profiles[user_id] = profile
            self._save_profiles()
            
            logger.info(f"Successfully imported profile for {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to import profile: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the preference engine and current user.
        
        Returns:
            Dict containing various statistics
        """
        stats = {
            'total_users': len(self.profiles),
            'current_user': self.current_user_id,
            'learning_enabled': self.learning_enabled
        }
        
        profile = self.get_current_profile()
        if profile:
            stats.update({
                'user_interactions': profile.total_interactions,
                'user_preferences_count': len(profile.preferences),
                'user_preferred_tools_count': len(profile.preferred_tools),
                'user_domain_interests_count': len(profile.domain_interests),
                'user_creation_time': profile.creation_time,
                'user_last_activity': profile.last_activity
            })
        
        return stats
    
    def _load_profiles(self):
        """Load user profiles from storage."""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                
                for user_id, profile_data in data.items():
                    profile = UserProfile(
                        user_id=user_id,
                        creation_time=profile_data.get('creation_time', time.time()),
                        last_activity=profile_data.get('last_activity', time.time()),
                        total_interactions=profile_data.get('total_interactions', 0),
                        preferred_tools=profile_data.get('preferred_tools', {}),
                        domain_interests=profile_data.get('domain_interests', {}),
                        execution_preferences=profile_data.get('execution_preferences', {}),
                        privacy_settings=profile_data.get('privacy_settings', {})
                    )
                    
                    # Load preference items
                    for key, pref_data in profile_data.get('preferences', {}).items():
                        pref_item = PreferenceItem(
                            preference_type=PreferenceType(pref_data['preference_type']),
                            key=pref_data['key'],
                            value=pref_data['value'],
                            confidence=pref_data.get('confidence', 0.5),
                            weight=pref_data.get('weight', 1.0),
                            last_updated=pref_data.get('last_updated', time.time()),
                            usage_count=pref_data.get('usage_count', 0),
                            feedback_history=pref_data.get('feedback_history', [])
                        )
                        profile.preferences[key] = pref_item
                    
                    self.profiles[user_id] = profile
                
                logger.info(f"Loaded {len(self.profiles)} user profiles")
                
            except Exception as e:
                logger.error(f"Failed to load profiles: {e}")
    
    def _save_profiles(self):
        """Save user profiles to storage."""
        try:
            # Ensure directory exists
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            
            data = {}
            for user_id, profile in self.profiles.items():
                # Convert profile to serializable format
                profile_data = {
                    'creation_time': profile.creation_time,
                    'last_activity': profile.last_activity,
                    'total_interactions': profile.total_interactions,
                    'preferred_tools': profile.preferred_tools,
                    'domain_interests': profile.domain_interests,
                    'execution_preferences': profile.execution_preferences,
                    'privacy_settings': profile.privacy_settings,
                    'preferences': {}
                }
                
                # Convert preference items
                for key, pref_item in profile.preferences.items():
                    profile_data['preferences'][key] = {
                        'preference_type': pref_item.preference_type.value,
                        'key': pref_item.key,
                        'value': pref_item.value,
                        'confidence': pref_item.confidence,
                        'weight': pref_item.weight,
                        'last_updated': pref_item.last_updated,
                        'usage_count': pref_item.usage_count,
                        'feedback_history': pref_item.feedback_history
                    }
                
                data[user_id] = profile_data
            
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save profiles: {e}")
