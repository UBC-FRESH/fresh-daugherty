"""Assemble the paper's LaTeX (Editorial Manager / journal submission format).

Reads ``planning/paper-draft.md``, converts the body (sections 1-6, software
availability, references) to LaTeX via pandoc, and wraps it in a proper
article-class preamble with the title/author/abstract/keywords as front
matter. Emits ``paper/paper.tex``.

Usage: python scripts/build_paper_tex.py
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MD = ROOT / "planning" / "paper-draft.md"
OUT = ROOT / "paper" / "paper.tex"


def _extract(md: str) -> tuple[str, str, str, str]:
    """Split the draft into (title, abstract, keywords, body)."""
    # Title: first markdown H1.
    title_m = re.search(r"^# (.+)$", md, flags=re.M)
    title = title_m.group(1).strip() if title_m else "Paper"
    # Abstract: the paragraph between "## Abstract" and "**Keywords".
    abs_m = re.search(r"## Abstract\n\n(.+?)\n\n\*\*Keywords", md, flags=re.S)
    abstract = abs_m.group(1).strip() if abs_m else ""
    # Keywords: the **Keywords:** line.
    kw_m = re.search(r"\*\*Keywords:\*\*(.+)", md)
    keywords = kw_m.group(1).strip() if kw_m else ""
    # Body: from "## 1. Introduction" to the end (drop the draft header and
    # the pandoc-level title/author block; the abstract/keywords go in front).
    body_m = re.search(r"## 1\. Introduction.*", md, flags=re.S)
    body = body_m.group(0) if body_m else md
    return title, abstract, keywords, body


def _pandoc_latex(md_body: str) -> str:
    return subprocess.run(
        ["pandoc", "-f", "markdown", "-t", "latex", "--wrap=none"],
        input=md_body,
        capture_output=True,
        text=True,
        check=True,
    ).stdout


def main() -> None:
    md = MD.read_text()
    title, abstract, keywords, body_md = _extract(md)
    body_tex = _pandoc_latex(body_md)
    # Convert the abstract + keywords through pandoc too (italic/code markup).
    abstract_tex = _pandoc_latex(abstract).strip()
    keywords_tex = _pandoc_latex(keywords).strip()

    # Demote pandoc's sections to LaTeX \section (markdown ## -> section).
    body_tex = body_tex.replace("\\subsection", "\\section").replace(
        "\\subsubsection", "\\subsection"
    )
    # Strip the manual section numbers (LaTeX auto-numbers).
    body_tex = re.sub(r"\\section\{(\d+(?:\.\d+)?)\.?\s+", r"\\section{", body_tex)
    body_tex = re.sub(r"\\subsection\{(\d+(?:\.\d+)?)\.?\s+", r"\\subsection{", body_tex)

    tex = rf"""\documentclass[12pt]{{article}}
\usepackage[utf8]{{inputenc}}
\usepackage[T1]{{fontenc}}
\usepackage{{amsmath,amssymb}}
\usepackage[margin=1in]{{geometry}}
\usepackage{{hyperref}}
\usepackage{{booktabs}}
\usepackage{{longtable}}
\title{{{title}}}
\author{{Gregory Paradis\thanks{{Department of Forest Resources Management,
Faculty of Forestry \& Environmental Stewardship, The University of British
Columbia, 2424 Main Mall, Vancouver, British Columbia, V6T 1Z4, Canada.
Corresponding author: gregory.paradis@ubc.ca}}}}
\date{{August 2026}}
\begin{{document}}
\maketitle
\begin{{abstract}}
{abstract_tex}
\end{{abstract}}
\noindent\textbf{{Keywords:}} {keywords_tex}

{body_tex}
\end{{document}}
"""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(tex)
    print(f"wrote {OUT} ({len(tex)} chars)")


if __name__ == "__main__":
    main()
