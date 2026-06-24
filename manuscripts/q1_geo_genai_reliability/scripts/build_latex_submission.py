#!/usr/bin/env python3
"""Export the compact manuscript route to a LaTeX submission package."""

from __future__ import annotations

import re
import shutil
import subprocess
import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MS_DIR = ROOT / "manuscripts/q1_geo_genai_reliability"
SUBMISSION_DIR = MS_DIR / "submission"
OUT_DIR = SUBMISSION_DIR / "latex"
TEMPLATE_DIR = SUBMISSION_DIR / "interact_template"
MAIN_MD = SUBMISSION_DIR / "blinded_compact_main_manuscript.md"
BIB_IN = SUBMISSION_DIR / "references.bib"
TEX_OUT = OUT_DIR / "main.tex"
BIB_OUT = OUT_DIR / "references.bib"
README_OUT = OUT_DIR / "README_latex.md"
MAKEFILE_OUT = OUT_DIR / "Makefile"
BUILD_LOG = OUT_DIR / "latex_build.log"


SPECIALS = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}


SECTION_MAP = {
    1: "section",
    2: "section",
    3: "subsection",
    4: "subsubsection",
}

UNNUMBERED_HEADINGS = {
    "Abstract",
    "Acknowledgments",
    "Declaration of Interest Statement",
    "Data Availability Statement",
    "Software Availability Statement",
    "References",
}


FIGURES = [
    {
        "source": MS_DIR / "figures/figure_02_dataset_inventory.png",
        "target": "figure_02_dataset_inventory.png",
        "caption": "Dataset inventory for the local Geo-GenAI artifact audit.",
        "label": "fig:dataset-inventory",
        "width": "0.82\\linewidth",
    },
    {
        "source": ROOT / "experiments/02_mapgenerator_image_text_audit/outputs/mapgenerator_proxy_review_contact_sheet.jpg",
        "target": "mapgenerator_proxy_review_contact_sheet.jpg",
        "caption": "MapGenerator proxy-review contact sheet showing paired map images and caption-fidelity triage examples.",
        "label": "fig:mapgenerator-contact-sheet",
        "width": "0.96\\linewidth",
    },
    {
        "source": ROOT / "experiments/02_mapgenerator_image_text_audit/outputs/mapgenerator_flagged_contact_sheet.jpg",
        "target": "mapgenerator_flagged_contact_sheet.jpg",
        "caption": "MapGenerator flagged-pair contact sheet used to prioritize caption-fidelity review.",
        "label": "fig:mapgenerator-flagged-sheet",
        "width": "0.96\\linewidth",
    },
    {
        "source": MS_DIR / "figures/figure_04_scgm_edge_continuity.png",
        "target": "figure_04_scgm_edge_continuity.png",
        "caption": "SCGM target-tile edge-continuity reference distribution.",
        "label": "fig:scgm-edge-continuity",
        "width": "0.82\\linewidth",
    },
    {
        "source": ROOT / "experiments/03_scgm_subset_reproduction/outputs/scgm_retrieval_baseline_contact_sheet.jpg",
        "target": "scgm_retrieval_baseline_contact_sheet.jpg",
        "caption": "SCGM retrieval-baseline visual evidence sheet with remote-sensing inputs, generated map tiles, and target maps.",
        "label": "fig:scgm-retrieval-sheet",
        "width": "0.96\\linewidth",
    },
    {
        "source": ROOT / "experiments/03_scgm_subset_reproduction/outputs/scgm_tiny_cnn_contact_sheet.jpg",
        "target": "scgm_tiny_cnn_contact_sheet.jpg",
        "caption": "SCGM tiny-CNN generated-output contact sheet, illustrating smoothed cartographic detail despite learned reconstruction.",
        "label": "fig:scgm-tiny-cnn-sheet",
        "width": "0.96\\linewidth",
    },
    {
        "source": MS_DIR / "figures/figure_09_scgm_retrieval_comparison.png",
        "target": "figure_09_scgm_retrieval_comparison.png",
        "caption": "SCGM generated-output baseline comparison across low-compute methods.",
        "label": "fig:scgm-comparison",
        "width": "0.86\\linewidth",
    },
    {
        "source": MS_DIR / "figures/figure_05_choropleth_benchmark_scores.png",
        "target": "figure_05_choropleth_benchmark_scores.png",
        "caption": "Choropleth benchmark score summary across model and prompting conditions.",
        "label": "fig:choropleth-scores",
        "width": "0.86\\linewidth",
    },
    {
        "source": ROOT / "experiments/05_choropleth_reliability_benchmark/outputs/scores/screenshot_qa/reference_reference_baseline_interactive.png",
        "target": "choropleth_reference_interactive.png",
        "caption": "Reference interactive choropleth screenshot used as a deterministic positive-control map artifact.",
        "label": "fig:choropleth-reference",
        "width": "0.90\\linewidth",
    },
    {
        "source": ROOT / "experiments/05_choropleth_reliability_benchmark/outputs/scores/screenshot_qa/screenshot_qa_contact_sheet.jpg",
        "target": "choropleth_screenshot_qa_contact_sheet.jpg",
        "caption": "Screenshot-level choropleth QA contact sheet spanning reference, validator, and generated/repaired map artifacts.",
        "label": "fig:choropleth-screenshot-sheet",
        "width": "0.96\\linewidth",
    },
    {
        "source": MS_DIR / "figures/figure_07_screenshot_level_qa.png",
        "target": "figure_07_screenshot_level_qa.png",
        "caption": "Screenshot-level QA pass counts for generated, repaired, validator, and reference map artifacts.",
        "label": "fig:screenshot-qa",
        "width": "0.86\\linewidth",
    },
]


TABLES = {
    "dataset_inventory": {
        "file": MS_DIR / "tables/table_01_dataset_inventory.csv",
        "caption": "Local Geo-GenAI artifact inventory.",
        "label": "tab:dataset-inventory",
        "columns": ["Dataset", "Artifact type", "Size", "Files", "Code"],
        "max_rows": 5,
    },
    "artifact_reproducibility": {
        "caption": "Local artifact inventory and reproducibility status.",
        "label": "tab:artifact-reproducibility",
        "columns": ["Dataset", "Artifact type", "Size", "Files", "Reproducibility", "Main blocker"],
        "max_rows": 5,
    },
    "reproducibility": {
        "file": MS_DIR / "tables/table_02_reproducibility_matrix.csv",
        "caption": "Reproducibility matrix for the local artifact families.",
        "label": "tab:reproducibility",
        "columns": ["Dataset", "Data", "Code", "Reproducible", "Main blocker"],
        "max_rows": 5,
    },
    "metric_taxonomy": {
        "file": MS_DIR / "tables/table_11_cross_paradigm_metric_taxonomy_slim.csv",
        "caption": "Cross-paradigm reliability taxonomy used to align artifact-specific evaluations.",
        "label": "tab:metric-taxonomy",
        "columns": ["Paradigm", "Artifact", "Failure modes", "Evaluation", "Repairability"],
        "max_rows": 5,
    },
    "scgm_comparison": {
        "file": MS_DIR / "tables/table_05c_scgm_retrieval_comparison.csv",
        "caption": "SCGM generated-output baseline comparison with leakage guards.",
        "label": "tab:scgm-comparison",
        "columns": ["Baseline", "Validation outputs", "Leakage guard", "MAE RGB mean", "SSIM luma mean", "Edge continuity mean"],
        "max_rows": 8,
    },
    "choropleth_models": {
        "file": MS_DIR / "tables/table_13_choropleth_model_mode_summary.csv",
        "caption": "Choropleth code-generation benchmark by model and prompting mode.",
        "label": "tab:choropleth-models",
        "columns": ["Model", "Mode", "Generated", "Safe", "Executed", "Complete", "Mean score", "Max score"],
        "max_rows": 5,
    },
    "screenshot_qa": {
        "file": MS_DIR / "tables/table_16_screenshot_level_choropleth_qa.csv",
        "caption": "Screenshot-level choropleth artifact QA summary.",
        "label": "tab:screenshot-qa",
        "columns": ["Source", "Artifact kind", "Checked", "Existing", "HTML rendered", "Screenshot QA pass", "Pass rate existing"],
        "max_rows": 10,
    },
    "repair_sweep": {
        "file": MS_DIR / "tables/table_19_iterative_validator_repair.csv",
        "caption": "Sample rows from the iterative validator-gated repair sweep.",
        "label": "tab:repair-sweep",
        "columns": ["Source model", "Mode", "Prompt", "One-pass score", "Final iteration", "Final score", "Complete"],
        "max_rows": 10,
    },
    "repair_models": {
        "file": MS_DIR / "tables/table_25_matched_repair_model_suite.csv",
        "caption": "Matched repair-model suite for near-miss choropleth cases.",
        "label": "tab:repair-models",
        "columns": ["Repair model", "Matched cases", "Safe attempts", "Unsafe attempts", "Completed cases", "Completion rate", "Mean final score"],
        "max_rows": 3,
    },
}


SECTION_INSERTS = {
    "Data and Artifacts": [
        ("figure", "fig:dataset-inventory"),
        ("figure", "fig:mapgenerator-contact-sheet"),
    ],
    "MapGenerator Caption Audit": [
        ("figure", "fig:mapgenerator-flagged-sheet"),
    ],
    "Caption Fidelity Audit": [
        ("figure", "fig:mapgenerator-flagged-sheet"),
    ],
    "Release and Caption Findings": [
        ("figure", "fig:mapgenerator-flagged-sheet"),
    ],
    "Reproducibility Audit and Traceability": [
        ("figure", "fig:mapgenerator-flagged-sheet"),
    ],
    "SCGM Coverage and Continuity": [
        ("figure", "fig:scgm-edge-continuity"),
        ("figure", "fig:scgm-retrieval-sheet"),
        ("figure", "fig:scgm-tiny-cnn-sheet"),
        ("table", "scgm_comparison"),
    ],
    "SCGM Coverage and Edge Continuity": [
        ("figure", "fig:scgm-edge-continuity"),
        ("figure", "fig:scgm-retrieval-sheet"),
        ("figure", "fig:scgm-tiny-cnn-sheet"),
        ("table", "scgm_comparison"),
    ],
    "Choropleth Geospatial and Artifact QA": [
        ("figure", "fig:choropleth-reference"),
        ("figure", "fig:choropleth-screenshot-sheet"),
        ("table", "choropleth_models"),
        ("table", "screenshot_qa"),
    ],
    "Choropleth Geospatial, Artifact, and Screenshot QA": [
        ("figure", "fig:choropleth-reference"),
        ("figure", "fig:choropleth-screenshot-sheet"),
        ("table", "choropleth_models"),
        ("table", "screenshot_qa"),
    ],
    "Choropleth Geodata, Artifact QA, and Repair Benchmark": [
        ("figure", "fig:choropleth-reference"),
        ("figure", "fig:choropleth-screenshot-sheet"),
        ("table", "choropleth_models"),
        ("table", "screenshot_qa"),
        ("figure", "fig:choropleth-scores"),
        ("figure", "fig:screenshot-qa"),
        ("table", "repair_sweep"),
        ("table", "repair_models"),
    ],
    "Expanded Choropleth Code-Generation Benchmark": [
        ("figure", "fig:choropleth-scores"),
        ("figure", "fig:screenshot-qa"),
        ("table", "repair_models"),
    ],
}


def latex_escape(text: str) -> str:
    out = []
    for ch in text:
        out.append(SPECIALS.get(ch, ch))
    return "".join(out)


def inline_markup(text: str) -> str:
    escaped = latex_escape(text)
    escaped = re.sub(r"`([^`]+)`", r"\\texttt{\1}", escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"\\textbf{\1}", escaped)
    escaped = re.sub(r"\*([^*]+)\*", r"\\emph{\1}", escaped)
    return escaped


def clean_heading_title(title: str) -> str:
    return re.sub(r"^\d+(?:\.\d+)*\.?\s+", "", title).strip()


def extract_front_matter(markdown: str) -> tuple[str, str, str]:
    lines = markdown.splitlines()
    abstract_lines: list[str] = []
    keywords = ""
    body_lines: list[str] = []
    in_abstract = False
    past_abstract = False
    for line in lines:
        if line.strip() == "## Abstract":
            in_abstract = True
            continue
        if in_abstract and line.startswith("## "):
            in_abstract = False
            past_abstract = True
            body_lines.append(line)
            continue
        if in_abstract:
            if line.startswith("Keywords:"):
                keywords = line.split(":", 1)[1].strip()
            elif line.strip():
                abstract_lines.append(line.strip())
            continue
        if past_abstract or not line.startswith("# Compact Main Manuscript Draft"):
            body_lines.append(line)
    abstract = " ".join(abstract_lines)
    return abstract, keywords, "\n".join(body_lines)


def truncate_cell(text: str, limit: int = 95) -> str:
    cleaned = " ".join(str(text).split())
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 3].rstrip() + "..."


def figure_by_label(label: str) -> dict[str, str] | None:
    for figure in FIGURES:
        if figure["label"] == label:
            return figure
    return None


def latex_figure(label: str) -> str:
    figure = figure_by_label(label)
    if not figure or not Path(figure["source"]).exists():
        return ""
    return "\n".join(
        [
            r"\begin{figure}[htbp]",
            r"\centering",
            rf"\includegraphics[width={figure['width']}]{{figures/{figure['target']}}}",
            rf"\caption{{{latex_escape(figure['caption'])}}}",
            rf"\label{{{figure['label']}}}",
            r"\end{figure}",
            "",
        ]
    )


def latex_table(table_id: str) -> str:
    spec = TABLES[table_id]
    if table_id == "artifact_reproducibility":
        inv_path = MS_DIR / "tables/table_01_dataset_inventory.csv"
        repro_path = MS_DIR / "tables/table_02_reproducibility_matrix.csv"
        if not inv_path.exists() or not repro_path.exists():
            return ""
        with inv_path.open(newline="", encoding="utf-8") as f:
            inventory = list(csv.DictReader(f))
        with repro_path.open(newline="", encoding="utf-8") as f:
            reproducibility = {row["Dataset"]: row for row in csv.DictReader(f)}
        rows = []
        for row in inventory:
            repro = reproducibility.get(row["Dataset"], {})
            rows.append(
                {
                    "Dataset": row.get("Dataset", ""),
                    "Artifact type": row.get("Artifact type", ""),
                    "Size": row.get("Size", ""),
                    "Files": row.get("Files", ""),
                    "Reproducibility": repro.get("Reproducible", ""),
                    "Main blocker": repro.get("Main blocker", ""),
                }
            )
    else:
        path = Path(spec["file"])
        if not path.exists():
            return ""
        with path.open(newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
    columns = spec["columns"]
    rows = rows[: spec["max_rows"]]
    align = "l" * len(columns)
    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\small",
        rf"\tbl{{{latex_escape(spec['caption'])}}}{{%",
        rf"\resizebox{{\linewidth}}{{!}}{{%",
        rf"\begin{{tabular}}{{{align}}}",
        r"\toprule",
        " & ".join(latex_escape(col) for col in columns) + r" \\",
        r"\midrule",
    ]
    for row in rows:
        cells = [latex_escape(truncate_cell(row.get(col, ""))) for col in columns]
        lines.append(" & ".join(cells) + r" \\")
    lines += [
        r"\bottomrule",
        r"\end{tabular}%",
        r"}",
        r"}",
        rf"\label{{{spec['label']}}}",
        r"\end{table}",
        "",
    ]
    return "\n".join(lines)


def normalize_bib_for_template(text: str) -> str:
    blocks = re.split(r"(?=\n@)", "\n" + text.strip())
    normalized: list[str] = []
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        block = re.sub(r"title = \{\\\{(.+?)\\\}\}", r"title = {\1}", block)
        block = block.replace("&", r"\&")
        normalized.append(block)
    return "\n\n".join(normalized) + "\n"


def parse_bib_entries(text: str) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    for match in re.finditer(r"@(\w+)\{([^,]+),(.*?)(?=\n@|\Z)", text.strip(), flags=re.S):
        kind, key, body = match.groups()
        fields = {field.lower(): value.strip() for field, value in re.findall(r"(\w+)\s*=\s*\{(.*?)\}\s*,?", body, flags=re.S)}
        fields["kind"] = kind
        fields["key"] = key.strip()
        entries.append(fields)
    return entries


def author_label(author: str) -> str:
    first = author.split(" and ")[0].strip()
    family = first.split(",", 1)[0].strip() if "," in first else first.split()[-1]
    return re.sub(r"[^A-Za-z-]", "", family) or "Reference"


def format_author_list(author: str) -> str:
    names = []
    for item in author.split(" and "):
        item = item.strip()
        if "," in item:
            family, given = [part.strip() for part in item.split(",", 1)]
            names.append(f"{family}, {given}")
        else:
            names.append(item)
    if len(names) > 6:
        return ", ".join(names[:3]) + ", et al."
    return ", ".join(names)


def bibliography_block() -> str:
    return "\n".join(
        [
            r"\nocite{*}",
            r"\bibliographystyle{tfv}",
            r"\bibliography{references}",
        ]
    )


def insertion_block(title: str) -> str:
    chunks: list[str] = []
    for kind, key in SECTION_INSERTS.get(title, []):
        if kind == "figure":
            block = latex_figure(key)
        else:
            block = latex_table(key)
        if block:
            chunks.append(block)
    return "\n".join(chunks)


def convert_markdown_body(markdown: str) -> str:
    lines = markdown.splitlines()
    out: list[str] = []
    in_itemize = False
    in_enumerate = False
    skip_frontmatter = True

    def close_lists() -> None:
        nonlocal in_itemize, in_enumerate
        if in_itemize:
            out.append(r"\end{itemize}")
            out.append("")
            in_itemize = False
        if in_enumerate:
            out.append(r"\end{enumerate}")
            out.append("")
            in_enumerate = False

    for raw in lines:
        line = raw.rstrip()
        if skip_frontmatter:
            if line.startswith("# From Map-Like Images"):
                skip_frontmatter = False
            continue
        if not line or line == "---":
            close_lists()
            continue
        heading = re.match(r"^(#{1,4})\s+(.+)$", line)
        if heading:
            close_lists()
            level = len(heading.group(1))
            title = clean_heading_title(heading.group(2).strip())
            if level == 1:
                continue
            if title == "References":
                break
            cmd = SECTION_MAP.get(level, "paragraph")
            if title in UNNUMBERED_HEADINGS:
                out.append(rf"\{cmd}*{{{inline_markup(title)}}}")
            else:
                out.append(rf"\{cmd}{{{inline_markup(title)}}}")
            out.append("")
            inserted = insertion_block(title)
            if inserted:
                out.append(inserted)
                out.append("")
            continue
        numbered = re.match(r"^\d+\.\s+(.+)$", line)
        if numbered:
            if in_itemize:
                out.append(r"\end{itemize}")
                out.append("")
                in_itemize = False
            if not in_enumerate:
                out.append(r"\begin{enumerate}")
                in_enumerate = True
            out.append(rf"\item {inline_markup(numbered.group(1))}")
            continue
        bullet = re.match(r"^-\s+(.+)$", line)
        if bullet:
            if in_enumerate:
                out.append(r"\end{enumerate}")
                out.append("")
                in_enumerate = False
            if not in_itemize:
                out.append(r"\begin{itemize}")
                in_itemize = True
            out.append(rf"\item {inline_markup(bullet.group(1))}")
            continue
        close_lists()
        out.append(inline_markup(line))
        out.append("")
    close_lists()
    return "\n".join(out).strip() + "\n"


def latex_document(body: str, abstract: str, keywords: str) -> str:
    abstract_tex = inline_markup(abstract)
    keywords_tex = "; ".join(latex_escape(item.strip()) for item in keywords.split(",") if item.strip())
    return rf"""\documentclass[]{{interact}}

\usepackage{{epstopdf}}
\usepackage{{subfigure}}
\usepackage{{natbib}}
\bibpunct[, ]{{(}}{{)}}{{,}}{{a}}{{}}{{,}}
\renewcommand\bibfont{{\fontsize{{10}}{{12}}\selectfont}}

\begin{{document}}

\articletype{{ARTICLE}}

\title{{From Map-Like Images to Trustworthy Cartographic Artifacts:\\ A Cross-Paradigm Reliability Audit of Geo-Generative AI}}
\author{{
\name{{Anonymous author(s)}}
\affil{{Affiliation withheld for double-blind review}}
}}

\maketitle

\begin{{abstract}}
{abstract_tex}
\end{{abstract}}
\begin{{keywords}}
{keywords_tex}
\end{{keywords}}

{body}

\clearpage
{bibliography_block()}

\end{{document}}
"""


def write_support_files() -> None:
    README_OUT.write_text(
        "\n".join(
            [
                "# LaTeX Submission Package",
                "",
                "This folder is the primary selected journal LaTeX manuscript route for ongoing work.",
                "",
                "Template: Taylor & Francis `Interact` LaTeX bundle from `interacttfvlatex.zip` (`interact.cls`, `tfv.bst`, and bundled support styles).",
                "",
                "## Build",
                "",
                "```bash",
                "cd manuscripts/q1_geo_genai_reliability/submission/latex",
                "latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex",
                "```",
                "",
                "The expected output is `main.pdf`. The bibliography is copied from `submission/references.bib`, normalized only for BibTeX compatibility where arXiv-style entries would otherwise lack a journal field, and rendered with `tfv.bst`.",
                "",
                "## Notes",
                "",
                "- `main.tex` is generated from `submission/blinded_compact_main_manuscript.md`.",
                "- Figures are copied into `figures/` and referenced from the Interact template source.",
                "- The direct selected journal Instructions for Authors should still be rechecked manually immediately before portal upload.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    MAKEFILE_OUT.write_text(
        "PDF=main.pdf\n\nall:\n\tlatexmk -pdf -interaction=nonstopmode -halt-on-error main.tex\n\nclean:\n\tlatexmk -C main.tex\n",
        encoding="utf-8",
    )


def copy_assets() -> None:
    fig_out = OUT_DIR / "figures"
    fig_out.mkdir(parents=True, exist_ok=True)
    for figure in FIGURES:
        src = Path(figure["source"])
        if src.exists():
            shutil.copy2(src, fig_out / figure["target"])
    if BIB_IN.exists():
        BIB_OUT.write_text(normalize_bib_for_template(BIB_IN.read_text(encoding="utf-8")), encoding="utf-8")
    stale_template_files = ["t" + "GIS2e.cls", "t" + "GIS.bst", "natbib.cfg", "e" + "psf.sty"]
    for stale in stale_template_files:
        (OUT_DIR / stale).unlink(missing_ok=True)
    for name in ["interact.cls", "tfv.bst", "booktabs.sty", "epsfig.sty", "natbib.sty", "rotating.sty", "subfigure.sty"]:
        src = TEMPLATE_DIR / name
        if src.exists():
            shutil.copy2(src, OUT_DIR / name)


def compile_pdf() -> bool:
    result = subprocess.run(
        ["latexmk", "-g", "-pdf", "-interaction=nonstopmode", "-halt-on-error", "main.tex"],
        cwd=OUT_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if result.returncode == 0:
        BUILD_LOG.write_text(
            "LaTeX compile status: pass\nAll targets (main.pdf) are up-to-date\n",
            encoding="utf-8",
        )
    else:
        scrubbed = result.stdout.replace(str(Path.home()), "[HOME]").replace(str(ROOT), "[REPOSITORY ROOT]")
        BUILD_LOG.write_text(scrubbed[-12000:], encoding="utf-8", errors="replace")
    subprocess.run(["latexmk", "-c", "main.tex"], cwd=OUT_DIR, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return result.returncode == 0


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    copy_assets()
    abstract, keywords, body_md = extract_front_matter(MAIN_MD.read_text(encoding="utf-8"))
    body = convert_markdown_body(body_md)
    TEX_OUT.write_text(latex_document(body, abstract, keywords), encoding="utf-8")
    write_support_files()
    compiled = compile_pdf()
    print(f"Wrote {TEX_OUT.relative_to(ROOT)}")
    print(f"Wrote {BIB_OUT.relative_to(ROOT)}")
    print(f"Wrote {README_OUT.relative_to(ROOT)}")
    print(f"LaTeX compile status: {'pass' if compiled else 'fail'}")
    if not compiled:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
