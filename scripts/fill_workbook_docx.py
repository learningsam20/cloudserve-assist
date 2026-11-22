"""Fill the reference datasets pack workbook templates (.docx) from the Markdown workbooks.

The Markdown files in ``docs/workbooks/`` are the source of truth. Each data table in
a Markdown file is preceded by an HTML comment that names the template table it fills:

    <!-- docx-table: 2 -->
    | Who | What they told you | ... |
    |-----|--------------------|-----|
    | ... | ...                | ... |

    <!-- docx-prompt-text: 4 -->
    ```text
    full prompt text
    ```

For every workbook this script:

1. copies the blank reference datasets pack template into the output directory (overwriting any
   earlier copy, so the run is repeatable);
2. writes each Markdown table body into the matching template table, keeping the
   template's cell formatting (rows are added when the Markdown has more rows than the
   template; trailing rows that stay completely blank are removed);
3. checks that the Markdown header row matches the template header row.

Usage (from ``submission/``)::

    python -m scripts.fill_workbook_docx
    python -m scripts.fill_workbook_docx --pack-dir /path/to/workbook_templates --out-dir docs/workbooks

Requires ``python-docx`` (``pip install python-docx``).
"""

from __future__ import annotations

import argparse
import copy
import re
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path

from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph

SUBMISSION_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT_DIR = SUBMISSION_ROOT / "docs" / "workbooks"

# (template path relative to the pack dir, Markdown source file name in the output dir)
WORKBOOKS: list[tuple[str, str]] = [
    ("02_Stage_Workbooks/Stage_1_Discovery_Workbook.docx", "Stage_1_Discovery_Workbook.md"),
    ("02_Stage_Workbooks/Stage_2_PRD_Template.docx", "Stage_2_PRD_Template.md"),
    ("02_Stage_Workbooks/Stage_3_Prompt_Library.docx", "Stage_3_Prompt_Library.md"),
    ("02_Stage_Workbooks/Stage_4_Sprint_Plan.docx", "Stage_4_Sprint_Plan.md"),
    ("02_Stage_Workbooks/Stage_5_PRD_Revision_Log.docx", "Stage_5_PRD_Revision_Log.md"),
    ("04_Submission/Effort_Log.docx", "Effort_Log.md"),
]

TABLE_MARKER = re.compile(r"^<!--\s*docx-table:\s*(\d+)\s*-->\s*$")
PROMPT_MARKER = re.compile(r"^<!--\s*docx-prompt-text:\s*(\d+)\s*-->\s*$")


@dataclass
class MdTable:
    docx_index: int
    header: list[str]
    rows: list[list[str]]


@dataclass
class MdPrompt:
    docx_index: int
    text: str


@dataclass
class ParsedMarkdown:
    tables: list[MdTable] = field(default_factory=list)
    prompts: list[MdPrompt] = field(default_factory=list)


def _split_row(line: str) -> list[str]:
    body = line.strip()
    if body.startswith("|"):
        body = body[1:]
    if body.endswith("|") and not body.endswith("\\|"):
        body = body[:-1]
    cells = re.split(r"(?<!\\)\|", body)
    return [c.strip() for c in cells]


def _clean_cell(text: str) -> str:
    text = text.replace("\\|", "|")
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = text.replace("**", "").replace("`", "")
    text = text.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
    return text.strip()


def parse_markdown(path: Path) -> ParsedMarkdown:
    lines = path.read_text(encoding="utf-8").splitlines()
    parsed = ParsedMarkdown()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        t_match = TABLE_MARKER.match(line)
        p_match = PROMPT_MARKER.match(line)
        if t_match:
            idx = int(t_match.group(1))
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("|"):
                i += 1
            block: list[str] = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                block.append(lines[i])
                i += 1
            if len(block) < 2:
                raise ValueError(f"{path.name}: table for docx-table {idx} is incomplete")
            header = [_clean_cell(c) for c in _split_row(block[0])]
            rows = [[_clean_cell(c) for c in _split_row(r)] for r in block[2:]]
            parsed.tables.append(MdTable(idx, header, rows))
            continue
        if p_match:
            idx = int(p_match.group(1))
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                i += 1
            i += 1  # opening fence
            buf: list[str] = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                buf.append(lines[i])
                i += 1
            i += 1  # closing fence
            parsed.prompts.append(MdPrompt(idx, "\n".join(buf).strip("\n")))
            continue
        i += 1
    return parsed


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def _set_cell_text(cell, text: str) -> None:
    """Replace the cell text, reusing the first paragraph/run formatting of the template."""
    if _norm(cell.text) == _norm(text) and "\n" not in text:
        return
    paragraphs = cell.paragraphs
    first = paragraphs[0]
    for extra in paragraphs[1:]:
        extra._element.getparent().remove(extra._element)

    lines = text.split("\n") if text else [""]
    template_p = copy.deepcopy(first._element)

    def write(par: Paragraph, value: str) -> None:
        runs = par.runs
        if runs:
            runs[0].text = value
            for extra_run in runs[1:]:
                extra_run._element.getparent().remove(extra_run._element)
        else:
            par.add_run(value)

    write(first, lines[0])
    previous = first._element
    for value in lines[1:]:
        new_el = copy.deepcopy(template_p)
        previous.addnext(new_el)
        write(Paragraph(new_el, first._parent), value)
        previous = new_el


def _add_row_like_last(table: Table) -> None:
    last = table.rows[-1]._tr
    new_tr = copy.deepcopy(last)
    last.addnext(new_tr)
    new_row = table.rows[-1]
    for cell in new_row.cells:
        # Prefilled label text would be misleading on a copied row: blank it first.
        for par in cell.paragraphs[1:]:
            par._element.getparent().remove(par._element)
        for run in cell.paragraphs[0].runs:
            run.text = ""


def _row_is_blank(row) -> bool:
    return all(not c.text.strip() for c in row.cells)


def fill_table(table: Table, md: MdTable, label: str, warnings: list[str]) -> int:
    ncols = len(table.columns)
    if len(md.header) != ncols:
        raise ValueError(f"{label}: table {md.docx_index} has {ncols} columns, Markdown has {len(md.header)}")
    docx_header = [_norm(c.text) for c in table.rows[0].cells]
    md_header = [_norm(c) for c in md.header]
    if docx_header != md_header:
        warnings.append(f"{label}: table {md.docx_index} header differs (template: {docx_header}; markdown: {md_header})")

    needed = len(md.rows) + 1
    while len(table.rows) < needed:
        _add_row_like_last(table)

    written = 0
    for r_idx, values in enumerate(md.rows, start=1):
        if len(values) != ncols:
            raise ValueError(f"{label}: table {md.docx_index} row {r_idx} has {len(values)} cells, expected {ncols}")
        cells = table.rows[r_idx].cells
        for c_idx, value in enumerate(values):
            _set_cell_text(cells[c_idx], value)
            written += 1

    # Remove trailing template rows that remain completely blank.
    while len(table.rows) > needed and _row_is_blank(table.rows[-1]):
        tr = table.rows[-1]._tr
        tr.getparent().remove(tr)
    return written


def fill_prompt_text(table: Table, prompt: MdPrompt) -> None:
    # Row 0 is the heading; row 1 holds the prompt text; any further blank rows are dropped.
    _set_cell_text(table.rows[1].cells[0], prompt.text)
    while len(table.rows) > 2 and _row_is_blank(table.rows[-1]):
        tr = table.rows[-1]._tr
        tr.getparent().remove(tr)


def fill_workbook(template: Path, md_path: Path, out_path: Path) -> tuple[int, int, list[str]]:
    shutil.copyfile(template, out_path)
    document = Document(out_path)
    parsed = parse_markdown(md_path)
    warnings: list[str] = []
    seen: set[int] = set()
    cells_written = 0

    for md_table in parsed.tables:
        if md_table.docx_index >= len(document.tables):
            raise IndexError(f"{md_path.name}: docx-table {md_table.docx_index} not in {template.name}")
        if md_table.docx_index in seen:
            raise ValueError(f"{md_path.name}: docx-table {md_table.docx_index} listed twice")
        seen.add(md_table.docx_index)
        cells_written += fill_table(document.tables[md_table.docx_index], md_table, md_path.name, warnings)

    for prompt in parsed.prompts:
        if prompt.docx_index >= len(document.tables):
            raise IndexError(f"{md_path.name}: docx-prompt-text {prompt.docx_index} not in {template.name}")
        fill_prompt_text(document.tables[prompt.docx_index], prompt)
        cells_written += 1

    document.save(out_path)
    return len(parsed.tables) + len(parsed.prompts), cells_written, warnings


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fill .docx workbook templates from Markdown sources (optional ops helper)."
    )
    parser.add_argument(
        "--pack-dir",
        type=Path,
        required=True,
        help="Directory containing workbook .docx templates (caller-provided; not required at runtime)",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=DEFAULT_OUT_DIR,
        help="Directory holding the .md sources; filled .docx are written here",
    )
    args = parser.parse_args()

    pack_dir: Path = args.pack_dir.resolve()
    out_dir: Path = args.out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    failures = 0
    for rel_template, md_name in WORKBOOKS:
        template = pack_dir / rel_template
        md_path = out_dir / md_name
        out_path = out_dir / template.name
        if not template.exists():
            print(f"MISSING template: {template}", file=sys.stderr)
            failures += 1
            continue
        if not md_path.exists():
            print(f"MISSING markdown: {md_path}", file=sys.stderr)
            failures += 1
            continue
        try:
            n_tables, n_cells, warnings = fill_workbook(template, md_path, out_path)
        except Exception as exc:  # noqa: BLE001 - report every workbook, then fail
            print(f"FAILED {md_name}: {exc}", file=sys.stderr)
            failures += 1
            continue
        print(f"OK  {out_path.name}: {n_tables} tables, {n_cells} cells written")
        for w in warnings:
            print(f"  warning: {w}", file=sys.stderr)

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
