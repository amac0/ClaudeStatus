# ABOUTME: Main Claude status display script for showing project status information
# ABOUTME: Displays last user prompt, git commit message, and current todo list

#!/usr/bin/env python3

import argparse
import os
import shutil
import time
from pathlib import Path
from typing import Optional, Tuple

from src.git_integration import GitIntegration
from src.jsonl_parser import JSONLParser


class Colors:
    """ANSI color codes for terminal output"""

    CYAN = "\033[96m"  # For prompt section
    GREEN = "\033[92m"  # For git section
    YELLOW = "\033[93m"  # For todos section
    RESET = "\033[0m"  # Reset to default


def get_minutes_ago(timestamp_seconds: float) -> int:
    """Calculate minutes ago from a timestamp

    Args:
        timestamp_seconds: Unix timestamp in seconds

    Returns:
        Number of minutes ago (rounded)
    """
    current_time = time.time()
    seconds_ago = current_time - timestamp_seconds
    return round(seconds_ago / 60)


def get_current_todo_with_status(todos: list) -> Tuple[str, bool]:
    """Get the most current todo with completion status

    Args:
        todos: List of todo dictionaries

    Returns:
        Tuple of (todo_text, is_completed)
    """
    if not todos:
        return "No todos", False

    # First look for in_progress todos
    for todo in todos:
        if todo.get("status") == "in_progress":
            return todo.get("content", "Unknown todo"), False

    # If no in_progress, find the first pending todo
    for todo in todos:
        if todo.get("status") == "pending":
            return todo.get("content", "Unknown todo"), False

    # If all completed, return the last one
    last_todo = todos[-1]
    is_completed = last_todo.get("status") == "completed"
    return last_todo.get("content", "Unknown todo"), is_completed


def get_default_jsonl_path(cwd: Optional[str] = None) -> Optional[Path]:
    """Get the default JSONL file path based on current working directory

    Args:
        cwd: Current working directory. If None, uses os.getcwd()

    Returns:
        Path to the most recent JSONL file, or None if not found
    """
    if cwd is None:
        cwd = os.getcwd()

    # Convert path to folder name (e.g., /var/home/a/Code/ClaudeStatus -> -var-home-a-Code-ClaudeStatus)  # noqa: E501
    folder_name = cwd.replace("/", "-")

    # Base directory for Claude projects
    base_dir = Path.home() / ".claude" / "projects" / folder_name

    if not base_dir.exists():
        return None

    # Find most recent .jsonl file
    jsonl_files = list(base_dir.glob("*.jsonl"))
    if not jsonl_files:
        return None

    # Sort by modification time, most recent first
    jsonl_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return jsonl_files[0]


def format_todo_status(todos: list, detailed: bool = False) -> str:
    """Format todo list for display

    Args:
        todos: List of todo dictionaries
        detailed: If True, show full todo list with strikethrough for completed items

    Returns:
        Formatted string representation of todos
    """
    if not todos:
        return "No todos found" if detailed else "No todos"

    if detailed:
        # Show full todo list with checkbox-style markers
        todo_lines = []
        for todo in todos:
            content = todo.get("content", "Unknown todo")
            status = todo.get("status", "unknown")
            priority = todo.get("priority", "")

            # Format checkbox based on completion status
            checkbox = "[x]" if status == "completed" else "[ ]"

            # Format priority marker
            priority_marker = f" [{priority.upper()}]" if priority else ""

            # Format the todo line
            todo_line = f"  {checkbox}{priority_marker} {content}"

            todo_lines.append(todo_line)

        return "\n".join(todo_lines)
    else:
        # Show summary counts
        status_counts: dict[str, int] = {}
        for todo in todos:
            status = todo.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1

        parts = []
        for status, count in status_counts.items():
            parts.append(f"{count} {status}")

        return f"Todos: {', '.join(parts)}"


def display_status(
    jsonl_path: Optional[Path],
    two_line: bool = False,
    terminal_width: Optional[int] = None,
) -> None:
    """Display the current status

    Args:
        jsonl_path: Path to JSONL file to parse
        two_line: Whether to format as two lines
        terminal_width: Terminal width for formatting (auto-detected if None)
    """
    if terminal_width is None:
        terminal_width = shutil.get_terminal_size().columns

    # Initialize components
    parser = JSONLParser()
    git = GitIntegration()

    # Get data with timestamps
    last_prompt = "No user prompt found"
    todos_info = "No todos found"
    git_message = "No git repository"

    # Time information
    prompt_minutes_ago = None
    todos_minutes_ago = None
    git_minutes_ago = None

    if jsonl_path and jsonl_path.exists():
        # Get prompt with timestamp from JSONL entries
        prompt, prompt_timestamp = parser.get_last_user_prompt_with_timestamp(
            jsonl_path
        )
        if prompt:
            last_prompt = prompt
            if prompt_timestamp:
                prompt_minutes_ago = get_minutes_ago(prompt_timestamp)

        # Get todos with timestamp from JSONL entries
        todos, todos_timestamp = parser.get_latest_todo_list_with_timestamp(jsonl_path)
        if todos:
            # Use detailed format for multi-line, summary for two-line
            todos_info = format_todo_status(todos, detailed=not two_line)
            if todos_timestamp:
                todos_minutes_ago = get_minutes_ago(todos_timestamp)

    if git.is_git_repository():
        commit_msg = git.get_last_commit_message()
        commit_timestamp = git.get_last_commit_timestamp()

        if commit_msg:
            git_message = commit_msg
            if commit_timestamp:
                git_minutes_ago = get_minutes_ago(commit_timestamp)
        else:
            git_message = "Git repository (no commits)"

    # Format labels with time information and colors
    prompt_label = f"{Colors.CYAN}Current Prompt"
    if prompt_minutes_ago is not None:
        prompt_label += f" ({prompt_minutes_ago} minutes ago)"
    prompt_label += f"{Colors.RESET}"

    git_label = f"{Colors.CYAN}Last Commit"
    if git_minutes_ago is not None:
        git_label += f" ({git_minutes_ago} minutes ago)"
    git_label += f"{Colors.RESET}"

    todos_label = f"{Colors.CYAN}Last Todos"
    if todos_minutes_ago is not None:
        todos_label += f" ({todos_minutes_ago} minutes ago)"
    todos_label += f"{Colors.RESET}"

    if two_line:
        # Two-line format: prompt on first line, todo --- commit on second line
        # First line: prompt (only truncate if needed)
        line1 = last_prompt
        if len(line1) > terminal_width:
            line1 = line1[: terminal_width - 3] + "..."

        # Second line: checkbox + todo --- commit message
        if todos:
            current_todo_text, is_completed = get_current_todo_with_status(todos)
            checkbox = "[x]" if is_completed else "[ ]"
            todo_with_checkbox = f"{checkbox} {current_todo_text}"
        else:
            todo_with_checkbox = "[ ] No todos"

        # Build second line with separator
        separator = " --- "
        line2_parts = [todo_with_checkbox, git_message]

        # Try to fit without truncation first
        line2_full = separator.join(line2_parts)

        if len(line2_full) <= terminal_width:
            # Fits without truncation
            line2 = line2_full
        else:
            # Need to truncate - calculate available space for each part
            separator_space = len(separator)
            available_space = terminal_width - separator_space
            part_space = available_space // 2

            # Truncate parts only if they exceed their allocated space
            truncated_parts = []
            for part in line2_parts:
                if len(part) > part_space:
                    truncated_parts.append(part[: part_space - 3] + "...")
                else:
                    truncated_parts.append(part)

            line2 = separator.join(truncated_parts)

            # Final safety check
            if len(line2) > terminal_width:
                line2 = line2[: terminal_width - 3] + "..."

        print(line1)
        print(line2)
    else:
        # Multi-line format with colors
        print(f"{prompt_label}: {last_prompt}")
        print(f"{git_label}: {git_message}")
        if "\n" in todos_info:
            # Multi-line todo display
            print(f"{todos_label}:")
            print(todos_info)
        else:
            # Single line todo display
            print(f"{todos_label}: {todos_info}")


def main():
    """Main entry point for the Claude status display script"""
    parser = argparse.ArgumentParser(
        description="Display Claude Code project status from JSONL files"
    )
    parser.add_argument(
        "--file",
        type=str,
        help="Path to JSONL file (default: auto-detect from ~/.claude/projects/)",
    )
    parser.add_argument(
        "--two-line",
        action="store_true",
        help="Display status on two lines: prompt, then todo --- commit",
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="Continuously update status display until interrupted",
    )

    args = parser.parse_args()

    # Determine JSONL file path
    if args.file:
        jsonl_path = Path(args.file)
    else:
        jsonl_path = get_default_jsonl_path()

    if args.update:
        try:
            while True:
                # Clear screen and display status
                if not args.two_line:
                    os.system("clear" if os.name == "posix" else "cls")  # nosec B605

                display_status(jsonl_path, args.two_line)

                if args.two_line:
                    # For two-line mode, just refresh in place
                    print("\r", end="")
                else:
                    print("\n--- Refreshing in 5 seconds (Ctrl+C to exit) ---")

                time.sleep(5)
        except KeyboardInterrupt:
            if not args.two_line:
                print("\nExiting...")
    else:
        # Single display
        display_status(jsonl_path, args.two_line)


if __name__ == "__main__":
    main()
