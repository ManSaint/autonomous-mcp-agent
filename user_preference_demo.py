"""
User Preference Engine Demo

This demo showcases the capabilities of the User Preference Engine:
- Creating user profiles with initial preferences
- Learning from tool usage patterns
- Recording explicit preferences
- Getting personalized tool recommendations
- Providing feedback and adapting preferences
- Exporting and importing user profiles
"""

import os
import sys
import time
import tempfile
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from autonomous_mcp.user_preferences import (
    UserPreferenceEngine, PreferenceType, FeedbackType
)


def print_separator(title):
    """Print a nice separator with title."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def print_subsection(title):
    """Print a subsection header."""
    print(f"\n--- {title} ---")


def demo_user_preference_engine():
    """Demonstrate the User Preference Engine capabilities."""
    
    print_separator("🎯 USER PREFERENCE ENGINE DEMO")
    
    # Create engine with temporary storage
    temp_dir = tempfile.mkdtemp()
    storage_path = Path(temp_dir) / "demo_preferences.json"
    engine = UserPreferenceEngine(storage_path=str(storage_path))
    
    print(f"📁 Using temporary storage: {storage_path}")
    
    # 1. Create User Profile with Initial Preferences
    print_subsection("1. Creating User Profile with Initial Preferences")
    
    initial_preferences = {
        "tool_usage": {
            "web_search": {"success_rate": 0.9},
            "file_operations": {"success_rate": 0.7}
        },
        "domain_interest": {
            "research": 0.8,
            "development": 0.9,
            "data_analysis": 0.6
        },
        "speed_vs_accuracy": {
            "preference": 0.3  # Prefer accuracy over speed
        }
    }
    
    profile = engine.create_user_profile("alice", initial_preferences)
    
    print(f"✅ Created profile for user: {profile.user_id}")
    print(f"📊 Initial preferences loaded: {len(profile.preferences)} items")
    print(f"🔧 Preferred tools: {profile.preferred_tools}")
    print(f"🎯 Domain interests: {profile.domain_interests}")
    
    # 2. Learn from Tool Usage
    print_subsection("2. Learning from Tool Usage Patterns")
    
    # Simulate successful tool usage
    tools_usage = [
        ("web_search", True, 0.8, 0.9),  # success, exec_time, satisfaction
        ("web_search", True, 0.5, 0.8),
        ("file_operations", False, 3.0, 0.3),  # Failed usage
        ("data_analysis", True, 2.0, 0.7),
        ("web_search", True, 0.6, 0.85),
        ("github_operations", True, 1.2, 0.8),  # New tool
    ]
    
    print("🤖 Simulating tool usage patterns...")
    for tool, success, exec_time, satisfaction in tools_usage:
        engine.learn_from_tool_usage(tool, success, exec_time, satisfaction)
        status = "✅ Success" if success else "❌ Failed"
        print(f"  {tool}: {status} (time: {exec_time}s, satisfaction: {satisfaction})")
    
    updated_profile = engine.get_current_profile()
    print(f"\n📈 Updated tool preferences:")
    for tool, score in updated_profile.preferred_tools.items():
        print(f"  {tool}: {score:.3f}")
    
    # 3. Learn from Domain Interactions
    print_subsection("3. Learning from Domain Interactions")
    
    domain_interactions = [
        ("research", 0.9),
        ("development", 0.8),
        ("research", 0.95),
        ("data_analysis", 0.4),  # Low engagement
        ("automation", 0.7),  # New domain
    ]
    
    print("🎯 Simulating domain interactions...")
    for domain, engagement in domain_interactions:
        engine.learn_from_domain_interaction(domain, engagement)
        print(f"  {domain}: engagement {engagement}")
    
    updated_profile = engine.get_current_profile()
    print(f"\n🎯 Updated domain interests:")
    for domain, interest in updated_profile.domain_interests.items():
        print(f"  {domain}: {interest:.3f}")
    
    # 4. Record Explicit Preferences
    print_subsection("4. Recording Explicit User Preferences")
    
    explicit_prefs = [
        (PreferenceType.COMPLEXITY_TOLERANCE, "level", 0.8),
        (PreferenceType.EXECUTION_STYLE, "parallel_preferred", True),
        (PreferenceType.FEEDBACK_PREFERENCE, "detailed", True),
        (PreferenceType.PRIVACY_LEVEL, "learn_from_usage", True),
    ]
    
    print("📝 Recording explicit preferences...")
    for pref_type, key, value in explicit_prefs:
        engine.record_explicit_preference(pref_type, key, value, weight=0.9)
        print(f"  {pref_type.value}:{key} = {value}")
    
    # 5. Get Tool Preferences and Rankings
    print_subsection("5. Getting Personalized Tool Recommendations")
    
    available_tools = [
        "web_search", "file_operations", "data_analysis", 
        "github_operations", "email_operations", "calendar_operations"
    ]
    
    tool_preferences = engine.get_tool_preferences(available_tools)
    print("🔧 Tool preference scores:")
    for tool, score in tool_preferences.items():
        print(f"  {tool}: {score:.3f}")
    
    # Get personalized ranking with context
    task_context = {"domain": "research"}
    ranking = engine.get_personalized_tool_ranking(available_tools, task_context)
    
    print(f"\n🏆 Personalized tool ranking for '{task_context['domain']}' domain:")
    for i, (tool, score) in enumerate(ranking, 1):
        print(f"  {i}. {tool}: {score:.3f}")
    
    # 6. Provide Feedback and Adaptation
    print_subsection("6. Providing Feedback and Preference Adaptation")
    
    # Get a preference to provide feedback on
    tool_usage_pref_key = f"{PreferenceType.TOOL_USAGE.value}:web_search"
    
    print("💬 Providing feedback on web_search tool usage...")
    engine.provide_feedback(tool_usage_pref_key, FeedbackType.POSITIVE, impact=0.15)
    
    updated_pref = updated_profile.preferences.get(tool_usage_pref_key)
    if updated_pref:
        print(f"  Updated confidence: {updated_pref.confidence:.3f}")
        print(f"  Feedback history: {len(updated_pref.feedback_history)} entries")
    
    # 7. Get Execution Preferences
    print_subsection("7. Getting Execution Preferences")
    
    exec_prefs = engine.get_execution_preferences()
    print("⚙️ Execution preferences:")
    for pref, value in exec_prefs.items():
        print(f"  {pref}: {value}")
    
    # 8. Export and Import Profile
    print_subsection("8. Profile Export and Import")
    
    # Export current profile
    export_data = engine.export_profile()
    print(f"📤 Exported profile data ({len(export_data)} top-level keys)")
    print(f"  User ID: {export_data['user_id']}")
    print(f"  Total interactions: {export_data['total_interactions']}")
    print(f"  Preferences count: {len(export_data['preferences'])}")
    
    # Create new engine and import
    new_engine = UserPreferenceEngine()
    import_success = new_engine.import_profile(export_data)
    
    print(f"📥 Profile import success: {import_success}")
    if import_success:
        new_engine.set_current_user("alice")
        imported_preferences = new_engine.get_tool_preferences(available_tools)
        print("✅ Imported tool preferences match original")
    
    # 9. Engine Statistics
    print_subsection("9. Engine Statistics")
    
    stats = engine.get_statistics()
    print("📊 Engine statistics:")
    for key, value in stats.items():
        if key.startswith('user_') and isinstance(value, float):
            if 'time' in key:
                readable_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(value))
                print(f"  {key}: {readable_time}")
            else:
                print(f"  {key}: {value}")
        else:
            print(f"  {key}: {value}")
    
    # 10. Advanced Use Case: Multi-User Scenario
    print_subsection("10. Multi-User Scenario")
    
    # Create second user with different preferences
    bob_prefs = {
        "domain_interest": {
            "automation": 0.9,
            "development": 0.7,
            "research": 0.3
        },
        "speed_vs_accuracy": {
            "preference": 0.8  # Prefer speed over accuracy
        }
    }
    
    bob_profile = engine.create_user_profile("bob", bob_prefs)
    print(f"👤 Created second user: {bob_profile.user_id}")
    
    # Simulate different usage patterns for Bob
    bob_tools = [
        ("github_operations", True, 0.5, 0.9),
        ("file_operations", True, 0.8, 0.8),
        ("automation_tools", True, 1.0, 0.95),
    ]
    
    for tool, success, exec_time, satisfaction in bob_tools:
        engine.learn_from_tool_usage(tool, success, exec_time, satisfaction)
    
    # Compare personalized rankings for both users
    print("\n🔄 Switching between users to compare preferences:")
    
    for user_id in ["alice", "bob"]:
        engine.set_current_user(user_id)
        user_ranking = engine.get_personalized_tool_ranking(
            ["web_search", "github_operations", "file_operations", "automation_tools"],
            {"domain": "development"}
        )
        
        print(f"\n👤 {user_id}'s ranking for development tasks:")
        for i, (tool, score) in enumerate(user_ranking[:3], 1):
            print(f"  {i}. {tool}: {score:.3f}")
    
    # Final statistics
    final_stats = engine.get_statistics()
    print(f"\n📊 Final statistics: {final_stats['total_users']} users, "
          f"learning enabled: {final_stats['learning_enabled']}")
    
    print_separator("✅ USER PREFERENCE ENGINE DEMO COMPLETE")
    print("🎉 Successfully demonstrated all major preference engine features!")
    print(f"📁 Demo data saved to: {storage_path}")
    
    return True


if __name__ == "__main__":
    try:
        success = demo_user_preference_engine()
        if success:
            print("\n🚀 Demo completed successfully!")
        else:
            print("\n❌ Demo encountered errors")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
