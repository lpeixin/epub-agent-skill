
---
name: epub-summary
description: Generate a summary of an EPUB file when given a file path pointing to an EPUB file.
---


## When to Use
Use this skill when:
- You are given a file path to an EPUB file
- The user requests a summary, outline, or key points from a book
- The content is too long to process in a single step

Do NOT use this skill when:
- The input is not an EPUB file
- The request is unrelated to summarization or content extraction

---

## Inputs
- `file_path` (string, required): Path to the EPUB file
- `mode` (string, optional):  
  - `outline` (default): Generate a structured outline of the book  
  - `chapter_summary`: Generate summaries for each chapter  
- `detail_level` (string, optional):  
  - `short`  
  - `medium` (default)  
  - `long`

---

## Outputs
The output should include:

### 1. Structured JSON
```json
{
  "title": "...",
  "sections": [
    {
      "title": "...",
      "chapters": [
        {
          "title": "...",
          "summary": "...",
          "key_points": ["...", "..."]
        }
      ]
    }
  ]
}