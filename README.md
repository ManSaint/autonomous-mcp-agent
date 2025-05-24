# Autonomous MCP Agent

An intelligent agent that automatically discovers, plans, and executes MCP (Model Context Protocol) tool chains to accomplish complex user tasks.

## 🚀 Features

- **Automatic Tool Discovery**: Categorizes and indexes available MCP tools
- **Intelligent Planning**: Creates execution plans with dependency resolution
- **Chain Execution**: Executes complex workflows using mcp_chain
- **Self-Improving**: Learns from usage patterns to optimize performance

## 📦 Current Status

**Phase 1: Core Components** (50% Complete)
- ✅ Tool Discovery System
- ✅ Basic Execution Planner
- ⏳ Chain Executor (Next)
- ⏳ Integration Testing

## 🛠️ Installation

```bash
# Clone the repository
git clone https://github.com/ManSaint/autonomous-mcp-agent.git
cd autonomous-mcp-agent

# Install dependencies (coming soon)
pip install -r requirements.txt
```

## 📖 Quick Start

```python
from autonomous_mcp.planner import BasicExecutionPlanner

# Create a planner
planner = BasicExecutionPlanner()

# Create a simple plan
plan = planner.create_linear_plan(
    ['brave_web_search', 'web_fetch', 'create_entities'],
    "Research a topic and save findings",
    [
        {'query': 'MCP tools'},
        {'url': 'https://example.com'},  
        {'entities': [...]}
    ]
)

# Validate the plan
is_valid, errors = plan.validate()
```

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_planner.py -v
```

## 📄 License

MIT License - see LICENSE file for details.
