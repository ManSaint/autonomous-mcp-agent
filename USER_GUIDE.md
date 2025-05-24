# 🚀 Autonomous MCP Agent - User Guide

**Complete Instructions for Using Your Production-Ready Autonomous MCP Agent**

---

## 📋 **Table of Contents**
1. [Quick Start Guide](#quick-start-guide)
2. [Claude Desktop Setup](#claude-desktop-setup)
3. [Available Tools & Capabilities](#available-tools--capabilities)
4. [Usage Examples](#usage-examples)
5. [Advanced Workflows](#advanced-workflows)
6. [Troubleshooting](#troubleshooting)
7. [Performance Optimization](#performance-optimization)

---

## 🚀 **Quick Start Guide**

### **Prerequisites**
- Python 3.8+ installed
- Claude Desktop application
- Git (for repository management)
- Internet connection (for MCP tool discovery)

### **Installation Steps**

#### 1. Clone the Repository
```bash
git clone https://github.com/ManSaint/autonomous-mcp-agent.git
cd autonomous-mcp-agent
```

#### 2. Install Dependencies
```bash
# Install core dependencies
pip install -r requirements.txt

# Install MCP-specific dependencies
pip install -r requirements_mcp.txt
```

#### 3. Verify Installation
```bash
# Test the framework
python -m pytest tests/ -v

# Test Phase 4 integration
python -c "from autonomous_mcp.mcp_protocol import MCPProtocolBridge; print('✅ Installation successful!')"
```

---

## 🖥️ **Claude Desktop Setup**

### **Method 1: Automatic Configuration**
```bash
# Run the deployment script
python deploy/startup_script.py
```

### **Method 2: Manual Configuration**
1. **Locate Claude Desktop Config**:
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **Mac**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`

2. **Add MCP Server Configuration**:
```json
{
  "mcpServers": {
    "autonomous-mcp-agent": {
      "command": "python",
      "args": ["D:/Development/Autonomous-MCP-Agent/mcp_server.py"],
      "env": {}
    }
  }
}
```

3. **Restart Claude Desktop**

### **Verification**
- Open Claude Desktop
- Look for autonomous agent tools in the tool list
- You should see 7 new autonomous tools available

---

## 🛠️ **Available Tools & Capabilities**

### **🤖 Autonomous Agent Tools (7 Tools)**

#### 1. **execute_autonomous_task**
**Purpose**: Execute complex tasks with intelligent planning and monitoring
```
Usage: "Execute autonomous task: Research AI trends and create a summary report"
```
**Features**:
- Intelligent task decomposition
- Automatic tool selection
- Progress monitoring
- Error recovery
- Performance optimization

#### 2. **discover_available_tools**  
**Purpose**: Discover and categorize all available MCP tools
```
Usage: "Discover available tools for data processing"
```
**Features**:
- Real-time tool discovery
- Capability-based filtering
- Performance metrics
- Tool recommendations

#### 3. **create_intelligent_workflow**
**Purpose**: Generate sophisticated multi-step workflows
```
Usage: "Create workflow for: Search news, analyze sentiment, create report"
```
**Features**:
- Workflow templates
- Dependency management
- Parallel execution planning
- Risk assessment
- Duration estimation

#### 4. **analyze_task_complexity**
**Purpose**: Analyze task difficulty and provide recommendations
```
Usage: "Analyze complexity of: Build a web scraping system for e-commerce data"
```
**Features**:
- Complexity scoring (0-10)
- Resource estimation  
- Risk factor identification
- Success probability
- Recommended approach

#### 5. **get_personalized_recommendations**
**Purpose**: ML-powered recommendations based on usage patterns
```
Usage: "Get recommendations for: Automating customer data analysis"
```
**Features**:
- Learning from usage history
- Preference-based suggestions
- Tool affinity scoring
- Optimization tips
- Context-aware recommendations

#### 6. **monitor_agent_performance**
**Purpose**: Real-time performance monitoring and insights
```
Usage: "Monitor performance for the last 24 hours with detailed metrics"
```
**Features**:
- Success rate tracking
- Response time analytics
- Tool usage statistics
- Performance trends
- Health monitoring

#### 7. **configure_agent_preferences**
**Purpose**: Customize agent behavior and preferences
```
Usage: "Configure preferences: prefer thorough analysis, complexity threshold 7"
```
**Features**:
- User preference learning
- Behavior customization
- Performance tuning
- Workflow optimization
- Personalization settings

### **🌐 Real MCP Tools Integration (9+ Tools)**
- **Web Search**: Brave search capabilities
- **Memory Operations**: Knowledge graph management  
- **GitHub Integration**: Repository operations
- **Task Management**: TaskMaster AI integration
- **File Operations**: Desktop Commander
- **Web Scraping**: Firecrawl integration
- **API Documentation**: Context7 integration
- **And many more...**

---

## 💡 **Usage Examples**

### **Example 1: Research and Analysis**
```
Prompt: "Research the latest trends in autonomous AI agents and create a comprehensive report"

Agent Actions:
1. Uses discover_available_tools to find research capabilities
2. Creates intelligent workflow with search → analysis → reporting steps  
3. Executes web searches using real MCP tools
4. Analyzes and synthesizes information
5. Creates structured report with findings
6. Monitors performance throughout process
```

### **Example 2: Development Automation**
```
Prompt: "Find trending machine learning repositories and create development tasks"

Agent Actions:  
1. Analyzes task complexity (moderate-high)
2. Discovers GitHub and task management tools
3. Creates workflow: search repos → analyze trends → create tasks
4. Uses GitHub MCP tools to find trending ML repos
5. Uses TaskMaster integration to create development tasks
6. Provides personalized recommendations for next steps
```

### **Example 3: Data Processing Workflow**
```
Prompt: "Create an automated workflow to process customer feedback data"

Agent Actions:
1. Analyzes requirements and complexity
2. Recommends data processing tools and approaches  
3. Creates intelligent workflow with error handling
4. Sets up monitoring for data processing jobs
5. Configures preferences for similar future tasks
6. Provides optimization recommendations
```

### **Example 4: Multi-Platform Integration**
```
Prompt: "Search security news, create GitHub issue, and add to project board"

Agent Actions:
1. Creates complex multi-step workflow
2. Uses web search tools for security news
3. Integrates with GitHub for issue creation
4. Uses task management for project board updates
5. Monitors each step for success/failure
6. Learns preferences for future security workflows
```

---

## ⚡ **Advanced Workflows**

### **🔗 MCP Chain Workflows** (Your Preferred Method)

#### **Simple Chain Example**:
```json
{
  "mcpPath": [
    {
      "toolName": "brave_web_search",
      "toolArgs": "{\"query\": \"latest AI research 2024\"}"
    },
    {
      "toolName": "memory_create_entities", 
      "toolArgs": "{\"entities\": [{\"name\": \"CHAIN_RESULT\", \"entityType\": \"research\", \"observations\": [\"CHAIN_RESULT\"]}]}",
      "inputPath": "$.results[0].title"
    }
  ]
}
```

#### **Complex Chain with Data Transformation**:
```json
{
  "mcpPath": [
    {
      "toolName": "github_search_repositories",
      "toolArgs": "{\"query\": \"machine learning python\", \"sort\": \"stars\"}"
    },
    {
      "toolName": "analyze_task_complexity",
      "toolArgs": "{\"task_description\": \"CHAIN_RESULT\", \"context\": {}}",
      "inputPath": "$.items[0].description"
    },
    {
      "toolName": "create_intelligent_workflow", 
      "toolArgs": "{\"task_description\": \"CHAIN_RESULT\", \"context\": {}}",
      "inputPath": "$.recommended_approach"
    }
  ]
}
```

#### **Parallel Execution Chain**:
```json
{
  "mcpPath": [
    {
      "toolName": "discover_available_tools",
      "toolArgs": "{\"category_filter\": [\"search\", \"analysis\"]}"
    },
    {
      "toolName": "get_personalized_recommendations",
      "toolArgs": "{\"task_description\": \"data analysis\", \"context\": {\"tools\": \"CHAIN_RESULT\"}}",
      "inputPath": "$.categorized_tools"
    }
  ]
}
```

### **🎯 Advanced Autonomous Workflows**

#### **Research Automation**:
```
1. "Execute autonomous task: Create weekly AI research digest"
   → Agent discovers research tools
   → Creates multi-source search workflow  
   → Analyzes and synthesizes findings
   → Generates formatted report
   → Learns preferences for future research
```

#### **Development Pipeline**:
```  
1. "Create intelligent workflow for CI/CD pipeline setup"
   → Analyzes project requirements
   → Recommends tools and approaches
   → Creates step-by-step implementation plan
   → Monitors setup progress
   → Optimizes based on performance metrics
```

#### **Content Creation Pipeline**:
```
1. "Analyze complexity of: Create automated content generation system"
   → Assesses technical requirements
   → Identifies necessary tools and APIs
   → Estimates timeline and resources
   → Provides risk assessment
   → Recommends implementation strategy
```

---

## 🔧 **Troubleshooting**

### **Common Issues & Solutions**

#### **Issue**: Agent tools not appearing in Claude Desktop
**Solution**:
```bash
# Check MCP server is running
python mcp_server.py

# Verify configuration path
echo $CLAUDE_DESKTOP_CONFIG  # Mac/Linux
echo %APPDATA%\Claude\claude_desktop_config.json  # Windows

# Restart Claude Desktop after configuration changes
```

#### **Issue**: Tool discovery returning empty results  
**Solution**:
```bash
# Test discovery system
python -c "from autonomous_mcp.real_mcp_discovery import RealMCPDiscovery; print(RealMCPDiscovery().discover_all_tools())"

# Check network connectivity
# Verify MCP servers are accessible
```

#### **Issue**: Performance degradation
**Solution**:
```bash
# Monitor performance
python -c "from autonomous_mcp.monitoring import MonitoringSystem; ms = MonitoringSystem(); print(ms.get_system_dashboard_data())"

# Clear caches if needed
python -c "from autonomous_mcp.discovery import ToolDiscovery; ToolDiscovery().clear_cache()"
```

#### **Issue**: Chain execution failures
**Solution**:
```bash
# Validate chain configuration
# Check tool compatibility  
# Review error logs in logs/ directory
# Test individual tools separately
```

### **Debugging Tips**

#### **Enable Detailed Logging**:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### **Check Component Health**:
```python
from autonomous_mcp.monitoring import MonitoringSystem
ms = MonitoringSystem()
health = ms.check_system_health()
print(health)
```

#### **Test Individual Components**:
```bash
# Test core framework
python -m pytest tests/test_discovery.py -v

# Test MCP integration  
python -m pytest tests/test_mcp_server_integration.py -v

# Test real tool discovery
python examples/test_real_discovery.py
```

---

## ⚡ **Performance Optimization**

### **🚀 Speed Optimization**

#### **Tool Discovery Caching**:
```python
# Tools are cached automatically
# Clear cache only when needed:
discovery.clear_cache()
```

#### **Workflow Optimization**:
- Use parallel execution when possible
- Cache frequently used workflows
- Optimize tool selection based on performance metrics
- Monitor and adjust based on usage patterns

#### **Resource Management**:
- Monitor memory usage during complex workflows
- Use streaming for large data processing
- Implement proper cleanup for long-running tasks

### **🎯 Accuracy Optimization**  

#### **Preference Learning**:
- Let the agent learn from your usage patterns
- Provide feedback on tool recommendations
- Configure preferences for consistent behavior

#### **Error Recovery**:
- Built-in retry mechanisms
- Fallback tool selection
- Graceful degradation for partial failures

#### **Quality Monitoring**:
- Track success rates for different task types
- Monitor and improve tool selection accuracy
- Analyze performance trends over time

---

## 📊 **Monitoring & Analytics**

### **Real-Time Monitoring**
```python
# Get current performance metrics
monitor_agent_performance("24h", include_details=True)

# View system health
check_system_health()

# Track tool usage patterns  
get_tool_usage_statistics()
```

### **Performance Analytics**
- Success rate tracking by task type
- Response time optimization
- Tool effectiveness metrics
- User satisfaction scoring
- Resource utilization monitoring

### **Reporting**
- Automated performance reports
- Usage pattern analysis
- Recommendation accuracy tracking
- System health summaries
- Trend analysis and predictions

---

## 🎉 **Best Practices**

### **🎯 Task Formulation**
- Be specific about desired outcomes
- Provide context and constraints
- Break complex tasks into phases when needed
- Use natural language descriptions

### **⚛️ Workflow Design**  
- Leverage mcp_chain for multi-step processes
- Use tool discovery before complex workflows
- Monitor performance of custom workflows
- Learn from successful patterns

### **🔧 Maintenance**
- Regular performance monitoring
- Update preferences based on usage
- Clear caches periodically
- Keep MCP tools updated

### **🛡️ Error Handling**
- Review error logs regularly
- Test critical workflows periodically  
- Have backup plans for important processes
- Monitor system health proactively

---

## 🚀 **Next Steps**

1. **Start with Simple Tasks**: Begin with basic autonomous tasks to learn the system
2. **Explore Tool Discovery**: Use discover_available_tools to see all capabilities  
3. **Build Custom Workflows**: Create mcp_chain workflows for repeated processes
4. **Monitor Performance**: Use performance monitoring to optimize usage
5. **Configure Preferences**: Set up personalization for better recommendations
6. **Scale Gradually**: Move from simple to complex autonomous workflows

---

**🎉 Congratulations! You now have a complete autonomous MCP agent ready for production use with full mcp_chain workflow support!**

**Need Help?** Check the troubleshooting section or review the comprehensive test suite in the `tests/` directory for usage examples.
