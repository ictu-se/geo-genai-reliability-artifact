# LaTeX Submission Package

This folder is the primary selected journal LaTeX manuscript route for ongoing work.

Template: Taylor & Francis `Interact` LaTeX bundle from `interacttfvlatex.zip` (`interact.cls`, `tfv.bst`, and bundled support styles).

## Build

```bash
cd manuscripts/q1_geo_genai_reliability/submission/latex
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

The expected output is `main.pdf`. The bibliography is copied from `submission/references.bib`, normalized only for BibTeX compatibility where arXiv-style entries would otherwise lack a journal field, and rendered with `tfv.bst`.

## Notes

- `main.tex` is generated from `submission/blinded_compact_main_manuscript.md`.
- Figures are copied into `figures/` and referenced from the Interact template source.
- The direct selected journal Instructions for Authors should still be rechecked manually immediately before portal upload.
