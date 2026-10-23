"""Build the CJFR submission package for the manuscript.

Assembles, from the Overleaf-linked manuscript repo, a submission-ready bundle:

- ``manuscript.pdf``   — the manuscript in CJFR submission format (double
  spaced, continuous line numbers, flush-left equation numbers, hidden link
  borders), compiled from a *flattened* self-contained source.
- ``title-page.pdf``   — the separate title page (single-blind review).
- ``title-page.tex``   — its source.
- ``references.bib`` / ``apalike-doi.bst`` — bibliography + custom style.
- ``fig_*.pdf``        — the figure files, for separate upload at resolution.
- ``submission-source.zip`` — a flat, self-contained LaTeX source bundle
  (inlined sections, bare figure filenames): ``main.tex`` +
  compiled ``main.pdf`` + ``references.bib`` + ``apalike-doi.bst`` +
  ``title-page.tex`` / ``title-page.pdf`` + figures.

The flattened ``main.tex`` forces the submission format (``\\submissiontrue``)
so the archived source compiles to the same PDF as ``manuscript.pdf``.

Usage:
    python scripts/build_cjfr_submission.py \
        --paper ../fresh_daugherty_manuscript \
        --out paper/cjfr-submission
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

FIG_RE = re.compile(r"\\includegraphics(?:\[[^\]]*\])?\{([A-Za-z0-9_\-]+\.(?:pdf|png))\}")


def run(cmd: list[str], cwd: Path) -> None:
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        sys.stderr.write(result.stdout[-3000:] + "\n" + result.stderr[-2000:] + "\n")
        raise SystemExit(f"command failed ({result.returncode}): {' '.join(cmd)}")


def flatten(tex: str, paper: Path) -> str:
    """Inline ``\\input{sections/x}`` and force the CJFR submission format."""

    def repl(m: re.Match) -> str:
        target = paper / (m.group(1) + ".tex")
        if not target.exists():
            target = paper / m.group(1)
        return target.read_text() if target.exists() else m.group(0)

    flat = re.sub(r"\\input\{([^}]+)\}", repl, tex)
    # Force the submission format on the standalone source.
    flat = re.sub(r"(?m)^\\submissionfalse\s*$", r"\\submissiontrue", flat)
    # Flat EM structure: figures/x.pdf -> x.pdf.
    flat = re.sub(r"(\\includegraphics(?:\[[^\]]*\])?\{)figures/", r"\1", flat)
    return flat


def compile_tex(work: Path, stem: str, *, bib: bool) -> None:
    args = ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", f"{stem}.tex"]
    run(args, work)
    if bib:
        run(["bibtex", stem], work)
    run(args, work)
    run(args, work)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--paper", default="../fresh_daugherty_manuscript", type=Path)
    ap.add_argument("--out", default="paper/cjfr-submission", type=Path)
    args = ap.parse_args()

    paper = args.paper.resolve()
    out = args.out.resolve()
    if not (paper / "main.tex").exists():
        raise SystemExit(f"no main.tex under --paper {paper}")

    # Work in a clean flat dir, then assemble the bundle at `out`.
    if out.exists():
        for item in out.iterdir():
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()
    out.mkdir(parents=True, exist_ok=True)
    flat = out / "source"
    flat.mkdir(parents=True)

    # 1. Flatten the manuscript and copy support files.
    (flat / "main.tex").write_text(flatten((paper / "main.tex").read_text(), paper))
    (flat / "references.bib").write_text((paper / "references.bib").read_text())
    (flat / "apalike-doi.bst").write_text((paper / "apalike-doi.bst").read_text())
    (flat / "title-page.tex").write_text((paper / "title-page.tex").read_text())

    # 2. Figures referenced by the flattened source.
    figures = sorted(set(FIG_RE.findall((flat / "main.tex").read_text())))
    for fig in figures:
        shutil.copy(paper / "figures" / fig, flat / fig)

    # 3. Compile the submission manuscript and the title page.
    compile_tex(flat, "main", bib=True)
    compile_tex(flat, "title-page", bib=False)

    # 4. Assemble the bundle (PDFs, sources, figures at the top level).
    shutil.copy(flat / "main.pdf", out / "manuscript.pdf")
    shutil.copy(flat / "title-page.pdf", out / "title-page.pdf")
    shutil.copy(flat / "title-page.tex", out / "title-page.tex")
    shutil.copy(flat / "references.bib", out / "references.bib")
    shutil.copy(flat / "apalike-doi.bst", out / "apalike-doi.bst")
    for fig in figures:
        shutil.copy(flat / fig, out / fig)

    # 5. Flat, self-contained Editorial Manager source zip.
    required = [
        "main.tex",
        "main.pdf",
        "references.bib",
        "apalike-doi.bst",
        "title-page.tex",
        "title-page.pdf",
        *figures,
    ]
    with zipfile.ZipFile(out / "submission-source.zip", "w", zipfile.ZIP_DEFLATED) as z:
        for name in required:
            z.write(flat / name, arcname=name)

    # The flat working tree is captured in the zip; drop it from the bundle.
    shutil.rmtree(flat)

    # 6. Bundle README.
    figs = ", ".join(f"`{f}`" for f in figures)
    (out / "README.md").write_text(
        f"""# CJFR submission package

For Canadian Journal of Forest Research (single-blind review). Generated by
`fresh-daugherty/scripts/build_cjfr_submission.py` from
`fresh_daugherty_manuscript` (Overleaf-linked).

- `manuscript.pdf` --- the complete manuscript in CJFR submission format
  (double spaced, continuous line numbers, flush-left equation numbers, hidden
  link borders): title, authors, abstract, text, figures, tables, references,
  and the declarations (Acknowledgements, Author contributions, Funding,
  Competing interests, Data availability).
- `title-page.pdf` / `title-page.tex` --- the separate title page (title,
  authors + affiliations, corresponding author, ORCIDs, keywords, article type).
- `references.bib`, `apalike-doi.bst` --- bibliography and custom style.
- Figures, for separate upload at resolution: {figs}.
- `submission-source.zip` --- flat, self-contained LaTeX source
  (`main.tex` with inlined sections, forced to the submission format, so it
  recompiles to `manuscript.pdf`); for the source-upload step (ScholarOne /
  Editorial Manager).

A cover letter is written at submission time. The benchmark record is archived
with a version DOI (see the manuscript's Data availability).
"""
    )

    print(f"wrote {out}")
    for name in ["manuscript.pdf", "title-page.pdf", "submission-source.zip", *figures]:
        print(f"  {name}: {(out / name).stat().st_size} bytes")


if __name__ == "__main__":
    main()
