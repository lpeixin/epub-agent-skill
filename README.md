# EPUB Agent Skill

An Agent Skill that extracts structured outlines and concise chapter summaries from EPUB books using LLM-driven pipelines.

## Overview

This module implements an Agent Skill that processes EPUB electronic books and extracts structured outlines and chapter summaries using large language models. It solves the problem of quickly understanding lengthy EPUB book content by automatically transforming unstructured text into structured knowledge overviews.

## Features

- EPUB parsing: Reads and processes EPUB formatted e-books
- Structured outline extraction: Identifies and extracts hierarchical structure (chapters, sections)
- Chapter summary generation: Uses LLMs to generate concise summaries for each chapter
- Agent Skills compatible: Standardized module that can be called by AI agents supporting the Agent Skills protocol

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd epub-agent-skill
```

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

The skill function can be called directly with the path to an EPUB file:

```python
from epub_agent_skill.main import skill

result = skill("/path/to/book.epub")
print(result)
```

The result contains:
- `metadata`: Book title, author, language, identifier
- `outline`: Hierarchical structure of the book
- `summaries`: Concise summaries for each chapter

## Configuration

To enable full LLM-powered processing, configure an LLM provider (e.g., OpenAI, Anthropic). Without an LLM provider, the module falls back to basic text extraction.

## Project Structure

```
epub-agent-skill/
├── epub_agent_skill/         # Main package
│   ├── __init__.py          # Package initialization
│   └── main.py              # Main skill implementation
├── requirements.txt         # Project dependencies
├── README.md               # Project documentation
└── LICENSE                 # License information
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.