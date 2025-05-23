import asyncio
from typing import Dict, List, Any, Optional
from .analyzer import MessageAnalyzer
from .discovery import ToolDiscovery
from .planner import ExecutionPlanner
from .executor import ChainExecutor
from .recovery import ErrorRecoverySystem
from .learning import LearningSystem
from .preferences import PreferenceEngine


class AutonomousMCPAgent:
    """
    The main autonomous MCP orchestration agent.
    
    Automatically discovers tools, plans execution, and handles complex
    multi-tool workflows based on natural language input.
    """
    
    def __init__(self, preferences: Optional[Dict] = None):
        self.tool_discovery = ToolDiscovery()
        self.message_analyzer = MessageAnalyzer()
        self.execution_planner = ExecutionPlanner()
        self.chain_executor = ChainExecutor()
        self.error_recovery = ErrorRecoverySystem()
        self.learning_system = LearningSystem()
        self.preference_engine = PreferenceEngine(preferences)
        
        # Initialize on first use
        self._initialized = False
        self._available_tools = {}
        
    async def initialize(self):
        """Initialize the agent by discovering available tools."""
        if not self._initialized:
            # Discover all available MCP tools
            self._available_tools = await self.tool_discovery.discover_all()
            
            # Load user preferences
            await self.preference_engine.load_preferences()
            
            # Initialize learning system
            await self.learning_system.initialize()
            
            self._initialized = True
            
    async def execute(self, message: str, context: Optional[Dict] = None) -> Dict:
        """
        Execute a user request autonomously.
        
        Args:
            message: Natural language description of what to do
            context: Optional context from previous executions
            
        Returns:
            Execution result with detailed information
        """
        # Ensure initialization
        await self.initialize()
        
        try:
            # Step 1: Analyze the message
            analysis = await self.message_analyzer.analyze(message, context)
            
            # Step 2: Create execution plan
            plan = await self.execution_planner.create_plan(
                analysis, 
                self._available_tools,
                self.preference_engine.preferences
            )
            
            # Step 3: Execute the plan
            result = await self.chain_executor.execute(
                plan,
                error_handler=self.error_recovery
            )
            
            # Step 4: Learn from execution
            await self.learning_system.record_execution(plan, result)
            
            # Step 5: Format response
            return self._format_response(analysis, plan, result)
            
        except Exception as e:
            # Handle catastrophic failures
            return {
                'success': False,
                'error': str(e),
                'recovery_attempted': True
            }
            
    def _format_response(self, analysis: Dict, plan: Dict, result: Dict) -> Dict:
        """Format the execution response based on transparency preferences."""
        transparency = self.preference_engine.preferences.get('transparency', 'detailed')
        
        response = {
            'success': result['success'],
            'output': result['final_output']
        }
        
        if transparency == 'detailed':
            response['analysis'] = {
                'intent': analysis['intent'],
                'entities': analysis['entities'],
                'actions': analysis['actions']
            }
            response['execution'] = {
                'plan': plan['steps'],
                'tools_used': result['tools_used'],
                'duration': result['duration']
            }
        elif transparency == 'summary':
            response['summary'] = {
                'tools_used': len(result['tools_used']),
                'steps_completed': result['steps_completed']
            }
            
        return response
        
    async def set_preferences(self, preferences: Dict):
        """Update user preferences for automation behavior."""
        await self.preference_engine.update_preferences(preferences)
        
    async def get_capabilities(self) -> Dict:
        """Get current agent capabilities based on available tools."""
        await self.initialize()
        return {
            'available_tools': list(self._available_tools.keys()),
            'tool_categories': self.tool_discovery.get_categories(),
            'automation_level': self.preference_engine.preferences['automation_level']
        }