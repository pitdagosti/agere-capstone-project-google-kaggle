"""
PROJECT AGERE (Agentic Recruiter)
AI-Powered CV Analysis System
"""

__version__ = "0.1.0"
__author__ = "Amos & Co."

# Make agents and tools easily accessible
from .src import agents
from .src import tools

__all__ = ['agents', 'tools']

