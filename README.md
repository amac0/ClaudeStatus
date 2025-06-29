# ClaudeStatus

A Python utility that displays the current status of your Claude Code projects by parsing JSONL conversation files and combining them with git repository information.

## Overview

ClaudeStatus provides a quick way to see what you were last working on in a Claude Code session. It displays:
- **Last user prompt** - The most recent question or request you sent to Claude
- **Latest git commit** - Your most recent commit message
- **Current todo list** - Active todos from your Claude session (only if created after the last prompt)

All information includes timestamps showing how long ago each item occurred.

## Installation

Clone this repository and ensure you have Python 3.8+ installed:

```bash
git clone <repository-url>
cd ClaudeStatus
pip install -r requirements.txt  # If requirements.txt exists
```

## Usage

### Basic Usage

Display the current project status:

```bash
python claude_status.py
```

**Sample Output:**
```
Prompt (0 minutes ago): Write a detailed Readme.md that gives the various user use cases. Also include sample results from the tool.
Commit (31 minutes ago): Fix todo filtering to only display todos created after last user prompt
Todos (0 minutes ago):
  [ ] [HIGH] Create comprehensive README.md with user use cases and examples
```

### Two-Line Compact Mode

For terminal integrations or status bars, use the compact two-line format:

```bash
python claude_status.py --two-line
```

**Sample Output:**
```
Write a detailed Readme.md that gives the various user use cases. Also include...
[ ] Create comprehensive README.md with user use cases and examples --- Fix todo filtering to only display todos created after last user prompt
```

### Custom JSONL File

Specify a custom JSONL file location:

```bash
python claude_status.py --file /path/to/your/conversation.jsonl
```

### Live Updates

Continuously monitor and update the status display:

```bash
python claude_status.py --update
```

The display refreshes every 5 seconds by default. You can specify a custom interval:

```bash
python claude_status.py --update 3  # Update every 3 seconds
```

Use `Ctrl+C` to exit update mode.

## User Use Cases

### 1. Project Context Recovery
**Use Case:** You return to a project after a break and want to quickly understand where you left off.

**Command:** `python claude_status.py`

**Sample Output:**
```
Prompt (45 minutes ago): Debug the authentication error in the login function
Commit (12 minutes ago): Add error logging to auth module
Todos (30 minutes ago):
  [x] [HIGH] Identify root cause of auth failure
  [ ] [MEDIUM] Implement better error messages
  [ ] [LOW] Add unit tests for auth edge cases
```

### 2. Terminal Integration
**Use Case:** Add Claude project status to your shell prompt or status bar.

**Command:** `python claude_status.py --two-line`

**Sample Output:**
```
Debug the authentication error in the login function
[x] Identify root cause of auth failure --- Add error logging to auth module
```

### 3. Team Status Updates
**Use Case:** Quickly generate a status update for team standups or progress reports.

**Command:** `python claude_status.py`

**Sample Output:**
```
Prompt (2 hours ago): Implement user registration with email verification
Commit (1 hour ago): Add email service integration and validation logic
Todos (90 minutes ago):
  [x] [HIGH] Set up email service configuration
  [x] [HIGH] Create user registration endpoint
  [ ] [MEDIUM] Add email verification flow
  [ ] [LOW] Write tests for registration process
```

### 4. Multi-Project Monitoring
**Use Case:** Monitor multiple Claude projects by specifying different JSONL files.

**Command:**
```bash
# Project A
python claude_status.py --file ~/.claude/projects/project-a/conversation.jsonl

# Project B
python claude_status.py --file ~/.claude/projects/project-b/conversation.jsonl
```

### 5. Development Workflow Integration
**Use Case:** Continuously monitor progress while working on long-running tasks.

**Command:** `python claude_status.py --update 10`

The display will refresh every 10 seconds, showing real-time updates as you interact with Claude and make git commits.

### 6. Quick Progress Check
**Use Case:** Rapidly check if there are any pending todos without switching contexts.

**Command:** `python claude_status.py --two-line`

**Sample Output - Active Work:**
```
Refactor the database connection pooling logic
[ ] Implement connection retry logic --- Optimize database query performance
```

**Sample Output - Work Complete:**
```
Refactor the database connection pooling logic
Implement connection pooling with retry logic and monitoring
```

## File Location Logic

ClaudeStatus automatically detects your JSONL files using this logic:

1. **Base Directory:** `~/.claude/projects/`
2. **Project Folder:** Current working directory converted to folder name
   - Example: `/var/home/a/Code/ClaudeStatus` → `var-home-a-Code-ClaudeStatus`
3. **JSONL File:** Most recent `.jsonl` file in the project folder

Full example path: `~/.claude/projects/var-home-a-Code-ClaudeStatus/conversation-2025-06-29.jsonl`

## Output Format Details

### Standard Multi-Line Format
- **Colored labels** with timestamps in parentheses
- **Prompt section** shows your last request to Claude
- **Commit section** shows your most recent git commit message
- **Todos section** displays active todos with checkbox format:
  - `[ ]` for pending/in-progress todos
  - `[x]` for completed todos
  - Priority levels shown as `[HIGH]`, `[MEDIUM]`, `[LOW]`

### Two-Line Compact Format
- **Line 1:** Last user prompt (truncated if too long)
- **Line 2:** Current todo with checkbox + "---" + commit message
- Automatically truncates text to fit terminal width
- Ideal for terminal integrations and status bars

### Todo Filtering
- Only displays todos created **after** your last user prompt
- This prevents showing stale todos from previous work sessions
- Ensures the displayed todos are relevant to your current context

## Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--file FILE` | Path to specific JSONL file | Auto-detect from `~/.claude/projects/` |
| `--two-line` | Compact two-line display format | Multi-line format |
| `--update [SECONDS]` | Continuously update display | Single display (no updates) |
| `--help` | Show help message and exit | - |

## Development

### Running Tests
```bash
python -m pytest
python -m pytest -v  # Verbose output
```

### Code Formatting
```bash
ruff format      # Format code
ruff check       # Check for issues
```

### Project Structure
```
ClaudeStatus/
├── claude_status.py      # Main script
├── src/
│   ├── jsonl_parser.py   # JSONL file parsing
│   └── git_integration.py # Git repository integration
├── tests/                # Test files
└── README.md            # This file
```

## Error Handling

- **No JSONL file found:** Displays "No user prompt found"
- **No git repository:** Shows "No git repository"
- **No git commits:** Shows "Git repository (no commits)"
- **No todos:** Shows "No todos found" or omits todos section
- **File parsing errors:** Gracefully skips malformed entries

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
