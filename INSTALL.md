# 🚀 Installation & Setup Guide

**Get your Autonomous MCP Agent running in minutes**

---

## 📋 Prerequisites

- **Python 3.8+** installed on your system
- **Claude Desktop** application installed
- **Git** for cloning the repository
- **Internet connection** for tool discovery

---

## ⚡ Quick Installation

### 1. Clone Repository
```bash
git clone https://github.com/ManSaint/autonomous-mcp-agent.git
cd autonomous-mcp-agent
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
pip install -r requirements_mcp.txt
```

### 3. Configure Claude Desktop
**Option A - Automatic (Recommended):**
```bash
python deploy/startup_script.py
```

**Option B - Manual:**
Add this to your Claude Desktop config file:
```json
{
  "mcpServers": {
    "autonomous-mcp-agent": {
      "command": "python",
      "args": ["/full/path/to/autonomous-mcp-agent/mcp_server.py"],
      "env": {}
    }
  }
}
```

**Config file locations:**
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Mac**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

### 4. Restart Claude Desktop
Close and reopen Claude Desktop to load the new tools.

### 5. Verify Installation
You should see **7 new autonomous agent tools** available in Claude Desktop:
- execute_autonomous_task
- discover_available_tools
- create_intelligent_workflow
- analyze_task_complexity
- get_personalized_recommendations
- monitor_agent_performance
- configure_agent_preferences

---

## ✅ Test Your Installation

### Quick Test
Try this command in Claude Desktop:
```
"Execute autonomous task: Test the autonomous agent by finding available tools and creating a simple workflow"
```

### Advanced Test
```bash
# Run the test suite
python -m pytest tests/ -v

# Test tool discovery
python -c "from autonomous_mcp.real_mcp_discovery import RealMCPDiscovery; print(f'Discovered {len(RealMCPDiscovery().discover_all_tools())} MCP tools')"
```

---

## 🎯 First Usage Examples

### Simple Task
```
"Execute autonomous task: Research Python best practices and summarize the key points"
```

### Tool Discovery
```
"Discover available tools for web development"
```

### Workflow Creation
```
"Create intelligent workflow for: Search trending GitHub repos, analyze their popularity, and create a report"
```

### Performance Monitoring
```
"Monitor agent performance for the last hour"
```

---

## 🛟 Troubleshooting

### Tools Not Showing in Claude Desktop?
1. Check that the MCP server starts without errors:
   ```bash
   python mcp_server.py
   ```
2. Verify your Claude Desktop config file has the correct path
3. Restart Claude Desktop completely
4. Check the Claude Desktop logs for errors

### Tool Discovery Issues?
```bash
# Test tool discovery
python -c "from autonomous_mcp.real_mcp_discovery import RealMCPDiscovery; rd = RealMCPDiscovery(); tools = rd.discover_all_tools(); print(f'Found {len(tools)} tools: {list(tools.keys())[:5]}...')"
```

### Performance Problems?
```bash
# Check system health
python -c "from autonomous_mcp.monitoring import MonitoringSystem; ms = MonitoringSystem(); print(ms.check_system_health())"
```

### Permission Issues?
- Ensure Python has proper permissions to access files
- On Windows, try running as administrator
- Check that the installation directory is writable

---

## 🔄 Updating

To update to the latest version:
```bash
cd autonomous-mcp-agent
git pull origin main
pip install -r requirements.txt
pip install -r requirements_mcp.txt
# Restart Claude Desktop
```

---

## 🚀 What's Next?

1. **Start Simple** - Try basic autonomous tasks to see how the agent works
2. **Explore Tools** - Use `discover_available_tools` to see all capabilities
3. **Create Workflows** - Let the agent design complex multi-step processes
4. **Monitor Performance** - Watch how the agent learns and optimizes over time
5. **Customize Preferences** - Configure the agent to match your working style

**The agent will automatically discover the best tools and workflows for any task you give it!**

---

*Need more help? Check the [Development Guide](DEVELOPMENT_GUIDE.md) or create an issue on GitHub.*
