#!/usr/bin/env python3
"""Extract content from EPUB files for summarization. Pure stdlib, no dependencies.

Usage:
    python extract_epub.py <epub_path> [-o output.json] [--max-chars N] [--toc-only]

Output: JSON with metadata, TOC structure, and cleaned chapter text in spine order.
"""

import argparse
import html.parser as _html_parser
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

# ── Namespace constants ──────────────────────────────────────────────

NS_CONTAINER = "urn:oasis:names:tc:opendocument:xmlns:container"
NS_OPF = "http://www.idpf.org/2007/opf"
NS_DC = "http://purl.org/dc/elements/1.1/"
NS_NCX = "http://www.daisy.org/z3986/2005/ncx/"
NS_XHTML = "http://www.w3.org/1999/xhtml"
EPUB_TYPE = "http://www.idpf.org/2007/ops"  # for epub:type attribute

# ── HTML stripper ────────────────────────────────────────────────────


class _HTMLStripper(_html_parser.HTMLParser):
    """Strip HTML tags and produce clean readable text."""

    def __init__(self):
        super().__init__()
        self._parts = []
        self._skip_stack = 0

    def handle_starttag(self, tag, _attrs):
        if tag in ("script", "style", "head", "title", "noscript"):
            self._skip_stack += 1
        if tag in ("br", "p", "div", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6",
                   "blockquote", "pre", "section", "article", "hr", "table"):
            self._parts.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style", "head", "title", "noscript"):
            if self._skip_stack > 0:
                self._skip_stack -= 1
        if tag in ("p", "div", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6",
                   "blockquote", "pre", "section", "article", "table"):
            self._parts.append("\n")

    def handle_data(self, data):
        if self._skip_stack == 0:
            self._parts.append(data)

    def get_text(self):
        raw = "".join(self._parts)
        raw = re.sub(r"\n{3,}", "\n\n", raw)
        raw = re.sub(r"[ \t]{2,}", " ", raw)
        raw = re.sub(r"\n +", "\n", raw)
        raw = re.sub(r" +\n", "\n", raw)
        return raw.strip()


def _strip_html(content):
    s = _HTMLStripper()
    s.feed(content)
    return s.get_text()


# ── XML helpers ───────────────────────────────────────────────────────


def _tag_local(elem):
    return elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag


# ── EPUB parsing ─────────────────────────────────────────────────────


def _get_opf_path(zf):
    """Find OPF file path from META-INF/container.xml."""
    try:
        raw = zf.read("META-INF/container.xml")
    except KeyError:
        return None
    tree = ET.fromstring(raw)
    rootfiles = tree.findall(".//{%s}rootfile" % NS_CONTAINER)
    for rf in rootfiles:
        path = rf.get("full-path") or rf.get("full-path") or rf.get("full_path")
        if path:
            return path
    return None


def _parse_opf(zf, opf_path):
    """Parse OPF: returns (metadata_dict, manifest_dict, spine_list)."""
    opf_dir = os.path.dirname(opf_path)
    raw = zf.read(opf_path)
    tree = ET.fromstring(raw)

    # Metadata — search within <metadata> element for precision
    meta = {}
    meta_elem = tree.find(".//{%s}metadata" % NS_OPF)
    search_root = meta_elem if meta_elem is not None else tree

    title_el = search_root.find(".//{%s}title" % NS_DC)
    meta["title"] = (title_el.text or "").strip() if title_el is not None and title_el.text else ""
    meta["authors"] = [c.text.strip() for c in search_root.findall(".//{%s}creator" % NS_DC) if c is not None and c.text]
    pub = search_root.find(".//{%s}publisher" % NS_DC)
    meta["publisher"] = (pub.text or "").strip() if pub is not None and pub.text else ""
    date_el = search_root.find(".//{%s}date" % NS_DC)
    meta["date"] = (date_el.text or "").strip() if date_el is not None and date_el.text else ""
    lang_el = search_root.find(".//{%s}language" % NS_DC)
    meta["language"] = (lang_el.text or "").strip() if lang_el is not None and lang_el.text else ""
    meta["identifiers"] = [i.text.strip() for i in search_root.findall(".//{%s}identifier" % NS_DC) if i is not None and i.text]
    desc_el = search_root.find(".//{%s}description" % NS_DC)
    meta["description"] = (desc_el.text or "").strip() if desc_el is not None and desc_el.text else ""

    # Manifest
    manifest = {}
    for item in tree.findall(".//{%s}item" % NS_OPF):
        item_id = item.get("id")
        href = item.get("href")
        if item_id and href:
            full = os.path.normpath(os.path.join(opf_dir, href))
            manifest[item_id] = full

    # Spine
    spine = []
    for ref in tree.findall(".//{%s}itemref" % NS_OPF):
        idref = ref.get("idref")
        if idref and idref in manifest:
            spine.append({"id": idref, "href": manifest[idref]})

    return meta, manifest, spine


def _parse_ncx(zf, ncx_href, opf_dir):
    """Parse NCX TOC (EPUB2). Returns flat+tree toc."""
    ncx_path = os.path.normpath(os.path.join(opf_dir, ncx_href))
    toc = []
    try:
        raw = zf.read(ncx_path)
    except KeyError:
        return toc
    tree = ET.fromstring(raw)

    nav_map = tree.find(".//{%s}navMap" % NS_NCX)
    if nav_map is None:
        return toc

    def _walk(parent, level=0):
        entries = []
        for np in parent.findall("{%s}navPoint" % NS_NCX):
            label = np.find("{%s}navLabel/{%s}text" % (NS_NCX, NS_NCX))
            content = np.find("{%s}content" % NS_NCX)
            title = (label.text or "Untitled").strip() if label is not None else "Untitled"
            src = content.get("src", "") if content is not None else ""
            entry = {"title": title, "src": src, "level": level, "children": []}
            entry["children"] = _walk(np, level + 1)
            entries.append(entry)
        return entries

    toc = _walk(nav_map)
    return toc


def _parse_nav(zf, nav_href, opf_dir):
    """Parse NAV XHTML TOC (EPUB3). Returns tree toc."""
    nav_path = os.path.normpath(os.path.join(opf_dir, nav_href))
    toc = []
    try:
        raw = zf.read(nav_path)
    except KeyError:
        return toc

    # Strip possible XML declaration before parsing
    raw_str = raw.decode("utf-8", errors="replace")
    tree = ET.fromstring(raw_str)

    # Find <nav epub:type="toc"> — first try with epub:type attribute
    nav_elem = None
    for elem in tree.iter():
        if _tag_local(elem) == "nav":
            attrs = elem.attrib
            epub_type = None
            for k, v in attrs.items():
                if k == "{%s}type" % EPUB_TYPE or k.endswith("}type"):
                    epub_type = v
                    break
            if epub_type == "toc":
                nav_elem = elem
                break
    # Fallback: first <nav>
    if nav_elem is None:
        for elem in tree.iter():
            if _tag_local(elem) == "nav":
                nav_elem = elem
                break

    if nav_elem is None:
        return toc

    # Find <ol> inside nav
    ol = nav_elem.find(".//{%s}ol" % NS_XHTML)
    if ol is None:
        # try without namespace
        for child in nav_elem.iter():
            if _tag_local(child) == "ol":
                ol = child
                break

    if ol is None:
        return toc

    def _walk_ol(parent, level=0):
        entries = []
        for li in parent:
            if _tag_local(li) != "li":
                continue
            a = None
            for child in li:
                if _tag_local(child) == "a":
                    a = child
                    break
            if a is None:
                continue
            title = (a.text or "Untitled").strip()
            href = a.get("href", "")
            entry = {"title": title, "src": href, "level": level, "children": []}
            # Check for nested ol
            for child in li:
                if _tag_local(child) == "ol":
                    entry["children"] = _walk_ol(child, level + 1)
                    break
            entries.append(entry)
        return entries

    toc = _walk_ol(ol)
    return toc


def _resolve_toc(toc_entries, manifest, opf_dir):
    """Resolve TOC src references to manifest item_ids and hrefs."""
    for entry in toc_entries:
        src = entry.get("src", "")
        fragment = ""
        if "#" in src:
            src, fragment = src.split("#", 1)
        if not src:
            _resolve_toc(entry.get("children", []), manifest, opf_dir)
            continue

        resolved = None
        src_basename = os.path.basename(src)
        for item_id, href in manifest.items():
            if href == src:
                resolved = (item_id, href)
                break
            if href.endswith("/" + src) or href.endswith("\\" + src):
                resolved = (item_id, href)
                break
            if os.path.basename(href) == src_basename:
                resolved = (item_id, href)
                break
            # try OPF-relative
            candidate = os.path.normpath(os.path.join(opf_dir, src))
            if href == candidate:
                resolved = (item_id, href)
                break

        if resolved:
            entry["item_id"] = resolved[0]
            entry["href"] = resolved[1]
        else:
            entry["href"] = os.path.normpath(os.path.join(opf_dir, src)) if not src.startswith("/") else src

        _resolve_toc(entry.get("children", []), manifest, opf_dir)


def _flatten_toc(toc, result=None, parent=None):
    if result is None:
        result = []
    for e in toc:
        result.append({
            "title": e["title"],
            "level": e.get("level", 0),
            "href": e.get("href", ""),
            "parent": parent,
        })
        _flatten_toc(e.get("children", []), result, e["title"])
    return result


def _find_toc_title(toc, href, item_id):
    """Find the best TOC title for a given spine item."""
    candidates = []
    for entry in toc:
        e_href = entry.get("href", "")
        e_id = entry.get("item_id", "")
        if e_href and href:
            if e_href == href:
                candidates.append((0, entry["title"]))
            elif href.endswith(os.path.basename(e_href)):
                candidates.append((1, entry["title"]))
            elif e_href.endswith(os.path.basename(href)):
                candidates.append((1, entry["title"]))
        if e_id and item_id and e_id == item_id:
            candidates.append((0, entry["title"]))
        sub = _find_toc_title(entry.get("children", []), href, item_id)
        if sub:
            candidates.append(sub)
    if candidates:
        candidates.sort(key=lambda x: x[0])
        return candidates[0]
    return None


# ── Main extraction ──────────────────────────────────────────────────


def extract_epub(filepath, max_chars_per_chapter=50000):
    """Extract metadata, TOC, and chapter content from an EPUB file."""
    filepath = os.path.abspath(filepath)

    if not os.path.exists(filepath):
        return {"error": "File not found: %s" % filepath}

    if not filepath.lower().endswith(".epub"):
        return {"error": "Not an EPUB file (extension must be .epub): %s" % filepath}

    try:
        zf = zipfile.ZipFile(filepath, "r")
    except zipfile.BadZipFile:
        return {"error": "Not a valid ZIP archive — the file may be DRM-protected or corrupted."}

    # ── Find OPF ──
    opf_path = _get_opf_path(zf)
    if not opf_path:
        zf.close()
        return {"error": "Invalid EPUB: META-INF/container.xml is missing or malformed."}

    # ── Parse OPF ──
    try:
        metadata, manifest, spine = _parse_opf(zf, opf_path)
    except Exception as e:
        zf.close()
        return {"error": "Failed to parse OPF (%s): %s" % (opf_path, str(e))}

    opf_dir = os.path.dirname(opf_path)

    # ── Find and parse TOC ──
    toc = []

    # Look for NCX id in spine
    ncx_id = None
    raw_opf = zf.read(opf_path).decode("utf-8", errors="replace")
    # spine toc attribute
    spine_elem = ET.fromstring(raw_opf).find(".//{%s}spine" % NS_OPF)
    if spine_elem is not None:
        ncx_id = spine_elem.get("toc") or spine_elem.get("{%s}toc" % NS_OPF)

    if ncx_id and ncx_id in manifest:
        toc = _parse_ncx(zf, manifest[ncx_id], opf_dir)

    # If no NCX TOC, try NAV
    if not toc:
        for item_id, href in manifest.items():
            base = os.path.basename(href).lower()
            if base in ("nav.xhtml", "nav.html", "nav.htm", "toc.xhtml", "toc.html"):
                toc = _parse_nav(zf, href, opf_dir)
                if toc:
                    break

    # Last resort: any .ncx in manifest
    if not toc:
        for item_id, href in manifest.items():
            if href.lower().endswith(".ncx"):
                toc = _parse_ncx(zf, href, opf_dir)
                if toc:
                    break

    _resolve_toc(toc, manifest, opf_dir)

    # ── Extract chapters in spine order ──
    chapters = []
    total_chars = 0

    for idx, item in enumerate(spine):
        href = item["href"]
        item_id = item["id"]

        # Skip non-content
        if href.lower().endswith((".ncx", ".css", ".js", ".svg")):
            continue

        try:
            raw = zf.read(href)
        except KeyError:
            continue

        content = raw.decode("utf-8", errors="replace")
        text = _strip_html(content)

        if not text.strip():
            continue

        char_count = len(text)
        total_chars += char_count

        if max_chars_per_chapter and char_count > max_chars_per_chapter:
            text = text[:max_chars_per_chapter] + "\n\n[Content truncated — chapter exceeds max_chars limit]"

        # Find title from TOC
        title = None
        found = _find_toc_title(toc, href, item_id)
        if found:
            title = found[1]
        if not title:
            title = "Chapter %d" % (idx + 1)

        chapters.append({
            "index": idx + 1,
            "item_id": item_id,
            "title": title,
            "char_count": char_count,
            "content": text,
        })

    zf.close()

    flat_toc = _flatten_toc(toc)

    result = {
        "metadata": metadata,
        "structure": {
            "total_chapters": len(chapters),
            "total_characters": total_chars,
            "toc_tree": toc,
            "toc_flat": flat_toc,
            "chapters": chapters,
        },
    }

    return result


# ── CLI ──────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="Extract content from EPUB files for summarization.")
    parser.add_argument("epub_path", help="Path to the EPUB file")
    parser.add_argument("-o", "--output", help="Write JSON output to file instead of stdout")
    parser.add_argument("--max-chars", type=int, default=50000,
                        help="Max characters per chapter (default: 50000)")
    parser.add_argument("--toc-only", action="store_true",
                        help="Extract only metadata and TOC, no chapter content")
    args = parser.parse_args()

    if args.toc_only:
        args.max_chars = 0

    result = extract_epub(args.epub_path, max_chars_per_chapter=args.max_chars)

    out = json.dumps(result, ensure_ascii=False, indent=2)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out)
        print("Output written to %s" % args.output, file=sys.stderr)
    else:
        print(out)


if __name__ == "__main__":
    main()
