"""
AGERE - Tools Module
Contains custom tools for agents.
"""

# ADK Tools - Use these in Agent tools=[] parameter
from .tools import (
    read_cv,
    list_available_cvs,
    compare_candidates,
)

# Helper functions - Use these for utility purposes
from .tools import (
    read_cv_file,
    load_all_cvs,
)

from .mcp_client import (
    CalendarClient,
)

__all__ = [
    # ADK Tools
    'read_cv',
    'list_available_cvs',
    'compare_candidates',
    # Helper functions
    'read_cv_file',
    'load_all_cvs',
    'CalendarClient',
]

