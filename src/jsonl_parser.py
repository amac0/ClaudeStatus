# ABOUTME: Parser for Claude Code JSONL files to extract user prompts and todo lists
# ABOUTME: Handles reading JSONL conversation files and extracting status information

import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple


class JSONLParser:
    """Parser for Claude Code JSONL conversation files"""

    def _parse_timestamp(self, timestamp_str: str) -> Optional[float]:
        """Parse ISO timestamp string to Unix timestamp

        Args:
            timestamp_str: ISO timestamp string (e.g., "2025-06-29T13:33:42.295Z")

        Returns:
            Unix timestamp as float, or None if parsing fails
        """
        try:
            dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            return dt.timestamp()
        except (ValueError, TypeError):
            return None

    def get_last_user_prompt_with_timestamp(
        self, jsonl_path: str | Path
    ) -> Tuple[Optional[str], Optional[float]]:
        """Extract the last user prompt and its timestamp from a JSONL file

        Args:
            jsonl_path: Path to the JSONL file

        Returns:
            Tuple of (prompt_text, timestamp) or (None, None) if not found
        """
        jsonl_path = Path(jsonl_path)
        if not jsonl_path.exists():
            return None, None

        last_user_prompt = None
        last_timestamp = None

        try:
            with open(jsonl_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        entry = json.loads(line)

                        # Check if this is a user message entry
                        if (
                            entry.get("type") == "user"
                            and "message" in entry
                            and entry["message"].get("role") == "user"
                        ):
                            content = entry["message"].get("content")
                            timestamp_str = entry.get("timestamp")

                            if isinstance(content, str):
                                last_user_prompt = content
                            elif isinstance(content, list):
                                # Handle content that might be a list (like in example)
                                for item in content:
                                    if (
                                        isinstance(item, dict)
                                        and item.get("type") == "text"
                                    ):
                                        last_user_prompt = item.get("text", "")
                                    elif isinstance(item, str):
                                        last_user_prompt = item

                            # Parse timestamp if available
                            if timestamp_str:
                                last_timestamp = self._parse_timestamp(timestamp_str)

                    except json.JSONDecodeError:
                        # Skip malformed JSON lines
                        continue

        except (IOError, OSError):
            return None, None

        return last_user_prompt, last_timestamp

    def get_last_user_prompt(self, jsonl_path: str | Path) -> Optional[str]:
        """Extract the last user prompt from a JSONL file

        Args:
            jsonl_path: Path to the JSONL file

        Returns:
            The last user prompt text, or None if no user messages found
        """
        jsonl_path = Path(jsonl_path)
        if not jsonl_path.exists():
            return None

        last_user_prompt = None

        try:
            with open(jsonl_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        entry = json.loads(line)

                        # Check if this is a user message entry
                        if (
                            entry.get("type") == "user"
                            and "message" in entry
                            and entry["message"].get("role") == "user"
                        ):
                            content = entry["message"].get("content")
                            if isinstance(content, str):
                                last_user_prompt = content
                            elif isinstance(content, list):
                                # Handle content that might be a list (like in example)
                                for item in content:
                                    if (
                                        isinstance(item, dict)
                                        and item.get("type") == "text"
                                    ):
                                        last_user_prompt = item.get("text", "")
                                    elif isinstance(item, str):
                                        last_user_prompt = item

                    except json.JSONDecodeError:
                        # Skip malformed JSON lines
                        continue

        except (IOError, OSError):
            return None

        return last_user_prompt

    def get_latest_todo_list_with_timestamp(
        self, jsonl_path: str | Path
    ) -> Tuple[Optional[List[dict]], Optional[float]]:
        """Extract the latest todo list and its timestamp from a JSONL file

        Args:
            jsonl_path: Path to the JSONL file

        Returns:
            Tuple of (todo_list, timestamp) or (None, None) if not found
        """
        jsonl_path = Path(jsonl_path)
        if not jsonl_path.exists():
            return None, None

        latest_todos = None
        latest_timestamp = None

        try:
            with open(jsonl_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        entry = json.loads(line)
                        timestamp_str = entry.get("timestamp")

                        # Check if this is an assistant message with tool usage
                        if (
                            entry.get("type") == "assistant"
                            and "message" in entry
                            and entry["message"].get("role") == "assistant"
                        ):
                            content = entry["message"].get("content", [])
                            if isinstance(content, list):
                                for item in content:
                                    if (
                                        isinstance(item, dict)
                                        and item.get("type") == "tool_use"
                                        and item.get("name") == "TodoWrite"
                                    ):
                                        input_data = item.get("input", {})
                                        todos = input_data.get("todos")
                                        if todos and isinstance(todos, list):
                                            latest_todos = todos
                                            if timestamp_str:
                                                latest_timestamp = (
                                                    self._parse_timestamp(timestamp_str)
                                                )

                        # Also check for tool result with todo data
                        elif entry.get("type") == "user" and "toolUseResult" in entry:
                            tool_result = entry["toolUseResult"]
                            if isinstance(tool_result, dict):
                                new_todos = tool_result.get("newTodos")
                                if new_todos and isinstance(new_todos, list):
                                    latest_todos = new_todos
                                    if timestamp_str:
                                        latest_timestamp = self._parse_timestamp(
                                            timestamp_str
                                        )

                    except json.JSONDecodeError:
                        # Skip malformed JSON lines
                        continue

        except (IOError, OSError):
            return None, None

        return latest_todos, latest_timestamp

    def get_latest_todo_list(self, jsonl_path: str | Path) -> Optional[List[dict]]:
        """Extract the latest todo list from a JSONL file

        Args:
            jsonl_path: Path to the JSONL file

        Returns:
            The latest todo list, or None if no todo lists found
        """
        jsonl_path = Path(jsonl_path)
        if not jsonl_path.exists():
            return None

        latest_todos = None

        try:
            with open(jsonl_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        entry = json.loads(line)

                        # Check if this is an assistant message with tool usage
                        if (
                            entry.get("type") == "assistant"
                            and "message" in entry
                            and entry["message"].get("role") == "assistant"
                        ):
                            content = entry["message"].get("content", [])
                            if isinstance(content, list):
                                for item in content:
                                    if (
                                        isinstance(item, dict)
                                        and item.get("type") == "tool_use"
                                        and item.get("name") == "TodoWrite"
                                    ):
                                        input_data = item.get("input", {})
                                        todos = input_data.get("todos")
                                        if todos and isinstance(todos, list):
                                            latest_todos = todos

                        # Also check for tool result with todo data
                        elif entry.get("type") == "user" and "toolUseResult" in entry:
                            tool_result = entry["toolUseResult"]
                            if isinstance(tool_result, dict):
                                new_todos = tool_result.get("newTodos")
                                if new_todos and isinstance(new_todos, list):
                                    latest_todos = new_todos

                    except json.JSONDecodeError:
                        # Skip malformed JSON lines
                        continue

        except (IOError, OSError):
            return None

        return latest_todos
