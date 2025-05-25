# Contributing Guide

## Welcome Contributors!

Thank you for your interest in contributing to the Autonomous MCP Agent! This guide will help you get started with contributing to the project.

## Quick Start

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
3. **Create a feature branch** from `main`
4. **Make your changes** with tests
5. **Submit a pull request**

## Development Setup

### Prerequisites

- Python 3.12 or higher
- Git
- Claude Desktop (for testing)

### Setup Development Environment

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/autonomous-mcp-agent.git
cd autonomous-mcp-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
pip install -e .

# Install development tools
pip install pytest black flake8 mypy pre-commit

# Setup pre-commit hooks
pre-commit install
```

## Code Standards

### Code Style

We use **Black** for code formatting and **flake8** for linting:

```bash
# Format code
black autonomous_mcp/ tests/

# Check linting
flake8 autonomous_mcp/ tests/

# Type checking
mypy autonomous_mcp/
```

### Commit Messages

Follow conventional commit format:
```
feat: add new autonomous tool for data processing
fix: resolve error in workflow generation
docs: update API reference for new features
test: add integration tests for monitoring system
```

## Testing

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test categories
python -m pytest tests/test_integration.py -v
python -m pytest tests/test_performance.py -v

# Run with coverage
python -m pytest tests/ --cov=autonomous_mcp --cov-report=html
```

### Writing Tests

All new features must include comprehensive tests:

```python
# tests/test_new_feature.py
import pytest
from autonomous_mcp.new_feature import NewFeature

class TestNewFeature:
    def test_basic_functionality(self):
        feature = NewFeature()
        result = feature.process("test input")
        assert result.success is True
        
    def test_error_handling(self):
        feature = NewFeature()
        with pytest.raises(ValueError):
            feature.process(None)
```

## Project Structure

```
autonomous-mcp-agent/
├── autonomous_mcp/          # Core framework
│   ├── autonomous_tools.py  # Main autonomous tools
│   ├── mcp_protocol.py      # MCP integration
│   ├── real_mcp_discovery.py # Tool discovery
│   └── ...                  # Other components
├── tests/                   # Test suite
├── docs/                    # Documentation
├── examples/               # Usage examples
└── deploy/                 # Deployment scripts
```

## How to Contribute

### Reporting Issues

**Before creating an issue:**
1. Check existing issues to avoid duplicates
2. Use the latest version
3. Provide clear reproduction steps

**Issue Template:**
```markdown
## Problem Description
Brief description of the issue

## Steps to Reproduce
1. Step one
2. Step two
3. Expected vs actual behavior

## Environment
- Python version:
- Operating system:
- Claude Desktop version:

## Additional Context
Any other relevant information
```

### Suggesting Features

We welcome feature suggestions! Please:

1. **Check existing issues** for similar requests
2. **Describe the use case** clearly
3. **Explain the benefits** to users
4. **Consider implementation complexity**

### Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clean, well-documented code
   - Add comprehensive tests
   - Update documentation if needed

3. **Test your changes**
   ```bash
   python -m pytest tests/ -v
   black autonomous_mcp/ tests/
   flake8 autonomous_mcp/ tests/
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

5. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Submit a pull request**
   - Use the PR template
   - Provide clear description
   - Link related issues
   - Request review

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
```

## Areas for Contribution

### High Priority
- **Performance optimizations**
- **Additional autonomous tools**
- **Enhanced error handling**
- **Documentation improvements**

### Medium Priority
- **UI/UX improvements**
- **Additional integrations**
- **Code quality improvements**
- **Test coverage expansion**

### Good First Issues
Look for issues labeled `good first issue` for beginner-friendly contributions.

## Community Guidelines

### Code of Conduct

- **Be respectful** to all contributors
- **Use inclusive language**
- **Focus on constructive feedback**
- **Help newcomers feel welcome**

### Communication

- **GitHub Issues** - Bug reports and feature requests
- **GitHub Discussions** - General questions and community
- **Pull Request Reviews** - Code feedback and collaboration

## Recognition

Contributors are recognized in:
- **README.md** contributors section
- **Release notes** for significant contributions
- **GitHub contributor graphs**

## Getting Help

If you need help:

1. **Check documentation** first
2. **Search existing issues**
3. **Ask in GitHub Discussions**
4. **Tag maintainers** for urgent issues

## Maintainer Guidelines

For project maintainers:

### Review Process
1. **Check code quality** and tests
2. **Verify documentation** updates
3. **Test functionality** manually
4. **Provide constructive feedback**
5. **Merge when ready**

### Release Process
1. **Update version** numbers
2. **Update changelog**
3. **Create release notes**
4. **Tag release** in Git
5. **Update documentation**

Thank you for contributing to the Autonomous MCP Agent! Your efforts help make intelligent automation accessible to everyone.
