r"""Build the flat Editorial-Manager submission ZIP for the paper.

EM (Editorial Manager) LaTeX submissions need a FLAT (non-nested) file
structure: all required source files at the top level, no subdirectories, and
no non-required files. This script inlines the ``\input{sections/...}`` files
into a single self-contained ``main.tex``, compiles it (and the title page),
and packages the ZIP with only the required files.

Required files for the EM LaTeX submission:
- main.tex (flat, self-contained manuscript source)
- references.bib (BibTeX database)
- apalike-doi.bst (the custom bibliography style, shipped with the submission)
- title-page.tex / title-page.pdf (the EM title page)
- main.pdf / title-page.pdf (the compiled PDFs)

Usage: python scripts/build_em_submission.py
"""

from __future__ import annotations

import re
import subprocess
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper"
OUT = ROOT / "paper" / "em-submission"
TECTONIC = "/tmp/tectonic"


def flatten(tex: str, paper_dir: Path) -> str:
    """Inline \\input{sections/x} (and \\input{...}) into a single flat source,
    and rewrite figure paths (``figures/x``) to bare filenames for the flat
    EM structure."""

    def repl(m: re.Match) -> str:
        target = paper_dir / (m.group(1) + ".tex")
        if not target.exists():
            target = paper_dir / m.group(1)
        return target.read_text() if target.exists() else m.group(0)

    flat = re.sub(r"\\input\{([^}]+)\}", repl, tex)
    # EM structure is flat: rewrite figures/x.pdf -> x.pdf in \includegraphics.
    flat = re.sub(r"(\\includegraphics(?:\[[^\]]*\])?\{)figures/", r"\1", flat)
    return flat


def compile_pdf(tex_path: Path) -> None:
    subprocess.run(
        [TECTONIC, tex_path.name],
        cwd=tex_path.parent,
        check=True,
        capture_output=True,
        text=True,
    )


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    # 1. Flatten main.tex (inline the section \inputs) into em-submission/.
    main_src = (PAPER / "main.tex").read_text()
    flat = flatten(main_src, PAPER)
    (OUT / "main.tex").write_text(flat)

    # 2. Copy the required support files (flat) and any referenced figures.
    (OUT / "references.bib").write_text((PAPER / "references.bib").read_text())
    (OUT / "apalike-doi.bst").write_text((PAPER / "apalike-doi.bst").read_text())
    (OUT / "title-page.tex").write_text((PAPER / "title-page.tex").read_text())
    # Find figures in the FLATTENED source (paths already rewritten to bare
    # filenames by flatten()) and copy them from paper/figures/.
    figures = []
    for m in re.finditer(r"\\includegraphics(?:\[[^\]]*\])?\{([A-Za-z0-9_\-]+\.(?:pdf|png))\}", flat):
        fig = m.group(1)
        (OUT / fig).write_bytes((PAPER / "figures" / fig).read_bytes())
        figures.append(fig)

    # 3. Compile the flat main.tex and the title page.
    compile_pdf(OUT / "main.tex")
    compile_pdf(OUT / "title-page.tex")

    # 4. Zip only the required files (flat).
    required = [
        "main.tex",
        "main.pdf",
        "references.bib",
        "apalike-doi.bst",
        "title-page.tex",
        "title-page.pdf",
    ] + figures
    zip_path = OUT / "em-submission.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for name in required:
            z.write(OUT / name, arcname=name)
    print(f"wrote {zip_path}")
    for name in required:
        print(f"  {name}: {(OUT / name).stat().st_size} bytes")


if __name__ == "__main__":
    main()
