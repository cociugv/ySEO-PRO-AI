"""
Prescriptions Registry — Maps issue codes to fix strategies.

Re-exported from fixer.py for standalone usage.
"""

from .fixer import get_prescription, Prescription

__all__ = ["get_prescription", "Prescription"]
