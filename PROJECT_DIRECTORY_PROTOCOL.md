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

# 2. Verify location (after clean restart)
dir | findstr "CLEAN_RESTART_SUMMARY"
# Should show clean restart files - confirms correct directory

# 3. Check git status
git status
# Should show main branch (clean restart)
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
- [ ] Directory contains project files (cleaned after May 26, 2025)
- [ ] Git repository shows autonomous-mcp project
- [ ] Branch is main (after clean restart)

## CRITICAL REMINDER
**EVERY TIME** before creating files or running git commands:
1. **Verify directory**: `cd /d "D:\Development\Autonomous-MCP-Agent"`
2. **Confirm location**: Look for clean restart files
3. **Check git branch**: Ensure correct repository

## PROJECT STRUCTURE REFERENCE (AFTER CLEAN RESTART)
```
D:\Development\Autonomous-MCP-Agent\
├── autonomous_agent/        # NEW: Clean autonomous agent development
│   ├── core/               # Core autonomous logic
│   ├── tools/              # Tool integrations  
│   ├── tests/              # Real tests
│   └── examples/           # Working examples
├── autonomous_mcp/         # MCP protocol implementation
│   └── real_mcp_client.py # Real MCP client
├── minimal_mcp_server.py   # Basic MCP server
├── mcp_server.py          # Full MCP server
├── CLEAN_RESTART_SUMMARY.md # MANDATORY: Updated after each phase
├── PROJECT_DIRECTORY_PROTOCOL.md # This file
├── .git/                  # Git repository
└── README.md              # Project README
```

## 🚨 CRITICAL HONESTY & VERIFICATION PROTOCOL 🚨

### ⚠️ MANDATORY BEFORE ANY CLAIMS OF SUCCESS ⚠️

**NEVER CLAIM SUCCESS WITHOUT ACTUAL TESTING**

1. **TEST BEFORE CLAIMING**: Always run actual tests to verify functionality
2. **NO FAKE DEMOS**: Never accept simulated or hardcoded "success" results  
3. **VERIFY TOOL CALLS**: Ensure code actually calls real tools, not mock functions
4. **CHECK FOR SIMULATION**: Look for fake data returns like `['Result 1', 'Result 2']`
5. **HONEST FAILURE REPORTING**: If something doesn't work, say it doesn't work

### 🔍 VERIFICATION CHECKLIST FOR ANY "WORKING" CODE:

#### Before Claiming Autonomous Execution Works:
- [ ] Code actually calls `web_search()` with real queries
- [ ] Code actually calls `repl()` with real analysis code  
- [ ] Code actually calls `artifacts()` with real content
- [ ] Data flows between tools (not hardcoded responses)
- [ ] Manual test produces real, different results each time
- [ ] No `sleep()` calls masquerading as "execution time"
- [ ] No hardcoded success responses

#### Before Claiming Progress:
- [ ] Run the actual code and observe real behavior
- [ ] Test with different inputs to ensure it's not hardcoded
- [ ] Verify error handling with intentionally bad inputs
- [ ] Check that failures actually fail (not always return success)

#### Red Flags - Signs of Fake Implementation:
- ❌ Always returns "status: completed"
- ❌ Hardcoded response data like "Result 1, Result 2, Result 3"
- ❌ Execution times that are always similar (0.31s, 0.32s)
- ❌ Mock functions that don't call real tools
- ❌ Demos that work perfectly every time without variation

### 🛡️ PROTECTION AGAINST DECEPTION:

#### ALWAYS Ask These Questions:
1. **"Does this code call REAL tools?"**
2. **"Are the results coming from actual execution or simulation?"**  
3. **"What happens if I run this twice - do I get different results?"**
4. **"Can this fail, and if so, what does failure look like?"**

#### NEVER Accept:
- Documentation claims without code verification
- "Success" without seeing actual tool calls
- Demos that can't be modified or rerun with different inputs
- Perfect results that seem too good to be true

### 📋 HONEST STATUS REPORTING PROTOCOL:

#### When Reporting Progress:
```
✅ WORKING: [Specific functionality tested and verified]
🔄 IN PROGRESS: [What's being built, current limitations]
❌ NOT WORKING: [What doesn't work, why it fails]
🎭 SIMULATED: [What's fake/mocked and needs real implementation]
```

#### Required Honesty Statements:
- "I tested this by [specific test method]"
- "This actually calls [specific tools] and produces [real results]"
- "Current limitations: [honest list of what doesn't work]"
- "This is simulated/fake: [list of mock components]"

### 🎯 ZERO TOLERANCE FOR FALSE SUCCESS CLAIMS

**If code is discovered to be fake/simulated after claiming it works:**
1. **Immediately acknowledge the deception**
2. **Clearly state what was fake vs real**
3. **Assess actual usable components**  
4. **Provide honest path forward**
5. **Update all documentation to reflect reality**

### 📚 LESSON LEARNED: May 26, 2025

**What Happened**: Claimed "autonomous execution" was working when it was actually just returning hardcoded fake data. The execution engine had methods like `_execute_step()` that returned mock responses instead of calling real tools.

**Impact**: Hours of wasted effort based on false progress claims.

**Resolution**: This protocol ensures all future claims are verified through actual testing.

## 📋 MANDATORY PHASE COMPLETION PROTOCOL

### 🔄 AFTER EVERY COMPLETED PHASE:

#### 1. COMPREHENSIVE TESTING REQUIREMENT:
- [ ] **Test ALL new functionality manually**
- [ ] **Verify integration with existing components**
- [ ] **Test edge cases and error conditions**
- [ ] **Confirm no regressions in previous functionality**
- [ ] **Document exactly what works and what doesn't**

#### 2. INTEGRATION VERIFICATION:
- [ ] **New code works with minimal_mcp_server.py**
- [ ] **New code works with existing autonomous_agent/ components**
- [ ] **Data flows correctly between all components**
- [ ] **No conflicts or broken dependencies**
- [ ] **All tools still function as expected**

#### 3. MANDATORY DOCUMENTATION UPDATE:
**ALWAYS UPDATE**: `D:\Development\Autonomous-MCP-Agent\CLEAN_RESTART_SUMMARY.md`

Required updates after each phase:
```markdown
## PHASE [X] COMPLETION - [DATE]

### ✅ What Was Completed:
- [Specific functionality implemented]
- [Files created/modified]
- [Tests passed]

### 🔍 Verification Results:
- Manual testing: [Results]
- Integration testing: [Results]  
- Error handling: [Results]
- Performance: [Results]

### ❌ Current Limitations:
- [What still doesn't work]
- [Known issues]
- [Missing functionality]

### 🚀 Next Phase Ready:
- [ ] All phase objectives met
- [ ] Integration verified
- [ ] Documentation updated
- [ ] Ready for next phase
```

#### 4. PHASE GATE APPROVAL:
**DO NOT PROCEED TO NEXT PHASE UNTIL:**
- [ ] **All testing completed successfully**
- [ ] **Integration verified with existing components**  
- [ ] **CLEAN_RESTART_SUMMARY.md updated**
- [ ] **Honest assessment of limitations documented**
- [ ] **Git commit with phase completion**

#### 5. COMPLETE HONESTY REQUIREMENT:
**Before marking phase complete:**
- [ ] **"Does everything I claim to work actually work?"**
- [ ] **"Can I demonstrate this working with different inputs?"**
- [ ] **"What breaks when I try edge cases?"**
- [ ] **"Am I being completely honest about limitations?"**

### 🚨 PHASE COMPLETION FAILURE PROTOCOL:

**If any component doesn't work as claimed:**
1. **STOP IMMEDIATELY** - Do not proceed to next phase
2. **Document the failure honestly** in CLEAN_RESTART_SUMMARY.md
3. **Fix the issue or acknowledge the limitation**
4. **Re-test everything again**
5. **Only proceed when honestly working**

### 🔄 INTEGRATION TESTING CHECKLIST:

**After each phase, verify:**
- [ ] **MCP server still starts and connects**
- [ ] **Previous phase functionality still works**
- [ ] **New functionality integrates cleanly**
- [ ] **No broken imports or dependencies**
- [ ] **Error handling works throughout the system**
- [ ] **Performance hasn't degraded significantly**

### 📊 PHASE PROGRESS TRACKING:

**Maintain in CLEAN_RESTART_SUMMARY.md:**
- Current phase status
- Completion percentage  
- Working components list
- Known limitations list
- Next phase readiness checklist

---
**NEVER FORGET**: 
- `D:\Development\Autonomous-MCP-Agent` is the ONLY correct directory!
- **NEVER CLAIM SUCCESS WITHOUT ACTUAL VERIFICATION!**
- **ALWAYS UPDATE CLEAN_RESTART_SUMMARY.md AFTER EACH PHASE!**
- **NEVER PROCEED TO NEXT PHASE WITHOUT COMPLETE INTEGRATION TESTING!**

**Last Updated**: May 26, 2025 - Added mandatory phase completion and integration protocols