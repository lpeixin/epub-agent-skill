"""
EPUB Agent Skill - Main implementation for processing EPUB files and extracting structured outlines
and chapter summaries using LLMs.
"""
import os
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from typing import Dict, List, Optional


class EPUBSkill:
    """
    An agent skill for extracting structured outlines and concise chapter summaries from EPUB books
    using LLM-driven pipelines.
    """

    def __init__(self, llm_provider=None):
        """
        Initialize the EPUB skill with an optional LLM provider.
        
        :param llm_provider: Optional LLM provider for processing content
        """
        self.llm_provider = llm_provider

    def extract_epub_content(self, epub_path: str) -> Dict[str, any]:
        """
        Extract chapters and content from an EPUB file.
        
        :param epub_path: Path to the EPUB file
        :return: Dictionary containing book metadata and chapters
        """
        if not os.path.exists(epub_path):
            raise FileNotFoundError(f"EPUB file not found: {epub_path}")
            
        book = epub.read_epub(epub_path)
        
        # Extract metadata
        metadata = {
            'title': self._extract_metadata(book.get_metadata('DC', 'title')),
            'creator': self._extract_metadata(book.get_metadata('DC', 'creator')),
            'language': self._extract_metadata(book.get_metadata('DC', 'language')),
            'identifier': self._extract_metadata(book.get_metadata('DC', 'identifier'))
        }
        
        # Extract chapters
        chapters = []
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                soup = BeautifulSoup(item.get_content(), 'html.parser')
                
                # Get chapter title from h1, h2 tags or first paragraph
                title_tag = soup.find(['h1', 'h2', 'h3'])
                chapter_title = title_tag.get_text().strip() if title_tag else f"Chapter {len(chapters)+1}"
                
                # Get chapter content
                content = soup.get_text().strip()
                
                if content:  # Only add chapters with actual content
                    chapters.append({
                        'title': chapter_title,
                        'content': content,
                        'order': len(chapters)
                    })
        
        return {
            'metadata': metadata,
            'chapters': chapters
        }

    def _extract_metadata(self, metadata_tuple_list):
        """Extract a single value from metadata tuple list."""
        if metadata_tuple_list:
            return metadata_tuple_list[0][0]
        return "Unknown"

    def generate_outline_and_summaries(self, epub_path: str) -> Dict[str, any]:
        """
        Process an EPUB file to generate structured outline and chapter summaries.
        
        :param epub_path: Path to the EPUB file
        :return: Dictionary containing book outline and summaries
        """
        content = self.extract_epub_content(epub_path)
        
        result = {
            'metadata': content['metadata'],
            'outline': [],
            'summaries': []
        }
        
        for chapter in content['chapters']:
            # Generate summary for each chapter
            summary = self._generate_summary(chapter['content'], chapter['title'])
            
            result['outline'].append({
                'title': chapter['title'],
                'order': chapter['order']
            })
            
            result['summaries'].append({
                'chapter_title': chapter['title'],
                'summary': summary,
                'order': chapter['order']
            })
        
        return result

    def _generate_summary(self, content: str, title: str) -> str:
        """
        Generate a summary for the given content using LLM.
        This is a placeholder implementation - in a real scenario, you would connect
        to an actual LLM provider.
        
        :param content: Content to summarize
        :param title: Title of the chapter
        :return: Generated summary
        """
        # In a real implementation, this would call an LLM provider
        if self.llm_provider:
            # Call to LLM provider would happen here
            return f"Summary of '{title}' would be generated using LLM."
        else:
            # Fallback implementation if no LLM provider is set
            words = content.split()[:50]  # Take first 50 words as a simple summary
            return " ".join(words) + "..." if len(content.split()) > 50 else content


def skill(epub_path: str) -> Dict[str, any]:
    """
    Agent skill entry point function that processes an EPUB file and returns
    structured outline and chapter summaries.
    
    :param epub_path: Path to the EPUB file to process
    :return: Dictionary containing book metadata, outline, and chapter summaries
    """
    epub_skill = EPUBSkill()
    return epub_skill.generate_outline_and_summaries(epub_path)