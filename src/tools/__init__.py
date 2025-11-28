"""
AGERE - Tools Module
Contains custom tools for agents.
"""

# ADK Tools - Use these in Agent tools=[] parameter

from .tools import (
    read_cv, 
    list_available_cvs, 
    compare_candidates, 
    job_listing_tool,
    calendar_get_busy_fn as calendar_get_busy,
    calendar_book_slot_fn as calendar_book_slot,
    code_execution_tool,
    problem_presenter_tool,
)

# Helper functions - Use these for utility purposes
from .tools import (
    read_cv_file,
    load_all_cvs,
)

__all__ = [
    # ADK Tools
    'read_cv',
    'list_available_cvs',
    'compare_candidates',
    'job_listing_tool',
    'calendar_get_busy',
    'calendar_book_slot',
    'code_execution_tool',
    # Helper functions
    'read_cv_file',
    'load_all_cvs',
]