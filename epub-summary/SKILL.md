
---
name: epub-summary
description: Generate comprehensive summaries of EPUB books including structured outlines, chapter summaries, key themes, and important insights.
---

## Purpose
This skill enables AI agents to extract, analyze, and summarize content from EPUB ebook files. It provides structured output suitable for quick understanding of book content, study guides, or content indexing.

## When to Use
Use this skill when:
- You are given a file path to an EPUB file (.epub extension)
- The user requests a summary, outline, table of contents, or key points from a book
- The user wants to understand the main themes, arguments, or narrative of a book
- The content is too long to process in a single step and needs structured extraction
- The user needs study notes, book reviews, or content analysis

Do NOT use this skill when:
- The input is not an EPUB file (e.g., PDF, MOBI, TXT, DOCX)
- The request is unrelated to book summarization or content extraction
- The file path is invalid or the file doesn't exist
- The user only wants metadata (use epub-metadata skill instead if available)

## Prerequisites
Before processing, verify:
1. The file exists at the specified path
2. The file has a .epub extension
3. The file is a valid EPUB format (can be opened as a ZIP archive)
4. The file is accessible and readable

## Inputs
- `file_path` (string, **required**): Absolute or relative path to the EPUB file
  - Example: `/books/moby-dick.epub` or `./documents/learning-python.epub`
  
- `mode` (string, optional): Summary mode to generate
  - `outline` (**default**): Generate a hierarchical structured outline showing book organization
  - `chapter_summary`: Generate detailed summaries for each chapter/section
  - `themes`: Extract main themes, concepts, and recurring ideas
  - `key_takeaways`: Focus on actionable insights and main conclusions
  - `comprehensive`: Combine outline + chapter summaries + themes + key takeaways
  
- `detail_level` (string, optional): Depth of summary detail
  - `brief`: Very concise, 1-2 sentences per section/chapter
  - `short` (**default**): Concise but informative, 2-4 sentences per section/chapter
  - `medium`: Detailed summaries with context, 4-8 sentences per section/chapter
  - `long`: Comprehensive coverage with examples and quotes, 8+ sentences per section/chapter
  
- `language` (string, optional): Output language for the summary
  - Default: Same language as the book content
  - Examples: `en`, `zh`, `es`, `fr`, `de`, `ja`
  
- `include_metadata` (boolean, optional): Whether to include book metadata
  - Default: `true`
  - Includes: title, author(s), publisher, publication date, ISBN, description

## Processing Steps

### Step 1: File Validation
1. Check if the file exists at the given path
2. Verify it's a valid EPUB file (ZIP-based format with proper structure)
3. If validation fails, return an error message with suggestions

### Step 2: EPUB Structure Analysis
1. Parse the EPUB container to extract:
   - Book metadata (title, author, publisher, etc.)
   - Table of Contents (TOC) structure
   - Chapter/section hierarchy
   - Content files (XHTML/HTML)
2. Identify the logical reading order
3. Map chapters to their content locations

### Step 3: Content Extraction
1. Extract text content from each chapter/section
2. Clean HTML markup while preserving structure
3. Handle special elements:
   - Images (note their presence but don't describe unless relevant)
   - Tables (summarize key data)
   - Code blocks (preserve for technical books)
   - Footnotes/endnotes (integrate into main text if relevant)
4. Preserve formatting cues (headings, emphasis, lists)

### Step 4: Content Analysis & Summarization
Based on the selected `mode`:

**For `outline` mode:**
- Create a hierarchical structure matching the book's TOC
- Include section titles and brief descriptions (1-2 sentences)
- Show the logical flow and organization

**For `chapter_summary` mode:**
- For each chapter/section:
  - Identify the main argument or narrative point
  - Extract 3-5 key points or ideas
  - Write a coherent summary paragraph
  - Note any important examples, case studies, or anecdotes

**For `themes` mode:**
- Identify 5-10 major themes or concepts
- For each theme:
  - Provide a clear definition
  - Note where it appears in the book
  - Explain its significance
  - Give examples from the text

**For `key_takeaways` mode:**
- Extract the most important lessons or conclusions
- Focus on actionable insights
- Organize by importance or chronology
- Limit to 10-20 key takeaways maximum

**For `comprehensive` mode:**
- Combine all above modes
- Ensure coherence and avoid excessive repetition
- Prioritize clarity over completeness

### Step 5: Quality Checks
Before finalizing the summary:
1. Verify accuracy against source content
2. Ensure consistent tone and style
3. Check that key points are covered
4. Validate JSON structure (if applicable)
5. Confirm appropriate length for the detail_level
6. Remove any spoilers for fiction (unless explicitly requested)

## Outputs

### Primary Output Format
The output should be well-structured and include the following sections:

#### 1. Book Metadata (if include_metadata=true)
```json
{
  "metadata": {
    "title": "Book Title",
    "authors": ["Author Name"],
    "publisher": "Publisher Name",
    "publication_date": "YYYY-MM-DD",
    "isbn": "978-XXXXXXXXXX",
    "language": "en",
    "description": "Brief book description"
  }
}
```

#### 2. Structured Summary (JSON format)
```json
{
  "title": "Book Title",
  "mode": "chapter_summary",
  "detail_level": "medium",
  "summary": {
    "overview": "Brief 2-3 sentence overview of the entire book",
    "total_chapters": 12,
    "sections": [
      {
        "section_number": 1,
        "section_title": "Part One: Introduction",
        "section_summary": "Brief overview of this section",
        "chapters": [
          {
            "chapter_number": 1,
            "chapter_title": "Chapter 1: Getting Started",
            "summary": "Detailed summary of the chapter content...",
            "key_points": [
              "First important point or concept",
              "Second key idea or argument",
              "Third significant insight"
            ],
            "important_quotes": [
              "Notable quote from the chapter (optional)"
            ],
            "page_estimate": "15-20 pages"
          }
        ]
      }
    ]
  },
  "themes": [
    {
      "theme": "Theme name",
      "description": "Explanation of this theme",
      "relevance": "Why this theme matters in the book"
    }
  ],
  "key_takeaways": [
    "Main takeaway 1",
    "Main takeaway 2"
  ]
}
```

#### 3. Alternative: Markdown Format
If JSON is not specifically requested, provide a well-formatted Markdown summary:

```markdown
# [Book Title]

## Metadata
- **Author(s):** Author Name
- **Publisher:** Publisher Name
- **Published:** Date

## Overview
[Brief 2-3 sentence overview of the entire book]

## Table of Contents
1. [Section/Chapter Title](#section-1)
2. [Section/Chapter Title](#section-2)
...

## Detailed Summary

### Part One: [Section Title]
[Brief section overview]

#### Chapter 1: [Chapter Title]
**Summary:** [Detailed paragraph summarizing the chapter]

**Key Points:**
- Point 1
- Point 2
- Point 3

---

## Major Themes
1. **Theme Name:** Description and significance
2. **Theme Name:** Description and significance

## Key Takeaways
1. Main takeaway 1
2. Main takeaway 2

## Conclusion
[Final thoughts on the book's overall message or value]
```

## Best Practices

### For Non-Fiction Books
- Focus on arguments, evidence, and conclusions
- Highlight frameworks, models, or methodologies
- Extract actionable advice and recommendations
- Note case studies and real-world examples
- Identify the author's main thesis or argument

### For Fiction/Literature
- Summarize plot without major spoilers (unless requested)
- Identify main characters and their arcs
- Note literary devices and writing style
- Discuss themes and symbolism
- Describe setting and atmosphere
- Focus on narrative structure and pacing

### For Technical Books
- Preserve code examples and technical terminology
- Summarize concepts and their practical applications
- Note prerequisites and assumed knowledge
- Highlight best practices and common pitfalls
- Include diagrams or architecture descriptions (textually)

### For Academic/Scholarly Works
- Identify the research question or hypothesis
- Summarize methodology (if applicable)
- Present key findings and results
- Note limitations and future research directions
- Maintain academic tone and precision

## Error Handling

### Common Issues and Solutions

1. **File not found**
   - Error: "The specified EPUB file does not exist at [path]"
   - Suggestion: "Please verify the file path and try again"

2. **Invalid EPUB format**
   - Error: "The file is not a valid EPUB file"
   - Suggestion: "Ensure the file has .epub extension and is not corrupted"

3. **Protected/DRM content**
   - Error: "Cannot process DRM-protected EPUB file"
   - Suggestion: "Please use an unprotected version of the file"

4. **Empty or minimal content**
   - Warning: "The EPUB file contains very little text content"
   - Action: "Proceed with available content but note the limitation"

5. **Very large books**
   - Warning: "This book is exceptionally long ([X] chapters/pages)"
   - Action: "Consider using 'brief' detail_level or processing in sections"

6. **Complex formatting**
   - Warning: "Some content may have complex formatting that affects extraction"
   - Action: "Summaries will focus on text content; visual elements noted separately"

## Language and Tone Guidelines

- Use clear, professional language
- Maintain objectivity in summaries
- Avoid personal opinions unless specifically requested
- Use present tense for describing content
- Be concise but comprehensive
- Adapt tone to match the book's genre:
  - Academic: Formal and precise
  - Business: Professional and actionable
  - Fiction: Engaging and descriptive
  - Technical: Clear and precise

## Special Considerations

### Multi-Author Books
- Clearly attribute different sections to different authors when possible
- Note if the book is an anthology or collection

### Translations
- Note if the book is a translation
- Mention the original language if known
- Be aware of potential translation nuances

### Editions and Updates
- Note if specific edition information is available
- Mention if content appears outdated (for technical books)

### Illustrations and Figures
- Note the presence of important visuals
- Describe critical diagrams or charts in text
- Don't attempt to reproduce images

## Example Usage Scenarios

### Scenario 1: Quick Book Overview
```
Input: file_path="/books/atomic-habits.epub", mode="outline", detail_level="brief"
Output: Hierarchical outline with 1-2 sentence descriptions per chapter
```

### Scenario 2: Study Guide Creation
```
Input: file_path="/books/textbook.epub", mode="comprehensive", detail_level="long"
Output: Full summary with chapter details, key concepts, and study questions
```

### Scenario 3: Book Review Preparation
```
Input: file_path="/books/novel.epub", mode="themes", detail_level="medium"
Output: Analysis of major themes, character development, and literary techniques
```

### Scenario 4: Executive Summary
```
Input: file_path="/books/business-book.epub", mode="key_takeaways", detail_level="short"
Output: Top 10 actionable insights and main conclusions
```

## Performance Tips

1. **For large books (>500 pages):**
   - Use `brief` or `short` detail_level
   - Consider processing major sections separately
   - Focus on chapter-level rather than sub-section summaries

2. **For quick scanning:**
   - Use `outline` mode with `brief` detail
   - Request only metadata and TOC structure

3. **For deep understanding:**
   - Use `comprehensive` mode with `long` detail
   - Request themes and key takeaways in addition to summaries

4. **Memory efficiency:**
   - Process chapters sequentially if memory is limited
   - Summarize each chapter before moving to the next
   - Discard full text after extracting key information