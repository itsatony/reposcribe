# reposcribe/git.py
from pathlib import Path
from typing import Optional
import git
from git.exc import GitCommandError, InvalidGitRepositoryError, NoSuchPathError
import logging
from rich.progress import Progress

from .config import Config

logger = logging.getLogger(__name__)

class GitError(Exception):
    """Custom exception for Git-related errors."""
    pass

class GitHandler:
    """Handles Git repository operations including cloning and validation."""
    
    def __init__(self, config: Config, progress: Progress):
        self.config = config
        self.progress = progress
        self._repo: Optional[git.Repo] = None

    def prepare_repository(self, force: bool = False) -> Path:
        """
        Prepare the repository for processing. Either clone a remote repository
        or validate and use a local one.
        
        Args:
            force: If True, allow processing of non-git directories
            
        Returns:
            Path to the repository root
            
        Raises:
            GitError: If there are issues with the repository
        """
        try:
            if self.config.repo_url:
                return self._clone_repository()
            else:
                return self._validate_local_repository(force)
        except Exception as e:
            raise GitError(f"Failed to prepare repository: {str(e)}")

    def _clone_repository(self) -> Path:
        """Clone a remote repository."""
        target_path = self.config.target_dir
        try:
            logger.info(f"Cloning repository from {self.config.repo_url} to {target_path}")
            
            # Handle existing directory
            if target_path.exists() and any(target_path.iterdir()):
                raise GitError(f"Target directory {target_path} exists and is not empty")
            
            # Ensure parent directory exists
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Clone the repository
            self._repo = git.Repo.clone_from(
                self.config.repo_url,
                target_path,
                progress=self._progress_printer
            )
            
            logger.info("Repository cloned successfully")
            return target_path

        except GitCommandError as e:
            raise GitError(f"Git clone failed: {str(e)}")
        except Exception as e:
            raise GitError(f"Failed to clone repository: {str(e)}")

    def _validate_local_repository(self, force: bool = False) -> Path:
        """Validate and prepare a local repository."""
        try:
            path = self.config.target_dir.resolve()
            
            if not path.exists():
                raise GitError(f"Directory does not exist: {path}")
            
            if force:
                logger.warning("Force flag used - processing directory without Git validation")
                return path
            
            try:
                self._repo = git.Repo(path)
            except InvalidGitRepositoryError:
                raise GitError(
                    f"Directory is not a Git repository: {path}\n"
                    "Use --force to process it anyway"
                )
            
            if self._repo.bare:
                raise GitError("Cannot process bare repositories")
            
            # Check for uncommitted changes
            if self._repo.is_dirty():
                logger.warning("Repository has uncommitted changes")
            
            logger.info(f"Using local repository at {path}")
            return path

        except Exception as e:
            if isinstance(e, GitError):
                raise
            raise GitError(f"Failed to validate local repository: {str(e)}")

    def get_current_branch(self) -> str:
        """Get the name of the current branch."""
        if not self._repo:
            return "unknown"
        try:
            return self._repo.active_branch.name
        except TypeError:  # HEAD might be detached
            return "detached-head"
        except Exception as e:
            logger.warning(f"Failed to get current branch: {e}")
            return "unknown"

    def get_repo_info(self) -> dict:
        """Get repository information for documentation."""
        if not self._repo:
            return {
                "branch": "unknown",
                "is_git_repo": False
            }
        
        return {
            "branch": self.get_current_branch(),
            "is_git_repo": True,
            "has_uncommitted_changes": self._repo.is_dirty(),
            "remotes": [remote.name for remote in self._repo.remotes],
            "root_path": str(self._repo.working_dir)
        }

    def _progress_printer(self, op_code: int, cur_count: int, max_count: int, message: str) -> None:
        """Callback for Git clone progress."""
        if max_count:
            percentage = cur_count / max_count * 100
            self.progress.console.print(
                f"Clone progress: {percentage:.1f}% ({message})",
                end="\r"
            )