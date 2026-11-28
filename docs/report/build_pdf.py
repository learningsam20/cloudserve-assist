#!/usr/bin/env python3
"""Build the CloudServe report PDF from Markdown (reportlab only, no network).

Usage (from ``submission/``):

    python docs/report/build_pdf.py
    python docs/report/build_pdf.py --input docs/report/CloudServe_Assistant_Report.md \
                                    --output docs/report/CloudServe_Assistant_Report.pdf

Dependency: ``pip install reportlab`` (documentation tooling only; it is not imported by
the runtime and is not part of ``requirements.txt``).

Supported Markdown subset
-------------------------
* ``#`` document title, ``##`` / ``###`` / ``####`` headings, ``---`` rules
* paragraphs, ``-`` / ``*`` bullet lists, ``1.`` numbered lists, ``>`` block quotes
* pipe tables (header row + separator), cell text may contain inline markup and ``<br>``
* fenced code blocks (monospace, wrapped)
* inline ``**bold**``, ``*italic*``, `` `code` ``, ``[text](url)`` (url dropped), HTML entities
* ``<!-- pagebreak -->`` forces a page break
* ```` ```chart ```` fenced JSON block -> native bar chart (``bar`` or ``hbar``)
* ```` ```diagram ```` fenced JSON block -> native flow / box diagram
* ``![alt](path)`` embeds a PNG/JPG relative to the Markdown file

Captions are ordinary bold lines starting ``**Table N.**`` or ``**Figure N.**``. The builder
checks that numbering is sequential and that every caption is referred to elsewhere in the
text, and prints warnings otherwise.

The PDF reports total pages and body pages (everything before the first heading that starts
with ``Appendix``).
"""
from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
from pathlib import Path

try:
    from reportlab.graphics.charts.barcharts import HorizontalBarChart, VerticalBarChart
    from reportlab.graphics.charts.legends import Legend
    from reportlab.graphics.shapes import Drawing, Line, Polygon, Rect, String
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import (
        BaseDocTemplate,
        Flowable,
        Frame,
        Image,
        KeepTogether,
        ListFlowable,
        ListItem,
        CondPageBreak,
        PageBreak,
        PageTemplate,
        Paragraph,
        Preformatted,
        Spacer,
        Table,
        TableStyle,
    )
    from reportlab.platypus.tableofcontents import TableOfContents
except ImportError as exc:  # pragma: no cover
    sys.stderr.write(f"error: reportlab is required ({exc}). Install with: pip install reportlab\n")
    raise SystemExit(2)

HERE = Path(__file__).resolve().parent
DEFAULT_INPUT = HERE / "CloudServe_Assistant_Report.md"
DEFAULT_OUTPUT = HERE / "CloudServe_Assistant_Report.pdf"

PAGE_W, PAGE_H = A4
MARGIN_X = 2.1 * cm
MARGIN_TOP = 2.2 * cm
MARGIN_BOTTOM = 2.0 * cm
FRAME_W = PAGE_W - 2 * MARGIN_X

INK = colors.HexColor("#1b2430")
ACCENT = colors.HexColor("#1f4e79")
RULE = colors.HexColor("#b8c2cc")
HEAD_BG = colors.HexColor("#e6edf4")
ZEBRA = colors.HexColor("#f6f8fa")
CODE_BG = colors.HexColor("#f3f4f6")
PALETTE = [
    colors.HexColor("#1f4e79"),
    colors.HexColor("#c0504d"),
    colors.HexColor("#6a9f58"),
    colors.HexColor("#e0a030"),
    colors.HexColor("#7d5ba6"),
]


# --------------------------------------------------------------------------- fonts
def register_fonts() -> dict[str, str]:
    """Prefer the Unicode-capable Vera family shipped with reportlab; fall back to core fonts."""
    fonts_dir = Path(os.path.dirname(__import__("reportlab").__file__)) / "fonts"
    wanted = {
        "Body": "Vera.ttf",
        "Body-Bold": "VeraBd.ttf",
        "Body-Italic": "VeraIt.ttf",
        "Body-BoldItalic": "VeraBI.ttf",
    }
    try:
        for name, fname in wanted.items():
            pdfmetrics.registerFont(TTFont(name, str(fonts_dir / fname)))
        pdfmetrics.registerFontFamily(
            "Body", normal="Body", bold="Body-Bold", italic="Body-Italic", boldItalic="Body-BoldItalic"
        )
        return {"body": "Body", "bold": "Body-Bold", "italic": "Body-Italic", "mono": "Courier", "unicode": "1"}
    except Exception:  # pragma: no cover - font files missing
        return {"body": "Helvetica", "bold": "Helvetica-Bold", "italic": "Helvetica-Oblique", "mono": "Courier", "unicode": "0"}


FONTS = register_fonts()

_LATIN_FALLBACK = {
    "\u2192": "->", "\u2190": "<-", "\u2264": "<=", "\u2265": ">=", "\u2248": "~", "\u2286": "in",
    "\u2014": "-", "\u2013": "-", "\u2019": "'", "\u2018": "'", "\u201c": '"', "\u201d": '"',
    "\u2026": "...", "\u00d7": "x", "\u2713": "ok", "\u2192 ": "-> ",
}


def latin1_safe(text: str) -> str:
    """Core PDF fonts cannot show many symbols; also used for Courier code blocks."""
    out = []
    for ch in text:
        if ch in _LATIN_FALLBACK:
            out.append(_LATIN_FALLBACK[ch])
        elif ord(ch) < 256:
            out.append(ch)
        else:
            out.append("?")
    return "".join(out)


def font_safe(text: str) -> str:
    return text if FONTS["unicode"] == "1" else latin1_safe(text)


# --------------------------------------------------------------------------- styles
def make_styles() -> dict[str, ParagraphStyle]:
    f = FONTS
    base = ParagraphStyle("base", fontName=f["body"], fontSize=9.6, leading=14.0, textColor=INK, alignment=TA_JUSTIFY)
    return {
        "body": ParagraphStyle("body", parent=base, spaceAfter=7),
        "title": ParagraphStyle("title", parent=base, fontName=f["bold"], fontSize=24, leading=29, textColor=ACCENT, alignment=TA_LEFT, spaceAfter=10),
        "meta": ParagraphStyle("meta", parent=base, fontSize=10.5, leading=16, alignment=TA_LEFT),
        "h2": ParagraphStyle("h2", parent=base, fontName=f["bold"], fontSize=15, leading=19, textColor=ACCENT, alignment=TA_LEFT, spaceBefore=14, spaceAfter=7, keepWithNext=1),
        "h3": ParagraphStyle("h3", parent=base, fontName=f["bold"], fontSize=11.5, leading=15, textColor=INK, alignment=TA_LEFT, spaceBefore=9, spaceAfter=4, keepWithNext=1),
        "h4": ParagraphStyle("h4", parent=base, fontName=f["bold"], fontSize=10, leading=13, textColor=INK, alignment=TA_LEFT, spaceBefore=6, spaceAfter=3, keepWithNext=1),
        "bullet": ParagraphStyle("bullet", parent=base, spaceAfter=3),
        "quote": ParagraphStyle("quote", parent=base, fontName=f["italic"], leftIndent=14, rightIndent=10, textColor=colors.HexColor("#3a4654"), spaceAfter=7, borderPadding=(2, 2, 2, 8)),
        "caption": ParagraphStyle("caption", parent=base, fontSize=8.6, leading=11.5, alignment=TA_LEFT, textColor=colors.HexColor("#33414f"), spaceBefore=3, spaceAfter=9),
        "tcaption": ParagraphStyle("tcaption", parent=base, fontSize=8.6, leading=11.5, alignment=TA_LEFT, textColor=colors.HexColor("#33414f"), spaceBefore=6, spaceAfter=3),
        "cell": ParagraphStyle("cell", parent=base, fontSize=8.0, leading=10.4, alignment=TA_LEFT),
        "cellh": ParagraphStyle("cellh", parent=base, fontName=f["bold"], fontSize=8.0, leading=10.4, alignment=TA_LEFT),
        "code": ParagraphStyle("code", fontName=f["mono"], fontSize=8, leading=10.2, textColor=INK, backColor=CODE_BG, borderPadding=5, leftIndent=4, rightIndent=4, spaceBefore=3, spaceAfter=9),
        "toc1": ParagraphStyle("toc1", parent=base, fontName=f["bold"], fontSize=9.4, leading=12.2, alignment=TA_LEFT),
        "toc2": ParagraphStyle("toc2", parent=base, fontSize=9, leading=13, leftIndent=14, alignment=TA_LEFT),
        "toch": ParagraphStyle("toch", parent=base, fontName=f["bold"], fontSize=15, leading=19, textColor=ACCENT, alignment=TA_LEFT, spaceAfter=8),
    }


STYLES = make_styles()


# --------------------------------------------------------------------------- inline markup
_CODE_RE = re.compile(r"`([^`]+)`")
_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
_BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
_ITAL_RE = re.compile(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])")


def inline(text: str) -> str:
    """Convert a Markdown inline string into reportlab Paragraph markup."""
    text = html.unescape(text.strip())
    text = re.sub(r"<br\s*/?>", "\x00BR\x00", text, flags=re.I)
    # Protect code spans first.
    codes: list[str] = []

    def stash(m: re.Match[str]) -> str:
        codes.append(m.group(1))
        return f"\x00C{len(codes) - 1}\x00"

    text = _CODE_RE.sub(stash, text)
    text = _LINK_RE.sub(lambda m: m.group(1), text)
    text = font_safe(text)
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = _BOLD_RE.sub(r"<b>\1</b>", text)
    text = _ITAL_RE.sub(r"<i>\1</i>", text)
    text = text.replace("\x00BR\x00", "<br/>")

    def unstash(m: re.Match[str]) -> str:
        raw = latin1_safe(codes[int(m.group(1))])
        raw = raw.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        return f'<font face="{FONTS["mono"]}" size="8.4" color="#7a2e2e">{raw}</font>'

    text = re.sub(r"\x00C(\d+)\x00", unstash, text)
    return text


# --------------------------------------------------------------------------- flowables
class AnchoredHeading(Paragraph):
    """Heading paragraph that notifies the TOC and records appendix start."""

    def __init__(self, text: str, style: ParagraphStyle, level: int, plain: str):
        super().__init__(text, style)
        self.toc_level = level
        self.plain = plain


class ReportDoc(BaseDocTemplate):
    def __init__(self, filename: str, title: str, author: str):
        super().__init__(
            filename,
            pagesize=A4,
            leftMargin=MARGIN_X,
            rightMargin=MARGIN_X,
            topMargin=MARGIN_TOP,
            bottomMargin=MARGIN_BOTTOM,
            title=title,
            author=author,
            subject="CloudServe Assistant - CloudServe Report",
        )
        frame = Frame(self.leftMargin, self.bottomMargin, FRAME_W, PAGE_H - MARGIN_TOP - MARGIN_BOTTOM, id="main", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
        self.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=self._decorate)])
        self.appendix_start_page: int | None = None
        self.body_start_page: int | None = None
        self.header_title = title

    def _decorate(self, canvas, doc):  # noqa: ANN001
        canvas.saveState()
        canvas.setStrokeColor(RULE)
        canvas.setLineWidth(0.5)
        if doc.page > 1:
            canvas.line(MARGIN_X, PAGE_H - 1.5 * cm, PAGE_W - MARGIN_X, PAGE_H - 1.5 * cm)
            canvas.setFont(FONTS["body"], 7.8)
            canvas.setFillColor(colors.HexColor("#5b6773"))
            canvas.drawString(MARGIN_X, PAGE_H - 1.25 * cm, font_safe(self.header_title))
        canvas.line(MARGIN_X, 1.5 * cm, PAGE_W - MARGIN_X, 1.5 * cm)
        canvas.setFont(FONTS["body"], 8)
        canvas.setFillColor(colors.HexColor("#5b6773"))
        canvas.drawRightString(PAGE_W - MARGIN_X, 1.0 * cm, f"Page {doc.page}")
        canvas.restoreState()

    def afterFlowable(self, flowable):  # noqa: ANN001
        if isinstance(flowable, AnchoredHeading):
            level, text = flowable.toc_level, flowable.plain
            if level in (0, 1):
                key = f"h{self.page}-{abs(hash(text))}"
                self.canv.bookmarkPage(key)
                self.canv.addOutlineEntry(text, key, level=level, closed=level == 1)
                if level == 0:  # contents lists sections only; subsections stay in the PDF outline
                    self.notify("TOCEntry", (level, text, self.page, key))
            if level == 0 and self.body_start_page is None and re.match(r"^1\.", text):
                self.body_start_page = self.page
            if level == 0 and text.lower().startswith("appendix") and self.appendix_start_page is None:
                self.appendix_start_page = self.page


class RuleLine(Flowable):
    def __init__(self, width: float, color=RULE, thickness: float = 0.6):  # noqa: ANN001
        super().__init__()
        self.width, self.color, self.thickness = width, color, thickness

    def wrap(self, aw, ah):  # noqa: ANN001
        return self.width, 8

    def draw(self):
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(self.thickness)
        self.canv.line(0, 4, self.width, 4)


# --------------------------------------------------------------------------- charts / diagrams
def build_chart(spec: dict) -> Drawing:
    kind = spec.get("type", "bar")
    cats = spec["categories"]
    series = spec["series"]
    width = FRAME_W
    height = float(spec.get("height", 215))
    d = Drawing(width, height)
    title = spec.get("title", "")
    if title:
        d.add(String(width / 2, height - 11, font_safe(title), fontName=FONTS["bold"], fontSize=9.5, textAnchor="middle", fillColor=INK))
    chart = VerticalBarChart() if kind == "bar" else HorizontalBarChart()
    left = 52 if kind == "bar" else 130
    multi = len(series) > 1
    chart.x = left
    chart.y = 34
    chart.width = width - left - 18
    chart.height = height - (34 + (58 if multi else 36))
    chart.data = [[(v if v is not None else 0) for v in s["values"]] for s in series]
    chart.categoryAxis.categoryNames = [font_safe(str(c)) for c in cats]
    chart.categoryAxis.labels.fontName = FONTS["body"]
    chart.categoryAxis.labels.fontSize = 7.6
    chart.categoryAxis.strokeColor = RULE
    if kind == "bar":
        chart.categoryAxis.labels.boxAnchor = "n"
        chart.categoryAxis.labels.dy = -3
    chart.valueAxis.labels.fontName = FONTS["body"]
    chart.valueAxis.labels.fontSize = 7.6
    chart.valueAxis.strokeColor = RULE
    chart.valueAxis.gridStrokeColor = colors.HexColor("#e3e8ee")
    chart.valueAxis.visibleGrid = True
    chart.valueAxis.valueMin = spec.get("min", 0)
    if "max" in spec:
        chart.valueAxis.valueMax = spec["max"]
    if "step" in spec:
        chart.valueAxis.valueStep = spec["step"]
    chart.barWidth = 11 if len(series) > 1 else 22
    chart.groupSpacing = 8
    chart.barSpacing = 1.5
    chart.bars.strokeColor = None
    for i, s in enumerate(series):
        chart.bars[i].fillColor = PALETTE[i % len(PALETTE)]
    chart.barLabelFormat = spec.get("label_format", "%s")
    chart.barLabels.fontName = FONTS["body"]
    chart.barLabels.fontSize = 7.4
    chart.barLabels.nudge = 7 if kind == "bar" else 12
    chart.barLabels.boxAnchor = "s" if kind == "bar" else "w"
    d.add(chart)
    ylabel = spec.get("ylabel", "")
    if ylabel:
        d.add(String(width / 2, 4, font_safe(ylabel), fontName=FONTS["italic"], fontSize=7.8, textAnchor="middle", fillColor=colors.HexColor("#5b6773")))
    if len(series) > 1:
        legend = Legend()
        legend.x = left
        legend.y = height - 38
        legend.fontName = FONTS["body"]
        legend.fontSize = 7.8
        legend.alignment = "right"
        legend.columnMaximum = 1
        legend.deltax = 190
        legend.dxTextSpace = 5
        legend.boxAnchor = "sw"
        legend.colorNamePairs = [(PALETTE[i % len(PALETTE)], font_safe(s["name"])) for i, s in enumerate(series)]
        d.add(legend)
    return d


def build_diagram(spec: dict) -> Drawing:
    """Flow of boxes in rows with arrows between consecutive boxes (row-major, wrapping)."""
    rows = spec["rows"]
    box_h = float(spec.get("box_height", 34))
    gap_y = 24
    height = len(rows) * box_h + (len(rows) - 1) * gap_y + 46
    width = FRAME_W
    d = Drawing(width, height)
    title = spec.get("title", "")
    if title:
        d.add(String(width / 2, height - 10, font_safe(title), fontName=FONTS["bold"], fontSize=9.5, textAnchor="middle", fillColor=INK))
    centers: dict[str, tuple[float, float, float]] = {}
    for r, row in enumerate(rows):
        n = len(row)
        gap_x = 16
        bw = (width - 16 - gap_x * (n - 1)) / n
        y = height - 26 - box_h - r * (box_h + gap_y)
        for i, node in enumerate(row):
            x = 8 + i * (bw + gap_x)
            label = node if isinstance(node, str) else node["label"]
            sub = "" if isinstance(node, str) else node.get("sub", "")
            fill = colors.HexColor("#e6edf4") if isinstance(node, str) else colors.HexColor(node.get("fill", "#e6edf4"))
            d.add(Rect(x, y, bw, box_h, rx=4, ry=4, fillColor=fill, strokeColor=ACCENT, strokeWidth=0.9))
            if sub:
                d.add(String(x + bw / 2, y + box_h - 14, font_safe(label), fontName=FONTS["bold"], fontSize=8.2, textAnchor="middle", fillColor=INK))
                d.add(String(x + bw / 2, y + 8, font_safe(sub), fontName=FONTS["body"], fontSize=6.8, textAnchor="middle", fillColor=colors.HexColor("#46525f")))
            else:
                d.add(String(x + bw / 2, y + box_h / 2 - 3, font_safe(label), fontName=FONTS["bold"], fontSize=8.2, textAnchor="middle", fillColor=INK))
            centers[f"{r}:{i}"] = (x, y, bw)
            if i > 0:  # horizontal arrow from previous box
                px, py, pbw = centers[f"{r}:{i - 1}"]
                x0, x1, ym = px + pbw, x, y + box_h / 2
                d.add(Line(x0, ym, x1 - 1, ym, strokeColor=ACCENT, strokeWidth=1))
                d.add(Polygon([x1, ym, x1 - 5, ym + 3, x1 - 5, ym - 3], fillColor=ACCENT, strokeColor=ACCENT))
        if r > 0:  # vertical arrow from last box of previous row down to the first box of this row (via elbow)
            px, py, pbw = centers[f"{r - 1}:{len(rows[r - 1]) - 1}"]
            fx, fy, fbw = centers[f"{r}:0"]
            xs, ys = px + pbw / 2, py
            ye = fy + box_h
            ymid = ys - gap_y / 2
            d.add(Line(xs, ys, xs, ymid, strokeColor=ACCENT, strokeWidth=1))
            d.add(Line(xs, ymid, fx + fbw / 2, ymid, strokeColor=ACCENT, strokeWidth=1))
            d.add(Line(fx + fbw / 2, ymid, fx + fbw / 2, ye + 1, strokeColor=ACCENT, strokeWidth=1))
            d.add(Polygon([fx + fbw / 2, ye, fx + fbw / 2 - 3, ye + 5, fx + fbw / 2 + 3, ye + 5], fillColor=ACCENT, strokeColor=ACCENT))
    note = spec.get("note", "")
    if note:
        d.add(String(width / 2, 2, font_safe(note), fontName=FONTS["italic"], fontSize=7.4, textAnchor="middle", fillColor=colors.HexColor("#5b6773")))
    return d


# --------------------------------------------------------------------------- tables
def _col_widths(header: list[str], rows: list[list[str]]) -> list[float]:
    """Width = longest unbreakable word (so ids never wrap mid-token) + share of the rest by content."""
    n = len(header)
    plain = lambda t: re.sub(r"<br\s*/?>", " ", re.sub(r"[`*]", "", t))  # noqa: E731
    mins, weights = [], []
    for c in range(n):
        cells = [plain(header[c])] + [plain(r[c]) if c < len(r) else "" for r in rows]
        longest_word = max((len(w) for cell in cells for w in cell.split()), default=4)
        mins.append(min(longest_word, 26) * 4.9 + 10)
        lens = [len(cell) for cell in cells]
        weights.append(max(1.0, min(sum(lens) / len(lens) * 0.6 + max(lens) * 0.4, 70.0)))
    if sum(mins) >= FRAME_W:
        scale = FRAME_W / sum(mins)
        return [m * scale for m in mins]
    spare = FRAME_W - sum(mins)
    tw = sum(weights)
    return [m + spare * w / tw for m, w in zip(mins, weights)]


def build_table(header: list[str], rows: list[list[str]]) -> Table:
    n = len(header)
    data = [[Paragraph(inline(h), STYLES["cellh"]) for h in header]]
    for r in rows:
        r = (r + [""] * n)[:n]
        data.append([Paragraph(inline(c) if c.strip() else "&nbsp;", STYLES["cell"]) for c in r])
    t = Table(data, colWidths=_col_widths(header, rows), repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), HEAD_BG),
        ("LINEBELOW", (0, 0), (-1, 0), 0.8, ACCENT),
        ("LINEBELOW", (0, 1), (-1, -1), 0.3, RULE),
        ("BOX", (0, 0), (-1, -1), 0.5, RULE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]
    for i in range(2, len(data), 2):
        style.append(("BACKGROUND", (0, i), (-1, i), ZEBRA))
    t.setStyle(TableStyle(style))
    return t


def split_row(line: str) -> list[str]:
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    cells, cur, in_code = [], [], False
    i = 0
    while i < len(line):
        ch = line[i]
        if ch == "\\" and i + 1 < len(line) and line[i + 1] == "|":
            cur.append("|")
            i += 2
            continue
        if ch == "`":
            in_code = not in_code
        if ch == "|" and not in_code:
            cells.append("".join(cur).strip())
            cur = []
        else:
            cur.append(ch)
        i += 1
    cells.append("".join(cur).strip())
    return cells


_SEP_RE = re.compile(r"^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$")


# --------------------------------------------------------------------------- markdown -> flowables
CAPTION_RE = re.compile(r"^\*\*(Table|Figure)\s+(\d+)\.\*\*")


def parse_markdown(md: str, base_dir: Path):
    lines = md.splitlines()
    story: list = []
    captions: list[tuple[str, int, str]] = []
    title_text = ""
    i = 0
    para: list[str] = []
    seen_title = False
    in_front_matter = True  # lines between title and first '---' / '##'
    appendix_seen = False

    def flush_para():
        nonlocal para
        if not para:
            return
        text = " ".join(s.strip() for s in para).strip()
        para = []
        if not text:
            return
        m = CAPTION_RE.match(text)
        if m:
            kind, num = m.group(1), int(m.group(2))
            captions.append((kind, num, text))
            style = STYLES["tcaption"] if kind == "Table" else STYLES["caption"]
            if kind == "Table":
                story.append(CondPageBreak(3.2 * cm))  # avoid a caption stranded at a page foot
            cap = Paragraph(inline(text), style)
            if kind == "Figure" and story and getattr(story[-1], "_is_chart", False):
                chart_block = story.pop()
                story.append(KeepTogether(list(chart_block._content) + [cap]))
            else:
                story.append(cap)
            return
        style = STYLES["meta"] if in_front_matter else STYLES["body"]
        story.append(Paragraph(inline(text), style))

    while i < len(lines):
        raw = lines[i]
        line = raw.rstrip()
        stripped = line.strip()

        if stripped.startswith("```"):
            flush_para()
            lang = stripped[3:].strip().lower()
            i += 1
            block: list[str] = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                block.append(lines[i])
                i += 1
            i += 1
            if lang in ("chart", "diagram"):
                try:
                    spec = json.loads("\n".join(block))
                    drawing = build_chart(spec) if lang == "chart" else build_diagram(spec)
                    block = KeepTogether([Spacer(1, 4), drawing])
                    block._is_chart = True
                    story.append(block)
                except Exception as exc:  # pragma: no cover
                    sys.stderr.write(f"warning: could not render {lang} block: {exc}\n")
            else:
                code = latin1_safe("\n".join(block))
                story.append(Preformatted(code, STYLES["code"]))
            continue

        if stripped == "<!-- pagebreak -->":
            flush_para()
            story.append(PageBreak())
            i += 1
            continue

        if not stripped:
            flush_para()
            i += 1
            continue

        if stripped == "---":
            flush_para()
            in_front_matter = False
            story.append(RuleLine(FRAME_W))
            i += 1
            continue

        hm = re.match(r"^(#{1,4})\s+(.*)$", stripped)
        if hm:
            flush_para()
            level = len(hm.group(1))
            text = hm.group(2).strip()
            if level == 1 and not seen_title:
                seen_title = True
                title_text = text
                story.append(Paragraph(inline(text), STYLES["title"]))
            else:
                in_front_matter = False
                if level == 2:
                    is_appendix = text.lower().startswith("appendix")
                    if is_appendix and not appendix_seen:
                        appendix_seen = True
                        story.append(PageBreak())
                    elif story and not is_appendix and text.lower().startswith(("1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.", "10.")):
                        pass
                    story.append(AnchoredHeading(inline(text), STYLES["h2"], 0, re.sub(r"[`*]", "", html.unescape(text))))
                elif level == 3:
                    story.append(AnchoredHeading(inline(text), STYLES["h3"], 1, re.sub(r"[`*]", "", html.unescape(text))))
                else:
                    story.append(AnchoredHeading(inline(text), STYLES["h4"], 2, re.sub(r"[`*]", "", html.unescape(text))))
            i += 1
            continue

        img = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)$", stripped)
        if img:
            flush_para()
            path = (base_dir / img.group(2)).resolve()
            if path.exists():
                im = Image(str(path))
                scale = min(1.0, FRAME_W / im.imageWidth)
                im.drawWidth, im.drawHeight = im.imageWidth * scale, im.imageHeight * scale
                story.append(im)
            else:
                sys.stderr.write(f"warning: image not found: {path}\n")
            i += 1
            continue

        if stripped.startswith("|") and i + 1 < len(lines) and _SEP_RE.match(lines[i + 1]):
            flush_para()
            header = split_row(stripped)
            i += 2
            rows: list[list[str]] = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(split_row(lines[i]))
                i += 1
            story.append(build_table(header, rows))
            story.append(Spacer(1, 9))
            continue

        if stripped.startswith(">"):
            flush_para()
            quote: list[str] = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quote.append(lines[i].strip().lstrip(">").strip())
                i += 1
            story.append(Paragraph(inline(" ".join(quote)), STYLES["quote"]))
            continue

        bm = re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)$", line)
        if bm:
            flush_para()
            ordered = bm.group(2)[0].isdigit()
            items: list[str] = []
            while i < len(lines):
                m2 = re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)$", lines[i].rstrip())
                if m2 and (m2.group(2)[0].isdigit() == ordered):
                    items.append(m2.group(3))
                    i += 1
                elif lines[i].startswith("  ") and lines[i].strip() and items and not re.match(r"^\s*([-*]|\d+\.)\s", lines[i]):
                    items[-1] += " " + lines[i].strip()
                    i += 1
                else:
                    break
            flow_items = [ListItem(Paragraph(inline(t), STYLES["bullet"]), leftIndent=16) for t in items]
            story.append(
                ListFlowable(
                    flow_items,
                    bulletType="1" if ordered else "bullet",
                    bulletFontName=FONTS["body"],
                    bulletFontSize=9,
                    leftIndent=16,
                    bulletFormat="%s." if ordered else None,
                    start="•" if not ordered else 1,
                )
            )
            story.append(Spacer(1, 4))
            continue

        # a line ending with two spaces is a hard break inside the front matter block
        if in_front_matter and raw.endswith("  "):
            para.append(stripped + "<br/>")
        else:
            para.append(stripped)
        i += 1

    flush_para()
    return story, title_text, captions


# --------------------------------------------------------------------------- caption checks
def check_captions(captions: list[tuple[str, int, str]], md: str) -> list[str]:
    problems: list[str] = []
    for kind in ("Table", "Figure"):
        nums = [n for k, n, _ in captions if k == kind]
        if nums != list(range(1, len(nums) + 1)):
            problems.append(f"{kind} captions are not sequential from 1: {nums}")
        for n in nums:
            cap_text = next(t for k, num, t in captions if k == kind and num == n)
            body = md.replace(cap_text, "")
            if not re.search(rf"\b{kind}s?\s+(?:\d+\s*(?:,|and|-|–)\s*)*{n}\b", body):
                problems.append(f"{kind} {n} is never referred to in the text")
    return problems


# --------------------------------------------------------------------------- build
def build(input_path: Path, output_path: Path) -> tuple[int, int | None, int | None]:
    md = input_path.read_text(encoding="utf-8")
    story, title_text, captions = parse_markdown(md, input_path.parent)
    author_m = re.search(r"\*\*Author:\*\*\s*([^\n*]+)", md)
    author = author_m.group(1).strip() if author_m else "Sameer J"
    title = re.sub(r"[`*]", "", title_text) or "CloudServe Assistant - CloudServe Report"

    for p in check_captions(captions, md):
        sys.stderr.write(f"warning: {p}\n")

    toc = TableOfContents()
    toc.levelStyles = [STYLES["toc1"]]
    toc.dotsMinLevel = 0

    # Insert TOC after the front matter (everything before the first '---' rule).
    insert_at = next((idx for idx, fl in enumerate(story) if isinstance(fl, RuleLine)), 1)
    front = story[: insert_at + 1]
    rest = story[insert_at + 1 :]
    toc_block = [Spacer(1, 6), Paragraph("Contents", STYLES["toch"]), toc, PageBreak()]
    full = front + toc_block + rest

    doc = ReportDoc(str(output_path), title, author)
    doc.multiBuild(full)

    from reportlab.pdfgen import canvas as _c  # noqa: F401  (ensures reportlab fully loaded)

    try:
        from pypdf import PdfReader  # optional

        total = len(PdfReader(str(output_path)).pages)
    except Exception:
        total = doc.page
    body = None
    if doc.appendix_start_page and doc.body_start_page:
        body = doc.appendix_start_page - doc.body_start_page
    appendix_pages = (total - doc.appendix_start_page + 1) if doc.appendix_start_page else None
    return total, body, appendix_pages


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    ap.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = ap.parse_args()
    if not args.input.exists():
        sys.stderr.write(f"error: input not found: {args.input}\n")
        return 2
    args.output.parent.mkdir(parents=True, exist_ok=True)
    total, body, appendix_pages = build(args.input, args.output)
    print(f"wrote {args.output}")
    print(f"pages_total={total}")
    if body is not None:
        print(f"pages_body_sections_1_to_10={body} (excludes cover/contents and appendices)")
    if appendix_pages is not None:
        print(f"pages_appendices={appendix_pages}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
