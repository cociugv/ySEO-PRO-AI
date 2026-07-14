"""
File/Git Target Adapter — Applies remediations to local files.

Capabilities:
- Read current file content (before state)
- Write new content (apply)
- Verify content matches expected (verify)
- Restore backup (rollback)
- Git commit integration (optional)

Safety:
- Writes restricted to approved workspace roots
- Creates backup before every modification
- Supports dry-run preview
- Rollback is always available for file targets
"""

import os
import shutil
import time
from dataclasses import dataclass, field
from typing import Optional

from ..core.remediation import Remediation, RemediationState


@dataclass
class FileChange:
    """Record of a file modification."""
    path: str
    backup_path: str = ""
    original_content: str = ""
    new_content: str = ""
    timestamp: float = field(default_factory=time.time)
    success: bool = False
    error: str = ""


class FileAdapter:
    """
    Applies remediations to local files within an allowed workspace.

    Usage:
        adapter = FileAdapter(workspace_root="/path/to/project")
        engine.set_adapter(adapter.apply)
        engine.set_verifier(adapter.verify)
    """

    def __init__(self, workspace_root: str, backup_dir: str = ".yseo/backups"):
        self.workspace_root = os.path.abspath(workspace_root)
        self.backup_dir = os.path.join(self.workspace_root, backup_dir)
        self._changes: list[FileChange] = []
        os.makedirs(self.backup_dir, exist_ok=True)

    def apply(self, remediation: Remediation) -> bool:
        """
        Apply a remediation to the target file.

        Returns True if the file was successfully modified.
        """
        target_path = self._resolve_path(remediation.target_path)
        if not target_path:
            return False

        # Security: verify path is within workspace
        if not self._is_safe_path(target_path):
            return False

        change = FileChange(path=target_path)

        # Read current content (before state)
        if os.path.exists(target_path):
            try:
                with open(target_path, "r", encoding="utf-8") as f:
                    change.original_content = f.read()
            except (OSError, UnicodeDecodeError) as e:
                change.error = f"Cannot read target: {e}"
                self._changes.append(change)
                return False

            # Create backup
            change.backup_path = self._create_backup(target_path, change.original_content)
        else:
            # New file — backup is "file didn't exist"
            change.backup_path = ""

        # Apply the change
        new_content = self._compute_new_content(
            change.original_content, remediation.after_content, remediation.target_scope
        )
        change.new_content = new_content

        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            change.success = True
        except OSError as e:
            change.error = f"Write failed: {e}"
            change.success = False

        self._changes.append(change)
        return change.success

    def verify(self, remediation: Remediation) -> bool:
        """
        Verify the remediation was applied correctly.

        Re-reads the file and checks that expected content is present.
        """
        target_path = self._resolve_path(remediation.target_path)
        if not target_path or not os.path.exists(target_path):
            return False

        try:
            with open(target_path, "r", encoding="utf-8") as f:
                current_content = f.read()
        except (OSError, UnicodeDecodeError):
            return False

        # Verify the remediation content is present in the file
        return remediation.after_content.strip() in current_content

    def rollback(self, remediation: Remediation) -> bool:
        """
        Rollback a remediation by restoring from backup.
        """
        target_path = self._resolve_path(remediation.target_path)
        if not target_path:
            return False

        # Find the matching change record
        matching = [c for c in self._changes if c.path == target_path and c.success]
        if not matching:
            return False

        change = matching[-1]  # Most recent change to this file

        if change.backup_path and os.path.exists(change.backup_path):
            try:
                shutil.copy2(change.backup_path, target_path)
                return True
            except OSError:
                return False
        elif not change.backup_path and change.original_content == "":
            # File was created — delete it
            try:
                os.remove(target_path)
                return True
            except OSError:
                return False

        return False

    def get_changes(self) -> list[FileChange]:
        """Get all recorded file changes."""
        return self._changes.copy()

    def preview(self, remediation: Remediation) -> dict:
        """
        Generate a preview of what would change without modifying anything.
        """
        target_path = self._resolve_path(remediation.target_path)
        current_content = ""

        if target_path and os.path.exists(target_path):
            try:
                with open(target_path, "r", encoding="utf-8") as f:
                    current_content = f.read()
            except (OSError, UnicodeDecodeError):
                pass

        new_content = self._compute_new_content(
            current_content, remediation.after_content, remediation.target_scope
        )

        return {
            "target_path": target_path,
            "file_exists": os.path.exists(target_path) if target_path else False,
            "current_size": len(current_content),
            "new_size": len(new_content),
            "will_create": not os.path.exists(target_path) if target_path else True,
            "diff_lines": self._line_diff(current_content, new_content),
        }

    def _resolve_path(self, target_path: str) -> Optional[str]:
        """Resolve a target path relative to workspace."""
        if not target_path:
            return None
        if os.path.isabs(target_path):
            return target_path
        return os.path.join(self.workspace_root, target_path)

    def _is_safe_path(self, path: str) -> bool:
        """Verify path is within the allowed workspace root."""
        resolved = os.path.realpath(path)
        workspace = os.path.realpath(self.workspace_root)
        return resolved.startswith(workspace)

    def _create_backup(self, target_path: str, content: str) -> str:
        """Create a timestamped backup of a file."""
        filename = os.path.basename(target_path)
        timestamp = int(time.time())
        backup_name = f"{filename}.{timestamp}.bak"
        backup_path = os.path.join(self.backup_dir, backup_name)

        try:
            with open(backup_path, "w", encoding="utf-8") as f:
                f.write(content)
            return backup_path
        except OSError:
            return ""

    def _compute_new_content(self, current: str, addition: str, scope: str) -> str:
        """
        Compute new file content based on scope.

        Scope patterns:
        - "append": Add content at end
        - "head": Insert into <head> section
        - "replace:<marker>": Replace content between markers
        - "" (empty): Replace entire file with addition
        """
        if not current:
            return addition

        if scope == "append":
            return current + "\n" + addition

        if scope == "head" and "</head>" in current:
            # Insert before </head>
            return current.replace("</head>", f"  {addition}\n</head>")

        if scope.startswith("replace:"):
            marker = scope[8:]
            if marker in current:
                return current.replace(marker, addition)

        # Default: append
        return current + "\n" + addition

    @staticmethod
    def _line_diff(before: str, after: str) -> int:
        """Count lines changed."""
        before_lines = set(before.splitlines())
        after_lines = set(after.splitlines())
        added = len(after_lines - before_lines)
        removed = len(before_lines - after_lines)
        return added + removed


class GitAdapter(FileAdapter):
    """
    Extends FileAdapter with Git commit integration.

    After applying remediations, creates a git commit with descriptive message.
    """

    def __init__(self, workspace_root: str, auto_commit: bool = False):
        super().__init__(workspace_root)
        self.auto_commit = auto_commit

    def commit_changes(self, message: str = "") -> bool:
        """Create a git commit for all applied changes."""
        import subprocess

        if not self._changes:
            return False

        changed_files = [c.path for c in self._changes if c.success]
        if not changed_files:
            return False

        if not message:
            message = f"fix(seo): apply {len(changed_files)} SEO remediation(s)\n\nGenerated by ySEO-PRO-AI"

        try:
            # Stage changed files
            for f in changed_files:
                rel = os.path.relpath(f, self.workspace_root)
                subprocess.run(
                    ["git", "add", rel],
                    cwd=self.workspace_root,
                    capture_output=True, check=True,
                )

            # Commit
            subprocess.run(
                ["git", "commit", "-m", message],
                cwd=self.workspace_root,
                capture_output=True, check=True,
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def create_branch(self, branch_name: str = "") -> bool:
        """Create a new branch for remediation changes."""
        import subprocess

        if not branch_name:
            branch_name = f"yseo/fix-{int(time.time())}"

        try:
            subprocess.run(
                ["git", "checkout", "-b", branch_name],
                cwd=self.workspace_root,
                capture_output=True, check=True,
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
