# 📂 Project Structure

```
autonomous-mcp-agent/
├── 📖 README.md                    # Main project overview and features
├── 🚀 INSTALL.md                   # Installation and setup guide
├── 💡 USAGE.md                     # How to use the agent effectively
├── 📄 LICENSE                      # MIT license
├── 📦 requirements.txt             # Core dependencies
├── 📦 requirements_mcp.txt         # MCP-specific dependencies
├── ⚙️ setup.py                     # Package setup configuration
├── 🧪 pytest.ini                  # Test configuration
│
├── 🤖 mcp_server.py               # Main MCP server entry point
│
├── 🧠 autonomous_mcp/             # Core agent framework
│   ├── 🔍 discovery.py           # Tool discovery system
│   ├── ⚡ executor.py             # Chain execution engine
│   ├── 🎯 planner.py             # Basic execution planner
│   ├── 🧠 advanced_planner.py    # AI-powered planning
│   ├── 🎲 smart_selector.py      # ML-based tool selection
│   ├── 👤 user_preferences.py    # User personalization
│   ├── 🛡️ error_recovery.py      # Error handling system
│   ├── 🛟 fallback_manager.py    # Fallback mechanisms
│   ├── 📊 monitoring.py          # Performance monitoring
│   ├── 🔗 mcp_protocol.py        # MCP protocol implementation
│   ├── 🌐 real_mcp_discovery.py  # Real MCP tool integration
│   ├── ⛓️ mcp_chain_executor.py   # Advanced chain execution
│   ├── 🤖 autonomous_tools.py     # Autonomous agent capabilities
│   └── 🏗️ workflow_builder.py     # Intelligent workflow creation
│
├── 🧪 tests/                      # Comprehensive test suite (213+ tests)
│   ├── test_discovery.py         # Tool discovery tests
│   ├── test_executor.py          # Execution engine tests
│   ├── test_monitoring.py        # Monitoring system tests
│   ├── test_mcp_server_integration.py  # MCP integration tests
│   └── ...                       # Additional test modules
│
├── 💼 examples/                   # Usage examples and demonstrations
│   ├── simple_discovery_test.py  # Basic tool discovery example
│   ├── test_real_discovery.py    # Real MCP tool discovery
│   └── production_workflows.py   # Production workflow examples
│
├── 🚀 deploy/                     # Deployment configuration
│   ├── claude_desktop_config.json  # Claude Desktop setup
│   └── startup_script.py         # Automated deployment script
│
└── 📚 docs/                       # Documentation and development guides
    ├── DEVELOPMENT_GUIDE.md       # Developer setup and guidelines
    └── archive/                   # Archived development documents
```

## 🔧 Key Components

### 🤖 **MCP Server** (`mcp_server.py`)
- Main entry point for Claude Desktop integration
- Exposes 7 autonomous agent tools via MCP protocol
- Handles tool discovery, execution, and monitoring

### 🧠 **Core Framework** (`autonomous_mcp/`)
- **Complete autonomous agent capabilities**
- Production-ready with 213+ passing tests
- ML-powered tool selection and workflow optimization
- Real-time performance monitoring and learning

### 🚀 **Deployment** (`deploy/`)
- Automated Claude Desktop configuration
- One-command setup script
- Production deployment helpers

### 🧪 **Testing** (`tests/`)
- Comprehensive test coverage
- Integration tests for MCP functionality
- Performance and reliability validation

---

**Clean, professional structure focused on ease of use and autonomous capabilities.**
