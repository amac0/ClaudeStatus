# ABOUTME: Test file for the main claude_status.py script functionality
# ABOUTME: Tests CLI argument parsing, JSONL file detection, and update mode behavior

from pathlib import Path
from unittest.mock import MagicMock, patch

from claude_status import get_default_jsonl_path, main


class TestClaudeStatus:
    """Test cases for the main Claude status script functionality"""

    def test_get_default_jsonl_path(self):
        """Test automatic JSONL file path detection"""
        test_cwd = "/var/home/a/Code/TestProject"

        with patch("claude_status.Path.home") as mock_home:
            mock_home_path = MagicMock()
            mock_home.return_value = mock_home_path

            # Create mock directory structure
            mock_base_dir = MagicMock()
            path_chain = (
                mock_home_path.__truediv__.return_value.__truediv__.return_value
            )
            path_chain.__truediv__.return_value = mock_base_dir

            # Test when directory doesn't exist
            mock_base_dir.exists.return_value = False
            result = get_default_jsonl_path(test_cwd)
            assert result is None

            # Test when directory exists but no JSONL files
            mock_base_dir.exists.return_value = True
            mock_base_dir.glob.return_value = []
            result = get_default_jsonl_path(test_cwd)
            assert result is None

            # Test when JSONL files exist - should return most recent
            mock_file1 = MagicMock()
            mock_file1.stat.return_value.st_mtime = 1000
            mock_file2 = MagicMock()
            mock_file2.stat.return_value.st_mtime = 2000  # More recent
            mock_base_dir.glob.return_value = [mock_file1, mock_file2]

            result = get_default_jsonl_path(test_cwd)
            assert result == mock_file2

    def test_get_default_jsonl_path_folder_name_conversion(self):
        """Test that CWD is correctly converted to folder name"""
        test_cwd = "/var/home/a/Code/ClaudeStatus"
        expected_folder = "-var-home-a-Code-ClaudeStatus"

        with patch("claude_status.Path.home") as mock_home:
            mock_home_path = MagicMock()
            mock_home.return_value = mock_home_path

            # Capture the folder name used in the path construction
            mock_projects_dir = MagicMock()
            mock_home_path.__truediv__.return_value.__truediv__.return_value = (
                mock_projects_dir
            )

            mock_base_dir = MagicMock()
            mock_projects_dir.__truediv__.return_value = mock_base_dir
            mock_base_dir.exists.return_value = False

            get_default_jsonl_path(test_cwd)

            # Verify the folder name was constructed correctly
            mock_projects_dir.__truediv__.assert_called_with(expected_folder)

    def test_file_freshness_check_in_update_mode(self):
        """Test that update mode checks for newer JSONL files"""
        with (
            patch("claude_status.get_default_jsonl_path") as mock_get_path,
            patch("claude_status.display_status") as mock_display,
            patch("claude_status.time.sleep") as mock_sleep,
            patch("claude_status.os.system"),
        ):
            # Mock initial path
            initial_path = Path("/path/to/initial.jsonl")
            newer_path = Path("/path/to/newer.jsonl")

            # Simulate path change after first iteration
            mock_get_path.side_effect = [initial_path, newer_path, newer_path]

            # Mock sleep to only allow a few iterations before KeyboardInterrupt
            mock_sleep.side_effect = [None, KeyboardInterrupt()]

            # Test update mode without explicit file (should use auto-detection)
            with patch("claude_status.argparse.ArgumentParser.parse_args") as mock_args:
                mock_args.return_value = MagicMock(
                    file=None,  # No explicit file - should use auto-detection
                    two_line=False,
                    update=5,
                )

                try:
                    main()
                except KeyboardInterrupt:
                    pass

                # Verify get_default_jsonl_path was called multiple times
                # (checking for newer files)
                assert mock_get_path.call_count >= 2

                # Verify display_status was called with the updated path
                calls = mock_display.call_args_list
                assert len(calls) >= 1
                # First call should use initial path, second call should use newer path
                if len(calls) >= 2:
                    assert calls[1][0][0] == newer_path

    def test_explicit_file_no_freshness_check(self):
        """Test that explicit file path doesn't trigger freshness check"""
        explicit_file = "/explicit/path/to/file.jsonl"

        with (
            patch("claude_status.get_default_jsonl_path") as mock_get_path,
            patch("claude_status.display_status") as mock_display,
            patch("claude_status.time.sleep") as mock_sleep,
            patch("claude_status.os.system"),
        ):
            # Mock sleep to only allow one iteration before KeyboardInterrupt
            mock_sleep.side_effect = [KeyboardInterrupt()]

            # Test update mode with explicit file
            with patch("claude_status.argparse.ArgumentParser.parse_args") as mock_args:
                mock_args.return_value = MagicMock(
                    file=explicit_file,  # Explicit file provided
                    two_line=False,
                    update=5,
                )

                try:
                    main()
                except KeyboardInterrupt:
                    pass

                # Verify get_default_jsonl_path was NOT called for freshness check
                # It might be called once during initial setup, but not in the
                # update loop
                mock_get_path.assert_not_called()

                # Verify display_status was called with the explicit file path
                calls = mock_display.call_args_list
                assert len(calls) >= 1
                assert str(calls[0][0][0]) == explicit_file
