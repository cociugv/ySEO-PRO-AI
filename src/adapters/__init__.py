"""
Target Adapters — Translate remediations into target-specific changes.

The engine never writes directly to arbitrary targets.
Adapters implement: preview, apply, verify, rollback.
"""
