"""
Q-Mail Backend Analysis Engine
Contains pure Python PST forensic parsers powered by pypff (libpff-python-windows).
"""

from .pst_parser import ParsedAttachment, ParsedEmail, PSTStreamParser

__all__ = ["ParsedAttachment", "ParsedEmail", "PSTStreamParser"]
