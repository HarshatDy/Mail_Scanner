"""
AI module for the Email Scanner system.
Handles topic generation using Gemini and OpenAI APIs.
"""

from .topic_generator import TopicGenerator
from .content_analyzer import ContentAnalyzer

__all__ = ['TopicGenerator', 'ContentAnalyzer'] 