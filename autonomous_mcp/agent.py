import asyncio
from typing import Dict, List, Any, Optional
import logging
from .analyzer import MessageAnalyzer
from .discovery import ToolDiscovery

# Placeholder imports for future modules
# from .planner import ExecutionPlanner
# from .executor import ChainExecutor
# from .recovery import ErrorRecoverySystem
# from .learning import LearningSystem
# from .preferences import PreferenceEngine

logger = logging.getLogger(__name__)


class AutonomousMCPAgent:
    """
    The main autonomous MCP orchestration agent.
    
    Automatically discovers tools, plans execution, and handles complex
    multi-tool workflows based on natural language input.
    """
    
    def __init__(self, preferences: Optional[Dict] = None):
        self.tool_discovery = ToolDiscovery()
        self.message_analyzer = MessageAnalyzer()
        # TODO: Initialize these as they're implemented
        # self.execution_planner = ExecutionPlanner()
        # self.chain_executor = ChainExecutor()
        # self.error_recovery = ErrorRecoverySystem()
        # self.learning_system = LearningSystem()
        # self.preference_engine = PreferenceEngine(preferences)
        
        # Initialize on first use
        self._initialized = False
        self._available_tools = {}
        self._preferences = preferences or {
            'automation_level': 'balanced',
            'transparency': 'detailed'
        }
        
    async def initialize(self, tool_list: List[Dict[str, Any]] = None):
        """
        Initialize the agent by discovering available tools.
        
        Args:
            tool_list: Optional list of tools to discover. If not provided,
                      will need to be obtained from the environment.
        """
        if not self._initialized:
            # Discover all available MCP tools
            if tool_list:
                self._available_tools = self.tool_discovery.discover_all_tools(tool_list)
                logger.info(f"Discovered {len(self._available_tools)} tools")
            else:
                logger.warning("No tool list provided. Use discover_from_environment() when available.")
            
            # TODO: Load user preferences
            # await self.preference_engine.load_preferences()
            
            # TODO: Initialize learning system
            # await self.learning_system.initialize()
            
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
        if not self._initialized:
            return {
                'success': False,
                'error': 'Agent not initialized. Call initialize() first.',
                'recovery_attempted': False
            }
        
        try:
            # Step 1: Analyze the message
            analysis = self.message_analyzer.analyze(message, context)
            
            # Step 2: Get tools for the intent
            intent = analysis.get('intent', {}).get('primary', '')
            matching_tools = self.tool_discovery.get_tools_for_intent(message)
            
            if not matching_tools:
                return {
                    'success': False,
                    'error': f'No tools found for intent: {intent}',
                    'analysis': analysis
                }
            
            # TODO: Create execution plan
            # plan = await self.execution_planner.create_plan(
            #     analysis, 
            #     self._available_tools,
            #     self._preferences
            # )
            
            # TODO: Execute the plan
            # result = await self.chain_executor.execute(
            #     plan,
            #     error_handler=self.error_recovery
            # )
            
            # TODO: Learn from execution
            # await self.learning_system.record_execution(plan, result)
            
            # For now, return a placeholder response showing what we found
            return {
                'success': True,
                'analysis': analysis,
                'discovered_tools': [
                    {
                        'name': tool.name,
                        'server': tool.server,
                        'capabilities': [
                            f"{cap.category}/{cap.subcategory}"
                            for cap in tool.capabilities
                        ]
                    }
                    for tool in matching_tools[:5]  # Top 5 tools
                ],
                'message': 'Tool discovery successful. Execution planning not yet implemented.'
            }
            
        except Exception as e:
            logger.error(f"Execution error: {e}")
            # Handle catastrophic failures
            return {
                'success': False,
                'error': str(e),
                'recovery_attempted': False
            }
            
    def _format_response(self, analysis: Dict, plan: Dict, result: Dict) -> Dict:
        """Format the execution response based on transparency preferences."""
        transparency = self._preferences.get('transparency', 'detailed')
        
        response = {
            'success': result['success'],
            'output': result.get('final_output', '')
        }
        
        if transparency == 'detailed':
            response['analysis'] = {
                'intent': analysis.get('intent', {}),
                'entities': analysis.get('entities', []),
                'actions': analysis.get('actions', [])
            }
            response['execution'] = {
                'plan': plan.get('steps', []),
                'tools_used': result.get('tools_used', []),
                'duration': result.get('duration', 0)
            }
        elif transparency == 'summary':
            response['summary'] = {
                'tools_used': len(result.get('tools_used', [])),
                'steps_completed': result.get('steps_completed', 0)
            }
            
        return response
        
    async def set_preferences(self, preferences: Dict):
        """Update user preferences for automation behavior."""
        self._preferences.update(preferences)
        # TODO: Persist preferences when PreferenceEngine is implemented
        # await self.preference_engine.update_preferences(preferences)
        
    async def get_capabilities(self) -> Dict:
        """Get current agent capabilities based on available tools."""
        if not self._initialized:
            return {
                'error': 'Agent not initialized',
                'available_tools': [],
                'tool_categories': {},
                'automation_level': self._preferences['automation_level']
            }
            
        return {
            'available_tools': list(self._available_tools.keys()),
            'tool_categories': self.tool_discovery.categorize_by_capability(),
            'automation_level': self._preferences['automation_level'],
            'tool_stats': self.tool_discovery.get_tool_stats()
        }
    
    def discover_from_chainable_tools(self, chainable_output: str) -> int:
        """
        Discover tools from the output of the chainable_tools function.
        
        Args:
            chainable_output: Comma-separated list of tool names from chainable_tools
            
        Returns:
            Number of tools discovered
        """
        # Parse the tool names
        tool_names = [name.strip() for name in chainable_output.split(',')]
        
        # Create tool list from names
        tool_list = []
        for name in tool_names:
            if name:
                # Extract server name from compound names like 'github_create_repository'
                parts = name.split('_')
                server = parts[0] if len(parts) > 1 else 'unknown'
                
                tool_list.append({
                    'name': name,
                    'server': server,
                    'description': f'Tool: {name}',  # Basic description
                    'parameters': {}  # Would need actual parameters from tool
                })
        
        # Discover tools
        self._available_tools = self.tool_discovery.discover_all_tools(tool_list)
        self._initialized = True
        
        return len(self._available_tools)


# Example usage for testing
if __name__ == "__main__":
    async def test_agent():
        # Initialize agent
        agent = AutonomousMCPAgent()
        
        # Example tool list (would come from mcp_chain in real usage)
        example_tools = [
            {
                'name': 'read_file',
                'server': 'desktop_commander',
                'description': 'Read the contents of a file from the file system',
                'parameters': {'path': 'string', 'offset': 'number', 'length': 'number'}
            },
            {
                'name': 'web_search',
                'server': 'brave_search',
                'description': 'Search the web using Brave search engine',
                'parameters': {'query': 'string', 'count': 'number'}
            }
        ]
        
        await agent.initialize(example_tools)
        
        # Test execution
        result = await agent.execute("I need to search for information about Python programming")
        print("Execution result:", result)
        
        # Get capabilities
        capabilities = await agent.get_capabilities()
        print("\nAgent capabilities:", capabilities)
    
    # Run test
    asyncio.run(test_agent())
