# ABOUTME: Main Claude status display script for showing project status information
# ABOUTME: Displays last user prompt, git commit message, and current todo list

#!/usr/bin/env python3

import argparse
import os
import shutil
import time
from pathlib import Path
from typing import Optional

from src.git_integration import GitIntegration
from src.jsonl_parser import JSONLParser


def get_default_jsonl_path(cwd: Optional[str] = None) -> Optional[Path]:
    """Get the default JSONL file path based on current working directory

    Args:
        cwd: Current working directory. If None, uses os.getcwd()

    Returns:
        Path to the most recent JSONL file, or None if not found
    """
    if cwd is None:
        cwd = os.getcwd()

    # Convert path to folder name (e.g., /var/home/a/Code/ClaudeStatus -> var-home-a-Code-ClaudeStatus)  # noqa: E501
    folder_name = cwd.lstrip("/").replace("/", "-")

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


def format_todo_status(todos: list) -> str:
    """Format todo list for display

    Args:
        todos: List of todo dictionaries

    Returns:
        Formatted string representation of todos
    """
    if not todos:
        return "No todos"

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
    one_line: bool = False,
    terminal_width: Optional[int] = None,
) -> None:
    """Display the current status

    Args:
        jsonl_path: Path to JSONL file to parse
        one_line: Whether to format as a single line
        terminal_width: Terminal width for formatting (auto-detected if None)
    """
    if terminal_width is None:
        terminal_width = shutil.get_terminal_size().columns

    # Initialize components
    parser = JSONLParser()
    git = GitIntegration()

    # Get data
    last_prompt = "No user prompt found"
    todos_info = "No todos found"
    git_message = "No git repository"

    if jsonl_path and jsonl_path.exists():
        prompt = parser.get_last_user_prompt(jsonl_path)
        if prompt:
            last_prompt = prompt

        todos = parser.get_latest_todo_list(jsonl_path)
        if todos:
            todos_info = format_todo_status(todos)

    if git.is_git_repository():
        commit_msg = git.get_last_commit_message()
        if commit_msg:
            git_message = f"Last commit: {commit_msg}"
        else:
            git_message = "Git repository (no commits)"

    if one_line:
        # Format as single line with truncation
        status_line = f"Prompt: {last_prompt} | {git_message} | {todos_info}"
        if len(status_line) > terminal_width:
            # Truncate with ellipsis
            status_line = status_line[: terminal_width - 3] + "..."
        print(status_line)
    else:
        # Multi-line format
        print(f"Last User Prompt: {last_prompt}")
        print(f"Git Status: {git_message}")
        print(f"Todo Status: {todos_info}")


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
        "--one-line",
        action="store_true",
        help="Display status on a single line truncated to terminal width",
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
                if not args.one_line:
                    os.system("clear" if os.name == "posix" else "cls")  # nosec B605

                display_status(jsonl_path, args.one_line)

                if args.one_line:
                    # For one-line mode, just refresh in place
                    print("\r", end="")
                else:
                    print("\n--- Refreshing in 5 seconds (Ctrl+C to exit) ---")

                time.sleep(5)
        except KeyboardInterrupt:
            if not args.one_line:
                print("\nExiting...")
    else:
        # Single display
        display_status(jsonl_path, args.one_line)


if __name__ == "__main__":
    main()
