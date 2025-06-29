# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python project that creates a status display script for Claude Code projects. The script parses JSONL files to display:
- Last user prompt from the JSONL file
- Last git commit status message
- Current todo list and its status

## Commands

### Development Commands
- `ruff check` - Run linting checks
- `ruff format` - Format code according to project standards
- `python -m pytest` - Run all tests
- `python -m pytest tests/specific_test.py` - Run a specific test file
- `python -m pytest -v` - Run tests with verbose output

### Running the Script
The main script should support these command-line flags:
- `--file` - Specify custom location of projects JSONL file (default: ~/.claude/projects/{cwd-based-foldername}/{most-recent-.jsonl-file})
- `--one-line` - Truncate status to fit on one terminal line based on terminal width
- `--update` - Continuously update and display current status until exited

## Project Structure

- `src/` - Main application code and libraries
- `tests/` - Test files following TDD approach
- `pyproject.toml` - Project configuration with Ruff linting/formatting rules

## Key Implementation Details

### JSONL File Location Logic
The default JSONL file path follows this pattern:
- Base: `~/.claude/projects/`
- Folder name: Current working directory converted to folder name (e.g., `/var/home/a/Code/ClaudeStatus` → `var-home-a-Code-ClaudeStatus`)
- File: Most recent `.jsonl` file in that directory

### Development Approach
This project follows Test-Driven Development (TDD):
1. Write failing tests first based on functional requirements
2. Implement minimal code to make tests pass
3. Refactor while keeping tests green
4. Commit each step of the development process

### Code Quality
- Ruff is configured for linting and formatting with isort-style import sorting
- Code should be clean, maintainable, and well-tested
- All functionality must be covered by tests
