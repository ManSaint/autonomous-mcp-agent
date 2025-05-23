import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class AnalysisResult:
    """Result of message analysis."""
    intent: str
    actions: List[str]
    entities: Dict[str, Any]
    constraints: Dict[str, Any]
    confidence: float


class MessageAnalyzer:
    """
    Analyzes user messages to understand intent and required actions.
    """
    
    def __init__(self):
        # Intent patterns
        self.intent_patterns = {
            'research': r'(research|find|search|look up|investigate)',
            'create': r'(create|make|build|generate|write)',
            'analyze': r'(analyze|examine|study|review|evaluate)',
            'modify': r'(update|modify|change|edit|fix)',
            'summarize': r'(summarize|summary|brief|overview)',
            'compare': r'(compare|contrast|versus|vs|difference)',
        }
        
        # Entity patterns
        self.entity_patterns = {
            'url': r'https?://[^\s]+',
            'file': r'\b\w+\.(py|js|md|txt|json|yaml|yml)\b',
            'github': r'github\.com/[^\s]+',
            'code_language': r'\b(python|javascript|typescript|java|c\+\+|rust)\b',
        }
        
        # Action verb mapping
        self.action_mapping = {
            'research': ['search', 'fetch', 'analyze'],
            'create': ['create', 'write', 'generate'],
            'analyze': ['read', 'process', 'evaluate'],
            'modify': ['update', 'edit', 'patch'],
        }
        
    async def analyze(self, message: str, context: Optional[Dict] = None) -> AnalysisResult:
        """
        Analyze a user message to extract intent and requirements.
        
        Args:
            message: The user's message
            context: Optional context from previous interactions
            
        Returns:
            AnalysisResult with extracted information
        """
        # Normalize message
        normalized = message.lower().strip()
        
        # Extract intent
        intent = self._extract_intent(normalized)
        
        # Extract entities
        entities = self._extract_entities(message)
        
        # Determine required actions
        actions = self._determine_actions(intent, entities, normalized)
        
        # Extract constraints
        constraints = self._extract_constraints(normalized)
        
        # Calculate confidence
        confidence = self._calculate_confidence(intent, actions, entities)
        
        return AnalysisResult(
            intent=intent,
            actions=actions,
            entities=entities,
            constraints=constraints,
            confidence=confidence
        )
        
    def _extract_intent(self, message: str) -> str:
        """Extract the primary intent from the message."""
        scores = {}
        
        for intent, pattern in self.intent_patterns.items():
            matches = re.findall(pattern, message, re.IGNORECASE)
            scores[intent] = len(matches)
            
        # Get highest scoring intent
        if scores:
            primary_intent = max(scores, key=scores.get)
            if scores[primary_intent] > 0:
                return primary_intent
                
        # Default to general intent
        return 'general'
        
    def _extract_entities(self, message: str) -> Dict[str, List[str]]:
        """Extract entities from the message."""
        entities = {}
        
        for entity_type, pattern in self.entity_patterns.items():
            matches = re.findall(pattern, message, re.IGNORECASE)
            if matches:
                entities[entity_type] = matches
                
        # Extract quoted strings as potential names/titles
        quoted = re.findall(r'"([^"]+)"', message)
        if quoted:
            entities['quoted'] = quoted
            
        # Extract numbers
        numbers = re.findall(r'\b\d+\b', message)
        if numbers:
            entities['numbers'] = numbers
            
        return entities
        
    def _determine_actions(self, intent: str, entities: Dict, message: str) -> List[str]:
        """Determine required actions based on intent and entities."""
        actions = []
        
        # Get base actions for intent
        if intent in self.action_mapping:
            actions.extend(self.action_mapping[intent])
            
        # Add entity-specific actions
        if 'url' in entities:
            actions.append('fetch_url')
        if 'file' in entities:
            actions.append('process_file')
        if 'github' in entities:
            actions.append('github_operation')
            
        # Check for specific keywords
        if 'and' in message:
            actions.append('chain_operations')
        if 'then' in message or 'after' in message:
            actions.append('sequential_operations')
            
        # Remove duplicates while preserving order
        seen = set()
        return [x for x in actions if not (x in seen or seen.add(x))]
        
    def _extract_constraints(self, message: str) -> Dict[str, Any]:
        """Extract constraints and preferences from the message."""
        constraints = {}
        
        # Time constraints
        if 'quickly' in message or 'fast' in message:
            constraints['speed'] = 'fast'
        if 'detailed' in message or 'comprehensive' in message:
            constraints['detail'] = 'high'
        if 'brief' in message or 'short' in message:
            constraints['detail'] = 'low'
            
        # Output format
        if 'markdown' in message:
            constraints['format'] = 'markdown'
        if 'json' in message:
            constraints['format'] = 'json'
            
        # Scope
        if 'latest' in message or 'recent' in message:
            constraints['recency'] = 'latest'
        if 'all' in message:
            constraints['scope'] = 'comprehensive'
            
        return constraints
        
    def _calculate_confidence(self, intent: str, actions: List[str], entities: Dict) -> float:
        """Calculate confidence score for the analysis."""
        confidence = 0.5  # Base confidence
        
        # Increase confidence for clear intent
        if intent != 'general':
            confidence += 0.2
            
        # Increase for specific actions
        if len(actions) > 0:
            confidence += min(0.2, len(actions) * 0.05)
            
        # Increase for identified entities
        if entities:
            confidence += min(0.1, len(entities) * 0.02)
            
        return min(1.0, confidence)