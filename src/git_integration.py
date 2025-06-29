# ABOUTME: Git integration functionality for Claude status display script
# ABOUTME: Handles extraction of git commit messages and repository status checks

import subprocess  # nosec B404
from typing import Optional


class GitIntegration:
    """Git integration for extracting commit information and repository status"""

    def get_last_commit_message(self, repo_path: Optional[str] = None) -> Optional[str]:
        """Get the last commit message from a git repository

        Args:
            repo_path: Path to the git repository. If None, uses current directory.

        Returns:
            The last commit message, or None if not available
        """
        try:
            cmd = ["git", "log", "-1", "--pretty=format:%s"]

            if repo_path:
                result = subprocess.run(  # nosec B603
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=10,
                    cwd=str(repo_path),
                )
            else:
                result = subprocess.run(  # nosec B603
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

            if result.returncode == 0:
                return result.stdout.strip()
            else:
                # Git command failed (no commits, not a repo, etc.)
                return None

        except (subprocess.TimeoutExpired, subprocess.SubprocessError, OSError):
            # Command timed out or other subprocess error
            return None
        except Exception:
            # Catch any other unexpected errors
            return None

    def is_git_repository(self, repo_path: Optional[str] = None) -> bool:
        """Check if the current or specified directory is a git repository

        Args:
            repo_path: Path to check. If None, uses current directory.

        Returns:
            True if it's a git repository, False otherwise
        """
        try:
            cmd = ["git", "rev-parse", "--git-dir"]

            if repo_path:
                result = subprocess.run(  # nosec B603
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=5,
                    cwd=str(repo_path),
                )
            else:
                result = subprocess.run(  # nosec B603
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
            return result.returncode == 0

        except (subprocess.TimeoutExpired, subprocess.SubprocessError, OSError):
            return False
        except Exception:
            return False
