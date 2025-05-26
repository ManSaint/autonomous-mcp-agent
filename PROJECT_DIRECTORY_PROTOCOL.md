# PROJECT DIRECTORY PROTOCOL - CRITICAL

## ⚠️ ALWAYS USE THE CORRECT PROJECT DIRECTORY ⚠️

### ✅ CORRECT PROJECT DIRECTORY
```
D:\Development\Autonomous-MCP-Agent
```

### ❌ WRONG DIRECTORIES (NEVER USE)
```
C:\Users\manu_\mcp-test-project          # WRONG - Test directory
C:\Users\manu_\                          # WRONG - User home
C:\                                      # WRONG - Root directory
```

## MANDATORY DIRECTORY CHECK PROTOCOL

### Before ANY File Operations:
1. **ALWAYS verify current directory first**
2. **ALWAYS use absolute path**: `D:\Development\Autonomous-MCP-Agent`
3. **ALWAYS use `/d` flag for Windows**: `cd /d "D:\Development\Autonomous-MCP-Agent"`

### Required Commands for Every Session:
```bash
# 1. Navigate to correct directory
cd /d "D:\Development\Autonomous-MCP-Agent"

# 2. Verify location
dir | findstr "PHASE_9"
# Should show Phase 9 files - confirms correct directory

# 3. Check git status
git status
# Should show phase-10-autonomous-integration branch or main branch
```

### File Creation Protocol:
```bash
# ALWAYS use full absolute paths
write_file(path="D:\Development\Autonomous-MCP-Agent\filename.ext")

# NEVER use relative paths like:
# write_file(path="filename.ext")  # WRONG
# write_file(path=".\filename.ext")  # WRONG
```

### Git Operation Protocol:
```bash
# ALWAYS prefix with directory change
cd /d "D:\Development\Autonomous-MCP-Agent" && git status
cd /d "D:\Development\Autonomous-MCP-Agent" && git add .
cd /d "D:\Development\Autonomous-MCP-Agent" && git commit -m "message"
```

### Directory Verification Checklist:
- [ ] Path contains "D:\Development\Autonomous-MCP-Agent"
- [ ] Directory contains Phase 9 completion files
- [ ] Git repository shows autonomous-mcp project
- [ ] Branch is phase-10-autonomous-integration or main

## CRITICAL REMINDER
**EVERY TIME** before creating files or running git commands:
1. **Verify directory**: `cd /d "D:\Development\Autonomous-MCP-Agent"`
2. **Confirm location**: Look for Phase 9 files
3. **Check git branch**: Ensure correct repository

## PROJECT STRUCTURE REFERENCE
```
D:\Development\Autonomous-MCP-Agent\
├── autonomous_mcp/           # Core MCP implementation
├── docs/                     # Documentation
├── tests/                    # Test suites
├── PHASE_9_*.md             # Phase 9 completion files
├── PHASE_10_*.md            # Phase 10 files (NEW)
├── .git/                    # Git repository
└── README.md                # Project README
```

---
**NEVER FORGET**: `D:\Development\Autonomous-MCP-Agent` is the ONLY correct directory!

**Last Updated**: May 26, 2025 - Directory Protocol Established