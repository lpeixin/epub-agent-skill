"""
Tests for the EPUB Agent Skill.
"""
import pytest
import os
from unittest.mock import Mock
from epub_agent_skill.main import EPUBSkill, skill


def test_epub_skill_initialization():
    """Test initializing the EPUBSkill class."""
    epub_skill = EPUBSkill()
    assert epub_skill is not None
    assert epub_skill.llm_provider is None


def test_epub_skill_with_llm_provider():
    """Test initializing the EPUBSkill class with an LLM provider."""
    mock_llm = Mock()
    epub_skill = EPUBSkill(llm_provider=mock_llm)
    assert epub_skill is not None
    assert epub_skill.llm_provider == mock_llm


def test_skill_function_exists():
    """Test that the skill function exists and is callable."""
    assert callable(skill)


def test_generate_summary_without_llm_provider():
    """Test the _generate_summary method without LLM provider."""
    epub_skill = EPUBSkill()
    content = "This is a sample content for testing purposes. " * 10  # Repeat to have more than 50 words
    title = "Test Chapter"
    
    summary = epub_skill._generate_summary(content, title)
    
    # Without LLM provider, it should return the first 50 words
    assert isinstance(summary, str)
    assert len(summary) > 0


def test_extract_epub_content_nonexistent_file():
    """Test extract_epub_content raises FileNotFoundError for nonexistent file."""
    epub_skill = EPUBSkill()
    
    with pytest.raises(FileNotFoundError):
        epub_skill.extract_epub_content("nonexistent.epub")


def test_epub_skill_structure():
    """Test that EPUBSkill has the required methods."""
    epub_skill = EPUBSkill()
    
    assert hasattr(epub_skill, 'extract_epub_content')
    assert hasattr(epub_skill, 'generate_outline_and_summaries')
    assert hasattr(epub_skill, '_generate_summary')