# ABOUTME: Test suite for JSONL parsing functionality in Claude status display script
# ABOUTME: Tests extraction of user prompts, todo lists, and assistant responses

import json
import tempfile
from pathlib import Path

from src.jsonl_parser import JSONLParser


class TestJSONLParser:
    def test_extract_last_user_prompt_from_example_jsonl(self):
        """Test extracting the last user prompt from example.jsonl"""
        example_jsonl_path = Path(__file__).parent.parent / "example.jsonl"
        parser = JSONLParser()

        last_prompt = parser.get_last_user_prompt(example_jsonl_path)

        assert last_prompt == "Do not do anything right now, this is a test."

    def test_extract_last_user_prompt_from_simple_jsonl(self):
        """Test extracting user prompt from a simple JSONL file"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            # Write a simple JSONL entry with a user message
            user_message = {
                "type": "user",
                "message": {"role": "user", "content": "Hello, this is a test message"},
            }
            f.write(json.dumps(user_message) + "\n")
            f.flush()

            parser = JSONLParser()
            last_prompt = parser.get_last_user_prompt(f.name)

            assert last_prompt == "Hello, this is a test message"

    def test_extract_last_user_prompt_no_user_messages(self):
        """Test behavior when no user messages exist"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            # Write only assistant messages
            assistant_message = {
                "type": "assistant",
                "message": {
                    "role": "assistant",
                    "content": "I'm an assistant response",
                },
            }
            f.write(json.dumps(assistant_message) + "\n")
            f.flush()

            parser = JSONLParser()
            last_prompt = parser.get_last_user_prompt(f.name)

            assert last_prompt is None

    def test_extract_last_user_prompt_empty_file(self):
        """Test behavior with empty JSONL file"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            f.flush()

            parser = JSONLParser()
            last_prompt = parser.get_last_user_prompt(f.name)

            assert last_prompt is None

    def test_extract_latest_todo_list_from_example_jsonl(self):
        """Test extracting the latest todo list from example.jsonl"""
        example_jsonl_path = Path(__file__).parent.parent / "example.jsonl"
        parser = JSONLParser()

        todos = parser.get_latest_todo_list(example_jsonl_path)

        # Should get the final completed todo list from the example
        assert todos is not None
        assert len(todos) == 4
        assert all(todo["status"] == "completed" for todo in todos)
        assert any("Explore codebase structure" in todo["content"] for todo in todos)
        assert any(
            "Create comprehensive CLAUDE.md" in todo["content"] for todo in todos
        )

    def test_extract_latest_todo_list_simple_jsonl(self):
        """Test extracting todo list from a simple JSONL file"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            # Write a TodoWrite tool usage
            todo_message = {
                "type": "assistant",
                "message": {
                    "role": "assistant",
                    "content": [
                        {
                            "type": "tool_use",
                            "name": "TodoWrite",
                            "input": {
                                "todos": [
                                    {
                                        "id": "1",
                                        "content": "Write test",
                                        "status": "completed",
                                        "priority": "high",
                                    },
                                    {
                                        "id": "2",
                                        "content": "Write code",
                                        "status": "in_progress",
                                        "priority": "medium",
                                    },
                                ]
                            },
                        }
                    ],
                },
            }
            f.write(json.dumps(todo_message) + "\n")
            f.flush()

            parser = JSONLParser()
            todos = parser.get_latest_todo_list(f.name)

            assert todos is not None
            assert len(todos) == 2
            assert todos[0]["content"] == "Write test"
            assert todos[0]["status"] == "completed"
            assert todos[1]["content"] == "Write code"
            assert todos[1]["status"] == "in_progress"

    def test_extract_latest_todo_list_no_todos(self):
        """Test behavior when no todo lists exist"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            # Write only user messages
            user_message = {
                "type": "user",
                "message": {"role": "user", "content": "Hello"},
            }
            f.write(json.dumps(user_message) + "\n")
            f.flush()

            parser = JSONLParser()
            todos = parser.get_latest_todo_list(f.name)

            assert todos is None

    def test_extract_last_user_prompt_from_example2_jsonl(self):
        """Test extracting the last user prompt from example2.jsonl, ignoring tool
        results"""
        example2_jsonl_path = Path(__file__).parent.parent / "example2.jsonl"
        parser = JSONLParser()

        last_prompt = parser.get_last_user_prompt(example2_jsonl_path)

        # Should get the actual user prompt, not tool result messages
        assert last_prompt is not None
        assert "The two-line display needs to ensure" in last_prompt
        assert "new-lines" in last_prompt

    def test_extract_latest_todo_list_from_example2_jsonl(self):
        """Test extracting todo list from example2.jsonl with timestamps"""
        example2_jsonl_path = Path(__file__).parent.parent / "example2.jsonl"
        parser = JSONLParser()

        todos = parser.get_latest_todo_list(example2_jsonl_path)

        # Should get the latest todo list
        assert todos is not None
        assert len(todos) >= 1
        # Check for the test todos we expect
        todo_contents = [todo["content"] for todo in todos]
        assert any("Test two-line display" in content for content in todo_contents)

    def test_extract_user_prompt_with_timestamp_example2_jsonl(self):
        """Test extracting user prompt with timestamp from example2.jsonl"""
        example2_jsonl_path = Path(__file__).parent.parent / "example2.jsonl"
        parser = JSONLParser()

        prompt, timestamp = parser.get_last_user_prompt_with_timestamp(
            example2_jsonl_path
        )

        assert prompt is not None
        assert timestamp is not None
        assert "The two-line display needs to ensure" in prompt
        # Timestamp should be from 2025-06-29T14:05:25.270Z
        assert timestamp > 1700000000  # Reasonable timestamp check

    def test_extract_todo_list_with_timestamp_example2_jsonl(self):
        """Test extracting todo list with timestamp from example2.jsonl"""
        example2_jsonl_path = Path(__file__).parent.parent / "example2.jsonl"
        parser = JSONLParser()

        todos, timestamp = parser.get_latest_todo_list_with_timestamp(
            example2_jsonl_path
        )

        assert todos is not None
        assert timestamp is not None
        assert len(todos) >= 1
        # Timestamp should be after the user prompt (2025-06-29T14:06:35.198Z)
        assert timestamp > 1700000000  # Reasonable timestamp check

    def test_ignore_tool_result_messages(self):
        """Test that tool result messages are ignored when finding user prompts"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            # Write a real user message
            real_user_message = {
                "type": "user",
                "message": {"role": "user", "content": "This is the real user prompt"},
                "timestamp": "2025-06-29T14:05:25.270Z",
            }
            f.write(json.dumps(real_user_message) + "\n")

            # Write a tool result message (should be ignored)
            tool_result_message = {
                "type": "user",
                "message": {
                    "role": "user",
                    "content": [
                        {
                            "tool_use_id": "123",
                            "type": "tool_result",
                            "content": "tool output",
                        }
                    ],
                },
                "toolUseResult": {"stdout": "some output"},
                "timestamp": "2025-06-29T14:06:35.284Z",
            }
            f.write(json.dumps(tool_result_message) + "\n")
            f.flush()

            parser = JSONLParser()
            last_prompt = parser.get_last_user_prompt(f.name)

            # Should get the real user prompt, not the tool result
            assert last_prompt == "This is the real user prompt"

    def test_ignore_tool_result_messages_with_timestamp(self):
        """Test that tool result messages are ignored when finding user prompts with
        timestamps"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            # Write a real user message
            real_user_message = {
                "type": "user",
                "message": {"role": "user", "content": "This is the real user prompt"},
                "timestamp": "2025-06-29T14:05:25.270Z",
            }
            f.write(json.dumps(real_user_message) + "\n")

            # Write a tool result message (should be ignored)
            tool_result_message = {
                "type": "user",
                "message": {
                    "role": "user",
                    "content": [
                        {
                            "tool_use_id": "123",
                            "type": "tool_result",
                            "content": "tool output",
                        }
                    ],
                },
                "toolUseResult": {"stdout": "some output"},
                "timestamp": "2025-06-29T14:06:35.284Z",
            }
            f.write(json.dumps(tool_result_message) + "\n")
            f.flush()

            parser = JSONLParser()
            prompt, timestamp = parser.get_last_user_prompt_with_timestamp(f.name)

            # Should get the real user prompt and its timestamp, not the tool result
            assert prompt == "This is the real user prompt"
            assert timestamp is not None
            # Should be the timestamp from the real message, not the tool result
            expected_timestamp = parser._parse_timestamp("2025-06-29T14:05:25.270Z")
            assert abs(timestamp - expected_timestamp) < 1  # Within 1 second
