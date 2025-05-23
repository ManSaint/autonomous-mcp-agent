# Autonomous MCP Agent - Development Guide

## 🚀 Quick Start for Developers

This guide helps you contribute to the Autonomous MCP Agent project efficiently while avoiding rate limits.

## 📋 Session Workflow

### Starting a New Session

1. **Check Current Status**
   ```bash
   # Read PROJECT_STATUS.md for current progress
   cat PROJECT_STATUS.md
   ```

2. **Load Memory Context**
   ```python
   # Use memory server to recall previous work
   memory.search_nodes("autonomous_mcp")
   ```

3. **Pick Next Task**
   - Find the next unchecked task in current phase
   - Focus on ONE task per session

### During Development

1. **Implement Component**
   ```python
   # Work on single file at a time
   # Example: implementing discovery.py
   ```

2. **Test Incrementally**
   ```python
   # Write tests alongside implementation
   # Run tests before moving to next component
   ```

3. **Save Progress**
   ```python
   # Use memory server for intermediate state
   memory.create_entities([{...}])
   ```

### Ending a Session

1. **Commit Changes**
   ```bash
   # Push completed work to GitHub
   git add .
   git commit -m "Implement [component]"
   git push
   ```

2. **Update Status**
   - Check off completed tasks in PROJECT_STATUS.md
   - Add session notes
   - Update "Next Session Goals"

## 🛠️ Development Best Practices

### To Avoid Rate Limits

1. **Single File Focus**
   - Work on one module at a time
   - Complete before moving to next

2. **Batch Operations**
   - Group related file operations
   - Use `push_files` for multiple files

3. **Efficient Testing**
   - Test core functionality first
   - Add edge cases gradually

4. **Memory Usage**
   - Store complex data structures in memory
   - Retrieve instead of regenerating

### Code Structure

```python
# Each module should follow this pattern
class ModuleName:
    """Clear docstring explaining purpose."""
    
    def __init__(self):
        # Minimal initialization
        pass
        
    async def main_method(self):
        """Core functionality."""
        # Implement incrementally
        pass
```

### Testing Strategy

```python
# tests/test_module.py
import pytest
from autonomous_mcp.module import ModuleName

@pytest.mark.asyncio
async def test_basic_functionality():
    # Test core features first
    pass
    
@pytest.mark.asyncio 
async def test_edge_cases():
    # Add edge cases later
    pass
```

## 📁 Project Structure

```
autonomous-mcp-agent/
├── autonomous_mcp/
│   ├── __init__.py          ✓ Complete
│   ├── agent.py             ✓ Complete
│   ├── analyzer.py          ✓ Complete
│   ├── discovery.py         ⏳ Next
│   ├── planner.py           ⏳ Week 1
│   ├── executor.py          ⏳ Week 1
│   ├── preferences.py       ⏳ Week 2
│   ├── recovery.py          ⏳ Week 3
│   └── learning.py          ⏳ Week 4
├── tests/
│   ├── test_analyzer.py     ⏳ Needed
│   ├── test_discovery.py    ⏳ Next
│   └── ...
├── examples/
│   └── basic_usage.py       ⏳ Week 5
├── docs/
│   └── architecture.md      ⏳ Week 5
├── README.md                ✓ Complete
├── PROJECT_STATUS.md        ✓ Complete
├── DEVELOPMENT_GUIDE.md     ✓ Complete
└── setup.py                 ✓ Complete
```

## 🔧 Implementation Checklist

### For Each Component:

- [ ] Create module file
- [ ] Implement core class
- [ ] Add docstrings
- [ ] Create unit tests
- [ ] Run and pass tests
- [ ] Update imports in `__init__.py`
- [ ] Document in PROJECT_STATUS.md
- [ ] Commit to GitHub

### For Each Phase:

- [ ] Complete all tasks
- [ ] Run integration tests
- [ ] Update documentation
- [ ] Performance benchmarks
- [ ] Move to next phase

## 💡 Tips for Success

1. **Start Small** - Get basic functionality working first
2. **Test Often** - Catch issues early
3. **Document Progress** - Help your future self
4. **Use Memory** - Store complex computations
5. **Ask for Help** - The community is here to support

## 🎯 Next Steps

Ready to contribute? Start with:

1. Read PROJECT_STATUS.md
2. Pick the next uncompleted task
3. Follow this guide
4. Make the agent smarter!

---

*Remember: One step at a time leads to revolutionary results!*