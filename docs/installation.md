# Installation Guide

## Prerequisites

Before installing the Autonomous MCP Agent, ensure you have:

- **Python 3.12 or higher**
- **Claude Desktop application**
- **Git** (for cloning the repository)
- **Administrative privileges** (for system-wide installation)

## Installation Methods

### Method 1: Standard Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/ManSaint/autonomous-mcp-agent.git
   cd autonomous-mcp-agent
   ```

2. **Create Virtual Environment** (Recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Method 2: Development Installation

For contributors and developers:

```bash
git clone https://github.com/ManSaint/autonomous-mcp-agent.git
cd autonomous-mcp-agent
pip install -e .
pip install -r requirements.txt
python -m pytest tests/  # Run tests to verify installation
```

## Claude Desktop Configuration

### Automatic Configuration

Run the setup script:
```bash
python deploy/setup_claude_config.py
```

### Manual Configuration

1. **Locate Claude Desktop Configuration**
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`

2. **Add MCP Server Configuration**
   ```json
   {
     "mcpServers": {
       "autonomous-mcp-agent": {
         "command": "python",
         "args": ["/absolute/path/to/autonomous-mcp-agent/mcp_server.py"],
         "env": {}
       }
     }
   }
   ```

3. **Restart Claude Desktop**

## Verification

### Test the Installation

1. **Start the MCP Server**
   ```bash
   python mcp_server.py
   ```
   
   You should see:
   ```
   [INFO] Autonomous MCP Server initialized successfully
   [INFO] Server ready to accept MCP connections
   ```

2. **Test in Claude Desktop**
   Open Claude Desktop and try:
   ```
   "Create an intelligent workflow for testing the autonomous agent"
   ```

### Run Test Suite

```bash
python -m pytest tests/ -v
```

Expected output:
```
tests/test_integration.py::test_all_tools_available PASSED
tests/test_integration.py::test_tool_functionality PASSED
tests/test_performance.py::test_response_times PASSED
================= 15 passed in 5.23s =================
```

## Troubleshooting

### Common Issues

**Issue: ModuleNotFoundError**
```bash
# Solution: Ensure virtual environment is activated and dependencies installed
pip install -r requirements.txt
```

**Issue: MCP Server Not Connecting**
```bash
# Solution: Check Claude Desktop configuration path
python deploy/verify_config.py
```

**Issue: Permission Denied**
```bash
# Solution: Run with appropriate permissions or use virtual environment
sudo python mcp_server.py  # Linux/macOS
# Or run as administrator on Windows
```

### Logs and Debugging

- **MCP Server Logs**: `logs/mcp_server.log`
- **Claude Desktop Logs**: Check Claude Desktop application logs
- **Verbose Mode**: Add `--verbose` flag to mcp_server.py

### Getting Help

- **Issues**: [GitHub Issues](https://github.com/ManSaint/autonomous-mcp-agent/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ManSaint/autonomous-mcp-agent/discussions)
- **Documentation**: [Full Documentation](README.md)

## Next Steps

After successful installation:

1. **Read the [API Reference](api.md)** to understand available tools
2. **Explore [Usage Examples](examples.md)** for common patterns
3. **Review [Architecture Guide](architecture.md)** for system understanding
4. **Join the community** for support and contributions
