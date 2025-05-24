# 🤖 Autonomous MCP Agent

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-213%2B_Passing-brightgreen.svg)](tests/)
[![Status](https://img.shields.io/badge/Status-Production_Ready-success.svg)]()

**An intelligent autonomous agent that automatically discovers, plans, and executes complex tasks using Model Context Protocol (MCP) tools.**

The agent intelligently selects the best tools and workflows for any task, learns from usage patterns, and provides autonomous task execution with human-like reasoning capabilities.

---

## ✨ Key Features

🧠 **Intelligent Task Execution** - Automatically breaks down complex tasks and creates optimal execution plans  
🔍 **Smart Tool Discovery** - Finds and categorizes the best tools for any task from available MCP servers  
⚡ **Autonomous Workflows** - Creates and executes multi-step workflows with dependency management  
📊 **Performance Learning** - Learns from execution patterns to improve future task performance  
🛡️ **Error Recovery** - Built-in error handling and automatic retry mechanisms  
📈 **Real-time Monitoring** - Tracks performance metrics and provides optimization insights  

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Claude Desktop application
- Internet connection

### Installation

```bash
# Clone the repository
git clone https://github.com/ManSaint/autonomous-mcp-agent.git
cd autonomous-mcp-agent

# Install dependencies
pip install -r requirements.txt
pip install -r requirements_mcp.txt

# Configure Claude Desktop
python deploy/startup_script.py

# Restart Claude Desktop
```

### Verify Installation
After restarting Claude Desktop, you should see **7 new autonomous agent tools** available.

---

## 🛠️ Available Tools

### Core Autonomous Tools

| Tool | Description | Example Usage |
|------|-------------|---------------|
| **execute_autonomous_task** | Executes complex tasks with intelligent planning | "Research AI trends and create a summary report" |
| **discover_available_tools** | Finds and categorizes available MCP tools | "Find tools for web development tasks" |
| **create_intelligent_workflow** | Generates optimized multi-step workflows | "Create workflow for data analysis and visualization" |
| **analyze_task_complexity** | Analyzes task difficulty and provides recommendations | "Analyze complexity of building a web scraper" |
| **get_personalized_recommendations** | Provides ML-powered tool and approach suggestions | "Recommend tools for automating social media posts" |
| **monitor_agent_performance** | Tracks and reports performance metrics | "Show performance metrics for the last 24 hours" |
| **configure_agent_preferences** | Customizes agent behavior and learning | "Configure preferences for thorough analysis" |

### Real MCP Tool Integration
The agent automatically discovers and integrates with available MCP servers, including:
- **Web Search & Research** - Brave Search, web scraping tools
- **Development Tools** - GitHub operations, code analysis
- **Task Management** - Project planning, task tracking
- **Data Processing** - File operations, data transformation
- **Documentation** - API docs, knowledge management
- **And many more...**

---

## 💡 Usage Examples

### Simple Task Execution
```
"Execute autonomous task: Research the latest Python frameworks and create a comparison table"
```
**What happens:**
1. Agent analyzes task complexity
2. Discovers relevant research and analysis tools
3. Creates optimized workflow: search → analyze → format → present
4. Executes workflow with monitoring
5. Provides comprehensive results with performance metrics

### Workflow Creation
```
"Create intelligent workflow for: Monitor GitHub repos, analyze issues, create weekly report"
```
**What happens:**
1. Agent designs multi-step workflow
2. Identifies required tools and dependencies
3. Estimates execution time and success probability
4. Provides detailed workflow plan with optimization suggestions

### Tool Discovery
```
"Discover available tools for machine learning development"
```
**What happens:**
1. Agent scans all connected MCP servers
2. Categorizes tools by capability and use case
3. Provides recommendations based on task requirements
4. Shows performance metrics for each tool

---

## 🏗️ How It Works

### Intelligent Planning Process
1. **Task Analysis** - Breaks down complex requests into manageable components
2. **Tool Discovery** - Automatically finds the best available tools for each component
3. **Workflow Generation** - Creates optimized execution plans with dependency management
4. **Execution & Monitoring** - Runs workflows with real-time performance tracking
5. **Learning & Optimization** - Learns from results to improve future performance

### Autonomous Decision Making
The agent uses advanced algorithms to:
- **Select optimal tools** based on performance history and task requirements
- **Create efficient workflows** with parallel execution when possible
- **Handle errors gracefully** with automatic retry and fallback mechanisms
- **Learn from usage patterns** to improve recommendations over time
- **Adapt to user preferences** while maintaining optimal performance

---

## 📊 Advanced Features

### Performance Monitoring
- Real-time execution metrics
- Success rate tracking by task type
- Tool performance analytics
- Optimization recommendations

### Learning Capabilities
- Adaptive tool selection based on success patterns
- User preference learning from feedback
- Workflow optimization from execution history
- Context-aware recommendations

### Error Recovery
- Automatic retry mechanisms with exponential backoff
- Intelligent fallback tool selection
- Graceful degradation for partial failures
- Comprehensive error reporting and analysis

---

## 🔧 Configuration

### Claude Desktop Setup
The agent automatically configures Claude Desktop during installation. For manual setup:

1. Locate your Claude Desktop config file:
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **Mac**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`

2. Add the MCP server configuration:
```json
{
  "mcpServers": {
    "autonomous-mcp-agent": {
      "command": "python",
      "args": ["/path/to/autonomous-mcp-agent/mcp_server.py"],
      "env": {}
    }
  }
}
```

3. Restart Claude Desktop

### Environment Variables
No additional environment variables are required. The agent automatically discovers and connects to available MCP servers.

---

## 🧪 Testing

Run the test suite to verify installation:

```bash
# Run all tests
python -m pytest tests/ -v

# Run integration tests
python -m pytest tests/test_mcp_server_integration.py -v

# Test specific components
python -m pytest tests/test_discovery.py tests/test_executor.py -v
```

**Test Coverage**: 213+ tests covering all core functionality and integration scenarios.

---

## 📚 Documentation

- **[Development Guide](DEVELOPMENT_GUIDE.md)** - Setup for developers and contributors
- **[API Documentation](docs/)** - Detailed API reference and examples
- **[Architecture Overview](docs/architecture.md)** - System design and component details

---

## 🤝 Contributing

We welcome contributions! Please see our [Development Guide](DEVELOPMENT_GUIDE.md) for:
- Development environment setup
- Code style and testing standards
- Pull request process
- Architecture guidelines

---

## 🛟 Troubleshooting

### Common Issues

**Tools not appearing in Claude Desktop?**
```bash
# Check MCP server status
python mcp_server.py

# Verify configuration
python -c "import json; print(json.load(open('deploy/claude_desktop_config.json')))"

# Restart Claude Desktop
```

**No tools discovered?**
```bash
# Test tool discovery
python -c "from autonomous_mcp.real_mcp_discovery import RealMCPDiscovery; print(f'Found {len(RealMCPDiscovery().discover_all_tools())} tools')"
```

**Performance issues?**
```bash
# Check system health
python -c "from autonomous_mcp.monitoring import MonitoringSystem; print(MonitoringSystem().check_system_health())"
```

For more troubleshooting help, see the [Development Guide](DEVELOPMENT_GUIDE.md#troubleshooting).

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🚀 Get Started

Ready to experience intelligent autonomous task execution? 

1. **Install** the agent following the Quick Start guide above
2. **Try** a simple task: "Execute autonomous task: Research current AI trends"
3. **Explore** the available tools and workflows
4. **Monitor** performance and let the agent learn your preferences

**The agent will automatically discover the best tools and create optimal workflows for any task you give it!**

---

*Built with the [Model Context Protocol (MCP)](https://github.com/modelcontextprotocol) for seamless integration with existing tool ecosystems.*
