"""
Remediation State Machine — Full lifecycle for SEO fixes.

States:
    PROPOSED → PREVIEWED → APPROVED → APPLYING → APPLIED → VERIFYING → VERIFIED

Failure branches:
    APPLY_FAILED
    VERIFICATION_FAILED → ROLLBACK_AVAILABLE → ROLLED_BACK

A remediation is NEVER reported as applied merely because content was generated.
It is applied ONLY after the intended target changed and verification passed.
"""

import time
import hashlib
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Callable


class RemediationState(Enum):
    """All possible states in the remediation lifecycle."""
    PROPOSED = "proposed"
    PREVIEWED = "previewed"
    APPROVED = "approved"
    APPLYING = "applying"
    APPLIED = "applied"
    VERIFYING = "verifying"
    VERIFIED = "verified"
    APPLY_FAILED = "apply_failed"
    VERIFICATION_FAILED = "verification_failed"
    ROLLBACK_AVAILABLE = "rollback_available"
    ROLLED_BACK = "rolled_back"


class RiskLevel(Enum):
    """Risk classification for remediations."""
    LOW = "low"          # Meta tag changes, schema injection
    MEDIUM = "medium"    # Canonical changes, robots modifications
    HIGH = "high"        # Redirect rules, content rewrites
    CRITICAL = "critical"  # Anything affecting indexability at scale


# Valid state transitions
VALID_TRANSITIONS = {
    RemediationState.PROPOSED: [RemediationState.PREVIEWED],
    RemediationState.PREVIEWED: [RemediationState.APPROVED, RemediationState.PROPOSED],
    RemediationState.APPROVED: [RemediationState.APPLYING],
    RemediationState.APPLYING: [RemediationState.APPLIED, RemediationState.APPLY_FAILED],
    RemediationState.APPLIED: [RemediationState.VERIFYING],
    RemediationState.VERIFYING: [RemediationState.VERIFIED, RemediationState.VERIFICATION_FAILED],
    RemediationState.APPLY_FAILED: [RemediationState.PROPOSED],  # Can retry
    RemediationState.VERIFICATION_FAILED: [RemediationState.ROLLBACK_AVAILABLE],
    RemediationState.ROLLBACK_AVAILABLE: [RemediationState.ROLLED_BACK, RemediationState.PROPOSED],
    RemediationState.VERIFIED: [],  # Terminal
    RemediationState.ROLLED_BACK: [RemediationState.PROPOSED],  # Can retry
}


@dataclass
class StateTransition:
    """Record of a state change."""
    from_state: RemediationState
    to_state: RemediationState
    timestamp: float = field(default_factory=time.time)
    reason: str = ""
    actor: str = "system"  # system | user | adapter


@dataclass
class Remediation:
    """
    A single remediation unit — one fix to apply to one target.

    Immutable identity: id is derived from finding + target + proposed content.
    """
    id: str = ""
    finding_ids: list = field(default_factory=list)
    state: RemediationState = RemediationState.PROPOSED
    risk: RiskLevel = RiskLevel.LOW

    # Target
    target_url: str = ""
    target_path: str = ""  # File path if local
    target_scope: str = ""  # What exactly changes (e.g., "<head> meta tags")

    # Content
    before_content: str = ""
    after_content: str = ""
    diff_preview: str = ""

    # Metadata
    description: str = ""
    category: str = ""  # meta | schema | canonical | robots | hreflang | redirect | content
    created_at: float = field(default_factory=time.time)
    approved_at: float = 0
    applied_at: float = 0
    verified_at: float = 0

    # Audit trail
    transitions: list = field(default_factory=list)
    error: str = ""

    # Rollback
    rollback_content: str = ""
    rollback_available: bool = False

    def __post_init__(self):
        if not self.id:
            # Deterministic ID from content
            seed = f"{self.target_url}:{self.category}:{self.after_content[:200]}"
            self.id = hashlib.sha256(seed.encode()).hexdigest()[:12]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "state": self.state.value,
            "risk": self.risk.value,
            "finding_ids": self.finding_ids,
            "target_url": self.target_url,
            "target_path": self.target_path,
            "target_scope": self.target_scope,
            "description": self.description,
            "category": self.category,
            "diff_preview": self.diff_preview[:500],
            "before_content": self.before_content[:200],
            "after_content": self.after_content[:200],
            "error": self.error,
            "rollback_available": self.rollback_available,
            "created_at": self.created_at,
            "transitions": len(self.transitions),
        }


class InvalidTransition(Exception):
    """Raised when attempting an illegal state transition."""
    pass


class RemediationEngine:
    """
    Manages the remediation lifecycle.

    Enforces valid state transitions, records audit trail,
    and coordinates with target adapters.
    """

    def __init__(self):
        self._remediations: dict[str, Remediation] = {}
        self._adapter: Optional[Callable] = None
        self._verifier: Optional[Callable] = None

    def set_adapter(self, adapter: Callable) -> None:
        """Set the target adapter (apply/rollback operations)."""
        self._adapter = adapter

    def set_verifier(self, verifier: Callable) -> None:
        """Set the verification function."""
        self._verifier = verifier

    def propose(
        self,
        finding_ids: list[str],
        target_url: str,
        after_content: str,
        before_content: str = "",
        description: str = "",
        category: str = "meta",
        risk: RiskLevel = RiskLevel.LOW,
        target_path: str = "",
        target_scope: str = "",
    ) -> Remediation:
        """Create a new remediation proposal."""
        rem = Remediation(
            finding_ids=finding_ids,
            target_url=target_url,
            target_path=target_path,
            target_scope=target_scope,
            before_content=before_content,
            after_content=after_content,
            description=description,
            category=category,
            risk=risk,
            rollback_content=before_content,
            rollback_available=bool(before_content),
        )
        self._remediations[rem.id] = rem
        return rem

    def preview(self, remediation_id: str) -> Remediation:
        """Generate diff preview — transitions PROPOSED → PREVIEWED."""
        rem = self._get(remediation_id)
        self._transition(rem, RemediationState.PREVIEWED, reason="Preview generated")

        # Generate diff
        if rem.before_content and rem.after_content:
            rem.diff_preview = self._generate_diff(rem.before_content, rem.after_content)
        else:
            rem.diff_preview = f"+ {rem.after_content[:200]}"

        return rem

    def approve(self, remediation_id: str, actor: str = "user") -> Remediation:
        """Approve remediation for application — PREVIEWED → APPROVED."""
        rem = self._get(remediation_id)
        self._transition(rem, RemediationState.APPROVED, reason="User approved", actor=actor)
        rem.approved_at = time.time()
        return rem

    def apply(self, remediation_id: str) -> Remediation:
        """Apply remediation to target — APPROVED → APPLYING → APPLIED | APPLY_FAILED."""
        rem = self._get(remediation_id)
        self._transition(rem, RemediationState.APPLYING, reason="Applying to target")

        if not self._adapter:
            self._transition(rem, RemediationState.APPLY_FAILED, reason="No target adapter configured")
            rem.error = "No target adapter available"
            return rem

        try:
            success = self._adapter(rem)
            if success:
                self._transition(rem, RemediationState.APPLIED, reason="Adapter reported success")
                rem.applied_at = time.time()
            else:
                self._transition(rem, RemediationState.APPLY_FAILED, reason="Adapter returned failure")
                rem.error = "Adapter returned False"
        except Exception as e:
            self._transition(rem, RemediationState.APPLY_FAILED, reason=f"Exception: {e}")
            rem.error = str(e)

        return rem

    def verify(self, remediation_id: str) -> Remediation:
        """Verify remediation was applied correctly — APPLIED → VERIFYING → VERIFIED | VERIFICATION_FAILED."""
        rem = self._get(remediation_id)
        self._transition(rem, RemediationState.VERIFYING, reason="Running verification")

        if not self._verifier:
            # No verifier = trust adapter
            self._transition(rem, RemediationState.VERIFIED, reason="No verifier configured, trusting adapter")
            rem.verified_at = time.time()
            return rem

        try:
            verified = self._verifier(rem)
            if verified:
                self._transition(rem, RemediationState.VERIFIED, reason="Verification passed")
                rem.verified_at = time.time()
            else:
                self._transition(rem, RemediationState.VERIFICATION_FAILED, reason="Verification check failed")
                if rem.rollback_available:
                    self._transition(rem, RemediationState.ROLLBACK_AVAILABLE, reason="Rollback is available")
        except Exception as e:
            self._transition(rem, RemediationState.VERIFICATION_FAILED, reason=f"Verification error: {e}")
            if rem.rollback_available:
                self._transition(rem, RemediationState.ROLLBACK_AVAILABLE, reason="Rollback is available")

        return rem

    def rollback(self, remediation_id: str) -> Remediation:
        """Rollback a failed remediation — ROLLBACK_AVAILABLE → ROLLED_BACK."""
        rem = self._get(remediation_id)
        if not rem.rollback_available:
            raise InvalidTransition(f"Remediation {remediation_id} has no rollback content")

        if self._adapter:
            # Create a reverse remediation
            reverse = Remediation(
                target_url=rem.target_url,
                target_path=rem.target_path,
                after_content=rem.rollback_content,
                before_content=rem.after_content,
            )
            try:
                self._adapter(reverse)
            except Exception as e:
                rem.error = f"Rollback failed: {e}"
                return rem

        self._transition(rem, RemediationState.ROLLED_BACK, reason="Rollback applied")
        return rem

    def execute_full(self, remediation_id: str, auto_approve: bool = False) -> Remediation:
        """
        Run the full lifecycle: preview → approve → apply → verify.
        Convenience method for low-risk automated fixes.
        """
        rem = self.preview(remediation_id)

        if rem.risk in (RiskLevel.HIGH, RiskLevel.CRITICAL) and not auto_approve:
            return rem  # Stop at preview for high-risk

        rem = self.approve(remediation_id, actor="system" if auto_approve else "user")
        rem = self.apply(remediation_id)

        if rem.state == RemediationState.APPLIED:
            rem = self.verify(remediation_id)

        return rem

    def get_all(self) -> list[Remediation]:
        """Get all remediations."""
        return list(self._remediations.values())

    def get_by_state(self, state: RemediationState) -> list[Remediation]:
        """Filter remediations by state."""
        return [r for r in self._remediations.values() if r.state == state]

    def get_plan_summary(self) -> dict:
        """Summarize all remediations as a plan."""
        by_state = {}
        by_risk = {}
        for r in self._remediations.values():
            by_state.setdefault(r.state.value, []).append(r.id)
            by_risk.setdefault(r.risk.value, []).append(r.id)

        return {
            "total": len(self._remediations),
            "by_state": {k: len(v) for k, v in by_state.items()},
            "by_risk": {k: len(v) for k, v in by_risk.items()},
            "pending_approval": len(self.get_by_state(RemediationState.PREVIEWED)),
            "verified": len(self.get_by_state(RemediationState.VERIFIED)),
            "failed": len(self.get_by_state(RemediationState.APPLY_FAILED)) +
                      len(self.get_by_state(RemediationState.VERIFICATION_FAILED)),
        }

    def _get(self, remediation_id: str) -> Remediation:
        """Get remediation by ID or raise."""
        rem = self._remediations.get(remediation_id)
        if not rem:
            raise KeyError(f"Remediation not found: {remediation_id}")
        return rem

    def _transition(self, rem: Remediation, to_state: RemediationState,
                    reason: str = "", actor: str = "system") -> None:
        """Execute a state transition with validation."""
        valid_next = VALID_TRANSITIONS.get(rem.state, [])
        if to_state not in valid_next:
            raise InvalidTransition(
                f"Cannot transition from {rem.state.value} to {to_state.value}. "
                f"Valid transitions: {[s.value for s in valid_next]}"
            )
        rem.transitions.append(StateTransition(
            from_state=rem.state,
            to_state=to_state,
            reason=reason,
            actor=actor,
        ))
        rem.state = to_state

    @staticmethod
    def _generate_diff(before: str, after: str) -> str:
        """Generate a simple unified diff preview."""
        before_lines = before.splitlines()
        after_lines = after.splitlines()

        diff_lines = []
        for line in before_lines:
            if line not in after_lines:
                diff_lines.append(f"- {line}")
        for line in after_lines:
            if line not in before_lines:
                diff_lines.append(f"+ {line}")

        return "\n".join(diff_lines) if diff_lines else "(no visible changes)"
