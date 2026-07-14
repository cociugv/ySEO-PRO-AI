"""
Prescriptions — Legacy compatibility module.

Fix logic is now inside AutoFixer (generate/apply/verify pattern).
This module provides the legacy get_prescription for backward compat.
"""

from .fixer import get_prescription

__all__ = ["get_prescription"]
