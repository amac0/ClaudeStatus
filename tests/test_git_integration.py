# ABOUTME: Test suite for git integration functionality in Claude status display script
# ABOUTME: Tests extraction of git commit messages and status information

from pathlib import Path
from unittest.mock import Mock, patch

from src.git_integration import GitIntegration


class TestGitIntegration:
    def test_get_last_commit_message_success(self):
        """Test successful extraction of last commit message"""
        with patch("subprocess.run") as mock_run:
            mock_result = Mock()
            mock_result.returncode = 0
            mock_result.stdout = "Add feature X to improve performance\n"
            mock_run.return_value = mock_result

            git_integration = GitIntegration()
            message = git_integration.get_last_commit_message()

            assert message == "Add feature X to improve performance"
            mock_run.assert_called_once_with(
                ["git", "log", "-1", "--pretty=format:%s"],
                capture_output=True,
                text=True,
                timeout=10,
            )

    def test_get_last_commit_message_no_commits(self):
        """Test behavior when no commits exist in repository"""
        with patch("subprocess.run") as mock_run:
            mock_result = Mock()
            mock_result.returncode = 128  # Git error for no commits
            mock_result.stderr = (
                "fatal: your current branch 'main' does not have any commits yet"
            )
            mock_run.return_value = mock_result

            git_integration = GitIntegration()
            message = git_integration.get_last_commit_message()

            assert message is None

    def test_get_last_commit_message_not_git_repo(self):
        """Test behavior when not in a git repository"""
        with patch("subprocess.run") as mock_run:
            mock_result = Mock()
            mock_result.returncode = 128
            mock_result.stderr = "fatal: not a git repository"
            mock_run.return_value = mock_result

            git_integration = GitIntegration()
            message = git_integration.get_last_commit_message()

            assert message is None

    def test_get_last_commit_message_timeout(self):
        """Test behavior when git command times out"""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = TimeoutError("Command timed out")

            git_integration = GitIntegration()
            message = git_integration.get_last_commit_message()

            assert message is None

    def test_get_last_commit_message_with_custom_directory(self):
        """Test getting commit message from a specific directory"""
        with patch("subprocess.run") as mock_run:
            mock_result = Mock()
            mock_result.returncode = 0
            mock_result.stdout = "Initial commit\n"
            mock_run.return_value = mock_result

            git_integration = GitIntegration()
            test_dir = Path("/tmp/test-repo")  # nosec B108
            message = git_integration.get_last_commit_message(str(test_dir))

            assert message == "Initial commit"
            mock_run.assert_called_once_with(
                ["git", "log", "-1", "--pretty=format:%s"],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=str(test_dir),
            )

    def test_is_git_repository_true(self):
        """Test detecting a valid git repository"""
        with patch("subprocess.run") as mock_run:
            mock_result = Mock()
            mock_result.returncode = 0
            mock_run.return_value = mock_result

            git_integration = GitIntegration()
            is_repo = git_integration.is_git_repository()

            assert is_repo is True
            mock_run.assert_called_once_with(
                ["git", "rev-parse", "--git-dir"],
                capture_output=True,
                text=True,
                timeout=5,
            )

    def test_is_git_repository_false(self):
        """Test detecting when not in a git repository"""
        with patch("subprocess.run") as mock_run:
            mock_result = Mock()
            mock_result.returncode = 128
            mock_run.return_value = mock_result

            git_integration = GitIntegration()
            is_repo = git_integration.is_git_repository()

            assert is_repo is False
