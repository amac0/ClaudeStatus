# ABOUTME: Parser for Claude Code JSONL files to extract user prompts and todo lists
# ABOUTME: Handles reading JSONL conversation files and extracting status information

import json
from pathlib import Path
from typing import Optional


class JSONLParser:
    """Parser for Claude Code JSONL conversation files"""

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
