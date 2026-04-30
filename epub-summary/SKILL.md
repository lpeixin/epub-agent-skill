---
name: epub-summary
description: Generate structured summaries of EPUB books including outlines, chapter summaries, themes, and key takeaways. Use when the user provides an .epub file path and wants a summary, outline, chapter-by-chapter analysis, key points, or themes of the book.
license: MIT
metadata:
  version: "2.0"
---

## Workflow

### 1. Extract EPUB Content
Run the extraction script first:
```bash
python scripts/extract_epub.py <file_path> -o /tmp/epub_content.json
```
This produces JSON with metadata, TOC structure, and cleaned chapter text in spine order.

Options:
- `--toc-only` — extract only metadata and TOC (fast, for outline mode)
- `--max-chars N` — limit per-chapter text (default 50000, lower for very large books)

### 2. Determine Mode
Default: **comprehensive** (outline + chapter summaries + themes + key takeaways).

Other modes, use only when the user explicitly requests:
- `outline` — TOC hierarchy with one-sentence descriptions
- `chapter_summary` — detailed chapter-by-chapter summaries only
- `themes` — major themes and recurring concepts only
- `key_takeaways` — top actionable insights and conclusions only

### 3. Generate Summary
Read the extracted JSON. Produce output using the template at `assets/summary_template.md`.

Genre-specific focus:
- **Non-fiction**: Author's thesis, arguments, evidence, frameworks, actionable advice
- **Fiction**: Plot without spoilers, characters and arcs, setting, themes, writing style
- **Technical**: Preserve terminology and code, summarize concepts, note prerequisites and best practices

### 4. Validate
- Confirm chapter count in summary matches the extracted TOC
- Verify key themes are traceable to specific chapter content
- For fiction: remove spoilers unless the user explicitly requested them
- For large books: process chapters in batches, discard full text after summarizing each batch

## EPUB Gotchas
- EPUB is a ZIP file; the real content entry point is `META-INF/container.xml` → OPF file
- Reading order is in the OPF `spine`, not the TOC — spine is authoritative
- TOC format differs: EPUB2 uses NCX, EPUB3 uses NAV (XHTML). The script handles both.
- Chapter titles in TOC may not match spine items exactly — the script does best-effort matching
- Some spine items are non-content (cover images, copyright, CSS). The script skips these.
- DRM-protected files will fail immediately — notify the user
- Very large books: use `--max-chars 20000` and process chapters in batches of 10-15
