# ⚡ Quick Start - Autonomous MCP Agent

**Get your autonomous MCP agent running in 5 minutes!**

## 🚀 **Instant Setup**

### 1. **Prerequisites Check**
- ✅ Python 3.8+ installed
- ✅ Claude Desktop application  
- ✅ Internet connection

### 2. **One-Command Installation**
```bash
# Clone and setup in one go
git clone https://github.com/ManSaint/autonomous-mcp-agent.git
cd autonomous-mcp-agent
pip install -r requirements.txt && pip install -r requirements_mcp.txt
```

### 3. **Configure Claude Desktop**
**Option A - Automatic** (Recommended):
```bash
python deploy/startup_script.py
```

**Option B - Manual**:
Add to your Claude Desktop config:
```json
{
  "mcpServers": {
    "autonomous-mcp-agent": {
      "command": "python", 
      "args": ["D:/Development/Autonomous-MCP-Agent/mcp_server.py"]
    }
  }
}
```

### 4. **Restart Claude Desktop**
- Close and reopen Claude Desktop
- Look for 7 new autonomous agent tools

## 🎯 **First Use - Try These Commands**

### **🤖 Simple Autonomous Task**
```
"Execute autonomous task: Research Python best practices and summarize key points"
```
**What happens**: Agent discovers tools → creates workflow → executes research → provides summary

### **🔍 Discover Available Tools**  
```
"Discover available tools for web development"
```
**What happens**: Agent scans all MCP servers → categorizes tools → shows relevant options

### **⚛️ Create Intelligent Workflow**
```
"Create workflow for: Search GitHub repos, analyze code quality, create report" 
```
**What happens**: Agent builds step-by-step workflow → estimates time → provides execution plan

### **📊 Check Performance**
```
"Monitor agent performance for the last hour"
```
**What happens**: Shows success rates → response times → tool usage → insights

## ⚡ **Advanced: MCP Chain Workflows**

**For power users who prefer chaining tools directly:**

### **Simple Chain**:
```json
{
  "mcpPath": [
    {"toolName": "brave_web_search", "toolArgs": "{\"query\": \"autonomous AI agents\"}"},
    {"toolName": "memory_create_entities", "toolArgs": "{\"entities\": [{\"name\": \"CHAIN_RESULT\", \"entityType\": \"research\"}]}", "inputPath": "$.results[0].title"}
  ]
}
```

### **Multi-Step Analysis Chain**:
```json
{
  "mcpPath": [
    {"toolName": "github_search_repositories", "toolArgs": "{\"query\": \"machine learning\"}"},
    {"toolName": "analyze_task_complexity", "toolArgs": "{\"task_description\": \"CHAIN_RESULT\", \"context\": {}}", "inputPath": "$.items[0].description"},
    {"toolName": "create_intelligent_workflow", "toolArgs": "{\"task_description\": \"CHAIN_RESULT\", \"context\": {}}", "inputPath": "$.recommended_approach"}
  ]
}
```

## 🛠️ **Available Tools (7 Autonomous + 9+ Real MCP)**

### **🤖 Autonomous Agent Tools**:
1. **execute_autonomous_task** - Complex task automation
2. **discover_available_tools** - Smart tool discovery  
3. **create_intelligent_workflow** - Workflow generation
4. **analyze_task_complexity** - Task analysis & recommendations
5. **get_personalized_recommendations** - ML-powered suggestions
6. **monitor_agent_performance** - Performance tracking
7. **configure_agent_preferences** - Personalization settings

### **🌐 Real MCP Tools** (Automatically Discovered):
- Web Search (Brave)
- Memory/Knowledge Graph
- GitHub Operations  
- Task Management (TaskMaster)
- File Operations (Desktop Commander)
- Web Scraping (Firecrawl)
- Documentation (Context7)
- And more...

## 🆘 **Quick Troubleshooting**

### **Tools not showing in Claude Desktop?**
```bash
# Check MCP server
python mcp_server.py

# Verify config location (Windows)
echo %APPDATA%\Claude\claude_desktop_config.json

# Restart Claude Desktop
```

### **No tools discovered?**
```bash
# Test discovery
python -c "from autonomous_mcp.real_mcp_discovery import RealMCPDiscovery; print(len(RealMCPDiscovery().discover_all_tools()))"
```

### **Performance issues?**
```bash
# Check system health
python -c "from autonomous_mcp.monitoring import MonitoringSystem; print(MonitoringSystem().check_system_health())"
```

## 📚 **Learn More**

- **Complete Guide**: See `USER_GUIDE.md` for detailed instructions
- **API Reference**: Check `autonomous_mcp/` directory for code examples  
- **Test Examples**: Browse `tests/` and `examples/` directories
- **Troubleshooting**: Full troubleshooting guide in main documentation

## 🎉 **You're Ready!**

Your autonomous MCP agent is now operational with:
- ✅ **7 Autonomous Tools** for intelligent task execution
- ✅ **9+ Real MCP Tools** for actual operations  
- ✅ **mcp_chain Support** for advanced workflows
- ✅ **Performance Monitoring** for optimization
- ✅ **Learning Capabilities** for personalization

**Start with simple tasks and gradually explore more complex autonomous workflows!**

---

**Need help?** Check `USER_GUIDE.md` for comprehensive instructions and examples.
